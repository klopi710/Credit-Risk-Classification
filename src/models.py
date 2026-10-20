from __future__ import annotations

from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier

from .preprocessing import make_preprocessor


def make_candidate_models(random_state: int = 77) -> dict[str, Pipeline]:
    """Return the Wave 3 candidate set with preprocessing inside each pipeline."""
    return {
        "majority_baseline": Pipeline(
            [("preprocess", make_preprocessor()), ("model", DummyClassifier(strategy="prior"))]
        ),
        "logistic_regression": Pipeline(
            [
                ("preprocess", make_preprocessor()),
                (
                    "model",
                    LogisticRegression(max_iter=2000, solver="lbfgs", random_state=random_state),
                ),
            ]
        ),
        "decision_tree": Pipeline(
            [
                ("preprocess", make_preprocessor()),
                (
                    "model",
                    DecisionTreeClassifier(max_depth=4, min_samples_leaf=10, random_state=random_state),
                ),
            ]
        ),
        "random_forest": Pipeline(
            [
                ("preprocess", make_preprocessor()),
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=300,
                        min_samples_leaf=3,
                        random_state=random_state,
                        n_jobs=1,
                    ),
                ),
            ]
        ),
    }
