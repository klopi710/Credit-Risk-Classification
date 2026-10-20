# Reviewer B - metrics and threshold

Verdict: PASS WITH FINDINGS

- Major: the previous Wave 4 report swapped high-precision accuracy and precision; the report was regenerated from the authoritative CSV.
- Major: previous deliverables contained a stale frozen-test F1; the final Logistic Regression policy now reports the authoritative test confusion matrix TN=125, FP=15, FN=35, TP=25 and F1=0.500.
- Minor: historical manifest status text was stale; final artifacts now state the Wave 9 repair status.

Verified: development OOF calculations, capacity economics, and test-set non-use for tuning. Wave 9 uses exact top-k capacity throughout.
