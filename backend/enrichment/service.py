"""High-level enrichment service for offline GeoIP/ASN resolution."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.enrichment.asn import resolve_asn_fallback
from backend.enrichment.geoip import resolve_country_fallback


def enrich_record(record: dict[str, Any], geoip_db_path: str | Path | None = None, asn_db_path: str | Path | None = None) -> dict[str, Any]:
    """Apply offline enrichment while preserving the synthetic dataset fallback behavior."""
    enriched = dict(record)
    enriched = resolve_country_fallback(enriched, geoip_db_path)
    enriched = resolve_asn_fallback(enriched, asn_db_path)
    return enriched


def enrich_records(records: list[dict[str, Any]], geoip_db_path: str | Path | None = None, asn_db_path: str | Path | None = None) -> list[dict[str, Any]]:
    """Enrich a list of records in place with offline GeoIP/ASN metadata."""
    return [enrich_record(record, geoip_db_path, asn_db_path) for record in records]


def get_offline_db_locations() -> dict[str, str]:
    """Return the expected local GeoIP/ASN database locations for this project."""
    return {
        "geoip": "data/geoip/local_geoip.json",
        "asn": "data/geoip/local_asn.json",
        "note": "These local files are optional. The synthetic dataset already contains geo_country and asn fields.",
    }


__all__ = ["enrich_record", "enrich_records", "get_offline_db_locations"]
