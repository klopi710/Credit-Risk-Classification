from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, OrdinalEncoder, StandardScaler

from .data_contract import CATEGORICAL_COLUMNS, NUMERIC_COLUMNS


ORDINAL_COLUMNS = ["beszeit", "rate", "wohnzeit", "bishkred", "beruf"]
NOMINAL_COLUMNS = [c for c in CATEGORICAL_COLUMNS if c not in ORDINAL_COLUMNS]
DOMAIN_NUMERIC_COLUMNS = NUMERIC_COLUMNS + ["amount_per_month", "log_amount"]
DOMAIN_CATEGORICAL_COLUMNS = CATEGORICAL_COLUMNS + ["duration_band"]


def add_domain_features(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    duration = out["laufzeit"].replace(0, np.nan)
    out["amount_per_month"] = out["hoehe"] / duration
    out["log_amount"] = np.log1p(out["hoehe"])
    out["duration_band"] = pd.cut(
        out["laufzeit"],
        bins=[0, 12, 24, 48, np.inf],
        labels=["short", "medium", "long", "very_long"],
        include_lowest=True,
    ).astype("object")
    return out


def _numeric_pipeline(scale: bool = True) -> Pipeline:
    steps = [("impute", SimpleImputer(strategy="median"))]
    if scale:
        steps.append(("scale", StandardScaler()))
    return Pipeline(steps)


def make_preprocessor_variant(variant: str) -> Pipeline | ColumnTransformer:
    if variant == "current":
        return ColumnTransformer(
            [
                ("numeric", _numeric_pipeline(True), NUMERIC_COLUMNS),
                (
                    "categorical",
                    Pipeline(
                        [
                            ("impute", SimpleImputer(strategy="most_frequent")),
                            ("onehot", OneHotEncoder(handle_unknown="ignore")),
                        ]
                    ),
                    CATEGORICAL_COLUMNS,
                ),
            ]
        )
    if variant == "ordinal":
        return ColumnTransformer(
            [
                ("numeric", _numeric_pipeline(True), NUMERIC_COLUMNS),
                (
                    "ordinal",
                    Pipeline(
                        [
                            ("impute", SimpleImputer(strategy="most_frequent")),
                            ("encode", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)),
                        ]
                    ),
                    ORDINAL_COLUMNS,
                ),
                (
                    "nominal",
                    Pipeline(
                        [
                            ("impute", SimpleImputer(strategy="most_frequent")),
                            ("onehot", OneHotEncoder(handle_unknown="ignore")),
                        ]
                    ),
                    NOMINAL_COLUMNS,
                ),
            ]
        )
    if variant == "domain":
        return Pipeline(
            [
                ("features", FunctionTransformer(add_domain_features)),
                (
                    "columns",
                    ColumnTransformer(
                        [
                            ("numeric", _numeric_pipeline(True), DOMAIN_NUMERIC_COLUMNS),
                            (
                                "categorical",
                                Pipeline(
                                    [
                                        ("impute", SimpleImputer(strategy="most_frequent")),
                                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                                    ]
                                ),
                                DOMAIN_CATEGORICAL_COLUMNS,
                            ),
                        ]
                    ),
                ),
            ]
        )
    raise ValueError(f"Unknown preprocessing variant: {variant}")


def make_performance_variants(random_state: int = 77) -> dict[str, Pipeline]:
    def pipe(preprocessor, model):
        return Pipeline([("preprocess", preprocessor), ("model", model)])

    return {
        "logistic_current": pipe(make_preprocessor_variant("current"), LogisticRegression(max_iter=3000, random_state=random_state)),
        "logistic_balanced": pipe(make_preprocessor_variant("current"), LogisticRegression(max_iter=3000, class_weight="balanced", random_state=random_state)),
        "logistic_ordinal": pipe(make_preprocessor_variant("ordinal"), LogisticRegression(max_iter=3000, random_state=random_state)),
        "logistic_domain": pipe(make_preprocessor_variant("domain"), LogisticRegression(max_iter=3000, random_state=random_state)),
        "random_forest_current": pipe(make_preprocessor_variant("current"), RandomForestClassifier(n_estimators=300, min_samples_leaf=3, random_state=random_state, n_jobs=1)),
        "random_forest_balanced": pipe(make_preprocessor_variant("current"), RandomForestClassifier(n_estimators=300, min_samples_leaf=3, class_weight="balanced", random_state=random_state, n_jobs=1)),
        "random_forest_ordinal": pipe(make_preprocessor_variant("ordinal"), RandomForestClassifier(n_estimators=300, min_samples_leaf=3, random_state=random_state, n_jobs=1)),
        "random_forest_domain": pipe(make_preprocessor_variant("domain"), RandomForestClassifier(n_estimators=300, min_samples_leaf=3, random_state=random_state, n_jobs=1)),
        "extra_trees_ordinal": pipe(make_preprocessor_variant("ordinal"), ExtraTreesClassifier(n_estimators=300, min_samples_leaf=3, random_state=random_state, n_jobs=1)),
        "hist_gradient_boosting_ordinal": pipe(make_preprocessor_variant("ordinal"), HistGradientBoostingClassifier(max_iter=150, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=15, l2_regularization=1.0, random_state=random_state)),
    }
