"""Normalization utilities that convert raw ingested records into a canonical schema."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

CANONICAL_FIELDS = (
    "timestamp",
    "src_ip",
    "dst_ip",
    "src_port",
    "dst_port",
    "txid",
    "input_addresses",
    "output_addresses",
    "input_amounts",
    "output_amounts",
    "fee",
    "script_type",
    "geo_country",
    "asn",
    "behavior_type",
)


def _ensure_list(value: Any) -> list[Any]:
    """Normalize a field that may be a list, tuple, or JSON string."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []
        try:
            decoded = json.loads(stripped)
            if isinstance(decoded, list):
                return decoded
        except json.JSONDecodeError:
            pass
        return [stripped]
    return [value]


def normalize_record(raw_record: dict[str, Any]) -> dict[str, Any]:
    """Convert a raw record to a canonical internal format."""
    if not isinstance(raw_record, dict):
        raise TypeError("Normalized records must be dictionaries.")

    normalized = {
        "timestamp": str(raw_record.get("timestamp", "")).strip(),
        "src_ip": str(raw_record.get("src_ip", "")).strip(),
        "dst_ip": str(raw_record.get("dst_ip", "")).strip(),
        "src_port": int(raw_record.get("src_port", 0) or 0),
        "dst_port": int(raw_record.get("dst_port", 0) or 0),
        "txid": str(raw_record.get("txid", "")).strip(),
        "input_addresses": [str(item) for item in _ensure_list(raw_record.get("input_addresses", []))],
        "output_addresses": [str(item) for item in _ensure_list(raw_record.get("output_addresses", []))],
        "input_amounts": [float(item) for item in _ensure_list(raw_record.get("input_amounts", []))],
        "output_amounts": [float(item) for item in _ensure_list(raw_record.get("output_amounts", []))],
        "fee": float(raw_record.get("fee", 0) or 0),
        "script_type": str(raw_record.get("script_type", "")).strip(),
        "geo_country": str(raw_record.get("geo_country", "")).strip(),
        "asn": int(raw_record.get("asn", 0) or 0),
        "behavior_type": str(raw_record.get("behavior_type", "")).strip(),
    }

    for key in ("block_height", "transaction_size"):
        if key in raw_record and raw_record[key] is not None:
            normalized[key] = int(raw_record[key])

    if normalized["timestamp"]:
        try:
            datetime.fromisoformat(normalized["timestamp"])
        except ValueError:
            raise ValueError(f"Invalid ISO timestamp: {normalized['timestamp']}")

    input_total = sum(normalized["input_amounts"])
    output_total = sum(normalized["output_amounts"])
    if normalized["fee"] == 0 and input_total >= output_total:
        normalized["fee"] = round(max(input_total - output_total, 0.0), 8)

    return normalized


def normalize_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Apply canonical normalization to each record in a list."""
    return [normalize_record(record) for record in records]
