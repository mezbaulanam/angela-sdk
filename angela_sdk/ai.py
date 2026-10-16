from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from .context import Context


class AIContext:
    def __init__(self, ctx: Context) -> None:
        self._ctx = ctx

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        tier: str = "ai_low",
        temperature: float = 1.0,
        max_tokens: int = 400,
        callback: str = "on_ai_ready",
    ) -> Dict[str, Any]:
        intent = {
            "op": "AI_GENERATE",
            "tier": str(tier),
            "system_prompt": str(system_prompt),
            "user_prompt": str(user_prompt),
            "temperature": float(temperature),
            "max_tokens": int(max_tokens),
            "callback_event_id": str(callback),
        }
        self._ctx.add_intent(intent)
        return intent


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

