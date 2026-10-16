from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from .context import Context


class EconomyContext:
    """Server economy operations.

    Every method accepts an optional ``currency`` argument.  When omitted
    (or ``None``), the host uses whichever currency the server admin
    configured for the game slot — so the same game works across servers
    with different currencies without code changes.  Pass an explicit
    currency name only when a game genuinely needs to target a specific
    currency (e.g. a multi-currency trading game).
    """

    def __init__(self, ctx: Context) -> None:
        self._ctx = ctx

    @staticmethod
    def _apply_currency(intent: Dict[str, Any], currency: Optional[str]) -> None:
        if currency is not None:
            intent["currency"] = str(currency)

    def get_balance(self, user_id: int, *, currency: Optional[str] = None) -> Dict[str, Any]:
        intent = {
            "op": "ECONOMY_MUTATE",
            "action": "GET_BALANCE",
            "user_id": int(user_id),
        }
        self._apply_currency(intent, currency)
        self._ctx.add_intent(intent)
        return intent

    def take(
        self,
        user_id: int,
        amount: int,
        reason: str = "",
        *,
        currency: Optional[str] = None,
    ) -> Dict[str, Any]:
        intent = {
            "op": "ECONOMY_MUTATE",
            "action": "TAKE",
            "user_id": int(user_id),
            "amount": int(amount),
            "reason": reason,
        }
        self._apply_currency(intent, currency)
        self._ctx.add_intent(intent)
        return intent

    def give(
        self,
        user_id: int,
        amount: int,
        reason: str = "",
        clamp_min: Optional[int] = None,
        clamp_max: Optional[int] = None,
        *,
        currency: Optional[str] = None,
    ) -> Dict[str, Any]:
        intent: Dict[str, Any] = {
            "op": "ECONOMY_MUTATE",
            "action": "GIVE",
            "user_id": int(user_id),
            "amount": int(amount),
            "reason": reason,
        }
        if clamp_min is not None:
            intent["clamp_min"] = int(clamp_min)
        if clamp_max is not None:
            intent["clamp_max"] = int(clamp_max)
        self._apply_currency(intent, currency)
        self._ctx.add_intent(intent)
        return intent

    def escrow_lock(
        self,
        user_id: int,
        amount: int,
        reason: str = "",
        *,
        currency: Optional[str] = None,
    ) -> Dict[str, Any]:
        intent = {
            "op": "ECONOMY_MUTATE",
            "action": "ESCROW_LOCK",
            "user_id": int(user_id),
            "amount": int(amount),
            "reason": reason,
        }
        self._apply_currency(intent, currency)
        self._ctx.add_intent(intent)
        return intent

    def escrow_release(
        self,
        user_id: int,
        amount: int,
        reason: str = "",
        *,
        currency: Optional[str] = None,
    ) -> Dict[str, Any]:
        intent = {
            "op": "ECONOMY_MUTATE",
            "action": "ESCROW_RELEASE",
            "user_id": int(user_id),
            "amount": int(amount),
            "reason": reason,
        }
        self._apply_currency(intent, currency)
        self._ctx.add_intent(intent)
        return intent

    def escrow_refund(
        self,
        user_id: int,
        amount: int,
        reason: str = "",
        *,
        currency: Optional[str] = None,
    ) -> Dict[str, Any]:
        intent = {
            "op": "ECONOMY_MUTATE",
            "action": "ESCROW_REFUND",
            "user_id": int(user_id),
            "amount": int(amount),
            "reason": reason,
        }
        self._apply_currency(intent, currency)
        self._ctx.add_intent(intent)
        return intent

    def auto_buy(self, user_id: int, item_ids: List[str], quantity: int = 10) -> Dict[str, Any]:
        intent = {
            "op": "ECONOMY_MUTATE",
            "action": "AUTO_BUY",
            "user_id": int(user_id),
            "item_ids": list(item_ids),
            "quantity": int(quantity),
        }
        self._ctx.add_intent(intent)
        return intent

