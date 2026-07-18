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