"""Evidence helpers for the synthetic explainability layer."""

from __future__ import annotations

from typing import Any


def summarize_evidence(wallet_record: dict[str, Any]) -> dict[str, Any]:
    """Summarize observed facts and investigative lead details for one wallet."""
    return {
        "observed_fact": {
            "transaction_count": wallet_record.get("transaction_count", 0),
            "unique_ips": wallet_record.get("unique_ips", 0),
            "unique_counterparties": wallet_record.get("unique_counterparties", 0),
            "average_time_between_transactions": wallet_record.get("average_time_between_transactions", 0),
            "graph_degree": wallet_record.get("graph_degree", 0),
        },
        "inference": "The wallet shows a cluster of synthetic behavioral anomalies that may warrant investigation.",
        "investigative_lead": "Compare this wallet to nearby IP and wallet activity to understand whether the pattern is a local anomaly or a broader grouping.",
    }
