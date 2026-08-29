"""Isolation Forest-based anomaly detection for wallet behavior features."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline


def train_isolation_forest(feature_frame: pd.DataFrame, contamination: float = 0.05, n_estimators: int = 200, random_state: int = 42) -> tuple[Pipeline, pd.DataFrame]:
    """Train an Isolation Forest on wallet-level features and return the model plus scored output."""
    numeric_frame = feature_frame.copy()
    if "wallet_id" in numeric_frame.columns:
        wallet_ids = numeric_frame["wallet_id"].copy()
    else:
        wallet_ids = pd.Series([f"wallet_{idx}" for idx in range(len(numeric_frame))], index=numeric_frame.index)

    feature_columns = [col for col in numeric_frame.columns if col != "wallet_id"]
    numeric_frame = numeric_frame[feature_columns].fillna(0.0)

    pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", IsolationForest(contamination=contamination, n_estimators=n_estimators, random_state=random_state)),
    ])

    pipeline.fit(numeric_frame)
    scores = pipeline.decision_function(numeric_frame)
    labels = pipeline.predict(numeric_frame)

    result = pd.DataFrame({
        "wallet_id": wallet_ids.values,
        "anomaly_score": scores,
        "anomaly_label": labels,
    })
    result["anomaly_score_norm"] = ((1 - (scores + 1) / 2) * 100).clip(0, 100)
    return pipeline, result


def save_model(model: Any, path: str | Path) -> Path:
    """Persist a trained model to a local file using joblib."""
    import joblib

    model_path = Path(path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    return model_path


def load_model(path: str | Path) -> Any:
    """Load a saved scikit-learn model from disk."""
    import joblib

    return joblib.load(path)


__all__ = ["train_isolation_forest", "save_model", "load_model"]
