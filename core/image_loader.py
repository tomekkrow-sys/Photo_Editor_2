#!/usr/bin/env python3
"""
Photo Editor 2.0

Image Loader

Version: 0.1.0
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QImage

from core.image_document import ImageDocument


class ImageLoader:
    """
    Loads images into ImageDocument.
    """

    SUPPORTED_EXTENSIONS = {
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".tif",
        ".tiff",
        ".webp",
    }

    @classmethod
    def load(cls, file_path: str | Path) -> ImageDocument:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(path)

        if path.suffix.lower() not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported format: {path.suffix}"
            )

        image = QImage(str(path))

        if image.isNull():
            raise ValueError(
                f"Cannot load image: {path}"
            )

        document = ImageDocument()

        document.load(
            image=image,
            file_path=path,
        )

        return document