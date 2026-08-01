#!/usr/bin/env python3
"""Photo Editor 2.0 — Image Document model."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage

from core.layer import Layer
from core.layer_stack import LayerStack
from core.renderer import Renderer

from .develop_settings import DevelopSettings


class ImageDocument:
    """
    Represents one opened image with layers, metadata and develop settings.
    """

    def __init__(self) -> None:
        self.id: UUID = uuid4()
        self.layer_stack: LayerStack = LayerStack()
        self.develop_settings: DevelopSettings = DevelopSettings()
        self.clear()

    @property
    def is_loaded(self) -> bool:
        return self.active_image is not None

    def clear(self) -> None:
        self.file_path: Path | None = None
        self.file_name: str = ""
        self.original_image: QImage | None = None
        self.modified: bool = False
        self.zoom: float = 100.0
        self.format: str = ""
        self.width: int = 0
        self.height: int = 0
        self.layer_stack.clear()
        self.develop_settings.reset()

    def load(self, image: QImage, file_path: Path) -> None:
        """Load an image into the document."""
        self.layer_stack.add_background(image)
        self.original_image = image.copy()
        self.file_path = file_path
        self.file_name = file_path.name
        self.width = image.width()
        self.height = image.height()
        self.format = file_path.suffix.lower().replace(".", "")
        self.zoom = 100.0
        self.modified = False

    def create(
        self,
        width: int,
        height: int,
        transparent: bool = False,
    ) -> None:
        """Create a new empty document."""
        self.clear()
        image = QImage(width, height, QImage.Format.Format_ARGB32)
        if transparent:
            image.fill(Qt.GlobalColor.transparent)
        else:
            image.fill(QColor("white"))
        self.layer_stack.add_background(image)
        self.original_image = image.copy()
        self.width = width
        self.height = height
        self.zoom = 100.0
        self.modified = False

    def add_layer(self, name: str | None = None) -> None:
        """Add a new transparent layer."""
        image = QImage(
            self.width,
            self.height,
            QImage.Format.Format_ARGB32,
        )
        image.fill(Qt.GlobalColor.transparent)
        if name is None:
            name = f"Layer {len(self.layer_stack.layers)}"
        self.layer_stack.add_layer(Layer(name=name, image=image))
        self.modified = True

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
        """Replace the image of the active layer."""
        layer = self.layer_stack.active_layer
        if layer is None:
            return
        layer.image = image
        self.width = image.width()
        self.height = image.height()
        self.modified = True
