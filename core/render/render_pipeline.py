#!/usr/bin/env python3
"""Photo Editor 2.0 — Render Pipeline."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtGui import QImage

from .render_cache import RenderCache
from .render_context import RenderContext
from .render_stage import (
    ApplyDevelopSettingsStage,
    ComposeLayersStage,
    RenderStage,
    ResizeToContextStage,
)

if TYPE_CHECKING:
    from core.layer import Layer


class RenderPipeline:
    """
    Orchestrates multi-stage image rendering with caching.
    """

    def __init__(self, cache_size: int = 3) -> None:
        self._cache = RenderCache(max_size=cache_size)
        self._stages: list[RenderStage] = []

    def build(
        self,
        layers: list[Layer],
        context: RenderContext,
    ) -> None:
        """Build the stage chain for a given render pass."""
        self._stages.clear()

        self._stages.append(ComposeLayersStage(layers))

        if context.apply_adjustments:
            self._stages.append(ApplyDevelopSettingsStage())

        if context.is_valid():
            self._stages.append(ResizeToContextStage())

    def render(
        self,
        layers: list[Layer],
        context: RenderContext,
    ) -> QImage | None:
        """
        Execute the full render pipeline.
        Returns the final QImage or None if nothing to render.
        """
        cached = self._cache.get(context)
        if cached is not None:
            return cached

        self.build(layers, context)

        if not self._stages:
            return None

        image: QImage | None = None
        for stage in self._stages:
            image = stage.process(image, context)
            if image is None:
                return None

        if image is not None and not image.isNull():
            self._cache.put(context, image)

        return image.copy() if image is not None else None

    def invalidate_cache(self) -> None:
        """Force full re-render on next call."""
        self._cache.invalidate()

    @property
    def cache_stats(self) -> dict[str, int]:
        """Return cache statistics."""
        return {
            "size": len(self._cache._entries),
            "max_size": self._cache._max_size,
        }
