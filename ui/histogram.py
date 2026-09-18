#!/usr/bin/env python3
"""RGB Histogram widget for Photo Editor 2."""
from __future__ import annotations
import numpy as np
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QImage, QPainter, QColor, QPen, QLinearGradient, QPainterPath
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from config.i18n import t


class HistogramWidget(QWidget):
    """Displays an RGB histogram of an image."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(120)
        self.setMaximumHeight(160)
        self._r = np.zeros(256, dtype=np.float64)
        self._g = np.zeros(256, dtype=np.float64)
        self._b = np.zeros(256, dtype=np.float64)
        self._lum = np.zeros(256, dtype=np.float64)

    def set_image(self, qimg: QImage | None):
        if qimg is None or qimg.isNull():
            self._r[:] = 0
            self._g[:] = 0
            self._b[:] = 0
            self._lum[:] = 0
            self.update()
            return

        img = qimg.convertToFormat(QImage.Format.Format_RGBA8888)
        w, h = img.width(), img.height()
        bpl = img.bytesPerLine()
        buf = img.bits()
        arr = np.frombuffer(buf, dtype=np.uint8, count=h * bpl).reshape(h, bpl)
        pixels = arr[:, :w * 4].reshape(h, w, 4)

        r = pixels[:, :, 0].ravel().astype(np.float64)
        g = pixels[:, :, 1].ravel().astype(np.float64)
        b = pixels[:, :, 2].ravel().astype(np.float64)

        self._r = np.bincount(r.astype(np.uint8), minlength=256).astype(np.float64)
        self._g = np.bincount(g.astype(np.uint8), minlength=256).astype(np.float64)
        self._b = np.bincount(b.astype(np.uint8), minlength=256).astype(np.float64)
        self._lum = np.bincount(
            (0.2126 * r + 0.7152 * g + 0.0722 * b).clip(0, 255).astype(np.uint8),
            minlength=256,
        ).astype(np.float64)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(4, 4, -4, -4)
        w, h = rect.width(), rect.height()

        # Background
        painter.fillRect(self.rect(), QColor(30, 30, 30))
        painter.setPen(QPen(QColor(60, 60, 60), 1))
        painter.drawRect(rect)

        # Find max value across all channels for normalization
        all_max = max(
            self._r.max(), self._g.max(), self._b.max(), self._lum.max(), 1.0
        )

        def draw_channel(data, color):
            if data.max() == 0:
                return
            path = QPainterPath()
            path.moveTo(rect.left(), rect.bottom())
            for i in range(256):
                x = rect.left() + (i / 255.0) * w
                y = rect.bottom() - (data[i] / all_max) * h * 0.9
                path.lineTo(x, y)
            path.lineTo(rect.right(), rect.bottom())
            path.closeSubpath()

            # Semi-transparent fill
            fill_color = QColor(color)
            fill_color.setAlpha(60)
            painter.fillPath(path, fill_color)

            # Outline
            painter.setPen(QPen(color, 1))
            outline = QPainterPath()
            first = True
            for i in range(256):
                x = rect.left() + (i / 255.0) * w
                y = rect.bottom() - (data[i] / all_max) * h * 0.9
                if first:
                    outline.moveTo(x, y)
                    first = False
                else:
                    outline.lineTo(x, y)
            painter.drawPath(outline)

        # Draw luminance first (behind)
        draw_channel(self._lum, QColor(180, 180, 180))
        draw_channel(self._r, QColor(220, 50, 50))
        draw_channel(self._g, QColor(50, 180, 50))
        draw_channel(self._b, QColor(50, 80, 220))

        painter.end()


class HistogramDock(QWidget):
    """Histogram panel with label."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        lbl = QLabel(t("histogram"))
        lbl.setStyleSheet("font-weight: bold; padding: 4px;")
        layout.addWidget(lbl)
        self.hist = HistogramWidget()
        layout.addWidget(self.hist)

    def set_image(self, qimg):
        self.hist.set_image(qimg)
