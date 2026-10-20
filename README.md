# Marc Torrens Assignment

The project is being built in bounded waves. Waves 0–3 establish provenance, the data contract, the leakage-safe preprocessing pipeline and candidate classification models.

The positive class is `bad/default-risk`, mapped from the source value `kredit == 0`. The 20% test split is frozen before model comparison. Threshold policy selection is intentionally deferred to Wave 4.

Run from this folder, in this order:

```powershell
py -m unittest discover -s tests -p "test_*.py"
py -m src.build_waves_0_3
py -m src.run_wave4
py -m src.run_wave5
py -m src.run_wave9_governance
```

The Wave 3 threshold-0.50 test metrics are provisional diagnostics, not the final operating policy. Wave 4 selects the model and exact ranked top-k policy from development out-of-fold predictions; the frozen test is evaluated once for confirmation. Wave 9 governance metrics are audit-only and never tune the model.

The notebook is an end-to-end presentation and results check. With the notebook dependencies installed, launch it from this folder so its cells can regenerate Waves 0-5:

```powershell
py -m jupyter lab notebooks\credit_risk_assignment.ipynb
```

The editable deck source is `slides/credit-risk-business-deck.md`. No automatic lending decision or external deployment is in scope.
