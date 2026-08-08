#!/usr/bin/env python3
from __future__ import annotations
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen, QPolygonF
from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QWidget

class HistogramWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._hist_r = self._hist_g = self._hist_b = self._hist_l = None
        self._clip_shadows = False
        self._clip_highlights = False
        self.setMinimumHeight(110)
        self.setMaximumHeight(130)
        self.setStyleSheet("background: #1E1E1E; border-top: 1px solid #333;")

    def set_image(self, pil_img):
        if pil_img is None:
            self._hist_r = self._hist_g = self._hist_b = self._hist_l = None
            self._clip_shadows = False
            self._clip_highlights = False
            self.update()
            return
        arr = np.array(pil_img.convert("RGB"), dtype=np.uint8)
        self._hist_r = np.histogram(arr[:, :, 0], bins=256, range=(0, 256))[0]
        self._hist_g = np.histogram(arr[:, :, 1], bins=256, range=(0, 256))[0]
        self._hist_b = np.histogram(arr[:, :, 2], bins=256, range=(0, 256))[0]
        gray = np.mean(arr.astype(np.float32), axis=2).astype(np.uint8)
        self._hist_l = np.histogram(gray, bins=256, range=(0, 256))[0]
        # Clipping detection
        total = arr.shape[0] * arr.shape[1]
        shadows = np.sum(arr < 5) / 3
        highlights = np.sum(arr > 250) / 3
        self._clip_shadows = shadows / total > 0.01
        self._clip_highlights = highlights / total > 0.01
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        w, h = self.width(), self.height()
        painter.fillRect(0, 0, w, h, QColor("#1E1E1E"))

        # Draw clipping triangles on top
        tri_h = 8
        if self._clip_shadows:
            painter.setBrush(QColor("#FF4444"))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPolygon(QPolygonF([
                QPointF(0, 0), QPointF(tri_h * 2, 0), QPointF(0, tri_h * 2)
            ]))
        if self._clip_highlights:
            painter.setBrush(QColor("#4444FF"))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPolygon(QPolygonF([
                QPointF(w, 0), QPointF(w - tri_h * 2, 0), QPointF(w, tri_h * 2)
            ]))

        # Histogram area (below triangles)
        top = tri_h + 2
        hh = h - top

        if self._hist_l is None:
            painter.end()
            return

        def draw(data, color, alpha=180):
            if data is None or data.max() == 0:
                return
            norm = data / data.max()
            pen = QPen(QColor(color))
            pen.setWidthF(max(1.0, w / 256.0))
            painter.setPen(pen)
            for i in range(256):
                x = int(i * w / 256)
                y = int(top + hh - norm[i] * hh * 0.95)
                painter.drawLine(x, top + hh, x, y)

        # Clipped areas on histogram edges
        if self._clip_shadows:
            painter.fillRect(0, top, int(w * 0.03), hh, QColor(255, 68, 68, 40))
        if self._clip_highlights:
            painter.fillRect(int(w * 0.97), top, int(w * 0.03), hh, QColor(68, 68, 255, 40))

        draw(self._hist_l, "#888888")
        draw(self._hist_r, "#FF5555")
        draw(self._hist_g, "#55FF55")
        draw(self._hist_b, "#5555FF")

        # Border line
        painter.setPen(QPen(QColor("#333333")))
        painter.drawLine(0, h - 1, w, h - 1)
        painter.end()
