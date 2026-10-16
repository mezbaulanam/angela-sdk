from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

if TYPE_CHECKING:
    from .canvas import CanvasScene
    from .context import Context


class Button:
    def __init__(
        self,
        custom_id: str,
        label: str = "",
        style: str = "primary",
        emoji: Optional[str] = None,
        disabled: bool = False,
        url: Optional[str] = None,
    ) -> None:
        self.custom_id = custom_id
        self.label = label
        self.style = style.lower()
        self.emoji = emoji
        self.disabled = disabled
        self.url = url

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "type": 2,
            "custom_id": self.custom_id,
            "label": self.label,
            "style": self.style,
            "disabled": self.disabled,
        }
        if self.emoji:
            data["emoji"] = self.emoji
        if self.url:
            data["url"] = self.url
        return data


class SelectOption:
    def __init__(
        self,
        label: str,
        value: str,
        description: Optional[str] = None,
        emoji: Optional[str] = None,
        default: bool = False,
    ) -> None:
        self.label = label
        self.value = value
        self.description = description
        self.emoji = emoji
        self.default = default

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "label": self.label,
            "value": self.value,
            "default": self.default,
        }
        if self.description:
            data["description"] = self.description
        if self.emoji:
            data["emoji"] = self.emoji
        return data


class Select:
    def __init__(
        self,
        custom_id: str,
        options: List[Union[SelectOption, Dict[str, Any]]],
        placeholder: Optional[str] = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
    ) -> None:
        self.custom_id = custom_id
        self.options = options
        self.placeholder = placeholder
        self.min_values = min_values
        self.max_values = max_values
        self.disabled = disabled

    def to_dict(self) -> Dict[str, Any]:
        serialized_options = [
            opt.to_dict() if isinstance(opt, SelectOption) else opt for opt in self.options
        ]
        data: Dict[str, Any] = {
            "type": 3,
            "custom_id": self.custom_id,
            "options": serialized_options,
            "min_values": self.min_values,
            "max_values": self.max_values,
            "disabled": self.disabled,
        }
        if self.placeholder:
            data["placeholder"] = self.placeholder
        return data


class TextInput:
    def __init__(
        self,
        custom_id: str,
        label: str,
        placeholder: Optional[str] = None,
        default: Optional[str] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        required: bool = True,
        style: str = "short",
    ) -> None:
        self.custom_id = custom_id
        self.label = label
        self.placeholder = placeholder
        self.default = default
        self.min_length = min_length
        self.max_length = max_length
        self.required = required
        self.style = style

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "type": 4,
            "custom_id": self.custom_id,
            "label": self.label,
            "required": self.required,
            "style": self.style,
        }
        if self.placeholder:
            data["placeholder"] = self.placeholder
        if self.default:
            data["value"] = self.default
        if self.min_length is not None:
            data["min_length"] = self.min_length
        if self.max_length is not None:
            data["max_length"] = self.max_length
        return data


class TextDisplay:
    def __init__(self, content: str) -> None:
        self.content = content

    def to_dict(self) -> Dict[str, Any]:
        return {"type": 10, "content": self.content}


class Thumbnail:
    def __init__(self, url: str) -> None:
        self.url = url

    def to_dict(self) -> Dict[str, Any]:
        return {"type": 11, "url": self.url}


class MediaGallery:
    def __init__(self, items: Union[str, List[str]]) -> None:
        self.items = [items] if isinstance(items, str) else list(items)

    def to_dict(self) -> Dict[str, Any]:
        return {"type": 12, "items": [{"url": it} for it in self.items]}


class Separator:
    def __init__(self, divider: bool = True, spacing: int = 1) -> None:
        self.divider = divider
        self.spacing = spacing

    def to_dict(self) -> Dict[str, Any]:
        return {"type": 14, "divider": self.divider, "spacing": self.spacing}


