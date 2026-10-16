"""
Angela Python SDK — Developer kit for Angela Games Ecosystem cartridges.
"""

from .canvas import CanvasLayer, CanvasScene
from .context import Context, GameContext
from .game import Game, dispatch
from .models import Args, Session, User
from .ui import (
    ActionRow,
    Button,
    Container,
    Embed,
    MediaGallery,
    Section,
    Select,
    SelectOption,
    Separator,
    TextDisplay,
    TextInput,
    Thumbnail,
)

__version__ = "0.1.0"

__all__ = [
    "ActionRow",
    "Args",
    "Button",
    "CanvasLayer",
    "CanvasScene",
    "Container",
    "Context",
    "Embed",
    "Game",
    "GameContext",
    "MediaGallery",
    "Section",
    "Select",
    "SelectOption",
    "Separator",
    "Session",
    "TextDisplay",
    "TextInput",
    "Thumbnail",
    "User",
    "__version__",
    "dispatch",
]

