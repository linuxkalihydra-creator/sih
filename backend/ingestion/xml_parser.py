"""XML ingestion utilities for the synthetic Bitcoin investigation dataset."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


def _read_text(element: ET.Element, tag: str) -> str | None:
    """Return a text value from an XML child element, or None if missing."""
    child = element.find(tag)
    if child is None or child.text is None:
        return None
    return child.text.strip()


def _read_list(element: ET.Element, tag: str) -> list[str | float]:
    """Read a repeated XML list such as output_addresses or output_amounts."""
    container = element.find(tag)
    if container is None:
        return []
    values: list[str | float] = []
    for child in container:
        text = child.text.strip() if child.text else ""
        if not text:
            continue
        try:
            values.append(float(text))
        except ValueError:
            values.append(text)
    return values


def parse_xml(path: str | Path) -> list[dict[str, Any]]:
    """Parse an XML document containing a list of <transaction> elements."""
    xml_path = Path(path)
    if not xml_path.exists():
        raise FileNotFoundError(f"XML file does not exist: {xml_path}")

    tree = ET.parse(xml_path)
    root = tree.getroot()
    records: list[dict[str, Any]] = []

    for node in root.findall("transaction"):
        record: dict[str, Any] = {
            "timestamp": _read_text(node, "timestamp") or "",
            "src_ip": _read_text(node, "src_ip") or "",
            "dst_ip": _read_text(node, "dst_ip") or "",
            "src_port": _read_text(node, "src_port") or 0,
            "dst_port": _read_text(node, "dst_port") or 0,
            "txid": _read_text(node, "txid") or "",
            "input_addresses": _read_list(node, "input_addresses"),
            "output_addresses": _read_list(node, "output_addresses"),
            "input_amounts": _read_list(node, "input_amounts"),
            "output_amounts": _read_list(node, "output_amounts"),
            "fee": _read_text(node, "fee") or 0,
            "script_type": _read_text(node, "script_type") or "",
            "geo_country": _read_text(node, "geo_country") or "",
            "asn": _read_text(node, "asn") or 0,
            "behavior_type": _read_text(node, "behavior_type") or "",
        }

        # Optional fields are permitted in the synthetic data and can be safely included.
        for key in ["block_height", "transaction_size"]:
            value = _read_text(node, key)
            if value is not None:
                record[key] = int(value) if key in {"block_height", "transaction_size"} else value

        records.append(record)

    return records
