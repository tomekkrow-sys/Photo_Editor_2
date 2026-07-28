#!/usr/bin/env python3
"""Photo Editor 2.0 — Render Cache."""

from __future__ import annotations

from PySide6.QtGui import QImage

from .render_context import RenderContext


class RenderCache:
    """
    Caches rendered QImage results keyed by state hash.
    Automatically invalidates when the hash changes.
    """

    def __init__(self, max_size: int = 3) -> None:
        self._max_size = max_size
        self._entries: dict[str, QImage] = {}
        self._access_order: list[str] = []

    def get(self, context: RenderContext) -> QImage | None:
        """Return cached image if state hash matches."""
        key = context.state_hash
        if not key:
            return None

        image = self._entries.get(key)
        if image is not None and not image.isNull():
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)
            return image.copy()

        return None

    def put(self, context: RenderContext, image: QImage) -> None:
        """Store rendered image in cache."""
        key = context.state_hash
        if not key or image is None or image.isNull():
            return

        while len(self._entries) >= self._max_size:
            oldest = self._access_order.pop(0)
            self._entries.pop(oldest, None)

        self._entries[key] = image.copy()
        self._access_order.append(key)

    def invalidate(self) -> None:
        """Clear all cached entries."""
        self._entries.clear()
        self._access_order.clear()

    def invalidate_key(self, state_hash: str) -> None:
        """Remove a specific cached entry."""
        self._entries.pop(state_hash, None)
        if state_hash in self._access_order:
            self._access_order.remove(state_hash)
