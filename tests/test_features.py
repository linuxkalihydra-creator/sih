import pandas as pd

from backend.ml.features import build_wallet_feature_frame


def test_feature_frame_has_wallet_rows_and_numeric_columns():
    records = [{
        "timestamp": "2024-01-01T00:00:00+00:00",
        "src_ip": "203.0.113.10",
        "dst_ip": "198.51.100.10",
        "src_port": 8333,
        "dst_port": 8333,
        "txid": "tx_1",
        "input_addresses": ["wallet_a"],
        "output_addresses": ["wallet_b"],
        "input_amounts": [1.0],
        "output_amounts": [0.95],
        "fee": 0.05,
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
        "input_addresses": ["wallet_b"],
        "output_addresses": ["wallet_c"],
        "input_amounts": [0.95],
        "output_amounts": [0.9],
        "fee": 0.05,
        "script_type": "P2WPKH",
        "geo_country": "US",
        "asn": 64512,
        "behavior_type": "NORMAL",
    }]
    frame = build_wallet_feature_frame(records)
    assert isinstance(frame, pd.DataFrame)
    assert not frame.empty
    assert "wallet_id" in frame.columns
    assert "transaction_count" in frame.columns
    assert "total_received" in frame.columns
