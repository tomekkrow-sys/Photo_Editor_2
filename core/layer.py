#!/usr/bin/env python3
"""
Photo Editor 2.0

Layer
"""

from __future__ import annotations

from enum import Enum
from typing import Callable
from uuid import UUID, uuid4

from PySide6.QtGui import QImage


class BlendMode(Enum):
    """Supported blend modes."""

    NORMAL = "normal"


class Layer:
    """Represents a single image layer with lazy loading support."""

    def __init__(
        self,
        name: str,
        image: QImage | None = None,
        image_loader: Callable[[], QImage] | None = None,
        visible: bool = True,
        opacity: float = 1.0,
        locked: bool = False,
        blend_mode: BlendMode = BlendMode.NORMAL,
        id: UUID | None = None,
    ) -> None:
        self.name = name
        self._image = image
        self.image_loader = image_loader
        self.visible = visible
        self.opacity = opacity
        self.locked = locked
        self.blend_mode = blend_mode
        self.id = id or uuid4()

    @property
    def image(self) -> QImage:
        if self._image is None and self.image_loader is not None:
            self._image = self.image_loader()
        return self._image

    @image.setter
    def image(self, img: QImage) -> None:
        self._image = img
