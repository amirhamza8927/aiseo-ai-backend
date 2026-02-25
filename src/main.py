"""FastAPI application entry point."""

from __future__ import annotations

import warnings

from fastapi import FastAPI

from src.api.routers import health, jobs

# Suppress Pydantic serializer warning from LangChain's with_structured_output(include_raw=True).
# The return dict has "parsed" which can be None or the model; Pydantic warns when serializing.
warnings.filterwarnings(
    "ignore",
    message=".*serialized value may not be as expected.*",
    category=UserWarning,
)

app = FastAPI(title="AIseo-AI")
app.include_router(health.router)
app.include_router(jobs.router)
