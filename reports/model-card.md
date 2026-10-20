# Model card — Credit Risk review-prioritization baseline

## Model

Logistic Regression classifier trained inside a preprocessing pipeline. The current policy ranks applications by predicted probability of `bad/default-risk` and sends exactly the highest-scoring 20% to manual review, with deterministic tie handling.

## Intended use

Prioritize enhanced manual review. The model is not intended for automatic approval, automatic rejection, pricing, eligibility or a final lending decision.

## Data

South German Credit: 1,000 historical records, 20 predictors and a binary `bad/good` outcome. `bad` is mapped to the positive class. Numeric fields are imputed and scaled; other predictors are imputed and one-hot encoded inside the pipeline.

## Performance

Development capacity policy: accuracy 0.753, precision 0.631, recall 0.421, F1 0.505. Frozen-test confirmation: accuracy 0.750, precision 0.625, recall 0.417, F1 0.500. The frozen test contains 125 TN, 15 FP, 35 FN and 25 TP, with exactly 40 of 200 cases selected.

## Limitations

- Historical data from the 1970s.
- The target is a proxy for bad credit, not a directly observed next-12-month default target.
- Small sample and unknown deployment prevalence.
- No causal claim that review prevents a default.
- The `famges` and `gastarb` fields are sensitive/proxy variables. Wave 9 reports selection rate, precision, TPR and FPR diagnostics; these small-sample results are governance gates, not fairness certification.
- No calibration or temporal validation has been completed.

## Human oversight

Every flagged application requires human review. Unflagged applications continue through the ordinary human credit process; they are not automatically approved, rejected or treated as safe. Reviewers must be able to override the queue, record evidence and escalate uncertain cases. The model output is one input to review, not the decision itself.

## Reproducibility

Source hash, environment, random seed and split are recorded in `artifacts/manifests/waves-0-3-run.json`. Wave 4 policy metrics are recorded in `artifacts/manifests/wave-4-policy.json`; governance audit lineage is recorded in `artifacts/manifests/wave-9-governance.json`.
