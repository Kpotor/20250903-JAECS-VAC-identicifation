import spacy
from spacy.matcher import DependencyMatcher
from collections import defaultdict

# 汎用関数
def filter_no_obj(token_ids, doc):
    result = True
    anchor_verb = doc[token_ids[0]]
    if any(child.dep_ == "dobj" for child in anchor_verb.children):
        result = False
    return result

def filter_passive(token_ids, doc):
    result = True
    anchor_verb = doc[token_ids[0]]
    if any(child.dep_ == "auxpass" for child in anchor_verb.children):
        result = False
    return result

def filter_past_participle_modifier(token_ids, doc):
    result = True
    anchor_verb = doc[token_ids[0]]
    if anchor_verb.tag_ == "VBN":
        # 現在完了形（have + VBN）または受動態（auxpass付き）の場合はTrue
        has_have_aux = any(child.dep_ == "aux" and child.lemma_ == "have" for child in anchor_verb.children)
        has_auxpass = any(child.dep_ == "auxpass" for child in anchor_verb.children)
        
        # どちらの条件も満たさない場合（単独の過去分詞修飾語）のみFalse
        if not (has_have_aux or has_auxpass):
            result = False
    return result

def word_order_check(anchor_verb, token, doc):
    if token.i < anchor_verb.i:
        return False
    return True

# 前置詞の指定
target_prep_simple = [
    "about", 
    "across", 
    "after", 
    "against", 
    "around",
    "round", 
    "as", 
    "at", 
    "between", 
    "for", 
    "from", 
    "in", 
    "into",
    "like",
    "of",
    "off",
    "on",
    "upon",
    "over",
    "through",
    "to",
    "toward",
    "towards",
    "under",
    "with"
]


target_prep_complex = [
    "about", "against", "as", "at", "between", 
    "among", "by", "for", "from", "in", "into", 
    "of", "off", "on", "upon", "over", "to", 
    "toward", "towards", "with"]


