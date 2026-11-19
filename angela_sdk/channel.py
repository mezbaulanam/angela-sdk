from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from .context import Context


class ChannelContext:
    """Manages temporary game channel and thread lifecycles."""

    def __init__(self, ctx: Context) -> None:
        self._ctx = ctx

    def create(
        self,
        name: str,
        category_id: Optional[int] = None,
        ttl_minutes: int = 60,
        callback: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Request creation of a dedicated temporary game channel."""
        intent = {
            "op": "CHANNEL_OP",
            "action": "CREATE",
            "name": str(name)[:32],
            "category_id": category_id,
            "max_ttl_minutes": int(ttl_minutes),
            "callback_event_id": callback,
        }
        self._ctx.add_intent(intent)
        return intent

    def delete(self, channel_id: Optional[int] = None) -> Dict[str, Any]:
        """Request deletion of a temporary game channel."""
        intent = {
            "op": "CHANNEL_OP",
            "action": "DELETE",
            "channel_id": channel_id or self._ctx.channel_id,
        }
        self._ctx.add_intent(intent)
        return intent
