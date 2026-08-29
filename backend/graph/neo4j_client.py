"""Neo4j client wrapper for offline-safe analysis tooling.

This project does not install or require Neo4j during local development. Instead,
this module provides a thin interface that raises a clear error when Neo4j is not
available while keeping the rest of the application compatible with a future local
Neo4j service.
"""

from __future__ import annotations

import os
from typing import Any


class Neo4jUnavailableError(RuntimeError):
    """Raised when a Neo4j dependency is required but not available."""


class Neo4jClient:
    """Very small wrapper around a Neo4j driver.

    The implementation intentionally avoids hard-coded dangerous operations and
    keeps the contract simple for later offline graph loading.
    """

    def __init__(self, uri: str | None = None, username: str | None = None, password: str | None = None):
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.username = username or os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "password")
        self._driver = None

    def connect(self) -> None:
        """Connect to Neo4j if the driver is installed and reachable."""
        try:
            from neo4j import GraphDatabase
        except ImportError as exc:  # pragma: no cover - environment-specific.
            raise Neo4jUnavailableError(
                "Neo4j is not installed in this environment. Install it locally with Ubuntu packages or Docker if needed for graph testing."
            ) from exc

        self._driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))

    def close(self) -> None:
        """Close the underlying driver if it exists."""
        if self._driver is not None:
            self._driver.close()
            self._driver = None

    def clear_graph(self) -> None:
        """Remove all existing graph data in the database."""
        if self._driver is None:
            raise Neo4jUnavailableError("Neo4j connection is not available; call connect() first.")
        with self._driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def get_status(self) -> dict[str, Any]:
        """Return a status dictionary that is safe for local diagnostics."""
        return {
            "uri": self.uri,
            "username": self.username,
            "connected": self._driver is not None,
            "availability": "requires_local_neo4j",
        }
