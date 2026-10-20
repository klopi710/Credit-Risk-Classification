# Wave 9 - governance and subgroup audit

Status: complete. Date: 2026-10-05.

The audit uses the already selected Logistic Regression model and the frozen test split. It is diagnostic only: no subgroup result was used to choose the model, threshold or queue.

Audited fields:

- `famges`: personal-status/sex proxy in the historical codebook;
- `gastarb`: foreign-worker proxy in the historical codebook.

For each group, the saved table reports sample size, selection rate with an exact beta interval, precision, TPR/recall and FPR. Small group sizes make intervals wide; these numbers are not a fairness certification. They are a governance gate before any real-world pilot.

The current decision is **no external deployment**. Before a pilot, the owner must justify the use of these fields or remove/constrain them, obtain a larger and time-valid sample, define acceptable disparity thresholds with legal/compliance review, and monitor actual human-review outcomes. The model remains a human-review prioritization aid, never an automatic approval or rejection system.

Evidence:

- `artifacts/tables/wave-9-subgroup-audit.csv`
- `artifacts/manifests/wave-9-governance.json`
- `src/run_wave9_governance.py`
