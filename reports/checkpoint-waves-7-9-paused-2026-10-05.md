# Checkpoint - Waves 7-9 paused

Date: 2026-10-05
Status: superseded after resume. Waves 7-9 are now accepted; this file remains the historical pause/resume record.

## Completed work

- Wave 7 deliverables exist: notebook, editable business deck, model card and GenAI-use manual.
- Wave 8 completed five zero-context independent reviews (A data/leakage, B metrics/threshold, C reproducibility, D business/rubric, E adversarial). Their reports are preserved under `review/submissions/`.
- Wave 9 repairs were applied:
  - model selection now uses development OOF net screening value at exact 20% capacity;
  - Logistic Regression is the selected model;
  - shared deterministic top-k selection is used for development policy and frozen-test confirmation;
  - stale/swapped report metrics were regenerated;
  - prediction-moment and feature-availability limits were documented;
  - subgroup governance audit for `famges` and `gastarb` was added;
  - scenario economics are explicitly conditional, not causal evidence;
  - README command order and notebook dependencies/path handling were improved.

## Important current evidence

- Development exact top-k: accuracy 0.753, precision 0.631, recall 0.421, F1 0.505, 1,600 reviews, conditional net value EUR 2,635,600.
- Frozen-test exact top-k: TN 125, FP 15, FN 35, TP 25; accuracy 0.750, precision 0.625, recall 0.417, F1 0.500; 40/200 selected.
- `py -m src.run_wave4` completed successfully after the policy repair and selected `logistic_regression`.
- `py -m src.run_wave5` completed successfully after the policy repair.
- The governance audit completed and wrote `artifacts/tables/wave-9-subgroup-audit.csv` and `artifacts/manifests/wave-9-governance.json`.
- Before the latest documentation/notebook edits, the test suite passed 11 tests. The notebook JSON and final edited files still need the final verification pass.

## Files changed or created in this paused block

Implementation:

- `src/threshold_policy.py`
- `src/performance_evaluation.py`
- `src/run_wave4.py`
- `src/run_wave9_governance.py`
- `tests/test_threshold_policy.py`
- `tests/test_leakage_guards.py`
- `README.md`
- `requirements.txt`

Deliverables and governance:

- `notebooks/credit_risk_assignment.ipynb`
- `slides/credit-risk-business-deck.md`
- `reports/model-card.md`
- `reports/wave-4-threshold-policy.md`
- `reports/wave-5-business-recommendation.md`
- `reports/feature-availability-audit.md`
- `reports/wave-9-governance-audit.md`
- `performance-improvement-plan.md`
- `reports/performance-improvement-research.md`

Review evidence:

- `review/prompts/reviewer-a-data-leakage.md`
- `review/prompts/reviewer-b-metrics-threshold.md`
- `review/prompts/reviewer-c-reproducibility.md`
- `review/prompts/reviewer-d-business-rubric.md`
- `review/prompts/reviewer-e-adversarial.md`
- `review/submissions/reviewer-a-data-leakage.md`
- `review/submissions/reviewer-b-metrics-threshold.md`
- `review/submissions/reviewer-c-reproducibility.md`
- `review/submissions/reviewer-d-business-rubric.md`
- `review/submissions/reviewer-e-adversarial.md`

Generated artifacts refreshed by the repaired runners include the Wave 4 tables/manifests, Wave 5 sensitivity tables/manifest, and Wave 9 governance table/manifest.

## Current blockers / unfinished items

1. Final acceptance has not been run after the last notebook and documentation edits.
2. The notebook's declared Jupyter dependencies were added to `requirements.txt`, but a full clean notebook execution has not been run in this environment.
3. At least one independent reviewer must re-check the repaired major findings before final acceptance.
4. `architecture.md` and the final Wave 7-9 handoff have now been updated; this checkpoint is retained as the historical pause record.
5. Performance P4-P8 remain a separate pending workstream and must not start automatically.

## Exact next action after resume

From `C:\Users\katom\iCloudDrive\Smaller Creator\Sky\Marc Torrens Assignment`, run this bounded verification sequence first:

```powershell
py -m unittest discover -s tests -v
py -m json.tool notebooks\credit_risk_assignment.ipynb > $null
py -m src.run_wave9_governance
```

The paused sequence is complete. The durable final acceptance is `reports/wave-9-final-acceptance.md`. The next action is a separate explicit authorization for performance P4, if desired.
