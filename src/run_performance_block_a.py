from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.model_selection import RandomizedSearchCV, train_test_split

from .data_contract import load_raw_data, make_xy
from .models import make_candidate_models
from .performance_evaluation import capacity_f1_scorer, exact_wave3_oof, repeated_capacity_evaluation
from .performance_variants import make_performance_variants, make_preprocessor_variant
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


RANDOM_STATE = 77


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    raw_path = root / "data" / "raw" / "SouthGermanCredit.asc"
    tables = root / "artifacts" / "performance" / "tables"
    models_dir = root / "artifacts" / "performance" / "models"
    manifests = root / "artifacts" / "performance" / "manifests"
    for path in (tables, models_dir, manifests):
        path.mkdir(parents=True, exist_ok=True)

    frame = load_raw_data(raw_path)
    X, y = make_xy(frame)
    X_dev, X_test_unused, y_dev, y_test_unused = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=RANDOM_STATE
    )

    # P0: reproduce the exact Wave 3 OOF metric without touching the frozen test.
    baseline_model = make_candidate_models(random_state=RANDOM_STATE)["random_forest"]
    exact = exact_wave3_oof(baseline_model, X_dev, y_dev, random_state=RANDOM_STATE)
    previous = pd.read_csv(root / "artifacts" / "tables" / "wave-3-development-oof-metrics.csv")
    previous_rf = previous[previous["model"] == "random_forest"].iloc[0]
    reproduction = {
        metric: {"new": float(exact[metric]), "previous": float(previous_rf[metric]), "match": bool(np.isclose(exact[metric], previous_rf[metric], atol=1e-12))}
        for metric in ("average_precision", "roc_auc", "precision", "recall", "f1")
    }
    (manifests / "p0-baseline-reproduction.json").write_text(json.dumps(reproduction, indent=2), encoding="utf-8")

    # P1/P2: representation and class-weight ablations, repeated CV only on development data.
    variants = make_performance_variants(random_state=RANDOM_STATE)
    repeated = repeated_capacity_evaluation(variants, X_dev, y_dev, random_state=RANDOM_STATE)
    repeated.to_csv(tables / "p1-p2-repeated-capacity-results.csv", index=False)
    repeated_summary = repeated.groupby("model").agg(
        accuracy_mean=("accuracy_at_capacity", "mean"),
        accuracy_std=("accuracy_at_capacity", "std"),
        precision_mean=("precision_at_capacity", "mean"),
        precision_std=("precision_at_capacity", "std"),
        recall_mean=("recall_at_capacity", "mean"),
        recall_std=("recall_at_capacity", "std"),
        f1_mean=("f1_at_capacity", "mean"),
        f1_std=("f1_at_capacity", "std"),
        average_precision_mean=("average_precision", "mean"),
        average_precision_std=("average_precision", "std"),
        roc_auc_mean=("roc_auc", "mean"),
        roc_auc_std=("roc_auc", "std"),
    ).reset_index().sort_values(["f1_mean", "average_precision_mean"], ascending=False)
    repeated_summary.to_csv(tables / "p1-p2-repeated-capacity-summary.csv", index=False)

    # P3: compact development-only search with a capacity-aware F1 scorer.
    searches = {
        "logistic_search": (
            Pipeline([( "preprocess", make_preprocessor_variant("ordinal")), ("model", LogisticRegression(max_iter=3000, random_state=RANDOM_STATE))]),
            {
                "model__C": np.logspace(-2, 2, 9),
                "model__class_weight": [None, "balanced"],
                "model__solver": ["lbfgs", "liblinear"],
            },
        ),
        "random_forest_search": (
            Pipeline([( "preprocess", make_preprocessor_variant("ordinal")), ("model", RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=1))]),
            {
                "model__n_estimators": [200, 300, 500],
                "model__max_depth": [None, 4, 6, 10],
                "model__min_samples_leaf": [1, 3, 5, 10, 20],
                "model__max_features": ["sqrt", "log2", 0.5, 1.0],
                "model__class_weight": [None, "balanced"],
            },
        ),
        "hist_gradient_boosting_search": (
            Pipeline([( "preprocess", make_preprocessor_variant("ordinal")), ("model", HistGradientBoostingClassifier(random_state=RANDOM_STATE))]),
            {
                "model__learning_rate": [0.02, 0.05, 0.1],
                "model__max_iter": [100, 150, 250],
                "model__max_leaf_nodes": [7, 15, 31],
                "model__min_samples_leaf": [10, 20, 30],
                "model__l2_regularization": [0.0, 1.0, 5.0, 10.0],
            },
        ),
    }
    search_rows = []
    search_manifests = {}
    for name, (estimator, params) in searches.items():
        search = RandomizedSearchCV(
            estimator=estimator,
            param_distributions=params,
            n_iter=12,
            scoring=capacity_f1_scorer,
            cv=5,
            random_state=RANDOM_STATE,
            n_jobs=1,
            refit=True,
            return_train_score=False,
        )
        search.fit(X_dev, y_dev)
        joblib.dump(search.best_estimator_, models_dir / f"{name}.joblib")
        search_rows.append({"search": name, "best_capacity_f1_cv": float(search.best_score_), **search.best_params_})
        search_manifests[name] = {"best_score": float(search.best_score_), "best_params": search.best_params_}
    pd.DataFrame(search_rows).to_csv(tables / "p3-search-results.csv", index=False)

    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Performance improvement Block P-A: P0-P3",
        "test_used": False,
        "raw_source_sha256": sha256(raw_path),
        "development_rows": int(len(X_dev)),
        "environment": {"python": sys.version, "platform": platform.platform(), "numpy": np.__version__, "pandas": pd.__version__, "scikit_learn": sklearn.__version__, "joblib": joblib.__version__},
        "p0_reproduction": reproduction,
        "p1_p2": {"cv": "RepeatedStratifiedKFold 5x3", "capacity_fraction": 0.20, "summary": "p1-p2-repeated-capacity-summary.csv"},
        "p3": search_manifests,
        "status": "P-A complete; P4-P8 not executed",
    }
    (manifests / "performance-block-a.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"status": "complete", "p0_reproduction": reproduction, "top_repeated_models": repeated_summary.head(5).to_dict(orient="records"), "p3": search_manifests}, indent=2, default=str))


if __name__ == "__main__":
    main()
