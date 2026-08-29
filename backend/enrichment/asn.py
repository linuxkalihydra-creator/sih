"""Offline ASN enrichment helpers.

The synthetic dataset already includes `asn` values. This adapter provides an
extension point for a local ASN table without requiring internet access.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ASNAdapter:
    """Minimal local ASN resolver contract."""

    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path) if db_path else None
        self._cache: dict[str, int] = {}
        self._load_local_database()

    def _load_local_database(self) -> None:
        """Load an optional local ASN mapping file."""
        if self.db_path is None or not self.db_path.exists():
            return

        try:
            with self.db_path.open("r", encoding="utf-8") as handle:
                records = json.load(handle)
        except (json.JSONDecodeError, OSError):
            return

        if isinstance(records, dict):
            records = records.get("data", [])

        for record in records:
            if not isinstance(record, dict):
                continue
            ip_value = record.get("ip")
            asn_value = record.get("asn")
            if ip_value and asn_value is not None:
                self._cache[str(ip_value)] = int(asn_value)

    def resolve_asn(self, ip_address: str) -> int | None:
        """Return an ASN for an IP when a local database is available."""
        if not ip_address:
            return None
        return self._cache.get(str(ip_address))

    def enrich_record(self, record: dict[str, Any]) -> dict[str, Any]:
        """Return a record with an ASN resolved when possible."""
        enriched = dict(record)
        ip_value = str(record.get("src_ip", "")).strip() or str(record.get("dst_ip", "")).strip()
        resolved = self.resolve_asn(ip_value)
        if resolved is not None:
            enriched["asn"] = resolved
            enriched["asn_source"] = "local_asn"
        else:
            enriched.setdefault("asn", record.get("asn", 0))
            enriched.setdefault("asn_source", "synthetic_fallback")
        return enriched


def resolve_asn_fallback(record: dict[str, Any], asn_db_path: str | Path | None = None) -> dict[str, Any]:
    """Resolve ASN for an IP if local data exists; otherwise keep the synthetic ASN value."""
    adapter = ASNAdapter(asn_db_path)
    return adapter.enrich_record(record)
