#!/usr/bin/env python3
"""Photo Editor 2.0 — History Panel with snapshots."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class HistoryItem(QFrame):
    """Single history snapshot."""

    selected = Signal()

    def __init__(self, name: str, timestamp: str, parent=None):
        super().__init__(parent)
        self.name = name
        self.timestamp = timestamp
        self._is_current = False

        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self.name_label = QLabel(name)
        self.name_label.setStyleSheet("color: #EEEEF0; font-weight: 600; font-size: 12px;")
        layout.addWidget(self.name_label)

        self.time_label = QLabel(timestamp)
        self.time_label.setStyleSheet("color: #5E5E6C; font-size: 10px;")
        layout.addWidget(self.time_label)

        self._update_style()

    def mark_current(self) -> None:
        self._is_current = True
        self._update_style()

    def _update_style(self) -> None:
        if self._is_current:
            self.setStyleSheet("""
                QFrame {
                    background: #1A2A3A;
                    border: 1px solid #4A9EFF;
                    border-radius: 8px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background: #1A1A20;
                    border: 1px solid #2C2C36;
                    border-radius: 8px;
                }
            """)


class HistoryPanel(QWidget):
    """History panel showing edit history and snapshots."""

    history_selected = Signal(object)
    snapshot_taken = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._history_items: list[HistoryItem] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        title = QLabel("<b>HISTORIA</b>")
        title.setStyleSheet("color: #4A9EFF; font-size: 11px; padding-bottom: 4px; letter-spacing: 1px;")
        layout.addWidget(title)

        buttons_layout = QHBoxLayout()
        self._take_snapshot_btn = QPushButton("Zrób snapshot")
        self._take_snapshot_btn.clicked.connect(self._on_take_snapshot)
        buttons_layout.addWidget(self._take_snapshot_btn)

        self._clear_history_btn = QPushButton("Wyczyść")
        self._clear_history_btn.clicked.connect(self._on_clear_history)
        buttons_layout.addWidget(self._clear_history_btn)
        layout.addLayout(buttons_layout)

        self._history_widget = QWidget()
        self._history_layout = QVBoxLayout(self._history_widget)
        layout.addWidget(self._history_widget)

    def add_history_step(self, name: str, timestamp: str) -> None:
        item = HistoryItem(name, timestamp)
        self._history_items.append(item)
        self._history_layout.insertWidget(0, item)
        item.selected.connect(lambda i=item: self.history_selected.emit(i))

        for other in self._history_items:
            other.mark_current = lambda i=item: (
                setattr(other, "_is_current", other is i),
                other._update_style(),
            )

    def _on_take_snapshot(self) -> None:
        import datetime
        now = datetime.datetime.now()
        name = f"Snapshot {len(self._history_items) + 1}"
        timestamp = now.strftime("%H:%M:%S")
        self.add_history_step(name, timestamp)
        self.snapshot_taken.emit(name)

    def _on_clear_history(self) -> None:
        for item in self._history_items:
            item.deleteLater()
        self._history_items.clear()

    def get_current_snapshot(self) -> HistoryItem | None:
        for item in self._history_items:
            if getattr(item, "_is_current", False):
                return item
        return self._history_items[0] if self._history_items else None