# DependencyMatcherを作成 ------------------------------------------------------------
def create_dependency_matcher(nlp):
    
    matcher = DependencyMatcher(nlp.vocab)

    V_ncomp_pattern = [
    {
        "RIGHT_ID": "anchor_verb",
        "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
    },
    {
        "LEFT_ID": "anchor_verb",
        "REL_OP": ">",
        "RIGHT_ID": "n-comp",
        "RIGHT_ATTRS": {
            "POS": {"IN": ["NOUN", "PRON", "PROPN"]},
            "DEP": {"IN":["attr", "oprd"]}
        }
    }
    ]
    
    V_pron_refl_pattern = [
    {
        "RIGHT_ID": "anchor_verb",
        "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
    },
    {
        "LEFT_ID": "anchor_verb",
        "REL_OP": ">",
        "RIGHT_ID": "pron-refl",
        "RIGHT_ATTRS": {
            "DEP": {"IN": ["dobj", "attr"]},
            "LEMMA": {"IN": [
                "myself",
                "yourself",
                "yourselves",
                "ourselves", 
                "himself", 
                "herself", 
                "itself", 
                "themselves",
                "oneself"
            ]}
        }
    }
    ]
    
    V_adj_pattern = [
    {
        "RIGHT_ID": "anchor_verb",
        "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
    },
    {
        "LEFT_ID": "anchor_verb",
        "REL_OP": ">",
        "RIGHT_ID": "adj",
        "RIGHT_ATTRS": {
            "POS": "ADJ",
            "DEP": {"IN": ["acomp", "oprd", "advcl"]},
        }
    }
    ]


    V_ing_pattern1 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "ing",
            "RIGHT_ATTRS": {
                "TAG": "VBG",
                "DEP": {"IN": ["xcomp"]},
            }
        }
    ]

    V_ing_pattern2 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {
                "TAG": {"REGEX": "^V"},
                "DEP":"aux"}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": "<",
            "RIGHT_ID": "ing",
            "RIGHT_ATTRS": {
                "TAG": "VBG",
            }
        }
    ]

    # V + being + V-ed を捕捉
    V_ing_pattern3= [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "past_participle",
            "RIGHT_ATTRS": {
                "TAG": "VBN",  # 過去分詞
                "DEP": {"IN": ["xcomp"]}
            }
        },
        {
            "LEFT_ID": "past_participle",
            "REL_OP": ">",
            "RIGHT_ID": "being",
            "RIGHT_ATTRS": {
                "TAG": "VBG",
                "LEMMA": "be",  # beingであることを確認
                "DEP": "auxpass"  # 受動態の助動詞
            }
        }
    ]


    # V + having + V-ed を捕捉
    V_ing_pattern4 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "past_participle",
            "RIGHT_ATTRS": {
                "TAG": "VBN",  # 過去分詞
                "DEP": {"IN": ["xcomp"]}
            }
        },
        {
            "LEFT_ID": "past_participle",
            "REL_OP": ">",
            "RIGHT_ID": "having",
            "RIGHT_ATTRS": {
                "TAG": "VBG",
                "ORTH": "having",  # havingであることを確認
                "DEP": "aux"  # 助動詞
            }
        }
    ]


    V_toinf_pattern1 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "infcl_verb",
            "RIGHT_ATTRS": {
                "TAG": "VB",
                "DEP": {"IN": ["xcomp", "advcl"]},
            }
        },
        {
            "LEFT_ID": "infcl_verb",
            "REL_OP": ">",
            "RIGHT_ID": "to",
            "RIGHT_ATTRS": {
                "TAG": "TO",
                "DEP": "aux"
            }
        }
    ]


    # V to be V-ed/V-ing を捕捉
    V_toinf_pattern2= [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "infcl_verb",
            "RIGHT_ATTRS": {
                "TAG": {"IN": ["VBN", "VBG"]}, 
                "DEP": {"IN": ["xcomp", "advcl"]}
            }
        },
        {
            "LEFT_ID": "infcl_verb",
            "REL_OP": ">",
            "RIGHT_ID": "be",
            "RIGHT_ATTRS": {
                "TAG": "VB",
                "ORTH": "be",
                "DEP": {"IN": ["auxpass", "aux"]}
            }
        },
        {
            "LEFT_ID": "infcl_verb",
            "REL_OP": ">",
            "RIGHT_ID": "to",
            "RIGHT_ATTRS": {
                "TAG": "TO",
                "DEP": "aux"
            }
        }
    ]

    # V to have V-ed を補足
    V_toinf_pattern3 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "infcl_verb",
            "RIGHT_ATTRS": {
                "TAG": "VBN",  
                "DEP": {"IN": ["xcomp", "advcl"]}
            }
        },
        {
            "LEFT_ID": "infcl_verb",
            "REL_OP": ">",
            "RIGHT_ID": "have",
            "RIGHT_ATTRS": {
                "TAG": "VB",
                "ORTH": "have",
                "DEP": "aux"
            }
        },
        {
            "LEFT_ID": "infcl_verb",
            "REL_OP": ">",
            "RIGHT_ID": "to",
            "RIGHT_ATTRS": {
                "TAG": "TO",
                "DEP": "aux"
            }
        }
    ]
    
    V_that_pattern = [
    {
        "RIGHT_ID": "anchor_verb",
        "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
    },
    {
        "LEFT_ID": "anchor_verb",
        "REL_OP": ">",
        "RIGHT_ID": "ccomp_verb",
        "RIGHT_ATTRS": {
            "TAG": {"REGEX": "^[VM]"},
            "DEP": "ccomp"
        }
    },
    {
        "LEFT_ID": "ccomp_verb",
        "REL_OP": ">",
        "RIGHT_ID": "comp_cl_subj",
        "RIGHT_ATTRS": {
            "DEP": {"IN": ["nsubj", "nsubjpass", "expl", "csubj"]}
        }
    },
    ]
    
    
    V_wh_pattern = [
    {
        "RIGHT_ID": "anchor_verb",
        "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
    },
    {
        "LEFT_ID": "anchor_verb",
        "REL_OP": ">",
        "RIGHT_ID": "ccomp_token",
        "RIGHT_ATTRS": {
            "DEP": "ccomp",
        }
    },
    {
        "LEFT_ID": "ccomp_token",
        "REL_OP": ">",
        "RIGHT_ID": "comp_cl_subj",
        "RIGHT_ATTRS": {
            "DEP": {"IN": ["nsubj", "nsubjpass", "expl"]}
        }
    },
    {
        "LEFT_ID": "ccomp_token",
        "REL_OP": ">>",
        "RIGHT_ID": "wh-token",
        "RIGHT_ATTRS": {
            "LEMMA": {"IN": ["what", "who", "which", "whom", "where", "when", "why", "how", "whether", "if"]},
        }
    },
    ]
    
    
    V_whtoinf_pattern = [
    {
        "RIGHT_ID": "anchor_verb",
        "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
    },
    {
        "LEFT_ID": "anchor_verb",
        "REL_OP": ">",
        "RIGHT_ID": "comp_token",
        "RIGHT_ATTRS": {
            "DEP": {"IN": ["xcomp", "ccomp"]},
        }
    },
    {
        "LEFT_ID": "comp_token",
        "REL_OP": ">>",
        "RIGHT_ID": "wh-token",
        "RIGHT_ATTRS": {
            "LEMMA": {"IN": ["what", "who", "which", "whom", "where", "when", "why", "how", "whether"]},
        }
    },
    {
        "LEFT_ID": "comp_token",
        "REL_OP": ">",
        "RIGHT_ID": "to",
        "RIGHT_ATTRS": {
            "TAG": "TO",
            "DEP": "aux"
        }
    }
    ]
    
    V_prep_n_pattern1 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "prep_token",
            "RIGHT_ATTRS": {
                "DEP": {"IN": ["prep"]},
                "LEMMA": {"IN": target_prep_simple}
            }
        },
    ]

    V_prep_n_pattern2 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "adv_token",
            "RIGHT_ATTRS": {
                "DEP": "advmod",
                "LEMMA": {"IN": ["away"]}
            }
        },
        {
            "LEFT_ID": "adv_token",
            "REL_OP": ">",
            "RIGHT_ID": "prep_token",
            "RIGHT_ATTRS": {
                "DEP": "prep",
                "LEMMA": {"IN": target_prep_simple}
            }
        }
    ]

    # passive pattern
    V_prep_n_pattern3 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "prep_token",
            "RIGHT_ATTRS": {
                "DEP": "prep",
                "LEMMA": {"IN": target_prep_simple}
            }
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "auxpass_token",
            "RIGHT_ATTRS": {"DEP": "auxpass"}
        },
    ]
    
    V_by_ing_pattern = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "by_token",
            "RIGHT_ATTRS": {
                "DEP": "prep",
                "LEMMA": "by"
            }
        },
        {
            "LEFT_ID": "by_token",
            "REL_OP": ">",
            "RIGHT_ID": "ing_token",
            "RIGHT_ATTRS": {
                "DEP": "pcomp",
                "TAG": "VBG"
            }
        }
    ]    


    V_out_of_n_pattern = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "out_token",
            "RIGHT_ATTRS": {
                "LEMMA": "out"
            }
        },
        {
            "LEFT_ID": "out_token",
            "REL_OP": ".",
            "RIGHT_ID": "of_token",
            "RIGHT_ATTRS": {
                "LEMMA": "of"
            }
        }
    ]


    V_onto_n_pattern1 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "on_token",
            "RIGHT_ATTRS": {
                "LEMMA": "on"
            }
        },
        {
            "LEFT_ID": "on_token",
            "REL_OP": ".",
            "RIGHT_ID": "to_token",
            "RIGHT_ATTRS": {
                "LEMMA": "to",
                "TAG": "IN"
            }
        }
    ]

    V_onto_n_pattern2 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "prep_token",
            "RIGHT_ATTRS": {
                "DEP": "prep",
                "LEMMA": "onto"
            }
        },
    ]
    

    V_n_ncomp_pattern1 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "comp_token",
            "RIGHT_ATTRS": {
                "TAG": {"REGEX": "^N"},
                "DEP": {"IN": ["oprd", "ccomp"]},
            }
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "dobj_token",
            "RIGHT_ATTRS": {
                "DEP": "dobj",
                "POS": {"IN": ["NOUN", "PROPN", "PRON"]}
            }
        },
    ]

    V_n_ncomp_pattern2 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "comp_token",
            "RIGHT_ATTRS": {
                "TAG": {"REGEX": "^N"},
                "DEP": {"IN": ["ccomp"]},
            }
        },
        {
            "LEFT_ID": "comp_token",
            "REL_OP": ">",
            "RIGHT_ID": "dobj_token",
            "RIGHT_ATTRS": {
                "DEP": "nsubj",
                "POS": {"IN": ["NOUN", "PROPN", "PRON"]}
            }
        },
    ]

    # passive pattern
    V_n_ncomp_pattern3 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {
                "TAG": "VBN"
                }
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "comp_token",
            "RIGHT_ATTRS": {
                "TAG": {"REGEX": "^N"},
                "DEP": {"IN": ["oprd"]},
            }
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "auxpass_token",
            "RIGHT_ATTRS": {
                "DEP": "auxpass",
            }
        },
    ]


    V_n_nobj_pattern1 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "dative_token",
            "RIGHT_ATTRS": {
                "DEP": "dative",
                "POS": {"IN": ["NOUN", "PRON", "PROPN"]}
                }
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "dobj_token",
            "RIGHT_ATTRS": {
                "DEP": "dobj",
            }
        }
    ]

    V_n_nobj_pattern2 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "auxpass_token",
            "RIGHT_ATTRS": {
                "DEP": "auxpass"}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "dobj_token",
            "RIGHT_ATTRS": {
                "DEP": "dobj",
            }
        }
    ]
    
    
    V_n_adj_pattern1 = [
    {
        "RIGHT_ID": "anchor_verb",
        "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
    },
    {
        "LEFT_ID": "anchor_verb",
        "REL_OP": ">",
        "RIGHT_ID": "comp_token",
        "RIGHT_ATTRS": {
            "DEP": {"IN": ["oprd", "advcl", "xcomp"]},
            "POS": "ADJ"
        }
    },
    {
        "LEFT_ID": "anchor_verb",
        "REL_OP": ">",
        "RIGHT_ID": "dobj_token",
        "RIGHT_ATTRS": {
            "DEP": "dobj",
            "POS": {"IN": ["NOUN", "PRON", "PROPN"]}
        }
    },
    ]

    V_n_adj_pattern2 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "comp_token",
            "RIGHT_ATTRS": {
                "DEP": "ccomp",
                "POS": "ADJ"
            }
        },
        {
            "LEFT_ID": "comp_token",
            "REL_OP": ">",
            "RIGHT_ID": "nsubj_token",
            "RIGHT_ATTRS": {
                "DEP": "nsubj",
                "POS": {"IN": ["NOUN", "PRON", "PROPN"]}
            }
        }
    ]

    V_n_adj_pattern3 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "comp_token",
            "RIGHT_ATTRS": {
                "DEP": {"IN": ["oprd", "advcl", "xcomp"]},
                "POS": "ADJ"
            }
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "auxpass_token",
            "RIGHT_ATTRS": {
                "DEP": "auxpass",
            }
        }
    ]
    

    V_n_toinf_pattern1 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "comp_token",
            "RIGHT_ATTRS": {
                "DEP": "ccomp",
                "TAG": {"REGEX": "^V"}
            }
        },
        {
            "LEFT_ID": "comp_token",
            "REL_OP": ">",
            "RIGHT_ID": "nsubj_token",
            "RIGHT_ATTRS": {
                "DEP": "nsubj",
                "POS": {"IN": ["NOUN", "PRON", "PROPN"]}
            }
        },
        {
            "LEFT_ID": "comp_token",
            "REL_OP": ">",
            "RIGHT_ID": "to",
            "RIGHT_ATTRS": {
                "TAG": "TO",
            }
        }
    ]

    V_n_toinf_pattern2 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "comp_token",
            "RIGHT_ATTRS": {
                "DEP": "xcomp",
                "TAG": {"REGEX": "^V"}
            }
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "dobj_token",
            "RIGHT_ATTRS": {
                "DEP": "dobj",
                "POS": {"IN": ["NOUN", "PRON", "PROPN"]}
            }
        },
        {
            "LEFT_ID": "comp_token",
            "REL_OP": ">",
            "RIGHT_ID": "to",
            "RIGHT_ATTRS": {
                "TAG": "TO",
            }
        }
    ]

    # passive pattern
    V_n_toinf_pattern3 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "comp_token",
            "RIGHT_ATTRS": {
                "DEP": "xcomp",
                "TAG": {"REGEX": "^V"}
            }
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "auxpass_token",
            "RIGHT_ATTRS": {
                "DEP": "auxpass",
            }
        },
        {
            "LEFT_ID": "comp_token",
            "REL_OP": ">",
            "RIGHT_ID": "to",
            "RIGHT_ATTRS": {
                "TAG": "TO",
                "DEP": "aux"
            }
        }
    ]
    

    V_n_inf_pattern1 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "comp_token",
            "RIGHT_ATTRS": {
                "DEP": "ccomp",
                "TAG": {"REGEX": "VB"}
            }
        },
        {
            "LEFT_ID": "comp_token",
            "REL_OP": ">",
            "RIGHT_ID": "nsubj_token",
            "RIGHT_ATTRS": {
                "DEP": "nsubj",
                "POS": {"IN": ["NOUN", "PRON", "PROPN"]}
            }
        },
    ]

    V_n_inf_pattern2 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "comp_token",
            "RIGHT_ATTRS": {
                "DEP": "xcomp",
                "TAG": "VB"
            }
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "dobj_token",
            "RIGHT_ATTRS": {
                "DEP": "dobj",
                "POS": {"IN": ["NOUN", "PRON", "PROPN"]}
            }
        },
    ]
    
    
    V_n_that_pattern1 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "ccomp_token",
            "RIGHT_ATTRS": {
                "DEP": "ccomp",
                "TAG": {"REGEX": "^V"}
            }
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "dobj_token",
            "RIGHT_ATTRS": {
                "DEP": "dobj",
                "POS": {"IN": ["NOUN", "PRON", "PROPN"]}
            }
        },
        {
            "LEFT_ID": "ccomp_token",
            "REL_OP": ">",
            "RIGHT_ID": "comp_cl_subj",
            "RIGHT_ATTRS": {
                "DEP": {"IN": ["nsubj", "nsubjpass", "expl"]}
            }
        },
    ]

    # passive pattern
    V_n_that_pattern2 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "ccomp_token",
            "RIGHT_ATTRS": {
                "DEP": "ccomp",
                "TAG": {"REGEX": "^V"}
            }
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "auxpass_token",
            "RIGHT_ATTRS": {
                "DEP": "auxpass",
            }
        },
        {
            "LEFT_ID": "ccomp_token",
            "REL_OP": ">",
            "RIGHT_ID": "comp_cl_subj",
            "RIGHT_ATTRS": {
                "DEP": {"IN": ["nsubj", "nsubjpass", "expl"]}
            }
        }
    ]


    V_n_wh_pattern1 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "ccomp_token",
            "RIGHT_ATTRS": {
                "DEP": "ccomp",
                "TAG": {"REGEX": "^V"}
            }
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "dobj_token",
            "RIGHT_ATTRS": {
                "DEP": "dobj",
            }
        },
        {
            "LEFT_ID": "ccomp_token",
            "REL_OP": ">>",
            "RIGHT_ID": "wh-token",
            "RIGHT_ATTRS": {
                "LEMMA": {"IN": ["what", "who", "which", "whom", "where", "when", "why", "how", "whether", "if"]},
            }
        },
        {
            "LEFT_ID": "ccomp_token",
            "REL_OP": ">",
            "RIGHT_ID": "comp_cl_subj",
            "RIGHT_ATTRS": {
                "DEP": {"IN": ["nsubj", "nsubjpass", "expl"]}
            }
        },
    ]

    # passive pattern
    V_n_wh_pattern2 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "ccomp_token",
            "RIGHT_ATTRS": {
                "DEP": "ccomp",
                "TAG": {"REGEX": "^V"}
            }
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "auxpass_token",
            "RIGHT_ATTRS": {
                "DEP": "auxpass",
            }
        },
        {
            "LEFT_ID": "ccomp_token",
            "REL_OP": ">>",
            "RIGHT_ID": "wh-token",
            "RIGHT_ATTRS": {
                "LEMMA": {"IN": ["what", "who", "which", "whom", "where", "when", "why", "how", "whether", "if"]},
            }
        },
    ]


    V_n_whtoinf_pattern1 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "dobj_token",
            "RIGHT_ATTRS": {
                "DEP": "dobj",
            }
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "comp_token",
            "RIGHT_ATTRS": {
                "DEP": {"IN": ["xcomp", "ccomp"]},
                "TAG": {"REGEX": "^V"}
            }
        },
        {
            "LEFT_ID": "comp_token",
            "REL_OP": ">>",
            "RIGHT_ID": "wh-token",
            "RIGHT_ATTRS": {
                "LEMMA": {"IN": ["what", "who", "which", "whom", "where", "when", "why", "how", "whether"]},
            }
        },
        {
            "LEFT_ID": "comp_token",
            "REL_OP": ">",
            "RIGHT_ID": "to",
            "RIGHT_ATTRS": {
                "TAG": "TO",
                "DEP": "aux"
            }
        }
    ]

    # passive pattern
    V_n_whtoinf_pattern2 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "auxpass_token",
            "RIGHT_ATTRS": {
                "DEP": "auxpass",
            }
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "comp_token",
            "RIGHT_ATTRS": {
                "DEP": {"IN": ["xcomp", "ccomp"]},
            }
        },
        {
            "LEFT_ID": "comp_token",
            "REL_OP": ">>",
            "RIGHT_ID": "wh-token",
            "RIGHT_ATTRS": {
                "LEMMA": {"IN": ["what", "who", "which", "whom", "where", "when", "why", "how", "whether"]},
            }
        },
        {
            "LEFT_ID": "comp_token",
            "REL_OP": ">",
            "RIGHT_ID": "to",
            "RIGHT_ATTRS": {
                "TAG": "TO",
                "DEP": "aux"
            }
        }
    ]


    V_n_Ved_pattern1 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "comp_token",
            "RIGHT_ATTRS": {
                "DEP": "ccomp",
                "TAG": "VBN"
            }
        },
        {
            "LEFT_ID": "comp_token",
            "REL_OP": ">",
            "RIGHT_ID": "nsubj_token",
            "RIGHT_ATTRS": {
                "DEP":"nsubj",
                "POS": {"IN": ["NOUN", "PRON", "PROPN"]}
            }
        }
    ]

    # passive pattern
    V_n_Ved_pattern2 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "comp_token",
            "RIGHT_ATTRS": {
                "DEP": "xcomp",
                "TAG": "VBN"
            }
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "auxpass_token",
            "RIGHT_ATTRS": {
                "DEP":"auxpass",
            }
        }
    ]



    V_n_ing_pattern1 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "comp_token",
            "RIGHT_ATTRS": {
                "DEP": {"IN": ["ccomp", "xcomp"]},
                "TAG": "VBG"
            }
        },
        {
            "LEFT_ID": "comp_token",
            "REL_OP": ">",
            "RIGHT_ID": "nsubj_token",
            "RIGHT_ATTRS": {
                "DEP":"nsubj",
                "POS": {"IN": ["NOUN", "PRON", "PROPN"]}
            }
        }
    ]


    V_n_ing_pattern2 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "comp_token",
            "RIGHT_ATTRS": {
                "DEP": "xcomp",
                "TAG": "VBG"
            }
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "dobj_token",
            "RIGHT_ATTRS": {
                "DEP":"dobj",
                "POS": {"IN": ["NOUN", "PRON", "PROPN"]}
            }
        }
    ]

    # V + n + being V-ed 
    V_n_ing_pattern3 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "comp_token",
            "RIGHT_ATTRS": {
                "DEP": "ccomp",
                "TAG": "VBN"
            }
        },
        {
            "LEFT_ID": "comp_token",
            "REL_OP": ">",
            "RIGHT_ID": "nsubj_token",
            "RIGHT_ATTRS": {
                "DEP":"nsubjpass",
                "POS": {"IN": ["NOUN", "PRON", "PROPN"]}
            }
        },
        {
            "LEFT_ID": "comp_token",
            "REL_OP": ">",
            "RIGHT_ID": "auxpass_token",
            "RIGHT_ATTRS": {
                "DEP":"auxpass",
                "TEXT": "being"
            }
        }
    ]

    # passive pattern
    V_n_ing_pattern4 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "comp_token",
            "RIGHT_ATTRS": {
                "DEP": {"IN": ["xcomp", "advcl"]},
                "TAG": "VBG"
            }
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "auxpass_token",
            "RIGHT_ATTRS": {
                "DEP":"auxpass",
            }
        }
    ]
    
    
    V_way_pattern = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "way_token",
            "RIGHT_ATTRS": {
                "DEP": "dobj",
                "LEMMA": "way"
            }
        },
        {
            "LEFT_ID": "way_token",
            "REL_OP": ">",
            "RIGHT_ID": "poss_token",
            "RIGHT_ATTRS": {
                "DEP": "poss",
            }
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "prep_adv_token",
            "RIGHT_ATTRS": {
                "DEP": {"IN": ["prep", "advmod"]},
            }
        }
    ]


    V_n_prep_n_pattern1 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "prep_token",
            "RIGHT_ATTRS": {
                "DEP": {"IN" :["prep", "dative"]},
                "LEMMA": {"IN": target_prep_complex}
            }
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "dobj_token",
            "RIGHT_ATTRS": {
                "DEP": "dobj",
                # "POS": {"IN": ["NOUN", "PRON", "PROPN"]}
            }
        }
    ]

    # passive pattern
    V_n_prep_n_pattern2 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "prep_token",
            "RIGHT_ATTRS": {
                "DEP": {"IN": ["prep", "dative"]},
                "LEMMA": {"IN": target_prep_complex}
            }
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "auxpass_token",
            "RIGHT_ATTRS": {
                "DEP": "auxpass",
            }
        }
    ]


    V_n_out_of_n_pattern1 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "out_token",
            "RIGHT_ATTRS": {
                "LEMMA": "out"
            }
        },
        {
            "LEFT_ID": "out_token",
            "REL_OP": ".",
            "RIGHT_ID": "of_token",
            "RIGHT_ATTRS": {
                "LEMMA": "of"
            }
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "dobj_token",
            "RIGHT_ATTRS": {
                "DEP": "dobj",
                "POS": {"IN": ["NOUN", "PRON", "PROPN"]}
            }
        }
    ]

    # passive pattern
    V_n_out_of_n_pattern2 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "out_token",
            "RIGHT_ATTRS": {
                "LEMMA": "out"
            }
        },
        {
            "LEFT_ID": "out_token",
            "REL_OP": ".",
            "RIGHT_ID": "of_token",
            "RIGHT_ATTRS": {
                "LEMMA": "of"
            }
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "auxpass_token",
            "RIGHT_ATTRS": {
                "DEP": "auxpass",
            }
        }
    ]


    it_V_nadj_toinf_pattern1 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "inf-comp_token",
            "RIGHT_ATTRS": {"DEP": "xcomp"}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "introductory-it",
            "RIGHT_ATTRS": {
                "DEP": "nsubj",
                "LEMMA": "it"
                }
        },
        {
            "LEFT_ID": "inf-comp_token",
            "REL_OP": ">",
            "RIGHT_ID": "to_token",
            "RIGHT_ATTRS": {
                "DEP": "aux",
                "TAG": "TO"
            }
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "comp_token",
            "RIGHT_ATTRS": {
                "DEP": {"IN": ["attr", "acomp", "dobj"]}
                }
        }
    ]

    it_V_nadj_toinf_pattern2 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "inf-comp_token",
            "RIGHT_ATTRS": {"DEP": "advcl"}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "introductory-it",
            "RIGHT_ATTRS": {
                "DEP": "nsubj",
                "LEMMA": "it"
                }
        },
        {
            "LEFT_ID": "inf-comp_token",
            "REL_OP": ">",
            "RIGHT_ID": "to_token",
            "RIGHT_ATTRS": {
                "DEP": "aux",
                "TAG": "TO"
            }
        },
        {
            "LEFT_ID": "inf-comp_token",
            "REL_OP": ">",
            "RIGHT_ID": "for_token",
            "RIGHT_ATTRS": {
                "DEP": "mark",
                "LEMMA": "for"
            }
        },
        {
            "LEFT_ID": "inf-comp_token",
            "REL_OP": ">",
            "RIGHT_ID": "n-comp",
            "RIGHT_ATTRS": {
                "DEP": "nsubj"
            }
        }
    ]


    it_V_that_pattern1 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "comp_token",
            "RIGHT_ATTRS": {"DEP": "ccomp"}
        },
        {
            "LEFT_ID": "comp_token",
            "REL_OP": ">",
            "RIGHT_ID": "that_token",
            "RIGHT_ATTRS": {
                "DEP": "mark",
                "LEMMA": "that"
                }
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "introductory-it",
            "RIGHT_ATTRS": {
                "DEP": "nsubj",
                "LEMMA": "it"
            }
        }
    ]


    V_for_n_toinf_pattern = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "comp_token",
            "RIGHT_ATTRS": {
                "DEP": "advcl",
                "TAG": {"REGEX": "^V"}
                }
        },
        {
            "LEFT_ID": "comp_token",
            "REL_OP": ">",
            "RIGHT_ID": "to_token",
            "RIGHT_ATTRS": {
                "DEP": "aux",
                "TAG": "TO"
            }
        },
        {
            "LEFT_ID": "comp_token",
            "REL_OP": ">",
            "RIGHT_ID": "for_token",
            "RIGHT_ATTRS": {
                "DEP": "mark",
                "LEMMA": "for"
            }
        },
        {
            "LEFT_ID": "comp_token",
            "REL_OP": ">",
            "RIGHT_ID": "nsubj_token",
            "RIGHT_ATTRS": {
                "DEP": "nsubj",
                "POS": {"IN": ["NOUN", "PRON", "PROPN"]}
            }
        }
    ]


    V_it_nadj_clause_pattern1 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "comp_token",
            "RIGHT_ATTRS": {
                "DEP": "ccomp",
                "TAG": {"REGEX": "^[JN]"}
            }
        },
        {
            "LEFT_ID": "comp_token",
            "REL_OP": ">",
            "RIGHT_ID": "it_token",
            "RIGHT_ATTRS": {
                "DEP": "nsubj",
                "LEMMA": "it"
            }
        },
        {
            "LEFT_ID": "comp_token",
            "REL_OP": ".",
            "RIGHT_ID": "to_token",
            "RIGHT_ATTRS": {
                "TAG": "TO",
                "DEP": "aux"}
        }
    ]

    V_it_nadj_clause_pattern2 = [
        {
            "RIGHT_ID": "anchor_verb",
            "RIGHT_ATTRS": {"TAG": {"REGEX": "^V"}}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">",
            "RIGHT_ID": "comp_token",
            "RIGHT_ATTRS": {
                "DEP": "ccomp",
                "TAG": {"REGEX": "^[JN]"}
            }
        },
        {
            "LEFT_ID": "comp_token",
            "REL_OP": ">",
            "RIGHT_ID": "it_token",
            "RIGHT_ATTRS": {
                "DEP": "nsubj",
                "LEMMA": "it"
            }
        },
        {
            "LEFT_ID": "comp_token",
            "REL_OP": ".",
            "RIGHT_ID": "that",
            "RIGHT_ATTRS": {
                "LEMMA": "that",
                "DEP": "mark"}
        }
    ]

    # matcherにパターンを追加
    matcher.add("V_n-comp", [V_ncomp_pattern])
    matcher.add("V_pron-refl", [V_pron_refl_pattern])
    matcher.add("V_adj", [V_adj_pattern])
    matcher.add("V_ing", [V_ing_pattern1, V_ing_pattern2, V_ing_pattern3, V_ing_pattern4])
    matcher.add("V_to-inf", [V_toinf_pattern1, V_toinf_pattern2, V_toinf_pattern3])
    matcher.add("V_that", [V_that_pattern])
    matcher.add("V_wh", [V_wh_pattern])
    matcher.add("V_wh-to-inf", [V_whtoinf_pattern])
    matcher.add("V_prep_n", [V_prep_n_pattern1, V_prep_n_pattern2, V_prep_n_pattern3])
    matcher.add("V_by_ing", [V_by_ing_pattern])
    matcher.add("V_out_of_n", [V_out_of_n_pattern])
    matcher.add("V_onto_n", [V_onto_n_pattern1, V_onto_n_pattern2])
    matcher.add("V_n_n-comp", [V_n_ncomp_pattern1, V_n_ncomp_pattern2, V_n_ncomp_pattern3])
    matcher.add("V_n_n-obj", [V_n_nobj_pattern1, V_n_nobj_pattern2])
    matcher.add("V_n_adj", [V_n_adj_pattern1, V_n_adj_pattern2, V_n_adj_pattern3])
    matcher.add("V_n_to-inf", [V_n_toinf_pattern1, V_n_toinf_pattern2, V_n_toinf_pattern3])
    matcher.add("V_n_inf", [V_n_inf_pattern1, V_n_inf_pattern2])
    matcher.add("V_n_that", [V_n_that_pattern1, V_n_that_pattern2])
    matcher.add("V_n_wh", [V_n_wh_pattern1, V_n_wh_pattern2])
    matcher.add("V_n_wh-to-inf", [V_n_whtoinf_pattern1, V_n_whtoinf_pattern2])
    matcher.add("V_n_V-ed", [V_n_Ved_pattern1, V_n_Ved_pattern2])
    matcher.add("V_n_ing", [V_n_ing_pattern1, V_n_ing_pattern2, V_n_ing_pattern3, V_n_ing_pattern4])
    matcher.add("V_way_prep/adv", [V_way_pattern])
    matcher.add("V_n_prep_n", [V_n_prep_n_pattern1, V_n_prep_n_pattern2])
    matcher.add("V_n_out_of_n", [V_n_out_of_n_pattern1, V_n_out_of_n_pattern2])
    matcher.add("it_V_n/adj_to-inf", [it_V_nadj_toinf_pattern1, it_V_nadj_toinf_pattern2])
    matcher.add("it_V_(n/adj)_that", [it_V_that_pattern1])
    matcher.add("V_for_n_to-inf", [V_for_n_toinf_pattern])
    matcher.add("V_it_n/adj_clause", [V_it_nadj_clause_pattern1, V_it_nadj_clause_pattern2])

    return matcher

