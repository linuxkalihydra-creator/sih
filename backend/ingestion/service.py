"""High-level ingestion service for synthetic Bitcoin transaction data."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.ingestion.csv_parser import parse_csv
from backend.ingestion.json_parser import parse_json
from backend.ingestion.normalizer import normalize_records
from backend.ingestion.validator import summarize_records, validate_record
from backend.ingestion.xml_parser import parse_xml


def detect_format(path: str | Path) -> str:
    """Return the dataset file format based on the extension."""
    suffix = Path(path).suffix.lower()
    if suffix == ".csv":
        return "csv"
    if suffix == ".json":
        return "json"
    if suffix == ".xml":
        return "xml"
    raise ValueError(f"Unsupported dataset format for path: {path}")


def load_dataset(path: str | Path, include_summary: bool = False) -> list[dict[str, Any]] | tuple[list[dict[str, Any]], dict[str, Any]]:
    """Load, normalize, validate and summarize a dataset.

    The returned records follow the canonical internal schema used throughout the
    offline investigation prototype.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    format_name = detect_format(file_path)
    if format_name == "csv":
        raw_records = parse_csv(file_path)
    elif format_name == "json":
        raw_records = parse_json(file_path)
    elif format_name == "xml":
        raw_records = parse_xml(file_path)
    else:
        raise ValueError(f"Unsupported format: {format_name}")

    normalized = normalize_records(raw_records)

    valid_records: list[dict[str, Any]] = []
    invalid_records = 0
    summary_missing: dict[str, int] = {}
    seen_txids: set[str] = set()

    for record in normalized:
        errors = validate_record(record)
        if errors:
            invalid_records += 1
            for error in errors:
                if error.startswith("Missing required field:"):
                    field = error.split(": ", 1)[1]
                    summary_missing[field] = summary_missing.get(field, 0) + 1
            continue

        txid = str(record.get("txid", "")).strip()
        if txid in seen_txids:
            continue
        seen_txids.add(txid)
        valid_records.append(record)

    summary = {
        "total_records": len(normalized),
        "valid_records": len(valid_records),
        "invalid_records": invalid_records,
        "duplicates": max(0, len(normalized) - len(valid_records) - invalid_records),
        "missing_fields": summary_missing,
    }

    if include_summary:
        return valid_records, summary
    return valid_records


__all__ = ["load_dataset", "detect_format"]
