#!/usr/bin/env python3
"""
Photo Editor 2.0

Image Document

Version: 0.2.0
"""

from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

from PySide6.QtGui import QImage

from core.layer_stack import LayerStack
from core.renderer import Renderer


class ImageDocument:
    """
    Represents one opened image.
    """

    def __init__(self) -> None:

        self.id: UUID = uuid4()
        self.layer_stack: LayerStack = LayerStack()

        self.clear()

    @property
    def is_loaded(self) -> bool:
        return self.image is not None

    def clear(self) -> None:

        self.file_path: Path | None = None
        self.file_name: str = ""

        self.image: QImage | None = None
        self.original_image: QImage | None = None

        self.modified: bool = False

        self.layer_stack.clear()

        self.zoom: float = 100.0

        self.format: str = ""

        self.width: int = 0
        self.height: int = 0

    def load(
        self,
        image: QImage,
        file_path: Path,
    ) -> None:

        self.image = image
        self.layer_stack.add_background(image)
        self.original_image = image.copy()

        self.file_path = file_path
        self.file_name = file_path.name

        self.width = image.width()
        self.height = image.height()

        self.format = file_path.suffix.lower().replace(".", "")

        self.zoom = 100.0

        self.modified = False

    @property
    def rendered_image(self) -> QImage | None:
        """Return the rendered document image."""

        return Renderer.render(self.layer_stack)


    @property
    def active_image(self) -> QImage | None:
        """Return the image of the active layer."""

        layer = self.layer_stack.active_layer

        if layer is None:
            return None

        return layer.image


    def set_active_image(self, image: QImage) -> None:
        """
        Replace the image of the active layer and keep the document
        state synchronized.
        """

        layer = self.layer_stack.active_layer

        if layer is None:
            return

        layer.image = image
        self.image = image

        self.width = image.width()
        self.height = image.height()

        self.modified = True
