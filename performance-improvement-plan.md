# Separate performance-improvement plan

Status: P0–P3 executed and verified. P4–P8 remain pending authorization.

## Objective

Improve the Credit Risk classifier’s precision, recall, F1 and accuracy while preserving the frozen test set and the capacity-constrained business policy. The existing Wave 4 result is the immutable baseline for comparison.

Wave 9 frozen baseline at the exact selected top-20% operating point:

- development OOF: accuracy 0.753, precision 0.631, recall 0.421, F1 0.505;
- frozen test: accuracy 0.750, precision 0.625, recall 0.417, F1 0.500.

## Non-negotiable evaluation protocol

- Never use the frozen test set to choose features, hyperparameters, class weights, resampling, calibration or thresholds.
- Use repeated stratified development cross-validation for experiments.
- Generate out-of-fold probabilities for threshold and calibration decisions.
- Compare every candidate at the same 20% review-capacity policy.
- Report precision, recall, F1 and accuracy together, plus PR-AUC, ROC-AUC, confusion matrix and business value.
- Keep a complete experiment registry: data representation, estimator, parameters, seed, fold scores, threshold and artifacts.
- Confirm only the final locked candidate once on the frozen test.

## Performance waves

### P0 — evaluation stabilization

Create repeated stratified 5-fold OOF evaluation, confidence intervals or fold dispersion, PR curves and a capacity-aware scorer. Reproduce the Wave 4 baseline through the new evaluator before testing improvements.

Done when the new evaluator reproduces the saved Wave 4 metrics within a documented tolerance.

### P1 — representation ablations

Compare:

1. current one-hot representation;
2. ordinal-aware representation for variables explicitly described as ordered;
3. one-hot plus a small, justified set of domain features:
   - amount per month of duration;
   - duration bands;
   - savings/employment/property interactions only if available at application time.

No feature enters the model without a data-contract entry and leakage review.

### P2 — class-weight ablations

For Logistic Regression, Decision Tree, Random Forest and any new tree model, compare `class_weight=None`, `balanced` and at most two explicit cost-informed weights. Recalibrate/reselect threshold after every variant.

Primary question: can recall improve at the fixed review capacity without unacceptable precision or F1 loss?

### P3 — compact hyperparameter search

Use development-only randomized or grid search:

- Logistic Regression: `C`, penalty/solver-compatible pairs, class weight;
- Decision Tree: depth, minimum leaf size, split criterion, class weight;
- Random Forest: number of trees, depth, minimum leaf size, max features and class weight;
- HistGradientBoosting or another small-tabular boosting candidate: learning rate, iterations, depth/leaf constraints and regularization.

Primary search score: capacity-constrained F1 or a documented cost-aware score. Secondary scores: precision, recall, accuracy, PR-AUC and calibration.

### P4 — resampling as a controlled experiment

Only after class-weight tests:

- test category-aware `SMOTENC` before one-hot encoding if technically justified;
- compare a conservative sampling ratio rather than forcing 50/50;
- keep sampler inside the cross-validation pipeline;
- assess whether synthetic records create implausible combinations;
- reject the variant if precision or calibration deteriorates at the operating point.

### P5 — calibration and probability quality

For the best two or three ranking models, compare raw probabilities with sigmoid and isotonic calibration using independent development folds. Then reselect the capacity-constrained threshold.

Accept calibration only if it improves probability reliability or stabilizes the operating policy; do not claim it improved discrimination if PR-AUC/ROC-AUC is unchanged.

### P6 — ensemble and final performance selection

Test a small blend of the strongest calibrated candidates only if their errors are meaningfully different. Select the final candidate using a Pareto rule:

- no material collapse in precision;
- no material collapse in recall;
- F1 improves or remains stable;
- accuracy is reported and does not fall below the agreed guardrail;
- capacity and net screening value remain acceptable.

Do not select a model because it wins one metric by sacrificing the others.

### P7 — independent performance review

Use zero-context sub-agents after the experiment registry is complete:

- metric auditor: recompute precision, recall, F1 and accuracy;
- split/leakage auditor: inspect whether any improvement used test information;
- imbalance auditor: inspect weights/resampling and calibration effects;
- model-selection auditor: verify the chosen candidate follows the predeclared Pareto rule;
- adversarial reviewer: attempt to find a threshold or feature-engineering artifact that makes the improvement illusory.

Each reviewer receives only the baseline, experiment registry, selected artifacts and a focused prompt. They return a structured verdict and do not edit code.

### P8 — final locked comparison

- freeze representation, model, calibration and threshold;
- rerun the full development evaluation;
- evaluate once on the frozen test;
- compare against Wave 4 in one table;
- record whether the improvement is real, metric-specific or not robust;
- preserve the Wave 4 model as rollback.

## Acceptance rule

The performance program succeeds only if the final candidate improves the agreed primary metric at the capacity-constrained operating point and does not materially worsen the other requested metrics. If no candidate beats the baseline robustly, keep the Wave 4 model and explain that the data, target proxy and sample size limit the achievable gain.

## Execution blocks and budget

Block P-A: P0–P3. Forecast: 4–7 root turns plus 3–5 independent review turns, approximately 10–20% of one weekly allowance. Stop for a budget review at 15%.

Block P-B: P4–P8. Forecast: 4–8 root turns plus 4–6 independent review turns, approximately 10–20% additional weekly allowance. It requires a new explicit authorization and never starts automatically after P-A.

## Current state

Wave 4 is complete. P0–P3 have now been executed without touching the frozen test set. P4–P8 have not been executed. The next action, if authorized, is P4 only.

Resume phrase: `Mejora Marc Torrens — P0.`
