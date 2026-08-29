from backend.graph.graph_builder import build_transaction_graph
from backend.graph.service import build_graph


def test_build_transaction_graph_returns_records():
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
        "output_amounts": [1.0],
        "fee": 0.0,
        "script_type": "P2WPKH",
        "geo_country": "US",
        "asn": 64512,
        "behavior_type": "NORMAL",
    }]
    graph = build_transaction_graph(records)
    assert len(graph) > 0
    assert build_graph(records) == graph
