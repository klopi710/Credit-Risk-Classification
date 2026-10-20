from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split

from .data_contract import load_raw_data, make_xy
from .models import make_candidate_models
from .threshold_policy import (
    BUSINESS_ASSUMPTIONS,
    metrics_at_capacity,
    metrics_at_threshold,
    operating_points,
)


RANDOM_STATE = 77


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    raw_path = root / "data" / "raw" / "SouthGermanCredit.asc"
    artifacts = root / "artifacts"
    tables = artifacts / "tables"
    models_dir = artifacts / "models"
    manifests = artifacts / "manifests"

    frame = load_raw_data(raw_path)
    X, y = make_xy(frame)
    X_dev, X_test, y_dev, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=RANDOM_STATE
    )
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    models = make_candidate_models(random_state=RANDOM_STATE)

    all_oof_rows = []
    all_test_rows = []
    points_by_model = {}

    for name, fresh_model in models.items():
        oof_score = cross_val_predict(fresh_model, X_dev, y_dev, cv=cv, method="predict_proba", n_jobs=1)[:, 1]
        points = operating_points(y_dev, oof_score)
        points_by_model[name] = points
        for policy_name, row in points.items():
            all_oof_rows.append({"model": name, "policy": policy_name, **row})

    selected_model = max(
        points_by_model,
        key=lambda name: (
            points_by_model[name]["recommended_capacity_constrained"]["net_screening_value"],
            points_by_model[name]["recommended_capacity_constrained"]["f1"],
            points_by_model[name]["recommended_capacity_constrained"]["precision"],
            name,
        ),
    )
    selected_points = points_by_model[selected_model]

    for name in models:
        fitted = joblib.load(models_dir / f"{name}.joblib")
        test_score = fitted.predict_proba(X_test)[:, 1]
        if name == selected_model:
            for policy_name, row in selected_points.items():
                if row.get("selection_rule") == "top_k":
                    test_row = metrics_at_capacity(
                        y_test,
                        test_score,
                        BUSINESS_ASSUMPTIONS["max_monthly_reviews"]
                        / BUSINESS_ASSUMPTIONS["monthly_applications"],
                    )
                else:
                    test_row = metrics_at_threshold(y_test, test_score, row["threshold"])
                all_test_rows.append({"model": name, "policy": policy_name, **test_row})

    oof_frame = pd.DataFrame(all_oof_rows)
    test_frame = pd.DataFrame(all_test_rows)
    oof_frame.to_csv(tables / "wave-4-oof-threshold-table-all-models.csv", index=False)
    test_frame.to_csv(tables / "wave-4-selected-model-frozen-test-thresholds.csv", index=False)

    recommendation = selected_points["recommended_capacity_constrained"]
    policy_manifest = {
        "selected_model": selected_model,
        "selection_basis": "development OOF net screening value at the exact 20% ranked review capacity; ties resolved by F1, precision, then model name",
        "business_assumptions": BUSINESS_ASSUMPTIONS,
        "operating_points": selected_points,
        "recommended_policy": recommendation,
        "test_evaluation": test_frame.to_dict(orient="records"),
        "test_was_used_for_threshold_selection": False,
        "status": "Wave 4 recalculated in Wave 9; exact top-k policy and business-objective model selection are frozen before test confirmation",
    }
    (manifests / "wave-4-policy.json").write_text(json.dumps(policy_manifest, indent=2), encoding="utf-8")

    print(json.dumps({
        "status": "complete",
        "selected_model": selected_model,
        "recommended_threshold": recommendation["threshold"],
        "recommended_precision_oof": recommendation["precision"],
        "recommended_recall_oof": recommendation["recall"],
        "recommended_f1_oof": recommendation["f1"],
        "recommended_accuracy_oof": recommendation["accuracy"],
        "recommended_monthly_reviews_oof": recommendation["monthly_reviews"],
        "recommended_net_value_oof": recommendation["net_screening_value"],
    }, indent=2))


if __name__ == "__main__":
    main()
