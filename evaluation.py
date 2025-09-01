from __future__ import annotations

import os
import sys
import spacy
from spacy.training import Example
from spacy.tokens import DocBin
from typing import List, Dict, Tuple, Optional

try:
    import pandas as pd
except Exception as exc:  # noqa: BLE001
    pd = None  # type: ignore[assignment]


def load_model(model_dir: str) -> spacy.Language:
    if not os.path.isdir(model_dir):
        raise FileNotFoundError(f"Model directory not found: {model_dir}")
    try:
        return spacy.load(model_dir)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Failed to load model: {model_dir}\n{exc}")


def load_docs(docbin_path: str, vocab) -> list:
    if not os.path.exists(docbin_path):
        raise FileNotFoundError(f"Evaluation data not found: {docbin_path}")
    db = DocBin().from_disk(docbin_path)
    docs = list(db.get_docs(vocab))
    if len(docs) == 0:
        raise ValueError("No documents found in the evaluation DocBin.")
    return docs


def get_gold_labels(docs: list) -> set[str]:
    labels: set[str] = set()
    for d in docs:
        for ent in d.ents:
            labels.add(ent.label_)
    return labels


def evaluate(nlp: spacy.Language, gold_docs: list) -> dict:
    # Example should be given unprocessed Doc and Gold as recommended. Unprocessed Doc only needs tokenizer
    examples: list[Example] = []
    for gold_doc in gold_docs:
        pred_doc = nlp.make_doc(gold_doc.text)
        examples.append(Example(pred_doc, gold_doc))
    # Evaluate through pipeline
    return nlp.evaluate(examples)


def build_per_label_metrics_df(scores: dict):
    if pd is None:
        return None
    ents_per_type = scores.get("ents_per_type", {}) or {}
    records = []
    for label, m in ents_per_type.items():
        records.append(
            {
                "Pattern": label,
                "Precision": float(m.get("p", 0.0)),
                "Recall": float(m.get("r", 0.0)),
                "F1": float(m.get("f", 0.0)),
            }
        )
    df = pd.DataFrame(records)
    if not df.empty:
        df = df.sort_values(by=["F1", "Precision", "Recall"], ascending=False, ignore_index=True)
    return df


def _collect_ent_char_spans(doc) -> List[Tuple[int, int, str]]:
    spans: List[Tuple[int, int, str]] = []
    for ent in doc.ents:
        spans.append((ent.start_char, ent.end_char, ent.label_))
    return spans


def _label_for_token_by_char_cover(
    token, ent_spans: List[Tuple[int, int, str]]
) -> str:
    start = token.idx
    end = token.idx + len(token.text)
    for s, e, label in ent_spans:
        if start >= s and end <= e:
            return label
    return "O"


def _sentence_text_for_token(token) -> str:
    try:
        return token.sent.text
    except Exception:  # If no sentence boundaries, return entire document text
        return token.doc.text


def build_token_level_rows(
    nlp: spacy.Language, gold_docs: List[spacy.tokens.Doc]
) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []

    # Execute predictions in batch
    texts = [d.text for d in gold_docs]
    pred_docs = list(nlp.pipe(texts))

    for gold_doc, pred_doc in zip(gold_docs, pred_docs):
        gold_ent_spans = _collect_ent_char_spans(gold_doc)
        pred_ent_spans = _collect_ent_char_spans(pred_doc)

        if not gold_ent_spans and not pred_ent_spans:
            continue

        for token in gold_doc:
            gold_label = _label_for_token_by_char_cover(token, gold_ent_spans)
            pred_label = _label_for_token_by_char_cover(token, pred_ent_spans)

            # Target tokens are those labeled in either Gold or Pred
            if gold_label == "O" and pred_label == "O":
                continue

            sentence_text = _sentence_text_for_token(token)
            match = "Match" if gold_label == pred_label else "Mismatch"

            rows.append(
                {
                    "Gold NER Label": gold_label,
                    "Predicted NER Label": pred_label,
                    "Target Token": token.text,
                    "Sentence Containing Target Token": sentence_text,
                    "Match or Mismatch": match,
                }
            )

    return rows