class ActionRow:
    def __init__(self, components: Optional[List[Union[Button, Select, Dict[str, Any]]]] = None) -> None:
        self.components = components or []

    def to_dict(self) -> Dict[str, Any]:
        serialized = []
        for c in self.components:
            if hasattr(c, "to_dict"):
                serialized.append(c.to_dict())
            else:
                serialized.append(c)
        return {"type": 1, "components": serialized}


class Section:
    def __init__(
        self,
        text_displays: Optional[List[Union[TextDisplay, str]]] = None,
        accessory: Optional[Union[Thumbnail, Button, Dict[str, Any]]] = None,
    ) -> None:
        self.text_displays = text_displays or []
        self.accessory = accessory

    def to_dict(self) -> Dict[str, Any]:
        texts = []
        for t in self.text_displays:
            if isinstance(t, str):
                texts.append({"type": 10, "content": t})
            elif hasattr(t, "to_dict"):
                texts.append(t.to_dict())
            else:
                texts.append(t)
        data: Dict[str, Any] = {"type": 9, "components": texts}
        if self.accessory:
            data["accessory"] = (
                self.accessory.to_dict() if hasattr(self.accessory, "to_dict") else self.accessory
            )
        return data


class Container:
    def __init__(
        self,
        accent_color: Optional[Union[int, str]] = None,
        components: Optional[List[Any]] = None,
    ) -> None:
        self.accent_color = accent_color
        self.components = components or []

    def add(self, component: Any) -> Container:
        self.components.append(component)
        return self

    def to_dict(self) -> Dict[str, Any]:
        serialized = []
        for c in self.components:
            if hasattr(c, "to_dict"):
                serialized.append(c.to_dict())
            else:
                serialized.append(c)
        data: Dict[str, Any] = {"type": 17, "components": serialized}
        if self.accent_color is not None:
            if isinstance(self.accent_color, str) and self.accent_color.startswith("#"):
                data["accent_color"] = int(self.accent_color.lstrip("#"), 16)
            else:
                data["accent_color"] = int(self.accent_color)
        return data


class Embed:
    def __init__(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        color: Optional[Union[int, str]] = None,
        fields: Optional[List[Dict[str, Any]]] = None,
        footer: Optional[Dict[str, str]] = None,
        thumbnail: Optional[str] = None,
        image: Optional[str] = None,
    ) -> None:
        self.title = title
        self.description = description
        self.color = color
        self.fields = fields or []
        self.footer = footer
        self.thumbnail = thumbnail
        self.image = image

    def add_field(self, name: str, value: str, inline: bool = False) -> Embed:
        self.fields.append({"name": name, "value": value, "inline": inline})
        return self

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        if self.title:
            data["title"] = self.title
        if self.description:
            data["description"] = self.description
        if self.color is not None:
            if isinstance(self.color, str) and self.color.startswith("#"):
                data["color"] = int(self.color.lstrip("#"), 16)
            else:
                data["color"] = int(self.color)
        if self.fields:
            data["fields"] = self.fields
        if self.footer:
            data["footer"] = self.footer
        if self.thumbnail:
            data["thumbnail"] = {"url": self.thumbnail}
        if self.image:
            data["image"] = {"url": self.image}
        return data


