from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class User:
    id: int
    name: str = ""
    avatar_url: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> User:
        if not data:
            return cls(id=0)
        return cls(
            id=int(data.get("id", 0)),
            name=str(data.get("name", "")),
            avatar_url=str(data.get("avatar_url", "")),
        )


@dataclass
class Args:
    subcommand: Optional[str] = None
    raw_args: Optional[str] = None
    target_user_id: Optional[int] = None
    modal_inputs: Dict[str, str] = field(default_factory=dict)
    select_values: List[str] = field(default_factory=list)
    message_content: Optional[str] = None
    callback_data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> Args:
        if not data:
            return cls()
        return cls(
            subcommand=data.get("subcommand"),
            raw_args=data.get("raw_args"),
            target_user_id=int(data["target_user_id"]) if data.get("target_user_id") is not None else None,
            modal_inputs=dict(data.get("modal_inputs", {})),
            select_values=list(data.get("select_values", [])),
            message_content=data.get("message_content"),
            callback_data=dict(data.get("callback_data", {})),
        )


@dataclass
class Session:
    session_id: str = ""
    round: int = 1
    participants: List[int] = field(default_factory=list)
    status: str = "ACTIVE"
    state: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> Session:
        if not data:
            return cls()
        return cls(
            session_id=str(data.get("session_id", "")),
            round=int(data.get("round", 1)),
            participants=[int(p) for p in data.get("participants", [])],
            status=str(data.get("status", "ACTIVE")),
            state=dict(data.get("state", {})),
        )

