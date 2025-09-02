# Files Description
- **`20250903_JAECS_presentation_slide.pdf`**: Presentation slides for the JAECS conference presentation on September 3, 2025.

- **`config.cfg`**: Configuration file for spaCy model training, specifying parameters for the transformer-based NER (Named Entity Recognition) model used for VAC pattern identification. 

- **`Demo.ipynb`**: Jupyter notebook demonstrating the VAC identification system.

- **`evaluation.py`**: Python script for evaluating the performance of the trained VAC identification model.

- **`rule-based_vac_extractor.py`**: Python script for rule-based VAC extraction system using spaCy's `DependencyMatcher`.

# Dataset and Model Availability
- The training dataset used in this research consists of example sentences from copyrighted materials and is therefore not publicly available. I plan to make it available once permission is obtained from the copyright holders. 
- The fine-tuned model will be released through Hugging Face after validation.

# Pattern list
|No.|Pattern|Examples|
|---|---|---|
|1|V_N_OBJ|The soldiers destroyed the building. / The children went in, and ate the biscuits.|
|2|V_N_COMP|My husband is a doctor. / For the first year after the divorce I felt a real failure.|
|3|V_PRON_REFL|I asserted myself. / He couldn't kid himself .|
|4|V_ADJ|The law has proved difficult to implement , however. / She was not young , but she was beautiful .|
|5|V_ING|He likes walking his dogs. / We ended up having dinner .|
|6|V_TO_INF|The arrangements appeared to be satisfactory. / The President agreed to be interviewed . / The paramedics rush to help.|
|7|V_THAT|I agree that the project has possibilities. / I found out they were planning to erase the tapes .|
|8|V_WH|We cannot estimate what the local interest will be . / People don't notice whether it's winter or summer .|
|9|V_WH_TO_INF|I've forgotten what to say. / We have to discuss how to divide the land .|
|10|V_ABOUT_N|I dream about winning the 100 meters . / I'm phoning about the arrangements for tomorrow .|
|11|V_ACROSS_N|She cut across the grass. / Birds skimmed across the water .|
|12|V_AFTER_N|The attendants chased after him . / Americans hanker after the big gas-guzzling cars of yesteryear .|
|13|V_AGAINST_N|You are competing against younger workers. / They have decided against boycotting the referendum .|
|14|V_AROUND/ROUND_N|The plot centres around a baffling murder. / The children clustered around me .|
|15|V_AS_ADJ|A large number of plants qualify as medicinal. / He comes over as smug and arrogant.|
|16|V_AS_N|The bacterium acts as a natural carrier for the gene . / The scandal began as a family feud .|
|17|V_AT_N|The unemployment rate peaked at 11 per cent . / The rivals shouted at each other.|
|18|V_BETWEEN_PL_N|Many customers cannot distinguish between psychiatrists and other psychotherapists. / I liaise between these groups .|
|19|V_BY_ING|She began by telling me what the exhibition was about. / The fans retaliated by pelting them with plastic chairs .|
|20|V_FOR_N|She could pass for a man. / The new president opted for the toughest plan.|
|21|V_FROM_N|Fitness comes from working against gravity. / He escaped from prison on Saturday.|
|22|V_IN_N|Holiness consists in doing God's will joyfully. / They would intervene in quarrels and crisis situations .|
|23|V_INTO_N|Mike sank into suicidal depression. / The sound of the engine faded into the distance.|
|24|V_LIKE_N|Music is like a living thing. / He didn't act like a 13-year-old.|
|25|V_OF_N|I do not approve of this change. / He despaired of finishing it.|
|26|V_OFF_N|All the components can run off battery power. / The light reflected off the stone.|
|27|V_ON_N|They cannot agree on what they want done. / He appeared on weekend TV talk shows.|
|28|V_ONTO_N|His garden backs onto a school. / She was clinging on to his arm .|
|29|V_OUT_OF_N|He had changed out of his work clothes. /He had to bail out of the aircraft.|
|30|V_OVER_N|They argued over whether to extend the deadline. / Sheer walls of limestone towered over us.|
|31|V_THROUGH_N|Some of the activists broke through a security cordon. / Thoughts of arson flitted through my head.|
|32|V_TO_N|His embarrassment turned to anger. / He did not return to the subject.|
|33|V_TOWARD_N|Britain was leaning towards the French view. Bernard worked towards reversing these attitudes.|
|34|V_UNDER_N|Franklin chafed under this arrangement. / Many campaigners have been labouring under an illusion .|
|35|V_WITH_N|The volunteers will help with teaching English. / I can't cope with relationships .|
|36|V_N_N_COMP|He named the child Siddhartha. / Music magazines proclaimed her their new genius.|
|37|V_N_N_OBJ|I bought him lunch. / Her boyfriend gave her a diamond ring.|
|38|V_N_ADJ|He wished both of them dead. /The darkness could drive a man mad.|
|39|V_N_ING|My husband hates me being a businesswoman. / She noticed a man sitting alone on the grass. / The driver killed time circling the area.|
|40|V_N_TO_INF|They would prefer the truth to remain untold. / My girlfriend nagged me to cut my hair.|
|41|V_N_INF|Pemberton felt something touch his knee. / She heard the man laugh.|
|42|V_N_THAT|She told me he'd planned to be away all that night. / I warned her that I might not last out my hours of duty .|
|43|V_N_WH|One boy asked another what was wrong with him. / Years of working in Louisiana have taught him why poor people need unions.|
|44|V_N_WH_TO_INF|He has instructed millions of people how to raise their children. / I'll show you what to watch out for .|
|45|V_N_V_ED|I must get the car serviced. / She found him murdered.|
|46|V_WAY_PREP/ADV|She ate her way through a pound of chocolate . / Labour is fighting its way back .|
|47|V_N_ABOUT_N|He advises senior managers about getting the best out of their teams. / I asked him about what his record company is like.|
|48|V_N_AGAINST_N|We have to weigh the pluses against the minuses. / Your policy insures you against redundancy .|
|49|V_N_AS_ADJ|We accept this premise as fundamental. / She perceived him as stupid.|
|50|V_N_AS_N|Joanna did not dismiss Maude as a fraud. / The government has presented these changes as major reforms.|
|51|V_N_AT_N|He flashed a loving smile at his new bride. / I sold my house at a profit.|
|52|V_N_BETWEEN/AMONG_PL_N|UN officials have mediated a meeting between the two sides. / I would rate him among the fastest bowlers.|
|53|V_N_BY_N|He began the day by laying a wreath at the National Memorial. / He grabbed her by the shoulders.|
|54|V_N_FOR_N|She has brought a nice present for you. / I don't blame you for being upset.|
|55|V_N_FROM_N|He borrowed money from friends. / The embargo prevents them from selling oil.|
|56|V_N_IN_N|You may split it in half. / The bolt embedded itself in the turf.|
|57|V_N_INTO_N|He will convert the Tudor kitchens into a living museum. / They trapped him into a confession.|
|58|V_N_INTO_ING|Richard's mother badgered him into taking a Spanish wife. / She bullied the printers into rushing through the invitations.|
|59|V_N_OF_N|The settlement absolved the company of all criminal responsibility. / Clear your mind of other thoughts.|
|60|V_N_OFF_N|I'll borrow some money off my family. / They'd cleared all the snow off the carpark.|
|61|V_N_ON_N|I don't force vegetarianism on patients. / McClaren sprang a new idea on him.|
|62|V_N_OUT_OF_N|He fished a timetable out of the drawer. / She couldn't get any more information out of Ted.|
|63|V_N_OVER_N|Brush melted butter over the pastry. / The youths poured kerosene over the floor.|
|64|V_N_TO_N|We explained the situation to him. / He converted the note to cash.|
|65|V_N_TOWARD_N|They contributed $3 toward costs. / He directed his efforts towards helping people.|
|66|V_N_WITH_N|Many people confuse a severe cold with flu. / You can exchange information with other computer users.|
|67|V_FOR_N_TO_INF|We sat back to wait for the phone to ring. / We can even arrange for your bank to transfer funds from your account into the trust account each month . |
|68|V_IT_N/ADJ_CLAUSE|The reflection of the sun on the surface of the water made it impossible to see the bottom. / From the very beginning he had made it clear

