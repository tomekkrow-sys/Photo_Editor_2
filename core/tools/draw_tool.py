#!/usr/bin/env python3
"""Photo Editor 2.0 — Freehand Drawing Tool."""

from __future__ import annotations

from dataclasses import dataclass, field

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QImage, QPainter


@dataclass
class DrawSettings:
    """Configurable drawing parameters."""
    size: float = 10.0
    color: QColor = field(default_factory=lambda: QColor("red"))
    opacity: float = 1.0
    hardness: float = 1.0


class DrawTool:
    """Simple freehand drawing tool for sketching on images."""

    def __init__(self) -> None:
        self.settings = DrawSettings()
        self._last_point: QPointF | None = None
        self._is_drawing = False

    @property
    def is_drawing(self) -> bool:
        return self._is_drawing

    def begin(self, point: QPointF, target: QImage) -> None:
        self._is_drawing = True
        self._last_point = point
        self._draw_line(point, point, target)

    def update(self, point: QPointF, target: QImage) -> None:
        if not self._is_drawing or self._last_point is None:
            return
        self._draw_line(self._last_point, point, target)
        self._last_point = point

    def finish(self) -> None:
        self._is_drawing = False
        self._last_point = None

    def cancel(self) -> None:
        self.finish()

    def _draw_line(self, from_pt: QPointF, to_pt: QPointF, target: QImage) -> None:
        if target.isNull():
            return
        painter = QPainter(target)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor(self.settings.color)
        color.setAlpha(int(255 * self.settings.opacity))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        # Draw circle at both ends and line between
        r = self.settings.size / 2
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        painter.drawEllipse(from_pt, r, r)
        painter.drawEllipse(to_pt, r, r)
        # Draw line
        pen = painter.pen()
        pen.setColor(color)
        pen.setWidthF(self.settings.size)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawLine(from_pt, to_pt)
        painter.end()
