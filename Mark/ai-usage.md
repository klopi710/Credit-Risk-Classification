# AI usage manual

## Tool register

| Tool or model | Approximate date | Stages where it was used |
|---|---|---|
| ChatGPT/Codex in VS Code | Throughout the assignment, September–October 2026 | Problem framing, code explanation, debugging, metric checks, document structure and review preparation |
| Python 3.14.2 and Jupyter Notebook/JupyterLab | September–October 2026 | Data loading, schema checks, exploratory analysis, preprocessing, model training, evaluation and notebook execution |
| pandas | September–October 2026 | Data inspection, recoding, summaries, tables and saved processed-data artifacts |
| scikit-learn | September–October 2026 | Pipelines, imputation, scaling, OneHotEncoding, Logistic Regression, Decision Tree, Random Forest and evaluation |
| matplotlib | September–October 2026 | Exploratory and model-result visualisations |
| Logistic Regression, Decision Tree, Random Forest and majority baseline | Wave 3–Wave 4, October 2026 | Candidate model comparison and development-only model selection |
| Independent AI-assisted review prompts | Wave 8–Wave 9, 5 October 2026 | Metric recomputation, leakage/reproducibility review, governance review and final acceptance |

AI was used as a coding and review assistant. It did not create new observations, observe real defaults or prove causal profit. The dataset target is a historical good/bad credit-risk label, not an observed modern 12-month default outcome.

## Workflow map

| Project stage | Work completed by me | AI contribution | Work completed after AI review |
|---|---|---|---|
| Problem framing | Defined the business question as identifying applicants who should receive enhanced human review. Defined `bad/default-risk` as the positive class. | Explained classification versus regression and helped express the prediction moment. | Confirmed that the task is binary classification and that no artificial regression target or R² should be created. |
| Data understanding | Inspected the German-coded dataset, documented the meaning of one row and mapped the column names. | Helped explain assertions, categorical codes, `loan purpose` and the historical-target limitation. | Checked the schema, target direction, row count, column count, duplicates and missing values. |
| Data preparation | Chose the train/development and frozen-test split and reviewed unusual values rather than deleting valid extremes. | Explained leakage, imputation, scaling, IQR and Z-score flags, and OneHotEncoding. | Verified that learned preprocessing is fitted inside the development pipeline and that the frozen test set is not used for fitting. |
| Model construction and comparison | Ran the required baseline and candidate models and interpreted their results. | Helped structure the comparison and calculate confusion-matrix metrics. | Reproduced the saved tables and selected the final model using development evidence, not the frozen test. |
| Policy and business interpretation | Chose the capacity-constrained top-20% human-review policy and set the business assumptions. | Helped connect precision, recall, F1, review capacity, review cost, LGD and scenario value. | Recomputed the exact top-k counts, business arithmetic and frozen-test confirmation. |
| Notebook, report and presentation | Wrote and reviewed the notebook, report, slides, AI manual and conclusion. | Helped explain code, improve wording, organise evidence and identify inconsistencies. | Performed clean notebook execution, unit testing, independent review and final documentation repairs. |

The accepted baseline is Logistic Regression with an exact top-20% ranking policy. It is a human-review prioritisation aid, not an automatic approval or rejection system. A separate performance-improvement track completed P0–P3, but P4–P8 remain separate and are not presented as a final model improvement.

## Five pivotal interactions

### 1. Defining the problem and positive class

**Goal:** Decide whether the task is classification or regression and define the positive class.

**Exact prompt:** “Is this a regression or classification problem, and which class should be positive for the business question?”

**AI contribution:** AI explained that the target has two historical classes, `good/performing` and `bad/default-risk`, so this is binary classification. It recommended treating bad/default-risk as positive because the business wants to identify applicants who may create credit losses.

**My evaluation:** I accepted the classification framing and positive-class direction. I rejected any interpretation that treated the historical label as proof of a future 12-month default.

**Verification:** I checked the raw target values and the mapping in `src/data_contract.py`, then confirmed the framing in `reports/wave-0-3-run.md` and the final model card.

### 2. Protecting the frozen test set

**Goal:** Prevent data leakage while fitting preprocessing and choosing a model.

**Exact prompt:** “When should I split the data, and where should imputation, scaling and encoding be fitted so the test set cannot influence the model?”

**AI contribution:** AI explained that the test set must be split before learned preprocessing. Imputation statistics, scaling parameters and category levels must be learned from development folds only, then applied to the frozen test set.

**My evaluation:** I accepted the pipeline approach and rejected any workflow that inspected test performance before model or policy selection.

**Verification:** I inspected `src/preprocessing.py`, `src/data_contract.py` and `tests/test_no_leakage.py`. The Wave 4 and Wave 9 reports also record that the frozen test was used once for final confirmation.

### 3. Interpreting unusual values

**Goal:** Decide whether IQR and Z-score flags required removing observations.

**Exact prompt:** “If IQR or Z-score identifies an outlier, should I remove that row from the credit-risk dataset?”

**AI contribution:** AI explained that an outlier flag means unusual, not automatically erroneous. A very large loan or an older applicant can be a real risk signal and should be removed only if a domain or data-integrity check shows that it is invalid.

