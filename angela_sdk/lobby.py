from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from .context import Context


class LobbyContext:
    def __init__(self, ctx: Context) -> None:
        self._ctx = ctx

    def create_join_lobby(
        self,
        max_players: int = 25,
        duration: int = 120,
        on_start: str = "on_lobby_start",
    ) -> Dict[str, Any]:
        intent = {
            "op": "LOBBY_OP",
            "action": "CREATE_JOIN_LOBBY",
            "max_players": int(max_players),
            "duration": int(duration),
            "callback_event_id": on_start,
        }
        self._ctx.add_intent(intent)
        return intent

    def create_duo_invite(
        self,
        partner_id: int,
        entry_fee: int = 10,
        loadout_shop: Optional[List[Dict[str, Any]]] = None,
        on_accept: str = "on_invite_accept",
    ) -> Dict[str, Any]:
        intent: Dict[str, Any] = {
            "op": "LOBBY_OP",
            "action": "CREATE_DUO_INVITE",
            "partner_id": int(partner_id),
            "entry_fee": int(entry_fee),
            "callback_event_id": on_accept,
        }
        if loadout_shop is not None:
            intent["loadout_shop"] = loadout_shop
        self._ctx.add_intent(intent)
        return intent

    def exclusive_claim_grid(
        self,
        count: int,
        eligible_users: List[int],
        timeout: int = 20,
        on_resolve: str = "on_claim_resolve",
    ) -> Dict[str, Any]:
        intent = {
            "op": "LOBBY_OP",
            "action": "EXCLUSIVE_CLAIM_GRID",
            "count": int(count),
            "eligible_users": [int(u) for u in eligible_users],
            "timeout": int(timeout),
            "callback_event_id": on_resolve,
        }
        self._ctx.add_intent(intent)
        return intent

