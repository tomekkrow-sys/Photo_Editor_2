#!/usr/bin/env python3
"""History of QImage states for undo and redo."""

from __future__ import annotations

from PySide6.QtGui import QImage


class ImageHistory:
    """Keep independent copies of image states."""

    def __init__(self) -> None:
        self.clear()

    @property
    def can_undo(self) -> bool:
        return self._index > 0

    @property
    def can_redo(self) -> bool:
        return 0 <= self._index < len(self._states) - 1

    def clear(self) -> None:
        self._states: list[QImage] = []
        self._index: int = -1

    def push(self, image: QImage) -> None:
        """Store a copy of the current image and drop redo states."""

        if image.isNull():
            return

        if self.can_redo:
            self._states = self._states[: self._index + 1]

        if self._index >= 0 and self._states[self._index] == image:
            return

        self._states.append(image.copy())
        self._index = len(self._states) - 1

    def undo(self) -> QImage | None:
        if not self.can_undo:
            return None

        self._index -= 1
        return self._states[self._index].copy()

    def redo(self) -> QImage | None:
        if not self.can_redo:
            return None

        self._index += 1
        return self._states[self._index].copy()
