"""Structured logging configuration (stdlib only)."""

from __future__ import annotations

import logging
import sys


_JSON_FORMAT = (
    '{"timestamp":"%(asctime)s",'
    '"level":"%(levelname)s",'
    '"module":"%(name)s",'
    '"message":"%(message)s"}'
)


def configure_logging(level: str = "INFO") -> None:
    """Set up the root logger with structured JSON-like output."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(fmt=_JSON_FORMAT, datefmt="%Y-%m-%dT%H:%M:%S")
    )

    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not root.handlers:
        root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger. Call *configure_logging* once at startup."""
    return logging.getLogger(name)