## フィルター関数群 ------------------------------------------------------------
def filter_V_ncomp(token_ids, doc):
    result = True
    anchor_verb = doc[token_ids[0]]
    comp_token = doc[token_ids[1]]
    if not filter_no_obj(token_ids, doc):
        return False
    if not filter_passive(token_ids, doc):
        return False
    if not filter_past_participle_modifier(token_ids, doc):
        return False
    # if not word_order_check(anchor_verb, comp_token, doc):
    #     return False
    
    # there is構文を除外
    if any(child.dep_ == "expl" for child in anchor_verb.children):
        return False
    
    # be oneselfを除外
    if comp_token.lemma_.lower() in [
        "myself", "yourself", "yourselves", "ourselves", "himself", 
        "herself", "itself", "themselves", "oneself"
        ]:
        return False
    
    return result


def filter_pron_refl(token_ids, doc):
    result = True
    anchor_verb = doc[token_ids[0]]
    pron_refl_token = doc[token_ids[1]]
    if not filter_passive(token_ids, doc):
        return False
    if not filter_past_participle_modifier(token_ids, doc):
        return False
    if not word_order_check(anchor_verb, pron_refl_token, doc):
        return False
    return result


def filter_V_adj(token_ids, doc):
    result = True
    anchor_verb = doc[token_ids[0]]
    adj_token = doc[token_ids[1]]
    
    if not filter_no_obj(token_ids, doc):
        return False
    if not filter_passive(token_ids, doc):
        return False
    if not filter_past_participle_modifier(token_ids, doc):
        return False
    # if not word_order_check(anchor_verb, adj_token, doc):
    #     return False
    
    # be able toを除外
    if (
        anchor_verb.lemma_.lower() == "be" and
        anchor_verb.i + 1 < len(doc) and
        anchor_verb.i + 2 < len(doc) and
        doc[anchor_verb.i + 1].lemma_.lower() == "able" and
        doc[anchor_verb.i + 2].lemma_.lower() == "to"
    ):
        result = False
        
    # be about toを除外
    if (
        anchor_verb.lemma_.lower() == "be" and
        anchor_verb.i + 1 < len(doc) and
        anchor_verb.i + 2 < len(doc) and
        doc[anchor_verb.i + 1].lemma_.lower() == "about" and
        doc[anchor_verb.i + 2].lemma_.lower() == "to"
    ):
        result = False
        
    return result


