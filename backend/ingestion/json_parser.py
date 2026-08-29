"""JSON ingestion utilities for the synthetic Bitcoin investigation dataset."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def parse_json(path: str | Path) -> list[dict[str, Any]]:
    """Load a JSON file and return a list of transaction dictionaries."""
    json_path = Path(path)
    if not json_path.exists():
        raise FileNotFoundError(f"JSON file does not exist: {json_path}")

    with json_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if isinstance(payload, list):
        return [dict(record) for record in payload]
    if isinstance(payload, dict):
        items = payload.get("transactions")
        if items is None:
            raise ValueError("JSON object does not contain a 'transactions' list.")
        if not isinstance(items, list):
            raise ValueError("JSON 'transactions' field must be a list.")
        return [dict(record) for record in items]
    raise ValueError("Unsupported JSON structure. Expected a list or a dict with a transactions list.")
