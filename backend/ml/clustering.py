"""DBSCAN clustering over wallet behavioral features."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline


def cluster_wallets(feature_frame: pd.DataFrame, eps: float = 1.0, min_samples: int = 5) -> tuple[Pipeline, pd.DataFrame]:
    """Cluster wallets using behavioral features while excluding the wallet_id column."""
    numeric_frame = feature_frame.copy()
    wallet_ids = numeric_frame["wallet_id"].copy() if "wallet_id" in numeric_frame.columns else pd.Series([f"wallet_{idx}" for idx in range(len(numeric_frame))], index=numeric_frame.index)
    feature_columns = [col for col in numeric_frame.columns if col != "wallet_id"]
    data = numeric_frame[feature_columns].fillna(0.0)

    pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", DBSCAN(eps=eps, min_samples=min_samples)),
    ])
    labels = pipeline.fit_predict(data)

    result = pd.DataFrame({
        "wallet_id": wallet_ids.values,
        "cluster_id": labels,
    })
    return pipeline, result


__all__ = ["cluster_wallets"]
