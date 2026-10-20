# Performance improvement — Block P-A report

Status: P0–P3 complete. P4–P8 not executed. Date: 2026-10-05.

## Scope

Executed only:

- P0 evaluation stabilization and exact Wave 3 reproduction;
- P1 representation ablations;
- P2 class-weight ablations;
- P3 compact hyperparameter searches.

The frozen test set was not used for model selection, hyperparameter selection, feature selection or threshold selection.

## P0 — baseline reproduction

The new evaluator reproduces the previous Wave 3 Random Forest OOF metrics exactly within numerical tolerance:

| Metric | Previous | Reproduced | Match |
|---|---:|---:|---|
| Average precision | 0.607092 | 0.607092 | yes |
| ROC-AUC | 0.788914 | 0.788914 | yes |
| Precision at 0.50 | 0.649123 | 0.649123 | yes |
| Recall at 0.50 | 0.308333 | 0.308333 | yes |
| F1 at 0.50 | 0.418079 | 0.418079 | yes |

This is the control result for the improvement experiments.

## P1/P2 — repeated development evaluation at fixed top-20% capacity

The table below uses 5 folds × 3 repeats on the 800-row development set. Metrics are means across validation folds; the capacity policy selects the top 20% of each fold by score.

| Variant | Accuracy | Precision | Recall | F1 | Avg precision | ROC-AUC |
|---|---:|---:|---:|---:|---:|---:|
| Logistic ordinal | 0.762 | 0.654 | 0.436 | 0.523 | 0.614 | 0.791 |
| Logistic domain | 0.757 | 0.642 | 0.428 | 0.513 | 0.614 | 0.784 |
| Random Forest domain | 0.756 | 0.640 | 0.426 | 0.512 | 0.625 | 0.798 |
| Extra Trees ordinal | 0.756 | 0.640 | 0.426 | 0.512 | 0.595 | 0.777 |
| Logistic balanced | 0.755 | 0.638 | 0.425 | 0.510 | 0.613 | 0.782 |
| HistGradientBoosting ordinal | 0.752 | 0.629 | 0.419 | 0.503 | 0.623 | 0.790 |
| Random Forest balanced | 0.752 | 0.629 | 0.419 | 0.503 | 0.617 | 0.784 |
| Logistic current | 0.752 | 0.629 | 0.419 | 0.503 | 0.615 | 0.782 |
| Random Forest current | 0.750 | 0.625 | 0.417 | 0.500 | 0.621 | 0.783 |
| Random Forest ordinal | 0.749 | 0.623 | 0.415 | 0.498 | 0.617 | 0.778 |

The strongest repeated-CV F1 is Logistic ordinal at 0.523. Compared with the current Random Forest at 0.500 in this repeated evaluator, that is a promising development improvement, not yet a final result.

The strongest average precision is Random Forest domain at 0.625, while its F1 is below Logistic ordinal. This is exactly why the model cannot be selected on one metric alone.

## P3 — compact searches

The search optimized capacity-constrained F1 using 5-fold development CV:

| Search | Best CV capacity F1 | Best parameters |
|---|---:|---|
| Logistic Regression | 0.535 | solver `liblinear`, class weight `balanced`, `C=100` |
| Random Forest | 0.515 | 300 trees, `min_samples_leaf=20`, `max_features=log2`, no depth limit, class weight `balanced` |
| HistGradientBoosting | 0.510 | 250 iterations, learning rate 0.02, 15 leaf nodes, min leaf 30, L2=10 |

The Logistic Regression search is the leading candidate for P4, but its apparent advantage still needs repeated evaluation, calibration and threshold-policy testing. The search score is not a frozen-test score.

## Corrections during execution

Two integration defects were found and repaired:

1. The P0 adapter initially returned capacity metrics while comparing against the Wave 3 threshold-0.50 table. It was corrected to return both metric families; exact reproduction then passed.
2. The domain feature transformer added columns while declaring an unchanged feature-name output. Its declaration was corrected, and the full experiment completed.

All seven tests pass after repair.

## Artifacts

- `src/performance_variants.py`
- `src/performance_evaluation.py`
- `src/run_performance_block_a.py`
- `tests/test_performance_evaluation.py`
- `artifacts/performance/tables/p1-p2-repeated-capacity-results.csv`
- `artifacts/performance/tables/p1-p2-repeated-capacity-summary.csv`
- `artifacts/performance/tables/p3-search-results.csv`
- `artifacts/performance/manifests/p0-baseline-reproduction.json`
- `artifacts/performance/manifests/performance-block-a.json`
- `artifacts/performance/models/`

## Remaining performance work

P4–P8 remain separate: category-aware resampling, calibration, final threshold re-selection, optional blending, zero-context reviewers and frozen-test confirmation. They must not start automatically from this result.
