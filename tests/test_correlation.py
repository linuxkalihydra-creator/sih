from backend.correlation.service import build_correlation_index, correlate_ip_to_wallet, correlate_wallets, get_related_transactions


def test_correlation_index_builds_successfully():
    records = []
    for i in range(3):
        records.append({
            "timestamp": f"2024-01-01T00:00:{i:02d}+00:00",
            "src_ip": "203.0.113.10",
            "dst_ip": "198.51.100.10",
            "src_port": 8333,
            "dst_port": 8333,
            "txid": f"tx_{i}",
            "input_addresses": [f"wallet_{i}"],
            "output_addresses": [f"wallet_{i+1}"],
            "input_amounts": [1.0],
            "output_amounts": [1.0],
            "fee": 0.0,
            "script_type": "P2WPKH",
            "geo_country": "US",
            "asn": 64512,
            "behavior_type": "NORMAL",
        })
    index = build_correlation_index(records)
    assert "wallet_map" in index
    assert len(index["transaction_wallet_map"]) == 3


def test_ip_to_wallet_correlation_is_numeric():
    records = [{
        "timestamp": "2024-01-01T00:00:00+00:00",
        "src_ip": "203.0.113.10",
        "dst_ip": "198.51.100.10",
        "src_port": 8333,
        "dst_port": 8333,
        "txid": "tx_1",
        "input_addresses": ["wallet_alpha"],
        "output_addresses": ["wallet_beta"],
        "input_amounts": [1.0],
        "output_amounts": [1.0],
        "fee": 0.0,
        "script_type": "P2WPKH",
        "geo_country": "US",
        "asn": 64512,
        "behavior_type": "NORMAL",
    }]
    index = build_correlation_index(records)
    score = correlate_ip_to_wallet("203.0.113.10", "wallet_alpha", index)
    assert score in (0.0, 1.0)


def test_wallet_overlap_score_is_numeric():
    records = [{
        "timestamp": "2024-01-01T00:00:00+00:00",
        "src_ip": "203.0.113.10",
        "dst_ip": "198.51.100.10",
        "src_port": 8333,
        "dst_port": 8333,
        "txid": "tx_1",
        "input_addresses": ["wallet_alpha"],
        "output_addresses": ["wallet_beta"],
        "input_amounts": [1.0],
        "output_amounts": [1.0],
        "fee": 0.0,
        "script_type": "P2WPKH",
        "geo_country": "US",
        "asn": 64512,
        "behavior_type": "NORMAL",
    }, {
        "timestamp": "2024-01-01T00:05:00+00:00",
        "src_ip": "203.0.113.11",
        "dst_ip": "198.51.100.11",
        "src_port": 8333,
        "dst_port": 8333,
        "txid": "tx_2",
        "input_addresses": ["wallet_alpha"],
        "output_addresses": ["wallet_gamma"],
        "input_amounts": [1.2],
        "output_amounts": [1.2],
        "fee": 0.0,
        "script_type": "P2WPKH",
        "geo_country": "US",
        "asn": 64512,
        "behavior_type": "NORMAL",
    }]
    index = build_correlation_index(records)
    score = correlate_wallets("wallet_alpha", "wallet_beta", index)
    assert 0.0 <= score <= 1.0


def test_related_transactions_are_returned():
    records = [{
        "timestamp": "2024-01-01T00:00:00+00:00",
        "src_ip": "203.0.113.10",
        "dst_ip": "198.51.100.10",
        "src_port": 8333,
        "dst_port": 8333,
        "txid": "tx_1",
        "input_addresses": ["wallet_alpha"],
        "output_addresses": ["wallet_beta"],
        "input_amounts": [1.0],
        "output_amounts": [1.0],
        "fee": 0.0,
        "script_type": "P2WPKH",
        "geo_country": "US",
        "asn": 64512,
        "behavior_type": "NORMAL",
    }]
    index = build_correlation_index(records)
    txs = get_related_transactions("wallet_alpha", index)
    assert txs == ["tx_1"]
