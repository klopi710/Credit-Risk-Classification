from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict


def binary_metrics(y_true: Iterable[int], y_score: Iterable[float], threshold: float = 0.5) -> dict[str, float]:
    y_true = np.asarray(list(y_true), dtype=int)
    y_score = np.asarray(list(y_score), dtype=float)
    y_pred = (y_score >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return {
        "threshold": float(threshold),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "specificity": float(tn / (tn + fp)) if (tn + fp) else 0.0,
        "roc_auc": float(roc_auc_score(y_true, y_score)),
        "average_precision": float(average_precision_score(y_true, y_score)),
        "log_loss": float(log_loss(y_true, np.column_stack([1 - y_score, y_score]), labels=[0, 1])),
        "brier": float(brier_score_loss(y_true, y_score)),
        "review_rate": float(y_pred.mean()),
    }


def oof_predictions(model, X, y, cv: StratifiedKFold) -> np.ndarray:
    return cross_val_predict(model, X, y, cv=cv, method="predict_proba", n_jobs=1)[:, 1]


def evaluate_candidates(models: dict, X_dev, y_dev, X_test, y_test, random_state: int = 77):
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)
    summary_rows = []
    test_rows = []
    prediction_frames = []
    fitted_models = {}

    for name, model in models.items():
        oof_score = oof_predictions(model, X_dev, y_dev, cv)
        oof = binary_metrics(y_dev, oof_score, threshold=0.5)
        fitted = model.fit(X_dev, y_dev)
        test_score = fitted.predict_proba(X_test)[:, 1]
        test = binary_metrics(y_test, test_score, threshold=0.5)
        fitted_models[name] = fitted

        summary_rows.append({
            "model": name,
            "evaluation": "development_oof",
            **oof,
        })
        test_rows.append({
            "model": name,
            "evaluation": "frozen_test_at_0.5",
            **test,
        })
        prediction_frames.append(
            pd.DataFrame(
                {
                    "model": name,
                    "split": "frozen_test",
                    "y_true": np.asarray(y_test, dtype=int),
                    "y_score_positive_bad": test_score,
                }
            )
        )

    cv_frame = pd.DataFrame(summary_rows)
    test_frame = pd.DataFrame(test_rows)
    selection = (
        cv_frame.sort_values(["average_precision", "roc_auc", "brier"], ascending=[False, False, True])
        .iloc[0]
        .to_dict()
    )
    return cv_frame, test_frame, pd.concat(prediction_frames, ignore_index=True), fitted_models, selection
