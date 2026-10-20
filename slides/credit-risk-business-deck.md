# Credit Risk Classification

## Slide 1 - Conclusion

Use Random Forest to rank the highest-risk 20% of applications.

Send them to human review.

Do not auto-approve or auto-reject.

Final test: 60% precision. 40% recall. 48% F1. 74% accuracy.

## Slide 2 - Monthly conclusion

8,000 applications.

1,600 human reviews.

Expected incremental net screening value: EUR 2,497,600.

EUR 2,592,000 loss avoided - EUR 56,000 review cost - EUR 38,400 friction loss.

Model-running cost is assumed negligible and is not quantified.

This is scenario-based value. It is not causal profit.

## Slide 3 - Required threshold table

| Split | Model and threshold | Reviews / month | TP | FP | FN | TN | Precision | Recall | Loss avoided / month | Net value / month |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Development OOF | Majority baseline; top 20% | 1,600 | 550 | 1,050 | 1,850 | 4,550 | 34.4% | 22.9% | EUR 1,485,000 | EUR 1,366,000 |
| Development OOF | Logistic Regression; top 20% | 1,600 | 1,020 | 580 | 1,380 | 5,020 | 63.8% | 42.5% | EUR 2,754,000 | EUR 2,663,200 |
| Development OOF | Decision Tree; top 20% | 1,600 | 770 | 830 | 1,630 | 4,770 | 48.1% | 32.1% | EUR 2,079,000 | EUR 1,973,200 |
| Development OOF | Random Forest; top 20% | 1,600 | 1,040 | 560 | 1,360 | 5,040 | 65.0% | 43.3% | EUR 2,808,000 | EUR 2,718,400 |
| Frozen test | Random Forest; top 20% | 1,600 | 960 | 640 | 1,440 | 4,960 | 60.0% | 40.0% | EUR 2,592,000 | EUR 2,497,600 |

All counts and values are scaled to 8,000 monthly applications.

## Slide 4 - Data and target

South German Credit.

1,000 historical applications. 20 predictors. 700 good. 300 bad.

Unit: one credit application.

Prediction moment: before the credit offer.

Target excluded from features. No rows removed.

The `good/bad` label is a historical credit-risk proxy.

It is not an observed 12-month default outcome.

The business values are assumptions, not measured causal savings.

## Slide 5 - Preparation

80/20 stratified split.

The 200-row test set stays frozen.

Numeric features: imputation and StandardScaler inside the pipeline.

Categorical features: OneHotEncoder inside the pipeline.

No target leakage.

## Slide 6 - Models and validation

Candidates: majority baseline, Logistic Regression, Decision Tree and Random Forest.

Random Forest was selected on development data at exact 20% capacity.

Five-fold development checks: ROC-AUC 0.797. Average precision 0.642. Brier 0.165.

Calibration and specificity were also checked.

Monitor: recall, precision, specificity, false-positive rate, calibration, queue volume, review cost and net value.

## Slide 7 - Outliers and sensitivity

IQR and Z-score flags were inspected.

Valid extremes were retained. Unusual does not mean wrong.

Sensitivity depends on review effectiveness, LGD, abandonment and future outcome rates.

## Slide 8 - Policy and governance

Rank risk scores.

Send exactly the highest-scoring 20% to enhanced human review.

Keep ordinary human processing for the remaining applications.

Monitor recall, precision, calibration, drift and subgroup error rates.

Record reviewer outcomes. Keep human override. Make no automatic lending decision.

Alternative rules: lower threshold for higher recall; higher threshold for higher precision; expected-value threshold; or segmented thresholds by risk group. A lower-threshold option must expand capacity or be re-optimised under the 1,600-review limit.

## Slide 9 - Recommendation

Use Random Forest as a review-prioritisation aid only.

Recall is 40%. The queue misses 60% of bad-risk cases.

It supplements human reviewers and other controls. It does not replace them.

Decision formula:

`Scenario net policy value = sum(review: p_bad × review effectiveness × LGD - review cost - (1 - p_bad) × abandonment rate × contribution) - all-applications × model-running cost.`

Here `p_bad` is the model's uncalibrated score for the historical bad-risk label, used for ranking. It is not an observed 12-month default probability. Calibrate and prospectively validate it before using the formula for monetary decisions.

At fixed capacity, rank applications by expected value and select the highest-scoring 20%.

Action plan: measure electricity, compute, cybersecurity and storage costs. Pilot the model as a supplement to human review. Record reviewer outcomes. Recalibrate and retrain only with new evidence. Use RAG for policy and case-document retrieval. Fine-tune an LLM only if enough reviewed text exists and it improves the workflow.

Before rollout: verify decision-time features, the outcome horizon, temporal validation, calibration and governance.
