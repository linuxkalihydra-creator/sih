"""High-level explainability service for synthetic investigative analysis."""

from __future__ import annotations

from typing import Any

import pandas as pd

from backend.explainability.evidence import summarize_evidence
from backend.explainability.reason_generator import generate_explanations


def build_explanations(wallet_features: pd.DataFrame, risk_df: pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame of wallet explanations and evidence."""
    explanations = generate_explanations(wallet_features, risk_df)
    if explanations.empty:
        return explanations
    explanations["evidence"] = explanations["wallet_id"].apply(
        lambda wallet_id: summarize_evidence(wallet_features[wallet_features["wallet_id"] == wallet_id].iloc[0].to_dict())
    )
    return explanations


__all__ = ["build_explanations"]