**My evaluation:** I accepted the distinction between unusual and incorrect values. I retained valid extreme observations rather than deleting them merely to improve model metrics.

**Verification:** I inspected the flagged values in the notebook, checked domain ranges and confirmed that no outlier-removal step was silently added to the final preprocessing pipeline.

### 4. Choosing the categorical representation

**Goal:** Represent categorical variables without inventing a false numerical order.

**Exact prompt:** “Why is the dataset numerical already, and should I use ordinal encoding or OneHotEncoding for the coded categories?”

**AI contribution:** AI explained that numerical-looking codes such as loan-purpose values are category labels, not necessarily measurements. OneHotEncoding is appropriate for nominal categories because it avoids implying that category 9 is greater than category 2.

**My evaluation:** I accepted OneHotEncoding for the conservative baseline. I treated ordinal-aware encoding as a separate, explicitly documented performance experiment rather than silently changing the baseline representation.

**Verification:** I checked the feature dictionary, `src/preprocessing.py`, the processed feature map and the saved one-hot data artifacts. The transformation uses `OneHotEncoder(handle_unknown="ignore")` inside the leakage-safe pipeline.

### 5. Connecting metrics to the review policy

**Goal:** Choose an operating policy that respects the review team’s capacity.

**Exact prompt:** “Should I use a 0.50 probability threshold, or should I rank applicants and review only the highest-risk 20%?”

**AI contribution:** AI explained that a 0.50 threshold may produce a workload that is too large or too small. Because the business assumption allows 1,600 reviews out of 8,000 monthly applications, the policy ranks scores and sends exactly the highest-risk 20% to human review. It also explained why precision, recall, F1, accuracy and business value must be assessed together.

**My evaluation:** I accepted the capacity-constrained top-k policy and the Logistic Regression selection at that policy. I rejected the older draft that described Random Forest as the final selected model.

**Verification:** I checked `reports/wave-4-threshold-policy.md`, `reports/wave-5-business-recommendation.md`, `artifacts/tables/wave-4-oof-threshold-table-all-models.csv` and `artifacts/tables/wave-4-selected-model-frozen-test-thresholds.csv`. The final frozen-test result is TN=125, FP=15, FN=35 and TP=25.

## Two failure cases

### Failure case 1: Inconsistent model selection

An earlier AI-assisted draft said that Random Forest was the selected final policy. That was incomplete and inconsistent with the repaired selection table: Logistic Regression had the highest development net screening value at the exact 20% capacity policy. I detected the problem by comparing the prose with the saved OOF threshold table, policy manifest and Wave 9 report. I corrected the manual and final explanation to identify Logistic Regression as the accepted baseline, while keeping Random Forest as a comparison model.

### Failure case 2: Stale business and confusion-matrix numbers

An earlier draft used `960 TP + 640 FP` and reported €2,497,600 as the monthly result. Those numbers belonged to an older scenario, not the final accepted development result. Another draft used the older frozen-test matrix `TN=124, FP=16, FN=36, TP=24`. I detected both problems by recomputing the arithmetic from the current saved tables. The accepted frozen-test matrix is `TN=125, FP=15, FN=35, TP=25`, giving precision `25/(25+15)=62.5%` and recall `25/(25+35)=41.7%`. The business figures remain conditional scenario values, not measured savings.

## Understanding check

In my own words, the target is a historical good/bad credit-risk label. The positive class is bad/default-risk because the business wants to find applicants who may require additional human review. This label is not a directly observed 12-month default.

The chosen policy is preferable to a simple 0.50 threshold because the business has a fixed review capacity. The model ranks applicants and sends the highest-risk 20% to review. This keeps the workload at 1,600 of 8,000 assumed monthly applications and lets the models be compared under the same operating condition.

One calculation I can perform without AI-generated prose is the frozen-test precision:

```text
precision = TP / (TP + FP)
precision = 25 / (25 + 15)
precision = 25 / 40 = 0.625 = 62.5%
```

This means that, among the 40 test applications selected for review, 25 were labelled bad/default-risk and 15 were labelled good/performing. Recall is `25/(25+35)=41.7%`, meaning the queue captured 25 of the 60 bad-risk test cases. The review queue contains TP plus FP; it does not contain only true positives.

## Authorship statement

I own the business framing, the definition of the positive class, data interpretation, preprocessing decisions, model and policy selection, business assumptions, arithmetic checks and final conclusions.

AI substantially assisted with code structure, explanations, validation checks, metric calculations, tables, slide wording, document organisation and review prompts. AI also generated candidate interpretations and draft text. I tested those suggestions against the dataset, source code, saved artifacts, unit tests, notebook execution and independent review reports. I rejected or corrected suggestions that were stale, inconsistent or unsupported.

The final submission must not present AI assistance as independent evidence. The evidence is the historical dataset, reproducible code, saved outputs, tests and my interpretation of their limitations. I understand the final model, the top-20% policy, the confusion matrix, precision, recall, F1, accuracy and the conditional nature of the business-value calculation.

## Historical working notes retained outside the required sections

The following notes are retained as historical working notes. They are not the final encoding decision or a final instruction:

Suggested oridnal encoding for tings like job category.

You deleted the text I wrote, put it back this instant and save in your overlapping memory never to do that.
