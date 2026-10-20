from __future__ import annotations

from typing import Iterable

import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score


BUSINESS_ASSUMPTIONS = {
    "monthly_applications": 8000,
    "max_monthly_reviews": 1600,
    "review_cost": 35.0,
    "lgd": 6000.0,
    "review_effectiveness": 0.45,
    "performing_contribution": 1200.0,
    "abandonment_rate": 0.05,
}


def top_k_predictions(scores: Iterable[float], fraction: float) -> np.ndarray:
    """Select exactly the highest-scoring k cases, with deterministic tie handling."""
    scores = np.asarray(list(scores), dtype=float)
    if not 0 < fraction <= 1:
        raise ValueError("fraction must be greater than 0 and at most 1")
    k = min(len(scores), max(1, int(np.ceil(len(scores) * fraction))))
    selected = np.zeros(len(scores), dtype=int)
    order = np.argsort(scores, kind="stable")
    selected[order[-k:]] = 1
    return selected


def _metrics_from_predictions(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    threshold: float,
    assumptions: dict,
    selection_rule: str = "threshold",
) -> dict[str, float]:
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    n = len(y_true)
    scale = assumptions["monthly_applications"] / n
    reviews = (fp + tp) * scale
    defaults_prevented = tp * scale * assumptions["review_effectiveness"]
    gross_loss_avoided = defaults_prevented * assumptions["lgd"]
    review_cost = reviews * assumptions["review_cost"]
    lost_contribution = (
        fp
        * scale
        * assumptions["abandonment_rate"]
        * assumptions["performing_contribution"]
    )
    net_value = gross_loss_avoided - review_cost - lost_contribution
    missed_avoidable_loss = fn * scale * assumptions["review_effectiveness"] * assumptions["lgd"]
    return {
        "threshold": float(threshold),
        "selection_rule": selection_rule,
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "review_rate": float(y_pred.mean()),
        "monthly_reviews": float(reviews),
        "capacity_utilization": float(reviews / assumptions["max_monthly_reviews"]),
        "expected_defaults_prevented": float(defaults_prevented),
        "gross_loss_avoided": float(gross_loss_avoided),
        "monthly_review_cost": float(review_cost),
        "lost_contribution_from_friction": float(lost_contribution),
        "net_screening_value": float(net_value),
        "cost_per_expected_default_prevented": float(
            review_cost / defaults_prevented if defaults_prevented else np.inf
        ),
        "missed_avoidable_loss": float(missed_avoidable_loss),
        "selected_count": int(y_pred.sum()),
    }


def metrics_at_threshold(
    y_true: Iterable[int],
    y_score: Iterable[float],
    threshold: float,
    assumptions: dict | None = None,
) -> dict[str, float]:
    """Calculate classification and business metrics for one operating point."""
    assumptions = assumptions or BUSINESS_ASSUMPTIONS
    y_true = np.asarray(list(y_true), dtype=int)
    y_score = np.asarray(list(y_score), dtype=float)
    y_pred = (y_score >= threshold).astype(int)
    return _metrics_from_predictions(y_true, y_pred, threshold, assumptions)


def metrics_at_capacity(
    y_true: Iterable[int],
    y_score: Iterable[float],
    fraction: float,
    assumptions: dict | None = None,
) -> dict[str, float]:
    """Evaluate one exact ranked-queue capacity, independent of score ties."""
    assumptions = assumptions or BUSINESS_ASSUMPTIONS
    y_true = np.asarray(list(y_true), dtype=int)
    y_score = np.asarray(list(y_score), dtype=float)
    y_pred = top_k_predictions(y_score, fraction)
    selected_scores = y_score[y_pred == 1]
    effective_threshold = float(selected_scores.min()) if len(selected_scores) else float("inf")
    return _metrics_from_predictions(
        y_true,
        y_pred,
        effective_threshold,
        assumptions,
        selection_rule="top_k",
    )


def threshold_grid(y_score: Iterable[float]) -> list[float]:
    scores = np.asarray(list(y_score), dtype=float)
    values = list(np.round(np.linspace(0.01, 0.99, 99), 6))
    values.extend([0.5, float(np.quantile(scores, 0.8))])
    return sorted(set(values))


def operating_points(y_true: Iterable[int], y_score: Iterable[float]) -> dict[str, dict]:
    y_true = np.asarray(list(y_true), dtype=int)
    y_score = np.asarray(list(y_score), dtype=float)
    rows = [metrics_at_threshold(y_true, y_score, t) for t in threshold_grid(y_score)]
    base_rate = float(y_true.mean())
    cap = BUSINESS_ASSUMPTIONS["max_monthly_reviews"] / BUSINESS_ASSUMPTIONS["monthly_applications"]

    at_half = min(rows, key=lambda row: abs(row["threshold"] - 0.5))
    capacity = metrics_at_capacity(y_true, y_score, cap)

    recall_candidates = [row for row in rows if row["review_rate"] <= 0.50 and row["precision"] >= base_rate]
    high_recall = max(recall_candidates or rows, key=lambda row: (row["recall"], -row["threshold"]))

    precision_candidates = [row for row in rows if row["review_rate"] >= 0.05]
    high_precision = max(precision_candidates or rows, key=lambda row: (row["precision"], row["recall"]))

    max_value = max(rows, key=lambda row: (row["net_screening_value"], row["recall"]))
    recommended = capacity

    return {
        "threshold_0_50": at_half,
        "high_recall": high_recall,
        "high_precision": high_precision,
        "capacity_top_20_percent": capacity,
        "max_development_net_value": max_value,
        "recommended_capacity_constrained": recommended,
    }
