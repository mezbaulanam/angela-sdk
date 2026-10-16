from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from .context import Context


class HTTPContext:
    def __init__(self, ctx: Context) -> None:
        self._ctx = ctx

    def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        callback: str = "on_http_response",
    ) -> Dict[str, Any]:
        return self.request(url, method="GET", headers=headers, callback=callback)

    def request(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        callback: str = "on_http_response",
    ) -> Dict[str, Any]:
        intent: Dict[str, Any] = {
            "op": "HTTP_REQUEST",
            "method": method.upper(),
            "url": str(url),
            "headers": dict(headers or {}),
            "body": body,
            "callback_event_id": str(callback),
        }
        self._ctx.add_intent(intent)
        return intent


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


class StorageContext:
    def __init__(self, ctx: Context) -> None:
        self._ctx = ctx

    def get(self, key: str, default: Any = None) -> Any:
        return self._ctx.state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._ctx.state[key] = value

    def set_cooldown(self, user_id: int, seconds: int) -> Dict[str, Any]:
        intent = {
            "op": "STORAGE_MUTATE",
            "action": "SET_COOLDOWN",
            "user_id": int(user_id),
            "seconds": int(seconds),
        }
        self._ctx.add_intent(intent)
        return intent

