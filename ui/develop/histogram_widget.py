from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget


class HistogramWidget(QWidget):
    """Placeholder histogram."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(160)

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.fillRect(self.rect(), QColor(35, 35, 35))

        pen = QPen(QColor(90, 90, 90))
        painter.setPen(pen)

        w = self.width()
        h = self.height()

        for i in range(0, 256, 32):
            x = int(i / 255 * w)
            painter.drawLine(x, 0, x, h)

        painter.setPen(QPen(Qt.white, 2))
        painter.drawText(
            self.rect(),
            Qt.AlignCenter,
            "Histogram"
        )
