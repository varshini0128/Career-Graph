"""Singleton Neo4j driver for CognoDB.

The driver is created lazily so the API can start even when the database is
unreachable — endpoints then surface a clean 503 instead of crashing on import.
"""
from __future__ import annotations

import logging
from typing import Any

from neo4j import Driver, GraphDatabase

from .config import settings

logger = logging.getLogger("careergraph.db")

_driver: Driver | None = None


def get_driver() -> Driver:
    """Return the shared driver, creating it on first use."""
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            settings.cognodb_uri,
            auth=(settings.cognodb_username, settings.cognodb_password),
        )
    return _driver


def close_driver() -> None:
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None


def verify_connectivity() -> bool:
    """Probe the database. Returns True on success, False on failure."""
    try:
        driver = get_driver()
        driver.verify_connectivity()
        return True
    except Exception as exc:  # noqa: BLE001
        logger.warning("CognoDB connectivity check failed: %s", exc)
        return False


def run_query(cypher: str, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Run a read query and return a list of record dicts. Raises on DB error."""
    driver = get_driver()
    with driver.session(database=settings.cognodb_database) as session:
        result = session.run(cypher, parameters or {})
        return [r.data() for r in result]


def run_write(tx_fn) -> Any:
    """Run a write transaction. ``tx_fn`` receives a ManagedTransaction."""
    driver = get_driver()
    with driver.session(database=settings.cognodb_database) as session:
        return session.execute_write(tx_fn)
