"""FastAPI application factory."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import close_driver, verify_connectivity
from .routers import (
    jobs_router,
    catalog_router,
    skill_gap_router,
    connections_router,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("careergraph")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("CareerGraph API starting — CognoDB URI: %s", settings.cognodb_uri)
    if verify_connectivity():
        logger.info("Connected to CognoDB.")
    else:
        logger.warning("Could not connect to CognoDB on startup. Endpoints will return 503.")
    yield
    close_driver()
    logger.info("CareerGraph API stopped.")


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    lifespan=lifespan,
    description="Career exploration and skill-gap analysis powered by CognoDB (Neo4j-compatible graph database).",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs_router)
app.include_router(catalog_router)
app.include_router(skill_gap_router)
app.include_router(connections_router)


@app.get("/health", tags=["health"])
def health():
    ok = verify_connectivity()
    return {"status": "ok" if ok else "unavailable", "database": "connected" if ok else "disconnected"}
