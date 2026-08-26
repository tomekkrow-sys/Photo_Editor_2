#!/usr/bin/env python3
"""Photo Editor 2.0 — Navigator Panel with Filmstrip."""

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


class NavigatorWidget(QWidget):
    """Mini navigator with zoom and pan."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._zoom = 1.0
        self._pan_x = 0
        self._pan_y = 0
        self._min_size = 200
        self._rect_width = 200
        self._rect_height = 150
        self._rect_x = 50
        self._rect_y = 50

    def paintEvent(self, event):
        from PySide6.QtGui import QPainter, QBrush, QPen

        painter = QPainter(self)
        painter.fillRect(self.rect(), "#222222")

        view_width = int(self._rect_width / self._zoom)
        view_height = int(self._rect_height / self._zoom)

        brush = QBrush("#333333")
        painter.fillRect(self._pan_x, self._pan_y, view_width, view_height, brush)

        pen = QPen("#4A9EFF")
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(self._pan_x + self._rect_x, self._pan_y + self._rect_y, self._rect_width, self._rect_height)

        painter.setPen("#666666")
        painter.drawText(10, 18, f"Zoom: {int(self._zoom * 100)}%")

    def zoom_in(self):
        self._zoom *= 1.25
        self.update()

    def zoom_out(self):
        self._zoom /= 1.25
        self.update()

    def zoom_fit(self):
        self._zoom = 1.0
        self.update()


class FilmstripWidget(QWidget):
    """Filmstrip showing thumbnails."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._thumbs = []
        self._selected_index = 0
        self._min_size = 100

    def paintEvent(self, event):
        from PySide6.QtGui import QPainter, QBrush

        painter = QPainter(self)
        painter.fillRect(self.rect(), "#222222")

        thumb_size = 80
        spacing = 10

        for i, thumb in enumerate(self._thumbs):
            x = i * (thumb_size + spacing) + 10
            y = 10

            brush = QBrush(thumb.get("color", "#333333"))
            painter.fillRect(x, y, thumb_size, thumb_size, brush)

            if i == self._selected_index:
                painter.setPen("#4A9EFF")
                painter.drawRect(x - 2, y - 2, thumb_size + 4, thumb_size + 4)

            painter.setPen("#CCCCCC")
            painter.drawText(x + 5, y + thumb_size + 15, thumb.get("name", f"Photo {i + 1}"))

    def set_thumbs(self, thumbs: list):
        self._thumbs = thumbs
        self.update()

    def select_index(self, index: int):
        self._selected_index = index
        self.update()


class NavigatorPanel(QWidget):
    """Navigator panel with navigator and filmstrip."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self._navigator = NavigatorWidget()
        self._filmstrip = FilmstripWidget()

        layout = QVBoxLayout(self)
        layout.addWidget(self._navigator)

        filmstrip_layout = QHBoxLayout()
        filmstrip_layout.addWidget(self._filmstrip)
        layout.addLayout(filmstrip_layout)

        button_layout = QHBoxLayout()
        zoom_out_btn = QPushButton("Zmniejsz")
        zoom_out_btn.clicked.connect(self._navigator.zoom_out)
        button_layout.addWidget(zoom_out_btn)

        zoom_fit_btn = QPushButton("Dopasuj")
        zoom_fit_btn.clicked.connect(self._navigator.zoom_fit)
        button_layout.addWidget(zoom_fit_btn)

        zoom_in_btn = QPushButton("Powiększ")
        zoom_in_btn.clicked.connect(self._navigator.zoom_in)
        button_layout.addWidget(zoom_in_btn)

        layout.addLayout(button_layout)

    def set_thumbs(self, thumbs: list):
        self._filmstrip.set_thumbs(thumbs)

    def select_thumbs(self, thumbs: list):
        self._filmstrip.set_thumbs(thumbs)
