#!/usr/bin/env python3
from __future__ import annotations

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
