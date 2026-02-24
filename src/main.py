"""FastAPI application entry point."""

from __future__ import annotations

from fastapi import FastAPI

from src.api.routers import health, jobs

app = FastAPI(title="AIseo-AI")
app.include_router(health.router)
app.include_router(jobs.router)
