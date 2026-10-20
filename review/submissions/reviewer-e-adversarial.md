# Reviewer E - adversarial red-team

Verdict: FAIL before repair

- Major: Random Forest was not strongest at the capacity-constrained business objective. Wave 9 reselected Logistic Regression using development OOF net value at exact 20% capacity.
- Major: threshold selection did not enforce exact top-k capacity. Wave 9 added shared deterministic top-k selection and regenerated all policy artifacts.
- Major: sensitive/proxy fields lacked subgroup diagnostics. Wave 9 added an audit for `famges` and `gastarb` with beta intervals, selection rate, precision, TPR and FPR; it is a deployment gate, not a tuning input.
- Major: economics were conditional scenario arithmetic, not causal evidence. Final reports explicitly state this.
- Minor: stale metrics were regenerated.
- Major: notebook was an artifact viewer. It now contains a clean regeneration cell and robust project-root discovery.