class UIContext:
    def __init__(self, ctx: Context) -> None:
        self._ctx = ctx

    def render(
        self,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        body_lines: Optional[Union[List[str], str]] = None,
        image: Optional[Union[str, CanvasScene]] = None,
        thumbnail: Optional[str] = None,
        buttons: Optional[List[Union[Button, Dict[str, Any]]]] = None,
        selects: Optional[List[Union[Select, Dict[str, Any]]]] = None,
        accent_color: Optional[Union[int, str]] = None,
        ephemeral: bool = False,
        target: str = "EDIT_MAIN",
        mode: str = "AUTO",
    ) -> Dict[str, Any]:
        layout: Dict[str, Any] = {}
        if title:
            layout["title"] = title
        if subtitle:
            layout["subtitle"] = subtitle
        if body_lines:
            layout["body_lines"] = (
                [body_lines] if isinstance(body_lines, str) else list(body_lines)
            )
        if thumbnail:
            layout["thumbnail"] = thumbnail
        if accent_color is not None:
            if isinstance(accent_color, str) and accent_color.startswith("#"):
                layout["accent_color"] = int(accent_color.lstrip("#"), 16)
            else:
                layout["accent_color"] = int(accent_color)
        if buttons:
            layout["buttons"] = [b.to_dict() if hasattr(b, "to_dict") else b for b in buttons]
        if selects:
            layout["selects"] = [s.to_dict() if hasattr(s, "to_dict") else s for s in selects]

        canvas_scene_payload = None
        if image is not None:
            if hasattr(image, "to_dict"):
                canvas_scene_payload = image.to_dict()
                layout["image"] = f"attachment://{image.filename}"
            else:
                layout["image"] = str(image)

        intent: Dict[str, Any] = {
            "op": "UI_RENDER",
            "target": target,
            "ephemeral": ephemeral,
            "mode": mode,
            "layout": layout,
        }
        if canvas_scene_payload:
            intent["canvas_scene"] = canvas_scene_payload

        self._ctx.add_intent(intent)
        return intent

    def render_cv2(
        self,
        container: Union[Container, Dict[str, Any]],
        ephemeral: bool = False,
        target: str = "EDIT_MAIN",
        canvas_scene: Optional[Union[CanvasScene, Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        layout = container.to_dict() if hasattr(container, "to_dict") else container
        intent: Dict[str, Any] = {
            "op": "UI_RENDER",
            "target": target,
            "ephemeral": ephemeral,
            "mode": "CV2",
            "layout": layout,
        }
        if canvas_scene:
            intent["canvas_scene"] = (
                canvas_scene.to_dict() if hasattr(canvas_scene, "to_dict") else canvas_scene
            )
        self._ctx.add_intent(intent)
        return intent

    def render_embed(
        self,
        embed: Union[Embed, Dict[str, Any]],
        components: Optional[List[Any]] = None,
        ephemeral: bool = False,
        target: str = "EDIT_MAIN",
        canvas_scene: Optional[Union[CanvasScene, Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        layout: Dict[str, Any] = {
            "embed": embed.to_dict() if hasattr(embed, "to_dict") else embed,
        }
        if components:
            serialized_comps = []
            for c in components:
                serialized_comps.append(c.to_dict() if hasattr(c, "to_dict") else c)
            layout["components"] = serialized_comps

        intent: Dict[str, Any] = {
            "op": "UI_RENDER",
            "target": target,
            "ephemeral": ephemeral,
            "mode": "CLASSIC_EMBED",
            "layout": layout,
        }
        if canvas_scene:
            intent["canvas_scene"] = (
                canvas_scene.to_dict() if hasattr(canvas_scene, "to_dict") else canvas_scene
            )
        self._ctx.add_intent(intent)
        return intent

    def reply_ephemeral(
        self,
        text: Optional[str] = None,
        embed: Optional[Union[Embed, Dict[str, Any]]] = None,
        container: Optional[Union[Container, Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        if container:
            return self.render_cv2(container, ephemeral=True, target="REPLY_EPHEMERAL")
        if embed:
            return self.render_embed(embed, ephemeral=True, target="REPLY_EPHEMERAL")
        return self.render(body_lines=[text or ""], ephemeral=True, target="REPLY_EPHEMERAL")

    def open_modal(
        self,
        title: str,
        inputs: List[Union[TextInput, Dict[str, Any]]],
        callback_id: str,
    ) -> Dict[str, Any]:
        serialized_inputs = [
            inp.to_dict() if hasattr(inp, "to_dict") else inp for inp in inputs
        ]
        intent = {
            "op": "UI_MODAL",
            "title": title,
            "callback_id": callback_id,
            "inputs": serialized_inputs,
        }
        self._ctx.add_intent(intent)
        return intent

