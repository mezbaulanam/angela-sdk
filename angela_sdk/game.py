from __future__ import annotations

import asyncio
import inspect
import json
from typing import Any, Callable, Dict, Optional, Union

from .context import Context


HandlerFunc = Callable[..., Any]


class Game:
    """The central game application and event router for an Angela cartridge."""

    def __init__(self, name: str = "angela_game") -> None:
        self.name = name
        self._command_handlers: Dict[Optional[str], HandlerFunc] = {}
        self._button_handlers: Dict[str, HandlerFunc] = {}
        self._select_handlers: Dict[str, HandlerFunc] = {}
        self._modal_handlers: Dict[str, HandlerFunc] = {}
        self._message_handlers: list[HandlerFunc] = []
        self._timer_wake_handlers: Dict[str, HandlerFunc] = {}
        self._callback_handlers: Dict[str, HandlerFunc] = {}
        self._default_handler: Optional[HandlerFunc] = None

    def on_command(self, subcommand: Optional[str] = None) -> Callable[[HandlerFunc], HandlerFunc]:
        def decorator(func: HandlerFunc) -> HandlerFunc:
            self._command_handlers[subcommand] = func
            return func
        return decorator

    def on_button(self, custom_id: str) -> Callable[[HandlerFunc], HandlerFunc]:
        def decorator(func: HandlerFunc) -> HandlerFunc:
            self._button_handlers[custom_id] = func
            return func
        return decorator

    def on_select(self, custom_id: str) -> Callable[[HandlerFunc], HandlerFunc]:
        def decorator(func: HandlerFunc) -> HandlerFunc:
            self._select_handlers[custom_id] = func
            return func
        return decorator

    def on_modal(self, callback_id: str) -> Callable[[HandlerFunc], HandlerFunc]:
        def decorator(func: HandlerFunc) -> HandlerFunc:
            self._modal_handlers[callback_id] = func
            return func
        return decorator

    def on_message(self, func: HandlerFunc) -> HandlerFunc:
        self._message_handlers.append(func)
        return func

    def on_wake(self, callback_event_id: str = "on_sleep_complete") -> Callable[[HandlerFunc], HandlerFunc]:
        def decorator(func: HandlerFunc) -> HandlerFunc:
            self._timer_wake_handlers[callback_event_id] = func
            return func
        return decorator

    def on_callback(self, callback_event_id: str) -> Callable[[HandlerFunc], HandlerFunc]:
        def decorator(func: HandlerFunc) -> HandlerFunc:
            self._callback_handlers[callback_event_id] = func
            return func
        return decorator

    def default(self, func: HandlerFunc) -> HandlerFunc:
        self._default_handler = func
        return func

    def handle(self, event: Union[dict[str, Any], str, Context]) -> dict[str, Any]:
        """Dispatch an incoming event to the matching registered handler and return the ABI response."""
        if isinstance(event, str):
            event_dict = json.loads(event)
            ctx = Context(event_dict)
        elif isinstance(event, dict):
            ctx = Context(event)
        elif isinstance(event, Context):
            ctx = event
        else:
            raise TypeError(f"Expected dict, str, or Context, got {type(event)}")

        handler: Optional[HandlerFunc] = None
        event_type = ctx.event_type.upper()
        event_id = ctx.event_id

        if event_type == "COMMAND":
            sub = ctx.args.subcommand
            handler = self._command_handlers.get(sub) or self._command_handlers.get(None)
        elif event_type == "BUTTON":
            handler = self._button_handlers.get(event_id)
        elif event_type == "SELECT":
            handler = self._select_handlers.get(event_id)
        elif event_type == "MODAL":
            handler = self._modal_handlers.get(event_id)
        elif event_type == "MESSAGE":
            handler = self._message_handlers[0] if self._message_handlers else None
        elif event_type == "TIMER_WAKE":
            handler = self._timer_wake_handlers.get(event_id) or self._timer_wake_handlers.get("on_sleep_complete")
        elif event_type == "CALLBACK":
            handler = self._callback_handlers.get(event_id)

        if handler is None:
            handler = self._default_handler

        if handler is not None:
            sig = inspect.signature(handler)
            if len(sig.parameters) == 0:
                res = handler()
            else:
                res = handler(ctx)
            if inspect.iscoroutine(res):
                # If handler is an async function, run it synchronously
                asyncio.run(res)

        return ctx.to_response()


def dispatch(handler: Callable[..., Any], event: Union[dict[str, Any], str, Context]) -> dict[str, Any]:
    """
    Universal dispatch helper.
    Wraps the incoming event in a Context if needed, calls handler, and returns the ABI response.
    """
    if isinstance(event, str):
        event_dict = json.loads(event)
        ctx = Context(event_dict)
    elif isinstance(event, dict):
        ctx = Context(event)
    elif isinstance(event, Context):
        ctx = event
    else:
        raise TypeError(f"Expected dict, str, or Context, got {type(event)}")

    sig = inspect.signature(handler)
    first_param = next(iter(sig.parameters.values()), None) if sig.parameters else None

    # Check if handler expects raw dict or Context
    if first_param is not None and first_param.name in {"event", "raw_event", "e"}:
        res = handler(ctx.raw_event)
    else:
        res = handler(ctx)

    if inspect.iscoroutine(res):
        res = asyncio.run(res)

    if isinstance(res, dict) and "status" in res and "intents" in res:
        return res

    return ctx.to_response()

