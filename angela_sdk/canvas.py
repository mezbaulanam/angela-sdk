from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Union


class CanvasLayer:
    def __init__(self, layer_id: str, cache_key: Optional[str] = None) -> None:
        self.id = layer_id
        self.cache_key = cache_key
        self.ops: List[Dict[str, Any]] = []

    def linear_gradient(
        self,
        rect: List[int],
        start_rgb: List[int],
        end_rgb: List[int],
        gamma: float = 1.0,
    ) -> CanvasLayer:
        self.ops.append({
            "type": "linear_gradient",
            "rect": list(rect),
            "start_rgb": list(start_rgb),
            "end_rgb": list(end_rgb),
            "gamma": float(gamma),
        })
        return self

    def celestial_body(
        self,
        x: int,
        y: int,
        radius: int,
        glow_radius: int,
        color: List[int],
        glow_color: List[int],
    ) -> CanvasLayer:
        self.ops.append({
            "type": "celestial_body",
            "x": int(x),
            "y": int(y),
            "radius": int(radius),
            "glow_radius": int(glow_radius),
            "color": list(color),
            "glow_color": list(glow_color),
        })
        return self

    def sine_waves(
        self,
        y_start: int,
        y_end: int,
        count: int,
        color: List[int],
    ) -> CanvasLayer:
        self.ops.append({
            "type": "sine_waves",
            "y_start": int(y_start),
            "y_end": int(y_end),
            "count": int(count),
            "color": list(color),
        })
        return self

    def procedural_palm(
        self,
        x: int,
        y_bottom: int,
        y_top: int,
        seed: int = 0,
    ) -> CanvasLayer:
        self.ops.append({
            "type": "procedural_palm",
            "x": int(x),
            "y_bottom": int(y_bottom),
            "y_top": int(y_top),
            "seed": int(seed),
        })
        return self

    def vignette(self, depth: int, intensity: float) -> CanvasLayer:
        self.ops.append({
            "type": "vignette",
            "depth": int(depth),
            "intensity": float(intensity),
        })
        return self

    def radial_glow(
        self,
        x: int,
        y: int,
        radius: int,
        color: List[int],
        max_alpha: int = 255,
    ) -> CanvasLayer:
        self.ops.append({
            "type": "radial_glow",
            "x": int(x),
            "y": int(y),
            "radius": int(radius),
            "color": list(color),
            "max_alpha": int(max_alpha),
        })
        return self

    def sprite(
        self,
        asset_key: str,
        x: int,
        y: int,
        max_w: Optional[int] = None,
        max_h: Optional[int] = None,
        anchor: str = "center",
        flip_x: bool = False,
        rotation: int = 0,
    ) -> CanvasLayer:
        op: Dict[str, Any] = {
            "type": "sprite",
            "asset_key": str(asset_key),
            "x": int(x),
            "y": int(y),
            "anchor": anchor,
            "flip_x": flip_x,
            "rotation": int(rotation),
        }
        if max_w is not None:
            op["max_w"] = int(max_w)
        if max_h is not None:
            op["max_h"] = int(max_h)
        self.ops.append(op)
        return self

    def avatar(
        self,
        user_id: int,
        x: int,
        y: int,
        size: int = 80,
        circular: bool = True,
        border_color: Optional[List[int]] = None,
        border_width: int = 0,
    ) -> CanvasLayer:
        op: Dict[str, Any] = {
            "type": "avatar",
            "user_id": int(user_id),
            "x": int(x),
            "y": int(y),
            "size": int(size),
            "circular": circular,
            "border_width": int(border_width),
        }
        if border_color is not None:
            op["border_color"] = list(border_color)
        self.ops.append(op)
        return self

    def polygon(
        self,
        points: List[List[int]],
        fill: Optional[List[int]] = None,
        outline: Optional[List[int]] = None,
    ) -> CanvasLayer:
        op: Dict[str, Any] = {
            "type": "polygon",
            "points": [list(p) for p in points],
        }
        if fill is not None:
            op["fill"] = list(fill)
        if outline is not None:
            op["outline"] = list(outline)
        self.ops.append(op)
        return self

    def line(
        self,
        points: List[List[int]],
        color: List[int],
        width: int = 1,
    ) -> CanvasLayer:
        self.ops.append({
            "type": "line",
            "points": [list(p) for p in points],
            "color": list(color),
            "width": int(width),
        })
        return self

    def arc(
        self,
        bbox: List[int],
        start_deg: int,
        end_deg: int,
        color: List[int],
        width: int = 1,
    ) -> CanvasLayer:
        self.ops.append({
            "type": "arc",
            "bbox": list(bbox),
            "start_deg": int(start_deg),
            "end_deg": int(end_deg),
            "color": list(color),
            "width": int(width),
        })
        return self

    def rounded_rect(
        self,
        rect: List[int],
        radius: int,
        fill: Optional[List[int]] = None,
        outline: Optional[List[int]] = None,
        width: int = 1,
    ) -> CanvasLayer:
        op: Dict[str, Any] = {
            "type": "rounded_rect",
            "rect": list(rect),
            "radius": int(radius),
            "width": int(width),
        }
        if fill is not None:
            op["fill"] = list(fill)
        if outline is not None:
            op["outline"] = list(outline)
        self.ops.append(op)
        return self

    def progress_bar(
        self,
        rect: List[int],
        value: float,
        max_value: float,
        bg_color: List[int],
        fill_color: List[int],
        radius: int = 0,
    ) -> CanvasLayer:
        self.ops.append({
            "type": "progress_bar",
            "rect": list(rect),
            "value": float(value),
            "max_value": float(max_value),
            "bg_color": list(bg_color),
            "fill_color": list(fill_color),
            "radius": int(radius),
        })
        return self

    def text_box(
        self,
        rect: List[int],
        text: str,
        font: str = "regular",
        size: int = 13,
        color: Optional[List[int]] = None,
        max_lines: int = 1,
        line_height: Optional[int] = None,
    ) -> CanvasLayer:
        op: Dict[str, Any] = {
            "type": "text_box",
            "rect": list(rect),
            "text": str(text),
            "font": font,
            "size": int(size),
            "color": list(color or [255, 255, 255]),
            "max_lines": int(max_lines),
        }
        if line_height is not None:
            op["line_height"] = int(line_height)
        self.ops.append(op)
        return self

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "id": self.id,
            "ops": self.ops,
        }
        if self.cache_key:
            data["cache_key"] = self.cache_key
        return data