def filter_V_ing(token_ids, doc):
    result = True
    anchor_verb = doc[token_ids[0]]
    ing_token = doc[token_ids[1]]

    
    if not filter_no_obj(token_ids, doc):
        return False
    if not filter_passive(token_ids, doc):
        return False
    if not filter_past_participle_modifier(token_ids, doc):
        return False
    if not word_order_check(anchor_verb, ing_token, doc):
        return False
    
    if anchor_verb.lemma_ == "be":
        return False
    if anchor_verb.lemma_ == "have" and anchor_verb.dep_ == "aux":
        return False
    
    if any(child.tag_ == "TO" and child.dep_ == "aux" for child in anchor_verb.children):
        return False
    
    return result


def filter_V_toinf(token_ids, doc):
    result = True

    anchor_verb = doc[token_ids[0]]
    inf_verb = doc[token_ids[1]]
    if doc[token_ids[2]].text.lower() == "to":
        to_token = doc[token_ids[2]]
    else:
        to_token = doc[token_ids[3]]
    
    if not filter_no_obj(token_ids, doc):
        return False
    
    if not filter_passive(token_ids, doc):
        return False

    if not filter_past_participle_modifier(token_ids, doc):
        return False
    
    if not word_order_check(anchor_verb, inf_verb, doc):
        return False
    
    
    # be going toを除外
    if anchor_verb.lemma_.lower() == "go" and anchor_verb.tag_ == "VBG":
        return False
    # have to を除外
    if anchor_verb.lemma_ == "have":
        return False
    # beを除外
    if anchor_verb.lemma_ == "be":
        return False
    # used toを除外
    if anchor_verb.text.lower() == "used":
        return False
    
    wh_words = {"what", "who", "which", "whom", "where", "when", "why", "how", "whether", "if"}
    # to_tokenの一つ前の単語がwh_wordsに含まれるものでないかどうかチェック
    if to_token.i > 0:
        prev_token = doc[to_token.i - 1]
        if prev_token.lemma_.lower() in wh_words:
            return False
    
    return result



