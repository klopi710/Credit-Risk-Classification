# Wave 9 independent re-check - reproducibility and governance

Verdict before the final documentation patch: PASS WITH FINDINGS.

The independent re-check confirmed 11/11 tests, valid notebook JSON, clean in-memory notebook execution, six subgroup rows and matching headline metrics. Findings were repaired: `jupyterlab` was added to requirements, governance provenance now records raw/model/Wave 4/runner hashes plus split seed, the deck now states no external pilot until feature and governance gates pass, the Wave 4 model-selection wording was corrected, and all notebook cells now have IDs.
