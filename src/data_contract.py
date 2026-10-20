from __future__ import annotations

from pathlib import Path

import pandas as pd


EXPECTED_COLUMNS = [
    "laufkont",
    "laufzeit",
    "moral",
    "verw",
    "hoehe",
    "sparkont",
    "beszeit",
    "rate",
    "famges",
    "buerge",
    "wohnzeit",
    "verm",
    "alter",
    "weitkred",
    "wohn",
    "bishkred",
    "beruf",
    "pers",
    "telef",
    "gastarb",
    "kredit",
]

TARGET_COLUMN = "kredit"
NUMERIC_COLUMNS = ["laufzeit", "hoehe", "alter"]
CATEGORICAL_COLUMNS = [c for c in EXPECTED_COLUMNS if c not in NUMERIC_COLUMNS + [TARGET_COLUMN]]


def load_raw_data(path: str | Path) -> pd.DataFrame:
    """Load the immutable UCI whitespace-delimited source file."""
    frame = pd.read_csv(path, sep=r"\s+", engine="python")
    validate_schema(frame)
    return frame


def validate_schema(frame: pd.DataFrame) -> None:
    """Fail closed if the source contract changes."""
    if list(frame.columns) != EXPECTED_COLUMNS:
        raise ValueError(
            f"Unexpected columns. Expected {EXPECTED_COLUMNS}; got {list(frame.columns)}"
        )
    if frame.empty:
        raise ValueError("The source dataset is empty")
    if frame.isna().any().any():
        missing = frame.isna().sum()
        raise ValueError(f"Missing values found: {missing[missing > 0].to_dict()}")
    if frame.duplicated().any():
        raise ValueError("Duplicate rows found in the source dataset")
    values = set(frame[TARGET_COLUMN].unique())
    if not values.issubset({0, 1}):
        raise ValueError(f"Unexpected target values: {sorted(values)}")
    if not set(NUMERIC_COLUMNS).issubset(frame.columns):
        raise ValueError("Numeric column contract is incomplete")


def make_xy(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Return X and a clearly named positive target: 1 means bad/default-risk."""
    X = frame.drop(columns=[TARGET_COLUMN]).copy()
    y = (frame[TARGET_COLUMN] == 0).astype("int8")
    y.name = "bad_default_risk"
    return X, y


def contract_summary(frame: pd.DataFrame) -> dict:
    return {
        "rows": int(len(frame)),
        "columns": int(frame.shape[1]),
        "predictor_columns": int(frame.shape[1] - 1),
        "missing_values": int(frame.isna().sum().sum()),
        "duplicate_rows": int(frame.duplicated().sum()),
        "raw_target_counts": {str(k): int(v) for k, v in frame[TARGET_COLUMN].value_counts().sort_index().items()},
        "positive_target_counts": {str(k): int(v) for k, v in make_xy(frame)[1].value_counts().sort_index().items()},
        "numeric_columns": NUMERIC_COLUMNS,
        "categorical_columns": CATEGORICAL_COLUMNS,
    }
