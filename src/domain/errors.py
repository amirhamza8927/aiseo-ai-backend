"""Domain-level exceptions."""

from __future__ import annotations


class DomainError(Exception):
    """Base exception for all domain errors."""


class ValidationDomainError(DomainError):
    """Raised when a domain validation rule is violated."""


class PlanIntegrityError(DomainError):
    """Raised when plan structure constraints are broken (e.g. duplicate IDs, dangling refs)."""
