#!/usr/bin/env python3
"""Photo Editor 2.0 — Render Stage."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter

from core.adjustments import ImageAdjustments
from core.layer import Layer

if TYPE_CHECKING:
    from .render_context import RenderContext


class RenderStage(ABC):
    """Abstract base for a single rendering step."""

    @abstractmethod
    def process(
        self,
        image: QImage | None,
        context: RenderContext,
    ) -> QImage | None:
        """Process the image and return the result."""
        ...

    @abstractmethod
    def name(self) -> str:
        """Return the stage name for debugging/profiling."""
        ...


class ComposeLayersStage(RenderStage):
    """Compose all visible layers into a single image."""

    def __init__(self, layers: list[Layer]) -> None:
        self.layers = layers

    def name(self) -> str:
        return "compose_layers"

    def process(
        self,
        image: QImage | None,
        context: RenderContext,
    ) -> QImage | None:
        if not self.layers:
            return None

        base = self.layers[0].image
        if base.isNull():
            return None

        result = QImage(base.size(), QImage.Format.Format_ARGB32)
        result.fill(Qt.GlobalColor.transparent)

        painter = QPainter(result)
        for layer in self.layers:
            if not layer.visible:
                continue
            painter.setOpacity(layer.opacity)
            painter.drawImage(0, 0, layer.image)
        painter.end()

        return result


class ApplyDevelopSettingsStage(RenderStage):
    """Apply tone, color and detail adjustments."""

    def name(self) -> str:
        return "apply_develop"

    def process(
        self,
        image: QImage | None,
        context: RenderContext,
    ) -> QImage | None:
        if image is None or image.isNull():
            return image

        settings = context.develop_settings
        if settings.is_identity():
            return image

        from core.adjustment_settings import AdjustmentSettings
        adj = AdjustmentSettings(
            exposure=int(settings.exposure),
            gamma=int((settings.gamma - 1.0) * 50),
            highlights=int(settings.highlights),
            shadows=int(settings.shadows),
            whites=int(settings.whites),
            blacks=int(settings.blacks),
            brightness=int(settings.brightness),
            contrast=int(settings.contrast),
            saturation=int(settings.saturation),
            temperature=int(settings.temperature),
            tint=int(settings.tint),
        )

        if adj.is_identity():
            return image

        return ImageAdjustments.apply_settings(image, adj)


class ResizeToContextStage(RenderStage):
    """Resize image to match context dimensions."""

    def name(self) -> str:
        return "resize"

    def process(
        self,
        image: QImage | None,
        context: RenderContext,
    ) -> QImage | None:
        if image is None or image.isNull() or not context.is_valid():
            return image

        if image.width() == context.width and image.height() == context.height:
            return image

        from PySide6.QtCore import Qt
        return image.scaled(
            context.width,
            context.height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
