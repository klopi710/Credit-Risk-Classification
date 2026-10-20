# Wave 5 - business recommendation and sensitivity

Status: complete. Date: 2026-10-05.

## Recommended policy

Use the selected Logistic Regression model as a ranking aid. Rank applications by predicted `bad/default-risk` score and send exactly the highest-scoring 20% - at most 1,600 of 8,000 monthly applications - to enhanced manual review, resolving score ties deterministically.

The policy must not automatically approve or reject an application. Reviewers should record the outcome, evidence considered and whether the review prevented a loss. Applications outside the queue continue through the ordinary human credit process; they are not automatically approved, rejected or treated as safe. The persisted probability is a reference boundary for this sample; production-like operation uses the exact top-k queue so capacity remains hard-bounded.

## Base development economics

At the Wave 9 capacity-constrained operating point:

- accuracy: 0.753;
- precision: 0.631;
- recall: 0.421;
- F1: 0.505;
- 1,600 monthly reviews;
- 454.5 modeled bad-credit events prevented;
- €2,727,000 scenario-estimated avoided loss;
- €56,000 review cost;
- €35,400 modeled friction loss;
- €2,635,600 conditional net screening value;
- €123.21 cost per modeled event prevented.

The frozen-test confirmation has accuracy 0.750, precision 0.625, recall 0.417 and F1 0.500 with 125 TN, 15 FP, 35 FN and 25 TP. Exactly 40 of 200 cases are selected. This is a confirmation of the locked policy, not a new threshold selection.

## Sensitivity

| Scenario | Review effectiveness | LGD | Review cost | Abandonment | Development net value | Test net value |
|---|---:|---:|---:|---:|---:|---:|
| Base | 45% | €6,000 | €35 | 5% | €2,635,600 | €2,608,000 |
| Conservative | 30% | €4,000 | €45 | 8% | €1,083,360 | €1,070,400 |
| Adverse | 20% | €3,000 | €60 | 10% | €439,200 | €432,000 |
| Upside | 60% | €8,000 | €25 | 3% | €4,786,760 | €4,738,400 |

The model's metric values do not change across these scenarios; the economics do. Even the adverse scenario is positive under the assignment's assumptions, but this is conditional scenario arithmetic, not evidence of real-world profitability or causal loss prevention because review effectiveness, LGD and real default outcomes are not observed in the dataset.

## Operating limits

- Manual-review capacity is a hard constraint.
- The queue must be ranked and selected by exact top-k, not by an arbitrary fixed probability if ties or prevalence drift alter workload.
- No automatic approve/reject action.
- Monitor precision, recall, F1, accuracy, review volume, actual review effectiveness, subgroup error rates and data drift.
- Re-estimate the policy if review effectiveness, LGD, abandonment or portfolio prevalence changes.

## Important qualification

The current policy is the Wave 9-frozen Logistic Regression baseline selected on development capacity value. The separate performance program remains a research track; no later candidate may replace this baseline without calibration, final threshold selection, independent review and one frozen-test confirmation.