# Per-pattern performance
- count: Number of occurrences in the gold-standard data.
- P_all: Precision on the full gold-standard set (training + test).
- R_all: Recall on the full gold-standard set (training + test).
- F1_all: F1 score on the full gold-standard set (training + test).
- P_test: Precision on the held-out test set (excludes training data).
- R_test: Recall on the held-out test set (excludes training data).
- F1_test: F1 score on the held-out test set (excludes training data).

Note: “N/A” means the label did not occur in the test set.

|No.|Pattern|count|Precision_all|Recall_all|F1_all|Precision_test|Recall_test|F1_test|
|---|---|---|---|---|---|---|---|---|
|1|V_N_OBJ|1225|0.988|0.984|0.986|0.929|0.914|0.921|
|2|V_N_COMP|166|0.964|0.976|0.970|0.933|0.875|0.903|
|3|V_PRON_REFL|68|1.000|0.971|0.985|1.000|0.857|0.923|
|4|V_ADJ|319|0.975|0.969|0.972|0.906|0.879|0.892|
|5|V_ING|98|1.000|0.990|0.995|1.000|0.875|0.933|
|6|V_TO_INF|353|0.992|1.000|0.996|0.930|1.000|0.964|
|7|V_THAT|246|0.992|1.000|0.996|0.923|1.000|0.960|
|8|V_WH|81|0.964|0.988|0.976|0.867|0.929|0.897|
|9|V_WH_TO_INF|29|1.000|0.966|0.982|1.000|1.000|1.000|
|10|V_ABOUT_N|47|1.000|1.000|1.000|1.000|1.000|1.000|
|11|V_ACROSS_N|6|1.000|1.000|1.000|N/A|N/A|N/A|
|12|V_AFTER_N|9|1.000|1.000|1.000|N/A|N/A|N/A|
|13|V_AGAINST_N|34|1.000|1.000|1.000|1.000|1.000|1.000|
|14|V_AROUND/ROUND_N|21|1.000|0.952|0.976|1.000|1.000|1.000|
|15|V_AS_ADJ|6|1.000|1.000|1.000|N/A|N/A|N/A|
|16|V_AS_N|32|1.000|1.000|1.000|1.000|1.000|1.000|
|17|V_AT_N|96|0.969|0.990|0.979|0.667|1.000|0.800|
|18|V_BETWEEN_PL_N|11|1.000|1.000|1.000|1.000|1.000|1.000|
|19|V_BY_ING|11|1.000|0.909|0.952|1.000|1.000|1.000|
|20|V_FOR_N|115|1.000|1.000|1.000|1.000|1.000|1.000|
|21|V_FROM_N|78|1.000|1.000|1.000|1.000|1.000|1.000|
|22|V_IN_N|117|0.991|0.991|0.991|1.000|1.000|1.000|
|23|V_INTO_N|84|1.000|0.988|0.994|1.000|0.923|0.960|
|24|V_LIKE_N|23|1.000|1.000|1.000|1.000|1.000|1.000|
|25|V_OF_N|32|1.000|1.000|1.000|1.000|1.000|1.000|
|26|V_OFF_N|9|1.000|1.000|1.000|1.000|1.000|1.000|
|27|V_ON_N|172|0.977|0.988|0.983|0.955|1.000|0.977|
|28|V_ONTO_N|14|1.000|0.929|0.963|1.000|0.667|0.800|
|29|V_OUT_OF_N|28|0.966|1.000|0.982|0.500|1.000|0.667|
|30|V_OVER_N|39|0.975|1.000|0.987|1.000|1.000|1.000|
|31|V_THROUGH_N|33|0.943|1.000|0.971|0.750|1.000|0.857|
|32|V_TO_N|192|0.995|0.995|0.995|0.929|0.929|0.929|
|33|V_TOWARD_N|19|1.000|1.000|1.000|N/A|N/A|N/A|
|34|V_UNDER_N|11|1.000|1.000|1.000|1.000|1.000|1.000|
|35|V_WITH_N|121|1.000|1.000|1.000|1.000|1.000|1.000|
|36|V_N_N_COMP|26|0.963|1.000|0.981|0.750|1.000|0.857|
|37|V_N_N_OBJ|88|1.000|1.000|1.000|1.000|1.000|1.000|
|38|V_N_ADJ|62|0.984|0.984|0.984|0.857|0.857|0.857|
|39|V_N_ING|65|1.000|1.000|1.000|1.000|1.000|1.000|
|40|V_N_TO_INF|156|0.994|1.000|0.997|0.944|1.000|0.971|
|41|V_N_INF|37|1.000|1.000|1.000|1.000|1.000|1.000|
|42|V_N_THAT|35|0.972|1.000|0.986|0.800|1.000|0.889|
|43|V_N_WH|11|1.000|1.000|1.000|1.000|1.000|1.000|
|44|V_N_WH_TO_INF|10|1.000|1.000|1.000|1.000|1.000|1.000|
|45|V_N_V_ED|51|0.981|1.000|0.990|0.667|1.000|0.800|
|46|V_WAY_PREP/ADV|62|1.000|1.000|1.000|1.000|1.000|1.000|
|47|V_N_ABOUT_N|39|1.000|1.000|1.000|1.000|1.000|1.000|
|48|V_N_AGAINST_N|33|1.000|0.970|0.985|1.000|0.750|0.857|
|49|V_N_AS_ADJ|20|1.000|1.000|1.000|1.000|1.000|1.000|
|50|V_N_AS_N|60|0.952|1.000|0.976|0.833|1.000|0.909|
|51|V_N_AT_N|36|1.000|0.972|0.986|1.000|0.800|0.889|
|52|V_N_BETWEEN/AMONG_PL_N|13|1.000|1.000|1.000|1.000|1.000|1.000|
|53|V_N_BY_N|22|1.000|0.955|0.977|0.000|0.000|0.000|
|54|V_N_FOR_N|102|0.962|1.000|0.981|0.769|1.000|0.870|
|55|V_N_FROM_N|83|0.988|0.988|0.988|1.000|1.000|1.000|
|56|V_N_IN_N|102|0.971|0.980|0.976|0.923|0.923|0.923|
|57|V_N_INTO_N|80|0.988|1.000|0.994|0.875|1.000|0.933|
|58|V_N_INTO_ING|22|1.000|1.000|1.000|1.000|1.000|1.000|
|59|V_N_OF_N|38|1.000|0.947|0.973|1.000|0.750|0.857|
|60|V_N_OFF_N|13|1.000|1.000|1.000|1.000|1.000|1.000|
|61|V_N_ON_N|110|0.965|1.000|0.982|0.867|1.000|0.929|
|62|V_N_OUT_OF_N|45|1.000|1.000|1.000|1.000|1.000|1.000|
|63|V_N_OVER_N|10|0.833|1.000|0.909|0.000|0.000|0.000|
|64|V_N_TO_N|222|0.991|0.986|0.989|0.952|0.952|0.952|
|65|V_N_TOWARD_N|14|1.000|1.000|1.000|1.000|1.000|1.000|
|66|V_N_WITH_N|149|0.980|0.993|0.987|0.941|0.941|0.941|
|67|V_FOR_N_TO_INF|6|1.000|1.000|1.000|N/A|N/A|N/A|
|68|V_IT_N/ADJ_CLAUSE|4|1.000|1.000|1.000|1.000|1.000|1.000|
