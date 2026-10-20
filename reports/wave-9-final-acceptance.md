# Wave 9 - final acceptance

Date: 2026-10-05
Status: ACCEPTED

## Frozen result

The final model is Logistic Regression. It was selected using development out-of-fold net screening value at exact 20% ranked capacity; the frozen test was not used for selection.

- Development: accuracy 0.753, precision 0.631, recall 0.421, F1 0.505; 160/800 selected.
- Frozen test: TN 125, FP 15, FN 35, TP 25; accuracy 0.750, precision 0.625, recall 0.417, F1 0.500; 40/200 selected.
- Base conditional economics: development EUR 2,635,600 net screening value; frozen-test EUR 2,608,000.

The persisted threshold is only a sample reference boundary. The operating policy is exact deterministic top-k ranking, so capacity is hard-bounded.

## Verification completed

- 11/11 unit tests pass.
- Notebook JSON validates, all ten cells have IDs, and the notebook executes in memory from both the project root and the `notebooks` working directory without overwriting its source.
- `jupyterlab 4.6.4` is available and declared in `requirements.txt`.
- Wave 4 and Wave 5 artifacts regenerate successfully.
- Wave 9 governance audit regenerates successfully and records raw-source, model, Wave 4 manifest and runner hashes, plus seed 42 and stratified split metadata.
- Five initial zero-context reviews completed; repaired major findings received independent re-review; final independent acceptance review returned PASS with no remaining findings.

## Governance boundary

This is a historical credit-risk proxy and a human-review prioritization demonstration. There is no external pilot or automatic approval/rejection authorization. Feature availability timestamps, outcome horizon, sensitive/proxy-feature governance, time-valid data and prospective monitoring must be resolved before any real-world pilot.

## Rollback

The final selection is recorded in `artifacts/manifests/wave-4-policy.json`, with supporting tables and models retained. Revert operational use by selecting the previous frozen manifest/model artifact; no raw data deletion is required.

## Remaining separate work

Performance P4-P8 (calibration, resampling, final improvement selection and independent performance review) remains pending and is not started by this acceptance.
