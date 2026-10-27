"""Custom exceptions for the SignalHouse SDK."""

from __future__ import annotations


class SignalHouseError(Exception):
    """Base exception for SignalHouse SDK errors."""

    def __init__(self, message: str, status: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.status = status


class SignalHouseValidationError(SignalHouseError):
    """Raised when a required parameter is missing or invalid."""

    def __init__(self, message: str) -> None:
        super().__init__(message, status=400)
