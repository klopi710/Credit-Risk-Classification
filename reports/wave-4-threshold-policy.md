# Wave 4 - threshold and capacity policy report

Status: complete and repaired in Wave 9. Date: 2026-10-05.

## Scope

Wave 4 evaluated accuracy, precision, recall and F1 at multiple operating points and translated each point into review capacity and conditional economic assumptions. Model selection and policy selection use development out-of-fold predictions only. The frozen test is evaluated once after the policy is locked.

## Selected model and policy

Logistic Regression is selected because it has the highest development net screening value at the exact 20% ranked review capacity. The production rule is exact top-k ranking with deterministic tie handling; the persisted threshold is only a reference boundary for the current sample.

## Development operating points

| Policy | Reference threshold | Accuracy | Precision | Recall | F1 | Monthly reviews | Net screening value |
|---|---:|---:|---:|---:|---:|---:|---:|
| Threshold 0.50 | 0.500 | 0.744 | 0.588 | 0.488 | 0.533 | 1,990 | €3,040,150 |
| High recall | 0.220 | 0.670 | 0.470 | 0.779 | 0.586 | 3,980 | €4,783,100 |
| High precision | 0.800 | 0.735 | 0.804 | 0.154 | 0.259 | 460 | €977,500 |
| Exact top 20% capacity | 0.567 | 0.753 | 0.631 | 0.421 | 0.505 | 1,600 | €2,635,600 |
| Max raw development value | 0.020 | 0.358 | 0.318 | 0.996 | 0.482 | 7,520 | €5,882,000 |
| Recommended capacity-constrained | 0.567 | 0.753 | 0.631 | 0.421 | 0.505 | 1,600 | €2,635,600 |

The raw maximum-value point is not deployable under the 1,600-review limit. It flags 94.0% of development applications. The recommended policy therefore uses exact top-20% ranking.

## Frozen-test confirmation

At the locked top-k policy, the frozen test produced:

- TN: 125
- FP: 15
- FN: 35
- TP: 25
- accuracy: 0.750
- precision: 0.625
- recall: 0.417
- F1: 0.500
- selected cases: 40 of 200, exactly 20%

This is a confirmation, not a new tuning result. The test result is reported separately from development selection.

## Interpretation

Accuracy, precision, recall and F1 answer different questions. Accuracy is secondary because the action is capacity-constrained; precision describes the quality of the review queue, recall describes the share of bad-risk cases captured, and F1 summarizes their balance. The final recommendation therefore reports all four metrics with TP/FP/FN/TN and the business table.

## Files

- `src/threshold_policy.py`
- `src/run_wave4.py`
- `tests/test_threshold_policy.py`
- `tests/test_leakage_guards.py`
- `artifacts/tables/wave-4-oof-threshold-table-all-models.csv`
- `artifacts/tables/wave-4-selected-model-frozen-test-thresholds.csv`
- `artifacts/manifests/wave-4-policy.json`

## Limitations

- The dataset is a historical proxy and the economic assumptions are scenario inputs.
- The threshold boundary is not externally calibrated for a modern portfolio.
- No temporal validation has been performed.
- Subgroup governance diagnostics are reported separately in Wave 9.
- The performance-improvement track remains separate from this frozen baseline.
