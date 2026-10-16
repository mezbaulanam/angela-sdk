from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from .context import Context


class InventoryContext:
    def __init__(self, ctx: Context) -> None:
        self._ctx = ctx

    def get_server_items(self, user_id: int) -> Dict[str, Any]:
        intent = {
            "op": "INVENTORY_MUTATE",
            "action": "GET_SERVER_ITEMS",
            "user_id": int(user_id),
        }
        self._ctx.add_intent(intent)
        return intent

    def consume_server_item(self, user_id: int, item_id: str, qty: int = 1) -> Dict[str, Any]:
        intent = {
            "op": "INVENTORY_MUTATE",
            "action": "CONSUME_SERVER_ITEM",
            "user_id": int(user_id),
            "item_id": str(item_id),
            "quantity": int(qty),
        }
        self._ctx.add_intent(intent)
        return intent

    def give_server_item(self, user_id: int, item_id: str, qty: int = 1) -> Dict[str, Any]:
        intent = {
            "op": "INVENTORY_MUTATE",
            "action": "GIVE_SERVER_ITEM",
            "user_id": int(user_id),
            "item_id": str(item_id),
            "quantity": int(qty),
        }
        self._ctx.add_intent(intent)
        return intent

    def roll_break(self, user_id: int, item_id: str, probability: float) -> Dict[str, Any]:
        intent = {
            "op": "INVENTORY_MUTATE",
            "action": "ROLL_BREAK",
            "user_id": int(user_id),
            "item_id": str(item_id),
            "break_chance": float(probability),
        }
        self._ctx.add_intent(intent)
        return intent

    def add_sub_item(self, user_id: int, item_id: str, qty: int = 1) -> Dict[str, Any]:
        intent = {
            "op": "INVENTORY_MUTATE",
            "action": "ADD_SUB_ITEM",
            "user_id": int(user_id),
            "item_id": str(item_id),
            "quantity": int(qty),
        }
        self._ctx.add_intent(intent)
        return intent

    def remove_sub_item(self, user_id: int, item_id: str, qty: int = 1) -> Dict[str, Any]:
        intent = {
            "op": "INVENTORY_MUTATE",
            "action": "REMOVE_SUB_ITEM",
            "user_id": int(user_id),
            "item_id": str(item_id),
            "quantity": int(qty),
        }
        self._ctx.add_intent(intent)
        return intent

