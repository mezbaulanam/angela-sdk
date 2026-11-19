from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

if TYPE_CHECKING:
    from .context import Context


class PermissionsContext:
    """Manages channel-level permission overwrites with lease-backed crash recovery."""

    def __init__(self, ctx: Context) -> None:
        self._ctx = ctx

    def set(
        self,
        target: Union[str, int],
        allow: Optional[List[str]] = None,
        deny: Optional[List[str]] = None,
        channel_id: Optional[int] = None,
        duration_seconds: Optional[int] = None,
        reason: str = "Game Permission Overwrite",
    ) -> Dict[str, Any]:
        """Sets permission overwrites for a user or role on the channel."""
        target_str = str(target).strip()
        is_everyone = target_str in ("@everyone", "0", "everyone")
        target_type = "ROLE" if is_everyone or (isinstance(target, str) and not target_str.isdigit()) else "USER"
        target_id = 0 if is_everyone else int(target)

        intent = {
            "op": "PERMISSION_OVERWRITE",
            "channel_id": channel_id or self._ctx.channel_id,
            "target_type": target_type,
            "target_id": target_id,
            "allow": list(allow or []),
            "deny": list(deny or []),
            "duration_seconds": duration_seconds,
            "reason": str(reason),
        }
        self._ctx.add_intent(intent)
        return intent

    def lock_channel(self, duration_seconds: int = 20, channel_id: Optional[int] = None) -> Dict[str, Any]:
        """Convenience helper to lock send_messages for @everyone."""
        return self.set(
            target=0,
            deny=["SEND_MESSAGES"],
            channel_id=channel_id,
            duration_seconds=duration_seconds,
            reason="Channel Lock",
        )
