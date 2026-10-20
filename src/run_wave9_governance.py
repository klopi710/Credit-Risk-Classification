from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from scipy.stats import beta
from sklearn.model_selection import train_test_split

from .data_contract import load_raw_data, make_xy
from .threshold_policy import BUSINESS_ASSUMPTIONS, top_k_predictions


RANDOM_STATE = 77


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def beta_interval(successes: int, trials: int, alpha: float = 0.05) -> tuple[float, float]:
    if successes == 0:
        return 0.0, float(beta.ppf(1 - alpha / 2, 1, trials + 1))
    if successes == trials:
        return float(beta.ppf(alpha / 2, trials + 1, 1)), 1.0
    return (
        float(beta.ppf(alpha / 2, successes, trials - successes + 1)),
        float(beta.ppf(1 - alpha / 2, successes + 1, trials - successes)),
    )


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    raw_path = root / "data" / "raw" / "SouthGermanCredit.asc"
    wave4_manifest_path = root / "artifacts" / "manifests" / "wave-4-policy.json"
    model_name = json.loads(wave4_manifest_path.read_text(encoding="utf-8"))["selected_model"]
    model_path = root / "artifacts" / "models" / f"{model_name}.joblib"
    frame = load_raw_data(raw_path)
    X, y = make_xy(frame)
    _X_dev, X_test, _y_dev, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=RANDOM_STATE
    )
    model = joblib.load(model_path)
    scores = model.predict_proba(X_test)[:, 1]
    fraction = BUSINESS_ASSUMPTIONS["max_monthly_reviews"] / BUSINESS_ASSUMPTIONS["monthly_applications"]
    reviewed = top_k_predictions(scores, fraction)
    rows: list[dict] = []
    for feature in ("famges", "gastarb"):
        for value, group in X_test[feature].sort_values().groupby(X_test[feature].sort_values()):
            idx = group.index
            group_reviewed = reviewed[X_test.index.get_indexer(idx)]
            group_y = y_test.loc[idx].to_numpy()
            tp = int(((group_reviewed == 1) & (group_y == 1)).sum())
            fp = int(((group_reviewed == 1) & (group_y == 0)).sum())
            positives = int((group_y == 1).sum())
            negatives = int((group_y == 0).sum())
            selected = int(group_reviewed.sum())
            selection_low, selection_high = beta_interval(selected, len(group_y))
            rows.append(
                {
                    "feature": feature,
                    "group": str(value),
                    "n": len(group_y),
                    "positive_bad_risk": positives,
                    "selected_for_review": selected,
                    "selection_rate": selected / len(group_y),
                    "selection_rate_ci_low": selection_low,
                    "selection_rate_ci_high": selection_high,
                    "precision": tp / selected if selected else 0.0,
                    "recall_tpr": tp / positives if positives else 0.0,
                    "fpr": fp / negatives if negatives else 0.0,
                }
            )
    out = root / "artifacts" / "tables" / "wave-9-subgroup-audit.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    audit_manifest = {
        "status": "audit-only; not used for model or threshold selection",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "selected_model": model_name,
        "selection_rule": "exact top-k ranked queue",
        "test_rows": int(len(X_test)),
        "monthly_review_fraction": fraction,
        "split": {
            "test_size": 0.20,
            "stratified": True,
            "random_state": RANDOM_STATE,
        },
        "features": ["famges", "gastarb"],
        "artifact": "artifacts/tables/wave-9-subgroup-audit.csv",
        "provenance": {
            "raw_source_sha256": sha256(raw_path),
            "model_artifact_sha256": sha256(model_path),
            "wave4_policy_manifest_sha256": sha256(wave4_manifest_path),
            "governance_runner_sha256": sha256(Path(__file__).resolve()),
        },
    }
    (root / "artifacts" / "manifests" / "wave-9-governance.json").write_text(
        json.dumps(audit_manifest, indent=2), encoding="utf-8"
    )
    print(json.dumps(audit_manifest, indent=2))


if __name__ == "__main__":
    main()
