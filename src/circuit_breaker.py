"""
Circuit Breaker pattern — preventing cascading failures.

A circuit breaker wraps a remote call and tracks failures. After a
threshold is reached it trips to OPEN, rejecting calls immediately
without hitting the failing service. After a timeout it moves to
HALF-OPEN to probe recovery; a success resets it to CLOSED.

States: CLOSED (normal) -> OPEN (failing) -> HALF-OPEN (testing) -> CLOSED

Reference: Release It! — Michael Nygard (2007)
"""

from __future__ import annotations

import time
from enum import Enum, auto
from typing import Callable, TypeVar

T = TypeVar("T")


class State(Enum):
    CLOSED = auto()
    OPEN = auto()
    HALF_OPEN = auto()


class CircuitBreakerOpen(Exception):
    """Raised when a call is rejected because the circuit is open."""


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        success_threshold: int = 2,
    ) -> None:
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._success_threshold = success_threshold

        self._state = State.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._opened_at: float = 0.0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def call(self, fn: Callable[[], T]) -> T:
        """Execute fn through the circuit breaker."""
        self._maybe_attempt_reset()

        if self._state is State.OPEN:
            raise CircuitBreakerOpen("Circuit is OPEN — call rejected")

        try:
            result = fn()
        except Exception:
            self._on_failure()
            raise

        self._on_success()
        return result

    @property
    def state(self) -> State:
        self._maybe_attempt_reset()
        return self._state

    # ------------------------------------------------------------------
    # Internal state machine
    # ------------------------------------------------------------------

    def _on_failure(self) -> None:
        self._failure_count += 1
        self._success_count = 0
        if self._state is State.HALF_OPEN or self._failure_count >= self._failure_threshold:
            self._trip()

    def _on_success(self) -> None:
        if self._state is State.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self._success_threshold:
                self._reset()
        else:
            self._failure_count = 0

    def _trip(self) -> None:
        self._state = State.OPEN
        self._opened_at = time.monotonic()

    def _reset(self) -> None:
        self._state = State.CLOSED
        self._failure_count = 0
        self._success_count = 0

    def _maybe_attempt_reset(self) -> None:
        if (
            self._state is State.OPEN
            and time.monotonic() - self._opened_at >= self._recovery_timeout
        ):
            self._state = State.HALF_OPEN
            self._success_count = 0
