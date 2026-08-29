"""Temporal correlation utilities for time-ordered synthetic activity."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def sort_records_by_time(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort records chronologically to support temporal correlation analysis."""
    return sorted(records, key=lambda record: datetime.fromisoformat(str(record["timestamp"])))


def time_gap_seconds(record_a: dict[str, Any], record_b: dict[str, Any]) -> float:
    """Return the elapsed time in seconds between two synthetic transaction timestamps."""
    first = datetime.fromisoformat(str(record_a["timestamp"]))
    second = datetime.fromisoformat(str(record_b["timestamp"]))
    return abs((second - first).total_seconds())


def wallet_temporal_score(wallet_address: str, records: list[dict[str, Any]]) -> float:
    """Return a simple score based on how many times the wallet appears across sorted transactions."""
    appearances = 0
    for record in records:
        wallets = record.get("input_addresses", []) + record.get("output_addresses", [])
        if str(wallet_address) in {str(wallet) for wallet in wallets}:
            appearances += 1
    return float(min(1.0, appearances / max(len(records), 1)))
