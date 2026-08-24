"""Reusable FastAPI dependencies for DB availability checks."""
from __future__ import annotations

from fastapi import HTTPException, status

from . import db


def require_db() -> None:
    """FastAPI dependency: abort with 503 if CognoDB is not reachable."""
    if not db.verify_connectivity():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cannot connect to CognoDB. Check that the database is running and credentials are correct.",
        )
