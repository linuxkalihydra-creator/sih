"""Graph-building utilities for the synthetic investigative prototype."""

from __future__ import annotations

from typing import Any


def build_transaction_graph(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Create a lightweight graph representation from transactions.

    This helps the later graph phase without creating an application dependency on a
    live Neo4j instance.
    """
    graph_nodes: list[dict[str, Any]] = []
    for record in records:
        txid = str(record.get("txid", ""))
        for wallet in record.get("input_addresses", []):
            graph_nodes.append({"type": "Wallet", "id": str(wallet), "relationship": "INPUT_FROM", "txid": txid})
        for wallet in record.get("output_addresses", []):
            graph_nodes.append({"type": "Wallet", "id": str(wallet), "relationship": "OUTPUT_TO", "txid": txid})
        graph_nodes.append({"type": "Transaction", "id": txid, "relationship": "OBSERVED_IN", "ip": record.get("src_ip")})
        graph_nodes.append({"type": "IP", "id": str(record.get("src_ip", "")), "relationship": "OBSERVED_IN", "txid": txid})
    return graph_nodes
