#!/usr/bin/env python3
"""
Photo Editor 2.0

Image Saver
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QImage


class ImageSaver:
    """Save QImage objects to supported image formats."""

    SUPPORTED_EXTENSIONS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".bmp",
        ".tif",
        ".tiff",
    }

    @classmethod
    def can_save(cls, file_path: str | Path) -> bool:
        """Return True when the file extension is supported."""

        suffix = Path(file_path).suffix.lower()
        return suffix in cls.SUPPORTED_EXTENSIONS

    @classmethod
    def save(
        cls,
        image: QImage,
        file_path: str | Path,
    ) -> bool:
        """Save an image to disk."""

        path = Path(file_path)

        if image.isNull() or not cls.can_save(path):
            return False

        return image.save(str(path))

    @staticmethod
    def file_dialog_filter() -> str:
        """Return the filter used by the Save As dialog."""

        return (
            "PNG (*.png);;"
            "JPEG (*.jpg *.jpeg);;"
            "WebP (*.webp);;"
            "BMP (*.bmp);;"
            "TIFF (*.tif *.tiff)"
        )