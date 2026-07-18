#!/usr/bin/env python3
"""
Photo Editor 2.0

Renderer
"""

from __future__ import annotations

from PySide6.QtGui import QImage

from core.layer_stack import LayerStack


class Renderer:
    """Composes a final image from a LayerStack."""

    @staticmethod
    def render(layer_stack: LayerStack) -> QImage | None:
        """Render the current document."""

        layer = layer_stack.active_layer

        if layer is None:
            return None

        return layer.image.copy()
