"""CSV ingestion utilities for the synthetic Bitcoin investigation dataset."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def _coerce_field(value: Any) -> Any:
    """Convert CSV values to Python-native types when they resemble JSON-like arrays."""
    if value is None:
        return value
    stripped = value.strip()
    if not stripped:
        return value
    if stripped.startswith("[") and stripped.endswith("]"):
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            return stripped
    if stripped.lower() in {"true", "false"}:
        return stripped.lower() == "true"
    try:
        return int(stripped)
    except ValueError:
        pass
    try:
        return float(stripped)
    except ValueError:
        return stripped


def parse_csv(path: str | Path) -> list[dict[str, Any]]:
    """Parse a CSV dataset into a list of dictionaries.

    Array-like fields such as input_addresses/output_addresses are decoded from JSON
    strings when present.
    """
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file does not exist: {csv_path}")

    rows: list[dict[str, Any]] = []
    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            cleaned = {key: _coerce_field(value) for key, value in row.items()}
            rows.append(cleaned)
    return rows