def export_token_report_to_excel(
    nlp: spacy.Language,
    gold_docs: List[spacy.tokens.Doc],
    output_xlsx_path: str,
    per_label_df=None,
) -> str:
    if pd is None:
        raise RuntimeError(
            "pandas not found. Excel output requires pandas and openpyxl.\n"
            "Example: pip install pandas openpyxl"
        )

    rows = build_token_level_rows(nlp, gold_docs)
    if not rows:
        # Output empty file even when there are no target outputs
        df = pd.DataFrame(
            columns=[
                "Gold NER Label",
                "Predicted NER Label",
                "Target Token",
                "Sentence Containing Target Token",
                "Match or Mismatch",
            ]
        )
    else:
        df = pd.DataFrame(rows)

    # Create directory (only if path contains directory)
    dir_path = os.path.dirname(output_xlsx_path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    # Save to Excel (multiple sheets: token_details / label_metrics)
    try:
        if per_label_df is None:
            df.to_excel(output_xlsx_path, index=False)
        else:
            with pd.ExcelWriter(output_xlsx_path, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="token_details", index=False)
                per_label_df.to_excel(writer, sheet_name="label_metrics", index=False)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Failed to output Excel: {output_xlsx_path}\n{exc}")

    return output_xlsx_path


def main(model_dir: str = "./output_v4/model-best", dev_path: str = "test.spacy", output_path: str = "eval_all.xlsx") -> int:
    # Prefer GPU usage (if available)
    spacy.prefer_gpu()

    nlp = load_model(model_dir)

    if "ner" not in nlp.pipe_names:
        print("Warning: Model does not contain `ner` component. NER metrics cannot be calculated.", file=sys.stderr)

    gold_docs = load_docs(dev_path, nlp.vocab)

    # Label validation
    gold_labels = get_gold_labels(gold_docs)
    model_labels = set()
    try:
        model_labels = set(nlp.get_pipe("ner").labels)  # type: ignore[arg-type]
    except Exception:
        pass

    if gold_labels and model_labels:
        missing_in_model = sorted(list(gold_labels - model_labels))
        if missing_in_model:
            print("Warning: The following Gold labels are not registered in the model (possible insufficient training): " + ", ".join(missing_in_model), file=sys.stderr)

    scores = evaluate(nlp, gold_docs)

    # Macro display
    ents_p = scores.get("ents_p")
    ents_r = scores.get("ents_r")
    ents_f = scores.get("ents_f")
    if ents_f is not None:
        print(f"Overall Precision (NER): {ents_p:.3f}")
        print(f"Overall Recall (NER): {ents_r:.3f}")
        print(f"Overall F1 (NER): {ents_f:.3f}")
    else:
        print("Overall Precision (NER): N/A")
        print("Overall Recall (NER): N/A")
        print("Overall F1 (NER): N/A")

    # Per label
    ents_per_type = scores.get("ents_per_type", {}) or {}
    for label, m in ents_per_type.items():
        p = m.get("p", 0.0)
        r = m.get("r", 0.0)
        f = m.get("f", 0.0)
        print(f"{label}: Precision={p:.3f}, Recall={r:.3f}, F1={f:.3f}")

    # Output token-level detailed report to Excel
    base = os.path.splitext(os.path.basename(dev_path))[0]
    xlsx_path = output_path
    try:
        per_label_df = build_per_label_metrics_df(scores)
        saved_path = export_token_report_to_excel(nlp, gold_docs, xlsx_path, per_label_df=per_label_df)
        print(f"Token-level detailed results and per-label metrics have been output: {saved_path}")
    except RuntimeError as exc:  # pandas not installed, etc.
        print(str(exc), file=sys.stderr)

    return 0


if __name__ == "__main__":
    MODEL_PATH = "./output/model-best"
    DEV_PATH = "test.spacy"
    OUTPUT_PATH = "eval_test.xlsx"
    sys.exit(main(MODEL_PATH, DEV_PATH, OUTPUT_PATH))