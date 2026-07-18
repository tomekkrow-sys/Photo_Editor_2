#!/usr/bin/env python3
"""
Photo Editor 2.0

Layer Stack
"""

from __future__ import annotations

from PySide6.QtGui import QImage

from core.layer import Layer


class LayerStack:
    """Stores and manages document layers."""

    def __init__(self) -> None:
        self._layers: list[Layer] = []
        self._active_index: int = -1

    @property
    def layers(self) -> list[Layer]:
        return self._layers

    @property
    def active_layer(self) -> Layer | None:
        if 0 <= self._active_index < len(self._layers):
            return self._layers[self._active_index]
        return None

    def clear(self) -> None:
        self._layers.clear()
        self._active_index = -1

    def add_background(self, image: QImage) -> Layer:
        """Create the initial Background layer."""
        self.clear()

        layer = Layer(
            name="Background",
            image=image.copy(),
        )

        self._layers.append(layer)
        self._active_index = 0

        return layer

    def add_layer(self, layer: Layer) -> None:
        """Add a layer above the active layer."""

        if self._active_index == -1:
            self._layers.append(layer)
            self._active_index = 0
            return

        index = self._active_index + 1
        self._layers.insert(index, layer)
        self._active_index = index

    def remove_active_layer(self) -> None:
        """Remove the active layer."""

        if self._active_index == -1:
            return

        del self._layers[self._active_index]

        if not self._layers:
            self._active_index = -1
        elif self._active_index >= len(self._layers):
            self._active_index = len(self._layers) - 1

    def set_active(self, index: int) -> None:
        """Select active layer."""

        if 0 <= index < len(self._layers):
            self._active_index = index


    def duplicate_active_layer(self) -> Layer | None:
        """Duplicate the active layer."""

        layer = self.active_layer
        if layer is None:
            return None

        copy = Layer(
            name=f"{layer.name} Copy",
            image=layer.image.copy(),
            visible=layer.visible,
            opacity=layer.opacity,
            locked=layer.locked,
            blend_mode=layer.blend_mode,
        )

        self.add_layer(copy)
        return copy

    def move_active_up(self) -> None:
        """Move the active layer up."""

        i = self._active_index
        if i < 0 or i >= len(self._layers) - 1:
            return

        self._layers[i], self._layers[i + 1] = self._layers[i + 1], self._layers[i]
        self._active_index += 1

    def move_active_down(self) -> None:
        """Move the active layer down."""

        i = self._active_index
        if i <= 0:
            return

        self._layers[i], self._layers[i - 1] = self._layers[i - 1], self._layers[i]
        self._active_index -= 1
