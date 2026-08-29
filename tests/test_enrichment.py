from backend.enrichment.service import enrich_record, get_offline_db_locations


def test_enrich_record_keeps_synthetic_fallback():
    record = {
        "src_ip": "203.0.113.10",
        "dst_ip": "198.51.100.15",
        "geo_country": "US",
        "asn": 64512,
    }
    enriched = enrich_record(record)
    assert enriched["geo_country"] == "US"
    assert enriched["asn"] == 64512


def test_offline_db_locations_are_documented():
    locations = get_offline_db_locations()
    assert "geoip" in locations
    assert "asn" in locations
