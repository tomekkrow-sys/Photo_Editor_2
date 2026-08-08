#!/usr/bin/env python3
from __future__ import annotations

from PySide6.QtGui import QImage

class History:
    def __init__(self, limit=100):
        self._limit = limit
        self._stack = []
        self._index = -1

    def push(self, state):
        self._stack = self._stack[: self._index + 1]
        self._stack.append(state)
        if len(self._stack) > self._limit:
            self._stack.pop(0)
        else:
            self._index += 1

    def undo(self):
        if self.can_undo():
            self._index -= 1
            return self._stack[self._index]
        return None

    def redo(self):
        if self.can_redo():
            self._index += 1
            return self._stack[self._index]
        return None

    def can_undo(self):
        return self._index > 0

    def can_redo(self):
        return self._index < len(self._stack) - 1


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


class EditHistory:
    """Two-stack undo/redo history for PIL images (deep copies)."""

    def __init__(self, limit: int = 10) -> None:
        self._limit = limit
        self._undo: list = []
        self._redo: list = []

    @property
    def can_undo(self) -> bool:
        return bool(self._undo)

    @property
    def can_redo(self) -> bool:
        return bool(self._redo)

    def clear(self) -> None:
        self._undo.clear()
        self._redo.clear()

    def push(self, current) -> None:
        """Store a copy of the current state; call BEFORE mutating."""

        self._undo.append(current.copy())
        if len(self._undo) > self._limit:
            self._undo.pop(0)
        self._redo.clear()

    def undo(self, current):
        """Return the previous state (or None) and move current to redo."""

        if not self._undo:
            return None
        self._redo.append(current)
        return self._undo.pop()

    def redo(self, current):
        """Return the re-done state (or None) and move current to undo."""

        if not self._redo:
            return None
        self._undo.append(current)
        return self._redo.pop()
