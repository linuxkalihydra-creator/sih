"""Reason generation based on actual wallet feature values and model output."""

from __future__ import annotations

from typing import Any

import pandas as pd


def generate_reason_rows(wallet_record: dict[str, Any]) -> list[dict[str, Any]]:
    """Create human-readable reasons from behavior features and risk score components."""
    reasons: list[dict[str, Any]] = []
    if wallet_record.get("transaction_count", 0) > 20:
        reasons.append({
            "category": "transaction_frequency",
            "label": "Transaction frequency is above the synthetic baseline",
            "evidence": f"Observed {wallet_record.get('transaction_count')} transactions",
            "inference": "High transaction velocity may indicate unusual wallet activity in the synthetic dataset",
            "investigative_lead": "Review surrounding wallet flows for bursty activity",
            "confidence": 0.8,
        })
    if wallet_record.get("unique_ips", 0) > 8:
        reasons.append({
            "category": "network_diversity",
            "label": "Unusually high IP diversity",
            "evidence": f"Observed {wallet_record.get('unique_ips')} unique IPs",
            "inference": "The wallet appears across a broad set of synthetic network observations",
            "investigative_lead": "Compare associated IPs against the wallet's transaction timeline",
            "confidence": 0.75,
        })
    if wallet_record.get("unique_counterparties", 0) > 12:
        reasons.append({
            "category": "counterparty_diversity",
            "label": "Unusually high counterparty diversity",
            "evidence": f"Observed {wallet_record.get('unique_counterparties')} unique counterparties",
            "inference": "Activity spans a broad network of synthetic wallet relationships",
            "investigative_lead": "Inspect the wallet's nearest-neighbor graph for repeated pathways",
            "confidence": 0.7,
        })
    if wallet_record.get("average_time_between_transactions", 0) < 60:
        reasons.append({
            "category": "time_velocity",
            "label": "Rapid transaction movement",
            "evidence": f"Observed average interval of {wallet_record.get('average_time_between_transactions')} seconds",
            "inference": "The wallet moves funds with unusually short intervals in the synthetic timeline",
            "investigative_lead": "Review for rapid transfer or layering patterns",
            "confidence": 0.78,
        })
    if wallet_record.get("graph_degree", 0) > 12:
        reasons.append({
            "category": "graph_connectivity",
            "label": "High graph connectivity",
            "evidence": f"Graph degree: {wallet_record.get('graph_degree')}",
            "inference": "The wallet participates in a dense synthetic graph neighborhood",
            "investigative_lead": "Trace the most connected counterparties and IPs",
            "confidence": 0.68,
        })
    return reasons


def generate_explanations(wallets_df: pd.DataFrame, risk_df: pd.DataFrame) -> pd.DataFrame:
    """Return detailed explanation rows for flagged wallets."""
    merged = wallets_df.merge(risk_df, on="wallet_id", how="inner")
    explanations: list[dict[str, Any]] = []
    for _, row in merged.iterrows():
        reasons = generate_reason_rows(row.to_dict())
        if reasons:
            explanations.append({
                "wallet_id": row["wallet_id"],
                "risk_score": row["risk_score"],
                "risk_level": row["risk_level"],
                "reasons": reasons,
            })
    return pd.DataFrame(explanations)


__all__ = ["generate_reason_rows", "generate_explanations"]