def filter_V_that(token_ids, doc):
    result = True
    anchor_verb = doc[token_ids[0]]
    ccomp_verb = doc[token_ids[1]]
    
    if not filter_no_obj(token_ids, doc):
        return False
    if not filter_passive(token_ids, doc):
        return False
    if not filter_past_participle_modifier(token_ids, doc):
        return False
    if not word_order_check(anchor_verb, ccomp_verb, doc):
        return False
    
    # be動詞は除外
    if anchor_verb.lemma_ == "be":
        return False
    
    # ccomp_verbはanchor_verbの後ろに限定
    if ccomp_verb.i < anchor_verb.i:
        return False
    
    # thatがあればその時点でOK
    if any(child.lemma_ == "that" and child.dep_ == "mark" for child in ccomp_verb.children):
        return True
    
    # 他のパターンと区別するための条件 ----------------------------
    # 引用符(quotation)のパターンは除外
    if any("Quot" in child.morph.get("PunctType", [""]) for child in anchor_verb.children):
        return False
    
    # V_n_to-infの場合を除外するフィルター
    if any(child.tag_ == "TO" for child in ccomp_verb.children):
        return False

    # 疑問詞が含まれている場合は除外
    wh_words = {"what", "who", "which", "whom", "where", "when", "why", "how", "whether", "if"}
    for descendant in ccomp_verb.subtree:
        if descendant.lemma_ in wh_words and descendant.i < ccomp_verb.i:
            return False
    
    # V_n_infと区別: Infがある場合は、助動詞がない場合は除外
    if "Inf" in ccomp_verb.morph.get("VerbForm", []):
        has_aux_md = any(child.tag_ == "MD" and child.dep_ == "aux" for child in ccomp_verb.children)
        has_aux_do = any(child.dep_ == "aux" and child.lemma_ == "do" for child in ccomp_verb.children)
        if not has_aux_md and not has_aux_do:
            return False
            
    # V_n_Vedと区別: 単独の過去分詞（助動詞なし）を除外
    if ccomp_verb.tag_ == "VBN":
        # 現在完了形（have + VBN）または受動態（auxpass付き）の場合はOK
        has_have_aux = any(child.lemma_ == "have" and child.dep_ == "aux" for child in ccomp_verb.children)
        has_auxpass = any(child.dep_ == "auxpass" for child in ccomp_verb.children)
        
        # どちらもない場合（単独の過去分詞）は除外
        if not has_have_aux and not has_auxpass:
            return False
        
    # V_n_ingと区別:
    if ccomp_verb.tag_ == "VBG":
        if not any(child.lemma_ == "be" and child.dep_ == "aux" for child in ccomp_verb.children):
            return False
        
    # ------------------------------------------------------------
        
    return result