class CanvasScene:
    def __init__(
        self,
        width: int = 640,
        height: int = 360,
        animated: bool = False,
        frame_duration_ms: int = 80,
        filename: str = "scene.png",
    ) -> None:
        self.width = min(int(width), 1280)
        self.height = min(int(height), 720)
        self.animated = animated
        self.frame_duration_ms = frame_duration_ms
        self.filename = filename
        self.layers: List[CanvasLayer] = []

    def layer(self, layer_id: str, cache_key: Optional[str] = None) -> CanvasLayer:
        lyr = CanvasLayer(layer_id, cache_key=cache_key)
        self.layers.append(lyr)
        return lyr

    def to_dict(self) -> Dict[str, Any]:
        return {
            "width": self.width,
            "height": self.height,
            "animated": self.animated,
            "frame_duration_ms": self.frame_duration_ms,
            "filename": self.filename,
            "layers": [lyr.to_dict() for lyr in self.layers],
        }


class CanvasContext:
    def create(
        self,
        width: int = 640,
        height: int = 360,
        animated: bool = False,
        frame_duration_ms: int = 80,
        filename: str = "scene.png",
    ) -> CanvasScene:
        return CanvasScene(
            width=width,
            height=height,
            animated=animated,
            frame_duration_ms=frame_duration_ms,
            filename=filename,
        )

