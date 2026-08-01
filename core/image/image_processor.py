#!/usr/bin/env python3
"""Photo Editor 2.0 — Image Processor."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QTransform

from core.adjustments import ImageAdjustments
from core.adjustment_settings import AdjustmentSettings

from .image_document import ImageDocument


class ImageProcessor:
    """
    Centralised image processing operations.
    All transformations are non-destructive (return new images).
    """

    @staticmethod
    def resize(
        image: QImage,
        width: int,
        height: int,
    ) -> QImage | None:
        """Resize image to exact dimensions."""
        if image.isNull() or width <= 0 or height <= 0:
            return None
        return image.scaled(
            width,
            height,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

    @staticmethod
    def rotate(image: QImage, angle: int) -> QImage | None:
        """Rotate image by given angle in degrees."""
        if image.isNull():
            return None
        transform = QTransform()
        transform.rotate(angle)
        return image.transformed(
            transform,
            Qt.TransformationMode.SmoothTransformation,
        )

    @staticmethod
    def flip(
        image: QImage,
        horizontal: bool = False,
        vertical: bool = False,
    ) -> QImage | None:
        """Flip image horizontally and/or vertically."""
        if image.isNull():
            return None
        return image.mirrored(horizontal, vertical)

    @staticmethod
    def crop(image: QImage, rect) -> QImage | None:
        """Crop image to the given rectangle."""
        if image.isNull() or rect.isEmpty():
            return None
        aligned = rect.toAlignedRect()
        cropped = image.copy(aligned)
        return cropped if not cropped.isNull() else None

    @staticmethod
    def apply_adjustments(
        image: QImage,
        settings: AdjustmentSettings,
    ) -> QImage | None:
        """Apply adjustment settings to an image."""
        if image.isNull() or settings.is_identity():
            return image.copy() if not image.isNull() else None
        return ImageAdjustments.apply_settings(image, settings)

    @staticmethod
    def render_document(document: ImageDocument) -> QImage | None:
        """Render a complete document (all layers)."""
        return document.rendered_image