def filter_V_wh(token_ids, doc):
    result = True

    anchor_verb = doc[token_ids[0]]
    ccomp_token = doc[token_ids[1]]
    wh_token = doc[token_ids[3]]
    
    if not filter_no_obj(token_ids, doc):
        return False
    if not filter_passive(token_ids, doc):
        return False
    if not filter_past_participle_modifier(token_ids, doc):
        return False
    if not word_order_check(anchor_verb, wh_token, doc):
        return False
    
    # be動詞は除外
    if anchor_verb.lemma_ == "be":
        return False
    
    # wh_token が ccomp_token よりも右側にある場合、このマッチを除外
    if wh_token.i >= ccomp_token.i:
        return False
    
    return result


def filter_V_whtoinf(token_ids, doc):
    result = True

    anchor_verb = doc[token_ids[0]]
    comp_token = doc[token_ids[1]]
    wh_token = doc[token_ids[2]]
    
    if not filter_no_obj(token_ids, doc):
        return False
    if not filter_passive(token_ids, doc):
        return False
    if not filter_past_participle_modifier(token_ids, doc):
        return False
    if not word_order_check(anchor_verb, wh_token, doc):
        return False
    
    # be動詞は除外
    if anchor_verb.lemma_ == "be":
        return False
    
    # wh_token が comp_token よりも右側にある場合、このマッチを除外
    if wh_token.i >= comp_token.i:
        return False
    
    return result


def filter_V_prep_n(token_ids, doc):
    result = True
    
    which_rule = ""
    if len(token_ids) == 2:
        which_rule = "rule1"
    elif len(token_ids) == 3 and doc[token_ids[1]].dep_ == "advmod":
        which_rule = "rule2"
    elif len(token_ids) == 3 and doc[token_ids[2]].dep_ == "auxpass":
        which_rule = "rule3"

    anchor_verb = doc[token_ids[0]]
    prep_token = doc[token_ids[1]] if doc[token_ids[1]].dep_ == "prep" else doc[token_ids[2]]
    advmod_token = doc[token_ids[1]] if doc[token_ids[1]].dep_ == "advmod" else None
    
    if not filter_no_obj(token_ids, doc):
        return False
    if which_rule == "rule1":
        if not filter_passive(token_ids, doc):
            return False
    if not filter_past_participle_modifier(token_ids, doc):
        return False
    if not word_order_check(anchor_verb, prep_token, doc):
        return False
    
    # pobjが主語になった受動態
    if which_rule == "rule3":
        if any(child.dep_ in ["pobj", "pcomp"] for child in prep_token.children):
            return False
    
    # V_n_out_of_nとの区別
    if prep_token.lemma_.lower() == "of":
        if doc[prep_token.i-1].lemma_.lower() == "out":
            return False

    # V_n_onto_nとの区別
    if prep_token.lemma_.lower() == "to":
        if doc[prep_token.i-1].lemma_.lower() == "on":
            return False
    if prep_token.lemma_.lower() == "on":
        # インデックスエラー防止のため、範囲内か確認
        if prep_token.i + 1 < len(doc):
            if doc[prep_token.i+1].lemma_.lower() == "to":
                return False
    
    # 過去分詞 + 前置詞を除く (完了形はOK)
    if which_rule == "rule1":
        if anchor_verb.tag_ == "VBN":
            if not(any(child.dep_ == "aux" and child.lemma_ == "have" for child in anchor_verb.children)):
                return False

    # 最初の前置詞のみを選択（最もanchor_verbに近いもの）
    prep_children = [child for child in anchor_verb.children 
                    if child.dep_ == "prep" and child.lemma_ in target_prep_simple]
    
    if prep_children:
        # 動詞に最も近い前置詞を選択
        first_prep = min(prep_children, key=lambda x: abs(x.i - anchor_verb.i))
        if prep_token.i != first_prep.i:
            return False

    return result

def get_V_prep_n_label(token_ids, doc):
    anchor_verb = doc[token_ids[0]]
    prep_token = doc[token_ids[1]] if doc[token_ids[1]].dep_ == "prep" else doc[token_ids[2]]
    if prep_token.lemma_.lower() in ["around", "round"]:
        pattern_label = f"V_around/round_n"
    
    elif prep_token.lemma_.lower() in ["on", "upon"]:
        pattern_label = f"V_on_n"
        
    elif prep_token.lemma_.lower() in ["toward", "towards"]:
        pattern_label = f"V_toward_n"
        
    elif prep_token.lemma_.lower() == "between":
        pattern_label = f"V_between_pl-n"
        
    # V_n_as_adjとの区別
    elif prep_token.lemma_.lower() == "as":
        if any(child.dep_ == "amod" and child.pos_ == "ADJ" for child in prep_token.children):
            pattern_label = f"V_{prep_token.lemma_.lower()}_adj"
        else:
            pattern_label = f"V_{prep_token.lemma_.lower()}_n"
            
    else:
        pattern_label = f"V_{prep_token.lemma_.lower()}_n"

    return pattern_label


def filter_V_by_ing(token_ids, doc):
    result = True

    anchor_verb = doc[token_ids[0]]
    by_token = doc[token_ids[1]]

    if not filter_no_obj(token_ids, doc):
        return False
    if not filter_passive(token_ids, doc):
        return False
    if not filter_past_participle_modifier(token_ids, doc):
        return False
    if not word_order_check(anchor_verb, by_token, doc):
        return False

    return result


def filter_V_out_of_n(token_ids, doc):
    result = True
    
    anchor_verb = doc[token_ids[0]]
    out_token = doc[token_ids[1]]
    
    if not filter_no_obj(token_ids, doc):
        return False
    if not filter_passive(token_ids, doc):
        return False
    if not filter_past_participle_modifier(token_ids, doc):
        return False
    if not word_order_check(anchor_verb, out_token, doc):
        return False
    
    return result


