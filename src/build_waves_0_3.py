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
from sklearn.model_selection import train_test_split

from .data_contract import contract_summary, load_raw_data, make_xy
from .evaluation import evaluate_candidates
from .models import make_candidate_models


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
    artifacts = root / "artifacts"
    tables = artifacts / "tables"
    models_dir = artifacts / "models"
    manifests = artifacts / "manifests"
    for path in (tables, models_dir, manifests):
        path.mkdir(parents=True, exist_ok=True)

    np.random.seed(RANDOM_STATE)
    frame = load_raw_data(raw_path)
    X, y = make_xy(frame)
    X_dev, X_test, y_dev, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        stratify=y,
        random_state=RANDOM_STATE,
    )

    models = make_candidate_models(random_state=RANDOM_STATE)
    cv_frame, test_frame, predictions, fitted_models, selection = evaluate_candidates(
        models, X_dev, y_dev, X_test, y_test, random_state=RANDOM_STATE
    )

    cv_frame.to_csv(tables / "wave-3-development-oof-metrics.csv", index=False)
    test_frame.to_csv(tables / "wave-3-frozen-test-metrics-at-0.5.csv", index=False)
    predictions.to_csv(tables / "wave-3-frozen-test-predictions.csv", index=False)
    for name, model in fitted_models.items():
        joblib.dump(model, models_dir / f"{name}.joblib")

    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Waves 0-3: data contract, preprocessing and candidate models",
        "raw_source": {
            "relative_path": "data/raw/SouthGermanCredit.asc",
            "sha256": sha256(raw_path),
            "bytes": raw_path.stat().st_size,
        },
        "random_state": RANDOM_STATE,
        "split": {
            "development_rows": int(len(X_dev)),
            "test_rows": int(len(X_test)),
            "development_positive_bad": int(y_dev.sum()),
            "test_positive_bad": int(y_test.sum()),
        },
        "contract": contract_summary(frame),
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
            "joblib": joblib.__version__,
        },
        "provisional_selection": {
            "criterion": "development out-of-fold average_precision, then roc_auc, then lower brier",
            "model": selection["model"],
            "average_precision": selection["average_precision"],
            "roc_auc": selection["roc_auc"],
            "threshold": 0.5,
            "status": "provisional; policy threshold is not selected until Wave 4",
        },
    }
    (manifests / "waves-0-3-run.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(json.dumps({
        "status": "complete",
        "development_rows": len(X_dev),
        "test_rows": len(X_test),
        "models": list(models),
        "provisional_selection": selection["model"],
        "artifacts": str(artifacts),
    }, indent=2))


if __name__ == "__main__":
    main()
