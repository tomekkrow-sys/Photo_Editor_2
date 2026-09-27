#!/usr/bin/env python3
"""Collapsible section widget — button header with icon + text."""

from __future__ import annotations
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget,
)


class CollapsibleSection(QWidget):
    """Accordion-style collapsible section with a styled header button."""

    _STYLE = """
    QPushButton#_section_btn {
        text-align: left;
        font-size: 13px;
        font-weight: 700;
        border: 1px solid {border};
        border-radius: 8px;
        padding: 8px 12px;
        background: {bg};
        color: {accent};
    }}
    QPushButton#_section_btn:hover {{
        background: {hover};
    }}
    """

    def __init__(self, title: str, icon: str = "\u25B6", parent=None):
        super().__init__(parent)
        self._icon_open = icon
        self._icon_close = "\u25BC"
        self._expanded = True

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # --- header button ---
        self._btn = QPushButton(f"  {self._icon_open}  {title}")
        self._btn.setObjectName("_section_btn")
        self._btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn.setCheckable(True)
        self._btn.setChecked(True)
        self._btn.clicked.connect(self._toggle)
        root.addWidget(self._btn)

        # --- content wrapper ---
        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(4, 4, 4, 4)
        self._content_layout.setSpacing(0)
        root.addWidget(self._content)

    def content_layout(self) -> QVBoxLayout:
        return self._content_layout

    def add_widget(self, w: QWidget):
        self._content_layout.addWidget(w)

    def add_layout(self, l):
        self._content_layout.addLayout(l)

    def _toggle(self):
        self._expanded = not self._expanded
        self._content.setVisible(self._expanded)
        icon = self._icon_open if self._expanded else self._icon_close
        # update button text preserving title (after last "  ")
        parts = self._btn.text().rsplit("  ", 1)
        title = parts[-1] if len(parts) > 1 else self._btn.text()
        self._btn.setText(f"  {icon}  {title}")

    def set_expanded(self, v: bool):
        if self._expanded != v:
            self._toggle()