def filter_V_onto_n(token_ids, doc):
    result = True
    
    anchor_verb = doc[token_ids[0]]
    out_token = doc[token_ids[1]]
    
    if not filter_no_obj(token_ids, doc):
        return False
    if not filter_passive(token_ids, doc):
        return False
    if not filter_past_participle_modifier(token_ids, doc):
        return False
    if not word_order_check(anchor_verb, out_token, doc):
        return False
    
    return result


def filter_V_n_ncomp(token_ids, doc):
    result = True
    anchor_verb = doc[token_ids[0]]
    comp_token = doc[token_ids[1]]
    if not word_order_check(anchor_verb, comp_token, doc):
        return False
    return result


def filter_V_n_nobj(token_ids, doc):
    result = True
    return result


def filter_V_n_adj(token_ids, doc):
    result = True
    anchor_verb = doc[token_ids[0]]
    comp_token = doc[token_ids[1]]
    
    if not word_order_check(anchor_verb, comp_token, doc):
        return False
    
    return result


def filter_V_n_toinf(token_ids, doc):
    result = True
    
    anchor_verb = doc[token_ids[0]]
    comp_token = doc[token_ids[1]]
    
    if not word_order_check(anchor_verb, comp_token, doc):
        return False
    
    # comp_token の子孫にwh疑問詞が含まれているかチェック
    wh_words = {"what", "who", "which", "whom", "where", "when", "why", "how", "whether"}
    for descendant in comp_token.subtree:
        if descendant.lemma_ in wh_words and descendant.i < comp_token.i:
            # wh疑問詞がある場合は、V_n_wh_to-infパターンとして扱うため除外
            return False
    return result

def filter_V_n_inf(token_ids, doc):
    result = True
    anchor_verb = doc[token_ids[0]]
    comp_token = doc[token_ids[1]]
    
    # let'sを除外する
    if anchor_verb.lemma_.lower() == "let" and doc[anchor_verb.i+1].text.lower() == "'s":
        return False
    
    if not word_order_check(anchor_verb, comp_token, doc):
        return False
    
    if any(child.tag_ == "TO" for child in comp_token.children):
        return False
    
    if any(child.dep_ == "aux" for child in comp_token.children):
        return False
    
    if "Inf" not in comp_token.morph.get("VerbForm"):
        return False
    
    if any(child.dep_ == "mark" and child.lemma_.lower() == "that" for child in comp_token.children):
        return False
    
    return result


def filter_V_n_that(token_ids, doc):
    result = True
    
    anchor_verb = doc[token_ids[0]]
    ccomp_verb = doc[token_ids[1]]
    
    if not word_order_check(anchor_verb, ccomp_verb, doc):
        return False
    
    # thatがあればその時点でOK
    if any(child.lemma_ == "that" and child.dep_ == "mark" for child in ccomp_verb.children):
        return True
    
    # 他のパターンと区別するための条件 ----
    # 引用符(quotation)のパターンは除外
    if any("Quot" in child.morph.get("PunctType", [""]) for child in anchor_verb.children):
        return False
    
    # 疑問詞が含まれている場合は除外
    wh_words = {"what", "who", "which", "whom", "where", "when", "why", "how", "whether", "if"}
    for descendant in ccomp_verb.subtree:
        if descendant.lemma_ in wh_words and descendant.i < ccomp_verb.i:
            return False
        
    return result


def filter_V_n_wh(token_ids, doc):
    result = True
    anchor_verb = doc[token_ids[0]]
    ccomp_token = doc[token_ids[1]]
    wh_token = doc[token_ids[3]]
    
    if not word_order_check(anchor_verb, ccomp_token, doc):
        return False

    # wh_token が ccomp_token よりも右側にある場合、このマッチを除外
    if wh_token.i >= ccomp_token.i:
        return False
    
    return result


def filter_V_n_whtoinf(token_ids, doc):
    result = True
    anchor_verb = doc[token_ids[0]]
    ccomp_token = doc[token_ids[2]]
    wh_token = doc[token_ids[3]]
    
    if not word_order_check(anchor_verb, ccomp_token, doc):
        return False

    # wh_token が ccomp_token よりも右側にある場合、このマッチを除外
    if wh_token.i >= ccomp_token.i:
        return False
    
    return result


def filter_V_n_Ved(token_ids, doc):
    result = True
    anchor_verb = doc[token_ids[0]]
    comp_token = doc[token_ids[1]]
    
    if not word_order_check(anchor_verb, comp_token, doc):
        return False
    
    if any(child.dep_ == "aux" and child.lemma_ == "have" for child in comp_token.children):
        return False
    
    if any(child.dep_ == "auxpass" for child in comp_token.children):
        return False
    
    if any(child.dep_ == "aux" and child.tag_ == "MD" for child in comp_token.children):
        return False
    
    return result


def filter_V_n_ing(token_ids, doc):
    result = True
    anchor_verb = doc[token_ids[0]]
    comp_token = doc[token_ids[1]]
    
    if not word_order_check(anchor_verb, comp_token, doc):
        return False
    
    if any(child.dep_ == "aux" and child.lemma_.lower() == "be" for child in comp_token.children):
        return False
    
    return result


def filter_V_way(token_ids, doc):
    result = True
    anchor_verb = doc[token_ids[0]]
    prep_adv_token = doc[token_ids[3]]

    if not word_order_check(anchor_verb, prep_adv_token, doc):
        return False
    
    return result


def filter_V_n_prep_n(token_ids, doc):
    result = True
    
    which_rule = ""
    if doc[token_ids[2]].dep_ == "dobj":
        which_rule = "rule1"
    elif doc[token_ids[2]].dep_ == "auxpass":
        which_rule = "rule2"
    
    anchor_verb = doc[token_ids[0]]
    prep_token = doc[token_ids[1]]
    
    if not word_order_check(anchor_verb, prep_token, doc):
        return False
    
    if which_rule == "rule2":
        if not any(child.dep_ in ["pobj", "pcomp"] for child in prep_token.children):
            return False
    
    # V_n_out_of_nとの区別
    if prep_token.lemma_.lower() == "of":
        if doc[prep_token.i-1].lemma_.lower() == "out":
            return False

    # 最初の前置詞のみを選択（最もanchor_verbに近いもの）
    prep_children = [child for child in anchor_verb.children 
                    if child.dep_ in ["prep", "dative"] and child.lemma_ in target_prep_complex]
    
    if prep_children:
        # 動詞に最も近い前置詞を選択
        first_prep = min(prep_children, key=lambda x: abs(x.i - anchor_verb.i))
        if prep_token.i != first_prep.i:
            return False
    
    return result


def get_V_n_prep_n_label(token_ids, doc):
    anchor_verb = doc[token_ids[0]]
    prep_token = doc[token_ids[1]]
    
    pattern_label = ""
    if prep_token.lemma_.lower() in ["between", "among"]:
        pattern_label = f"V_n_between/among_pl-n"

    elif prep_token.lemma_.lower() in ["on", "upon"]:
        pattern_label = f"V_n_on_n"
        
    # V_n_as_adjとの区別
    elif prep_token.lemma_.lower() == "as":
        if any(child.dep_ == "amod" and child.pos_ == "ADJ" for child in prep_token.children):
            pattern_label = f"V_n_{prep_token.lemma_.lower()}_adj"
        else:
            pattern_label = f"V_n_{prep_token.lemma_.lower()}_n"
    # V_n_into_ingとの区別
    elif prep_token.lemma_.lower() == "into":
        if any(child.dep_ == "pcomp" and child.tag_ == "VBG" for child in prep_token.children):
            pattern_label = f"V_n_{prep_token.lemma_.lower()}_ing"
        else:
            pattern_label = f"V_n_{prep_token.lemma_.lower()}_n"
    elif prep_token.lemma_.lower() in ["toward", "towards"]:
        pattern_label = "V_n_toward_n"
    else:
        pattern_label = f"V_n_{prep_token.lemma_.lower()}_n"

    return pattern_label


def filter_V_n_out_of_n(token_ids, doc):
    result = True
    anchor_verb = doc[token_ids[0]]
    out_token = doc[token_ids[1]]
    
    if not word_order_check(anchor_verb, out_token, doc):
        return False
    
    return result


