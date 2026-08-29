"""Offline GeoIP and country enrichment helpers.

This project is synthetic by design. The enrichment layer should not claim to know
real geographic intelligence about a real Bitcoin transaction. Instead, it supports
mapping IPs to a local, offline dataset or gracefully falling back to the synthetic
country field already present in the generated dataset.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class GeoIPAdapter:
    """Interface for a local GeoIP dataset.

    A real implementation could consume MaxMind-style or locally generated CSV/JSON
    records. This prototype keeps the contract simple and offline-safe.
    """

    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path) if db_path else None
        self._cache: dict[str, str] = {}
        self._load_local_database()

    def _load_local_database(self) -> None:
        """Load an optional local GeoIP database if one is provided on disk."""
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
            country = record.get("country")
            if ip_value and country:
                self._cache[str(ip_value)] = str(country)

    def resolve_country(self, ip_address: str) -> str | None:
        """Resolve an IP to a country code if a local database is available."""
        if not ip_address:
            return None
        return self._cache.get(str(ip_address))

    def enrich_record(self, record: dict[str, Any]) -> dict[str, Any]:
        """Return a record with a resolved country when available."""
        enriched = dict(record)
        ip_value = str(record.get("src_ip", "")).strip() or str(record.get("dst_ip", "")).strip()
        resolved = self.resolve_country(ip_value)
        if resolved:
            enriched["geo_country"] = resolved
            enriched["geo_country_source"] = "local_geoip"
        else:
            enriched.setdefault("geo_country", record.get("geo_country", "UNKNOWN"))
            enriched.setdefault("geo_country_source", "synthetic_fallback")
        return enriched


def resolve_country_fallback(record: dict[str, Any], geoip_db_path: str | Path | None = None) -> dict[str, Any]:
    """Resolve the IP to a country if possible; otherwise fall back to the synthetic field."""
    adapter = GeoIPAdapter(geoip_db_path)
    return adapter.enrich_record(record)
