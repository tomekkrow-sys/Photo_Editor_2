#!/usr/bin/env python3
"""Multi-tab manager for Photo Editor 2."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from PIL import Image
from core.adjustments import Adjustments
from core.history import EditHistory
import numpy as np


@dataclass
class TabData:
    """Stores all state for a single tab/image."""
    path: Path | None = None
    orig: Image.Image | None = None
    preview_arr: np.ndarray | None = None
    adj: Adjustments = field(default_factory=Adjustments)
    history: EditHistory = field(default_factory=EditHistory)
    adj_history: EditHistory = field(default_factory=lambda: EditHistory(limit=30))
    adj_last_push: float = 0.0
    ba_active: bool = False
    spot_size: int | None = None
    brush_size: int | None = None
    draw_size: int | None = None
    title: str = "Bez nazwy"


class TabManager:
    """Manages multiple open image tabs."""

    def __init__(self):
        self._tabs: list[TabData] = []
        self._current: int = -1

    @property
    def tabs(self) -> list[TabData]:
        return self._tabs

    @property
    def current_index(self) -> int:
        return self._current

    @property
    def current(self) -> TabData | None:
        if 0 <= self._current < len(self._tabs):
            return self._tabs[self._current]
        return None

    def add_tab(self, data: TabData | None = None) -> TabData:
        if data is None:
            data = TabData()
        self._tabs.append(data)
        self._current = len(self._tabs) - 1
        return data

    def remove_tab(self, index: int) -> TabData | None:
        if 0 <= index < len(self._tabs):
            removed = self._tabs.pop(index)
            if self._current >= len(self._tabs):
                self._current = len(self._tabs) - 1
            return removed
        return None

    def set_current(self, index: int) -> TabData | None:
        if 0 <= index < len(self._tabs):
            self._current = index
            return self._tabs[self._current]
        return None

    def next_tab(self) -> TabData | None:
        if len(self._tabs) <= 1:
            return None
        idx = (self._current + 1) % len(self._tabs)
        return self.set_current(idx)

    def prev_tab(self) -> TabData | None:
        if len(self._tabs) <= 1:
            return None
        idx = (self._current - 1) % len(self._tabs)
        return self.set_current(idx)

    def count(self) -> int:
        return len(self._tabs)

    def clear(self):
        self._tabs.clear()
        self._current = -1