def filter_it_V_nadj_toinf(token_ids, doc):
    result = True
    anchor_verb = doc[token_ids[0]]
    inf_comp_token = doc[token_ids[1]]
    
    if not word_order_check(anchor_verb, inf_comp_token, doc):
        return False
    
    return result


def filter_it_V_that(token_ids, doc):
    result = True
    anchor_verb = doc[token_ids[0]]
    comp_token = doc[token_ids[1]]
    
    if not word_order_check(anchor_verb, comp_token, doc):
        return False
    
    return result


def filter_V_for_n_toinf(token_ids, doc):
    result = True
    anchor_verb = doc[token_ids[0]]
    comp_token = doc[token_ids[1]]
    return result


def filter_it_nadj_clause(token_ids, doc):
    result = True
    anchor_verb = doc[token_ids[0]]
    comp_token = doc[token_ids[1]]
    return result
## フィルター関数の定義終了 ------------------------------------------------------------


# フィルター関数を適用
def apply_filter(match_label, token_ids, doc):
    if match_label == "V_n-comp":
        result = filter_V_ncomp(token_ids, doc)
        return result
    elif match_label == "V_pron-refl":
        result = filter_pron_refl(token_ids, doc)
        return result
    elif match_label == "V_adj":
        result = filter_V_adj(token_ids, doc)
        return result
    elif match_label == "V_ing":
        result = filter_V_ing(token_ids, doc)
        return result
    elif match_label == "V_to-inf":
        result = filter_V_toinf(token_ids, doc)
        return result
    elif match_label == "V_that":
        result = filter_V_that(token_ids, doc)
        return result
    elif match_label == "V_wh":
        result = filter_V_wh(token_ids, doc)
        return result
    elif match_label == "V_wh-to-inf":
        result = filter_V_whtoinf(token_ids, doc)
        return result
    elif match_label == "V_prep_n":
        result = filter_V_prep_n(token_ids, doc)
        return result
    elif match_label == "V_by_ing":
        result = filter_V_by_ing(token_ids, doc)
        return result
    elif match_label == "V_out_of_n":
        result = filter_V_out_of_n(token_ids, doc)
        return result
    elif match_label == "V_onto_n":
        result = filter_V_onto_n(token_ids, doc)
        return result
    elif match_label == "V_n_n-comp":
        result = filter_V_n_ncomp(token_ids, doc)
        return result
    elif match_label == "V_n_n-obj":
        result = filter_V_n_nobj(token_ids, doc)
        return result
    elif match_label == "V_n_adj":
        result = filter_V_n_adj(token_ids, doc)
        return result
    elif match_label == "V_n_to-inf":
        result = filter_V_n_toinf(token_ids, doc)
        return result
    elif match_label == "V_n_inf":
        result = filter_V_n_inf(token_ids, doc)
        return result
    elif match_label == "V_n_that":
        result = filter_V_n_that(token_ids, doc)
        return result
    elif match_label == "V_n_wh":
        result = filter_V_n_wh(token_ids, doc)
        return result
    elif match_label == "V_n_wh-to-inf":
        result = filter_V_n_whtoinf(token_ids, doc)
        return result
    elif match_label == "V_n_V-ed":
        result = filter_V_n_Ved(token_ids, doc)
        return result
    elif match_label == "V_n_ing":
        result = filter_V_n_ing(token_ids, doc)
        return result
    elif match_label == "V_way_prep/adv":
        result = filter_V_way(token_ids, doc)
        return result
    elif match_label == "V_n_prep_n":
        result = filter_V_n_prep_n(token_ids, doc)
        return result
    elif match_label == "V_n_out_of_n":
        result = filter_V_n_out_of_n(token_ids, doc)
        return result
    elif match_label == "it_V_n/adj_to-inf":
        result = filter_it_V_nadj_toinf(token_ids, doc)
        return result
    elif match_label == "it_V_(n/adj)_that":
        result = filter_it_V_that(token_ids, doc)
        return result
    elif match_label == "V_for_n_to-inf":
        result = filter_V_for_n_toinf(token_ids, doc)
        return result
    elif match_label == "V_it_n/adj_clause":
        result = filter_it_nadj_clause(token_ids, doc)
        return result
    
    result = False
    return result

pattern_priority_dict = {
    "V_about_n": 2,
    "V_across_n": 2,
    "V_adj": 2,
    "V_after_n": 2,
    "V_against_n": 2,
    "V_around/round_n": 2,
    "V_as_adj": 2,
    "V_as_n": 2,
    "V_at_n": 2,
    "V_between_pl-n": 2,
    "V_by_ing": 1,
    "V_for_n": 1,
    "V_from_n": 2,
    "V_in_n": 2,
    "V_ing": 2,
    "V_into_n": 2,
    "V_like_n": 2,
    "V_n_about_n": 3,
    "V_n_adj": 3,
    "V_n_against_n": 3,
    "V_n_as_adj": 3,
    "V_n_as_n": 3,
    "V_n_at_n": 3,
    "V_n_between/among_pl-n": 3,
    "V_n_by_n": 2,
    "V_n_for_n": 1,
    "V_n_from_n": 3,
    "V_n_in_n": 3,
    "V_n_inf": 3,
    "V_n_ing": 3,
    "V_n_into_ing": 3,
    "V_n_into_n": 3,
    "V_n_n-comp": 3,
    "V_n_n-obj": 3,
    "V_n_of_n": 3,
    "V_n_off_n": 3,
    "V_n_on_n": 3,
    "V_n_onto_n": 3,
    "V_n_out_of_n": 3,
    "V_n_over_n": 3,
    "V_n_that": 3,
    "V_n_to_n": 3,
    "V_n_to-inf": 3,
    "V_n_toward_n": 3,
    "V_n_V-ed": 3,
    "V_n_wh": 3,
    "V_n_wh-to-inf": 5,
    "V_n_with_n": 3,
    "V_n-comp": 3,
    "V_of_n": 2,
    "V_off_n": 2,
    "V_on_n": 2,
    "V_onto_n": 3,
    "V_out_of_n": 2,
    "V_over_n": 2,
    "V_pron-refl": 1,
    "V_that": 2,
    "V_through_n": 2,
    "V_to_n": 2,
    "V_to-inf": 1,
    "V_toward_n": 2,
    "V_under_n": 2,
    "V_way_prep/adv": 4,
    "V_wh": 2,
    "V_wh-to-inf": 2,
    "V_with_n": 2,
    "it_V_n/adj_to-inf": 4,
    "it_V_(n/adj)_that": 4,
    "V_for_n_to-inf": 4,
    "V_it_n/adj_clause": 4
}


def extract_VAC(doc, matcher, spacy_nlp):
    matches = matcher(doc)
    match_dict = defaultdict(list)
    
    for match_id, token_ids in matches:
        match_label = spacy_nlp.vocab.strings[match_id]
        anchor_idx = doc[token_ids[0]].i
        
        if apply_filter(match_label, token_ids, doc):
            # V_prep_n の場合は、prep_token のlemmaを取得して、labelを作成
            if match_label == "V_prep_n":
                V_prep_n_label = get_V_prep_n_label(token_ids, doc)
                match_dict[anchor_idx].append(V_prep_n_label)
                
            elif match_label == "V_n_prep_n":
                V_n_prep_n_label = get_V_n_prep_n_label(token_ids, doc)
                match_dict[anchor_idx].append(V_n_prep_n_label)
                
            else:
                match_dict[anchor_idx].append(match_label)
    
    for idx, labels in match_dict.items():
        # labelsの要素が2つ以上ある場合、pattern_priority_dictに基づいて並べ替える
        # print(doc[idx].text, labels, doc)
        if len(labels) >= 2:
            labels.sort(key=lambda x: pattern_priority_dict.get(x, float('-inf')), reverse=True)
        match_dict[idx] = labels[0] # 複数のラベルがつく場合、最初のラベルを選択
    
    return [(idx, label) for idx, label in match_dict.items()]