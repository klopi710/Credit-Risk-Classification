# Reviewer A — data contract and leakage

You are an independent reviewer with no access to the conversation that initiated this work. Inspect the assignment folder at `C:\Users\katom\iCloudDrive\Smaller Creator\Sky\Marc Torrens Assignment` read-only.

Review `src/data_contract.py`, `src/preprocessing.py`, `src/build_waves_0_3.py`, the raw-data documentation, manifests, `reports/model-card.md`, and the notebook. Verify target direction, prediction moment, schema, missingness, leakage controls, split discipline, preprocessing fit boundaries, and whether any test information influences model or threshold selection.

Do not edit files. You may run bounded read-only inspection or the existing test suite. Return a structured report with:
- verdict: PASS, PASS WITH FINDINGS, or FAIL;
- each finding with severity blocker/major/minor;
- exact evidence path and line/cell/table where possible;
- explanation and proposed fix;
- explicit statement if no issue was found.
