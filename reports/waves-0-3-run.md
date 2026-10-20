# Waves 0–3 execution report

Status: complete. Date: 2026-10-05.

## Scope executed

- Wave 0: provenance, environment, project structure and reproducibility manifest.
- Wave 1: exact schema contract, target mapping and source audit.
- Wave 2: leakage-safe preprocessing pipeline and frozen stratified split.
- Wave 3: majority baseline, Logistic Regression, controlled Decision Tree and Random Forest.

The source copy is `data/raw/SouthGermanCredit.asc`. Its SHA-256 is recorded in `artifacts/manifests/waves-0-3-run.json`. The positive class is `bad/default-risk`, mapped from `kredit == 0`.

## Verification

The test suite ran successfully:

- 4 tests passed.
- Exact 21-column schema verified.
- 1,000 rows verified.
- No missing values.
- No duplicate rows.
- Positive class count: 300.
- Frozen test split: 200 rows, including 60 positive cases.

Preprocessing is inside each estimator pipeline. Numeric columns are median-imputed and standardized; all other predictors are most-frequent-imputed and one-hot encoded. The pipeline is fitted within development folds, so the frozen test set is not used to learn transformations.

## Development out-of-fold results at threshold 0.50

| Model | Average precision | ROC-AUC | Precision | Recall | F1 | Brier |
|---|---:|---:|---:|---:|---:|---:|
| Majority baseline | 0.300 | 0.500 | 0.000 | 0.000 | 0.000 | 0.210 |
| Logistic Regression | 0.603 | 0.779 | 0.588 | 0.488 | 0.533 | 0.169 |
| Decision Tree | 0.476 | 0.698 | 0.468 | 0.425 | 0.445 | 0.181 |
| Random Forest | 0.607 | 0.789 | 0.649 | 0.308 | 0.418 | 0.164 |

Random Forest is the provisional development champion by average precision, followed closely by Logistic Regression. The result is not a final policy decision: threshold selection is deliberately deferred to Wave 4.

## Frozen-test diagnostic at threshold 0.50

| Model | TN | FP | FN | TP | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Majority baseline | 140 | 0 | 60 | 0 | 0.000 | 0.000 | 0.000 | 0.500 |
| Logistic Regression | 122 | 18 | 34 | 26 | 0.591 | 0.433 | 0.500 | 0.742 |
| Decision Tree | 126 | 14 | 38 | 22 | 0.611 | 0.367 | 0.458 | 0.700 |
| Random Forest | 133 | 7 | 39 | 21 | 0.750 | 0.350 | 0.477 | 0.761 |

The test table is diagnostic only. It must not be used to select a threshold after the fact. The low recall at 0.50 is precisely why Wave 4 needs a threshold sweep and business-cost translation.

## Files

- `src/data_contract.py`
- `src/preprocessing.py`
- `src/models.py`
- `src/evaluation.py`
- `src/build_waves_0_3.py`
- `tests/test_data_contract.py`
- `tests/test_metrics.py`
- `artifacts/tables/wave-3-development-oof-metrics.csv`
- `artifacts/tables/wave-3-frozen-test-metrics-at-0.5.csv`
- `artifacts/tables/wave-3-frozen-test-predictions.csv`
- `artifacts/models/*.joblib`
- `artifacts/manifests/waves-0-3-run.json`

## Limitations and next step

No threshold policy, business-value table, subgroup analysis, regression branch or zero-context sub-agent review has been run. The next bounded action is Wave 4: calculate development-only threshold candidates, select a policy without touching the frozen test set, and then confirm it once on the frozen test set.
