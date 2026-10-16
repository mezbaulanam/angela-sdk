from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from .context import Context


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

