#!/usr/bin/env python3
"""
Photo Editor 2.0

Renderer
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter

from core.layer_stack import LayerStack


class Renderer:
    """Composes a final image from a LayerStack."""

    @staticmethod
    def render(layer_stack: LayerStack) -> QImage | None:
        """Render all visible layers."""

        if not layer_stack.layers:
            return None

        base = layer_stack.layers[0].image

        result = QImage(
            base.size(),
            QImage.Format.Format_ARGB32,
        )
        result.fill(Qt.GlobalColor.transparent)

        painter = QPainter(result)

        for layer in layer_stack.layers:
            if not layer.visible:
                continue

            painter.setOpacity(layer.opacity)
            painter.drawImage(0, 0, layer.image)

        painter.end()

        return result
