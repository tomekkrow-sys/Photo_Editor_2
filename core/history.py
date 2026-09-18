#!/usr/bin/env python3
from __future__ import annotations

import time

from PIL import Image
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
    """Two-stack undo/redo history for PIL images with operation names and thumbnails."""

    def __init__(self, limit: int = 30) -> None:
        self._limit = limit
        self._undo: list = []
        self._redo: list = []
        self._names: list = []
        self._redo_names: list = []
        self.last_change: float = 0.0

    @property
    def can_undo(self) -> bool:
        return bool(self._undo)

    @property
    def can_redo(self) -> bool:
        return bool(self._redo)

    @property
    def entries(self) -> list:
        """Return list of (index, name) for all states."""
        result = []
        for i, name in enumerate(self._names):
            result.append((i, name))
        return result

    @property
    def current_index(self) -> int:
        return len(self._undo) - 1

    def clear(self) -> None:
        self._undo.clear()
        self._redo.clear()
        self._names.clear()
        self._redo_names.clear()
        self.last_change = 0.0

    def push(self, current, name: str = "") -> None:
        """Store a copy of the current state; call BEFORE mutating."""

        self._undo.append(current.copy())
        if len(self._undo) > self._limit:
            self._undo.pop(0)
        self._names.append(name or f"Krok {len(self._names) + 1}")
        if len(self._names) > self._limit:
            self._names.pop(0)
        self._redo.clear()
        self._redo_names.clear()
        self.last_change = time.monotonic()

    def undo(self, current):
        """Return the previous state (or None) and move current to redo."""

        if not self._undo:
            return None
        self._redo.append(current)
        name = self._names.pop() if self._names else ""
        self._redo_names.append(name)
        self.last_change = time.monotonic()
        return self._undo.pop()

    def redo(self, current):
        """Return the re-done state (or None) and move current to undo."""

        if not self._redo:
            return None
        self._undo.append(current)
        name = self._redo_names.pop() if self._redo_names else ""
        self._names.append(name)
        self.last_change = time.monotonic()
        return self._redo.pop()

    def get_state(self, index: int):
        """Get state at specific index (0 = first undo state)."""
        if 0 <= index < len(self._undo):
            return self._undo[index]
        return None

    def get_name(self, index: int) -> str:
        """Get operation name at index."""
        if 0 <= index < len(self._names):
            return self._names[index]
        return ""

    @staticmethod
    def make_thumbnail(img, size=(80, 60)):
        """Create a small thumbnail from a PIL image."""
        if img is None:
            return None
        thumb = img.copy()
        thumb.thumbnail(size, Image.Resampling.LANCZOS)
        return thumb
