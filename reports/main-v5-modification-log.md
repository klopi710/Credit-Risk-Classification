# `main.v5.ipynb` modification log

Date: 2026-11-06

## Modified file

`notebooks/main.v5.ipynb`

The original `main.v4.ipynb` was not modified.

## Changes made

1. Kept Random Forest as the selected model and added an explicit note that model and policy selection use development out-of-fold results; the frozen test set is confirmation only.
2. Clarified that a threshold is a cutoff on the estimated probability of historical `bad/default-risk`.
3. Clarified that the deployable policy is exact top-20% ranking because review capacity is fixed at 1,600 of 8,000 applications. The displayed probability is a reference boundary for the current sample.
4. Added frozen-test ROC and precision-recall plots, including ROC-AUC and average precision.
5. Replaced the incomplete threshold table with six operating points and made the cutoff explicit in each label:
   - default threshold 0.50;
   - high recall threshold 0.29;
   - additional mid-range threshold 0.40;
   - high precision threshold 0.58;
   - higher-precision low-volume threshold 0.65;
   - capacity-constrained / recommended top-20% queue with a reference threshold.
6. Added the required TP, FP, FN, TN, precision, recall, loss avoided and net value columns, plus reviews, review percentage, F1, expected defaults prevented, review cost, friction loss, cost per expected default prevented and missed avoidable loss.
7. Added development OOF comparison beside the frozen-test confirmation table.
8. Added sensitivity analysis for base, conservative, adverse and upside assumptions.
9. Added the subgroup governance audit for `famges` and `gastarb`, with the small-sample/fairness-certification limitation.
10. Added the reproducibility note with Python/package versions, random seed, relative project paths and the execution command.
11. Corrected the broken relative image path from `../Mark/image/business_assumptions.png` to `../image/business_assumptions.png`.
12. Preserved the existing proxy-target limitation: `good/bad` is not an observed 12-month default outcome.
13. Simplified the operating-point labels so the reader can immediately see which score cutoff is being tested. The recommended row remains a top-20% capacity rule; its displayed threshold is only a reference boundary.
14. Converted the existing plain-English cut-off explanation from a Python cell to a Markdown cell so the notebook passes code syntax checks without changing the sentence.

## Preservation backups

- `reports/save-conflict-backups/main.v5-before-edit-20261106-105215.ipynb`
- `reports/save-conflict-backups/main.v5-after-structure-before-path-fix-20261106-105652.ipynb`
- `reports/save-conflict-backups/main.v5-execution-input-after-kernel-failure.ipynb`

The first backup matched the original `main.v5.ipynb` byte-for-byte before editing.

## Verification

- Notebook JSON parses successfully.
- All code cells pass Python AST syntax parsing.
- Required static checks pass for the six operating points, ROC curve, precision-recall curve, sensitivity analysis, governance audit, reproducibility note, proxy-target limitation, Random Forest selection and corrected image path.
- Final notebook SHA-256: `58ec3fba358d19ce215a9512e000bbf10fb83570ca3a89562f25f8aaad16430a`.

A clean Jupyter execution was attempted from the project-relative location. The kernel died in the local Windows ZeroMQ/Jupyter environment before producing a completed executed notebook (`Assertion failed: error not defined ... ip.cpp:464`). The edited notebook is therefore syntactically and structurally verified, but a full clean-kernel run remains an environment-level verification item.

## Follow-up audit and fixes

Two independent zero-context reviewers audited v5 against v4 and the assignment specification. Both confirmed that the original narrative and conclusion cells remain; one identified that the previous replacement of the threshold cell had removed the per-model TP/FP/FN/TN and loss-avoided comparison, and the other identified incomplete management interpretation, sensitivity policy re-evaluation and package documentation.

The follow-up changes were:

- restored the original v4 threshold-section title and original Random Forest explanation wording;
- restored the all-model fixed-capacity comparison with scaled TP, FP, FN, TN, loss avoided and net value;
- added explicit answers for recall/precision trade-offs, error cost, capacity binding, prevalence, net value versus missed avoidable loss, and missing information;
- re-evaluated all six operating points under all four sensitivity scenarios and verified that the capacity-constrained top-20% policy remains the highest-value feasible point;
- added `openpyxl` and `joblib` to the reproducibility package list;
- corrected the reproducibility note to describe current-working-directory root discovery accurately.

Additional preservation backup:

- `reports/save-conflict-backups/main.v5-before-current-audit-20261106-164815.ipynb`
- `reports/save-conflict-backups/main.v5-before-review-fixes-20261106-165857.ipynb`

The current notebook contains 72 cells, has no Python syntax errors or duplicate cell IDs, and passes the static requirement checks. Current notebook SHA-256: `774ae5f58fb01043c5e93f5200989ba98a6f2ac8abd09f9e92d068ac0bd73ff6`.
