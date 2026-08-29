"""Graph service façade for the synthetic investigation prototype."""

from __future__ import annotations

from typing import Any

from backend.graph.graph_builder import build_transaction_graph
from backend.graph.neo4j_client import Neo4jClient, Neo4jUnavailableError


def build_graph(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build a local graph structure from records without requiring Neo4j."""
    return build_transaction_graph(records)


def ensure_graph_available() -> None:
    """Raise a clear error if the environment is not prepared for Neo4j access."""
    client = Neo4jClient()
    try:
        client.connect()
    except Neo4jUnavailableError:
        raise
    finally:
        client.close()


__all__ = ["build_graph", "ensure_graph_available"]
