# Wave 9 independent re-check - policy and metrics

Verdict before the final documentation patch: PASS WITH FINDINGS.

The independent recomputation confirmed Logistic Regression as the exact-top-k development winner (EUR 2,635,600 versus Random Forest EUR 2,525,200), exact 160/800 development selection, exact 40/200 frozen-test selection, and frozen-test TN=125, FP=15, FN=35, TP=25. All Wave 5 economics recomputed exactly. The only finding was the stale Random Forest sentence in `reports/waves-5-7-handoff.md`; it was corrected in the final documentation patch.
