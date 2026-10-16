from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from .context import Context


class MediaContext:
    def __init__(self, ctx: Context) -> None:
        self._ctx = ctx

    def search_gif(self, query: str, callback: str = "on_gif_ready") -> Dict[str, Any]:
        intent = {
            "op": "MEDIA_SEARCH_GIF",
            "query": str(query),
            "callback_event_id": str(callback),
        }
        self._ctx.add_intent(intent)
        return intent

