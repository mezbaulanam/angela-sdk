from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from .context import Context


class DiscordContext:
    def __init__(self, ctx: Context) -> None:
        self._ctx = ctx

    def lock_channel(self, duration_seconds: int = 20) -> Dict[str, Any]:
        intent = {
            "op": "CHANNEL_LOCK",
            "duration_seconds": int(duration_seconds),
        }
        self._ctx.add_intent(intent)
        return intent

    def listen_messages(
        self,
        exact_match: Optional[str] = None,
        regex: Optional[str] = None,
        callback: str = "on_message",
        enabled: bool = True,
    ) -> Dict[str, Any]:
        intent: Dict[str, Any] = {
            "op": "LISTEN_MESSAGES",
            "enabled": bool(enabled),
            "callback_event_id": str(callback),
        }
        if exact_match is not None:
            intent["exact_match"] = str(exact_match)
        if regex is not None:
            intent["regex"] = str(regex)
        self._ctx.add_intent(intent)
        return intent

