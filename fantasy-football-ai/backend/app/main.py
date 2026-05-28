"""Application entry point for the Fantasy Football AI Draft Evaluator."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import players, projections, draft

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Fantasy Football AI API")
    yield
    logger.info("Shutting down Fantasy Football AI API")


app = FastAPI(
    title="Fantasy Football AI API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(players.router, prefix="/api/players", tags=["players"])
app.include_router(projections.router, prefix="/api/projections", tags=["projections"])
app.include_router(draft.router, prefix="/api/draft", tags=["draft"])


@app.get("/health")
async def health():
    return {"status": "ok", "environment": settings.ENVIRONMENT}
