# Reviewer A - data and leakage

Verdict: PASS WITH FINDINGS

- Major: prediction moment and feature availability were not established by the historical source. Fix: add `reports/feature-availability-audit.md`, define application-submission timing, and block deployment until timestamps and outcome horizon are verified.
- Minor: no dedicated leakage-guard test existed. Fix: add `tests/test_leakage_guards.py`.
- Minor: categorical domains and numeric ranges were not fail-closed. Current data passed the observed codebook check; future domain validation remains a follow-up.

Verified clean: target mapping, target exclusion, no missing/duplicate rows, stratified seeded split, pipeline-local preprocessing, development OOF selection and frozen-test separation.
