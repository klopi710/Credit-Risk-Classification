from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import accuracy_score, average_precision_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import RepeatedStratifiedKFold, StratifiedKFold, cross_val_predict

from .evaluation import binary_metrics
from .threshold_policy import top_k_predictions as _top_k_predictions


CAPACITY_FRACTION = 0.20


def top_k_predictions(scores: np.ndarray, fraction: float = CAPACITY_FRACTION) -> np.ndarray:
    return _top_k_predictions(scores, fraction)


def capacity_metrics(y_true, scores, fraction: float = CAPACITY_FRACTION) -> dict[str, float]:
    y_true = np.asarray(y_true, dtype=int)
    scores = np.asarray(scores, dtype=float)
    pred = top_k_predictions(scores, fraction)
    return {
        "accuracy_at_capacity": float(accuracy_score(y_true, pred)),
        "precision_at_capacity": float(precision_score(y_true, pred, zero_division=0)),
        "recall_at_capacity": float(recall_score(y_true, pred, zero_division=0)),
        "f1_at_capacity": float(f1_score(y_true, pred, zero_division=0)),
        "average_precision": float(average_precision_score(y_true, scores)),
        "roc_auc": float(roc_auc_score(y_true, scores)),
        "selected_count": int(pred.sum()),
    }


def capacity_f1_scorer(estimator, X, y) -> float:
    scores = estimator.predict_proba(X)[:, 1]
    return capacity_metrics(y, scores)["f1_at_capacity"]


def repeated_capacity_evaluation(models: dict, X, y, random_state: int = 77) -> pd.DataFrame:
    splitter = RepeatedStratifiedKFold(n_splits=5, n_repeats=3, random_state=random_state)
    rows = []
    for name, model in models.items():
        fold = 0
        for train_idx, valid_idx in splitter.split(X, y):
            fitted = clone(model).fit(X.iloc[train_idx], y.iloc[train_idx])
            scores = fitted.predict_proba(X.iloc[valid_idx])[:, 1]
            rows.append({"model": name, "fold": fold, **capacity_metrics(y.iloc[valid_idx], scores)})
            fold += 1
    return pd.DataFrame(rows)


def exact_wave3_oof(model, X, y, random_state: int = 77) -> dict[str, float]:
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)
    scores = cross_val_predict(model, X, y, cv=cv, method="predict_proba", n_jobs=1)[:, 1]
    return binary_metrics(y, scores, threshold=0.5) | capacity_metrics(y, scores, fraction=0.20) | {"oof_scores": scores}
