from __future__ import annotations

import types
from typing import Any, Dict, List, Optional, Union

from .ai import AIContext
from .canvas import CanvasContext
from .discord import DiscordContext
from .economy import EconomyContext
from .http import HTTPContext
from .inventory import InventoryContext
from .lobby import LobbyContext
from .media import MediaContext
from .models import Args, Session, User
from .storage import StorageContext
from .ui import UIContext


class Context:
    """The GameContext passed into every Angela game event handler."""

    def __init__(self, raw_event: dict[str, Any]) -> None:
        self.raw_event: dict[str, Any] = raw_event
        self.event_type: str = str(raw_event.get("event_type", "COMMAND"))
        self.event_id: str = str(raw_event.get("event_id", ""))
        self.guild_id: int = int(raw_event.get("guild_id", 0))
        self.channel_id: int = int(raw_event.get("channel_id", 0))
        self.user: User = User.from_dict(raw_event.get("user"))
        self.args: Args = Args.from_dict(raw_event.get("args"))
        self.session: Session = Session.from_dict(raw_event.get("session"))

        self.status: str = self.session.status
        self.round: int = self.session.round
        self.state: dict[str, Any] = dict(self.session.state)

        # Config and secrets are read-only
        self.config: types.MappingProxyType[str, Any] = types.MappingProxyType(
            dict(raw_event.get("config", {}))
        )
        self.secrets: types.MappingProxyType[str, Any] = types.MappingProxyType(
            dict(raw_event.get("secrets", {}))
        )

        self._intents: List[Dict[str, Any]] = []

        # Sub-APIs
        self.economy: EconomyContext = EconomyContext(self)
        self.inventory: InventoryContext = InventoryContext(self)
        self.ui: UIContext = UIContext(self)
        self.canvas: CanvasContext = CanvasContext()
        self.lobby: LobbyContext = LobbyContext(self)
        self.ai: AIContext = AIContext(self)
        self.media: MediaContext = MediaContext(self)
        self.http: HTTPContext = HTTPContext(self)
        self.discord: DiscordContext = DiscordContext(self)
        self.storage: StorageContext = StorageContext(self)

    @property
    def host_id(self) -> int:
        """The creator / first participant of the session, or the triggering user."""
        if self.session.participants:
            return self.session.participants[0]
        return self.user.id

    def add_intent(self, intent: Dict[str, Any]) -> None:
        self._intents.append(intent)

    def finish(self) -> None:
        """Mark the session as FINISHED."""
        self.status = "FINISHED"

    def pause(self) -> None:
        """Mark the session as PAUSED."""
        self.status = "PAUSED"

    def next_round(self) -> int:
        """Increment round number and return the new round."""
        self.round += 1
        return self.round

    def schedule(self, delay_seconds: int, callback: str = "on_sleep_complete") -> Dict[str, Any]:
        """Explicitly schedule a wake event after a delay."""
        intent = {
            "op": "SCHEDULE_WAKE",
            "delay_seconds": int(delay_seconds),
            "callback_event_id": str(callback),
        }
        self.add_intent(intent)
        return intent

    def sleep(self, seconds: int, callback: str = "on_sleep_complete") -> Dict[str, Any]:
        """
        Sleep for a number of seconds.
        If seconds > 3, hibernates the session (status = SLEEPING) with SCHEDULE_WAKE.
        """
        if seconds > 3:
            self.status = "SLEEPING"
            return self.schedule(seconds, callback)
        return self.schedule(seconds, callback)

    def to_response(self) -> Dict[str, Any]:
        """Build the ABI JSON output contract."""
        return {
            "status": self.status,
            "round": self.round,
            "updated_state": self.state,
            "intents": self._intents,
        }


# Alias for convenience
GameContext = Context

