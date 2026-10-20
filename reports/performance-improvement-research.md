# Performance-improvement research

Date: 2026-10-05  
Status: research complete; no performance-improvement experiment executed.

## Baseline to beat

Wave 9 selected Logistic Regression with the exact capacity-constrained top 20% policy. On development OOF predictions at the selected operating point:

- accuracy: 0.753;
- precision: 0.631;
- recall: 0.421;
- F1: 0.505.

On the frozen test confirmation:

- accuracy: 0.750;
- precision: 0.625;
- recall: 0.417;
- F1: 0.500.

The improvement work must compare every candidate at the same capacity-constrained policy and keep the frozen test untouched until the final confirmation.

## Research findings

### 1. Threshold tuning is not model improvement

The default 0.50 decision rule is not guaranteed to be optimal for a decision problem. Current scikit-learn provides `TunedThresholdClassifierCV` for post-tuning a classifier threshold using cross-validation and a selected scoring function. The official cost-sensitive example also demonstrates custom scores built from the confusion matrix.

For this assignment, the existing manual threshold table is preferable to optimizing generic accuracy because the policy has a hard review capacity and explicit costs. A future implementation may use `TunedThresholdClassifierCV` as a cross-check, but the business scorer must remain capacity-aware.

Source: scikit-learn threshold tuning and cost-sensitive learning documentation.

### 2. PR analysis should lead model comparison under imbalance

The positive class is 30% in the UCI sample, and the operational policy reviews only 20% of monthly applications. ROC-AUC remains useful for ranking comparison, but precision-recall curves and average precision expose the quality of the positive queue more directly. Saito and Rehmsmeier’s peer-reviewed PLOS ONE analysis argues that PR plots are more informative than ROC plots for imbalanced binary classification.

This does not mean PR-AUC is sufficient: precision changes with prevalence, and the final decision still needs precision, recall, F1, accuracy, confusion counts and business value at the fixed capacity.

Source: Saito & Rehmsmeier (2015), PLOS ONE, DOI 10.1371/journal.pone.0118432.

### 3. Class weighting is the first low-risk imbalance experiment

scikit-learn supports `class_weight='balanced'` for Logistic Regression and tree-based classifiers. It reweights the loss inversely to observed class frequency. This can improve minority recall without inventing observations, but it can change probability calibration and reduce precision at a fixed threshold.

Therefore class weighting must be tested as a separate ablation and followed by threshold re-selection and calibration checks. It must not be judged at an unchanged threshold of 0.50.

Source: scikit-learn Logistic Regression API.

### 4. SMOTE is a candidate, not a default

The original SMOTE paper by Chawla, Bowyer, Hall and Kegelmeyer (2002) supports synthetic minority oversampling as one approach to imbalanced classification. Modern imbalanced-learn documentation shows that samplers should be placed inside an imbalanced-learn pipeline so resampling happens during fitting and stays within the training folds.

For this dataset, one-hot encoded categorical variables make naive SMOTE questionable because interpolation between dummy columns can create artificial combinations. If resampling is tested, the order should be:

1. use class weights first;
2. test `SMOTENC` before one-hot encoding if category-aware resampling is justified;
3. use SMOTE only inside cross-validation training folds;
4. assess precision, recall, F1, accuracy, PR-AUC and calibration;
5. reject it if it improves recall only by producing an unusably noisy review queue.

Sources: Chawla et al. (2002), Journal of Artificial Intelligence Research; imbalanced-learn pipeline and resampling documentation.

### 5. Hyperparameter search should target the real objective

Grid or randomized search is useful only if its scoring function matches the intended operating point. Searching for maximum accuracy would favor the majority class and can select the wrong model. Search should use development-only cross-validation and record multiple metrics, with a custom capacity-aware score as the primary business objective.

The search space should remain small because the dataset has only 1,000 rows. Large unconstrained searches increase variance and make the assignment harder to explain.

### 6. Calibration matters because the threshold uses probabilities

scikit-learn recommends fitting calibration on data independent of the data used to fit the base classifier. It supports sigmoid and isotonic calibration through `CalibratedClassifierCV`. Niculescu-Mizil and Caruana’s ICML 2005 study shows that accuracy/AUC and probability quality are different properties, and that calibration can materially change the quality of predicted probabilities.

Calibration is not expected to improve ranking metrics such as ROC-AUC by itself. Its role is to make a score such as 0.46 more defensible as a probability-like operating input and to stabilize threshold decisions.

Sources: scikit-learn probability-calibration documentation; Niculescu-Mizil & Caruana (2005), ICML.

### 7. Feature representation is probably the strongest dataset-specific lever

The current baseline treats all non-continuous predictors as one-hot categorical variables. The UCI documentation distinguishes quantitative, ordinal and categorical fields. A controlled representation ablation should compare:

- current conservative one-hot treatment;
- ordinal-aware encoding for genuinely ordered variables;
- one-hot plus domain features such as amount per month of duration and duration bands;
- regularized Logistic Regression with interactions only where justified;
- tree models using the same leakage-safe raw representation.

Any derived feature must be available at the prediction moment and documented. Feature engineering is more defensible here than blindly adding a more complex model because the dataset is small and historical.

### 8. A second model family is justified, but deep learning is not

The next model candidates should be HistGradientBoosting or a carefully tuned gradient-boosted tree, ExtraTrees, and calibrated variants of the current Logistic Regression and Random Forest. These are small-tabular-data candidates.

Deep learning should not be the next experiment: 1,000 rows and mixed low-cardinality variables do not justify its complexity for this assignment, and it would make the explanation weaker without a clear expected gain.

## Recommended conclusion

The consensus-supported sequence is:

1. stabilize repeated/nested development evaluation;
2. test representation and class weights;
3. tune a small set of Logistic Regression, Random Forest and gradient-boosted-tree parameters;
4. test category-aware resampling only as a controlled ablation;
5. calibrate the best few candidates;
6. reselect the capacity-constrained threshold;
7. compare precision, recall, F1 and accuracy together;
8. confirm exactly once on the frozen test.

No method is accepted merely because one metric rises. A candidate must improve the relevant Pareto position without producing an unacceptable collapse in another requested metric or in the business review queue.

## Sources

- scikit-learn threshold tuning: https://scikit-learn.org/stable/auto_examples/model_selection/plot_tuned_decision_threshold.html
- scikit-learn cost-sensitive threshold tuning: https://scikit-learn.org/stable/auto_examples/model_selection/plot_cost_sensitive_learning.html
- scikit-learn probability calibration: https://scikit-learn.org/stable/modules/calibration.html
- scikit-learn Logistic Regression and class weights: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html
- Saito & Rehmsmeier (2015): https://doi.org/10.1371/journal.pone.0118432
- Chawla et al. (2002), SMOTE: https://www.cs.cmu.edu/afs/cs.cmu.edu/project/jair/pub/volume16/chawla02a.pdf
- imbalanced-learn pipeline: https://imbalanced-learn.org/stable/references/pipeline.html
- Niculescu-Mizil & Caruana (2005): https://icml.cc/Conferences/2005/proceedings/papers/079_GoodProbabilities_NiculescuMizilCaruana.pdf
