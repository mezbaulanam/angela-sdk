from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from .context import Context


class TimerContext:
    """Manages asynchronous hibernation and scheduled wakes."""

    def __init__(self, ctx: Context) -> None:
        self._ctx = ctx

    def schedule(self, delay_seconds: float, callback: str = "on_wake") -> Dict[str, Any]:
        """Schedule a wake event after a delay."""
        intent = {
            "op": "SCHEDULE_WAKE",
            "delay_seconds": float(delay_seconds),
            "callback_event_id": str(callback),
        }
        self._ctx.add_intent(intent)
        return intent

    def cancel(self) -> Dict[str, Any]:
        """Cancel an active scheduled wake for this session early."""
        intent = {
            "op": "TIMER_CANCEL",
        }
        self._ctx.add_intent(intent)
        return intent
