#!/usr/bin/env python3
"""Photo Editor 2.0 — Brush Tool."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import (
    QColor,
    QImage,
    QPainter,
    QRadialGradient,
)


class BrushMode(Enum):
    """Brush application modes."""
    PAINT = "paint"
    ERASE = "erase"
    DODGE = "dodge"
    BURN = "burn"
    SATURATE = "saturate"
    DESATURATE = "desaturate"


@dataclass
class BrushSettings:
    """Configurable brush parameters."""
    size: float = 20.0
    hardness: float = 0.8
    opacity: float = 1.0
    flow: float = 1.0
    color: QColor = field(default_factory=lambda: QColor("white"))
    mode: BrushMode = BrushMode.PAINT
    spacing: float = 0.25


class BrushTool:
    """Paint brush with soft edges, opacity, flow and multiple modes."""

    def __init__(self) -> None:
        self.settings = BrushSettings()
        self._last_point: QPointF | None = None
        self._is_drawing = False

    @property
    def is_drawing(self) -> bool:
        return self._is_drawing

    def begin(self, point: QPointF, target: QImage) -> None:
        self._is_drawing = True
        self._last_point = point
        self._dab(point, target)

    def update(self, point: QPointF, target: QImage) -> None:
        if not self._is_drawing or self._last_point is None:
            return
        distance = self._distance(self._last_point, point)
        spacing_px = self.settings.size * self.settings.spacing
        if distance < spacing_px:
            return
        steps = int(distance / spacing_px)
        for i in range(1, steps + 1):
            t = i / steps
            interp = QPointF(
                self._last_point.x() + (point.x() - self._last_point.x()) * t,
                self._last_point.y() + (point.y() - self._last_point.y()) * t,
            )
            self._dab(interp, target)
        self._last_point = point

    def finish(self) -> None:
        self._is_drawing = False
        self._last_point = None

    def cancel(self) -> None:
        self.finish()

    def _dab(self, center: QPointF, target: QImage) -> None:
        if target.isNull():
            return
        r = self.settings.size / 2
        rect = target.rect().intersected(
            target.rect().adjusted(
                int(center.x() - r), int(center.y() - r),
                int(center.x() + r), int(center.y() + r),
            )
        )
        if rect.isEmpty():
            return
        stamp = QImage(rect.size(), QImage.Format.Format_ARGB32)
        stamp.fill(Qt.GlobalColor.transparent)
        painter = QPainter(stamp)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        grad = QRadialGradient(QPointF(r, r), r)
        alpha = int(255 * self.settings.opacity * self.settings.flow)
        color = QColor(self.settings.color)
        hard_color = QColor(color)
        hard_color.setAlpha(alpha)
        soft_color = QColor(color)
        soft_color.setAlpha(0)
        fade = self.settings.hardness
        grad.setColorAt(0.0, hard_color)
        grad.setColorAt(fade, hard_color)
        grad.setColorAt(1.0, soft_color)
        painter.setBrush(grad)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(r, r), r, r)
        painter.end()
        target_painter = QPainter(target)
        target_painter.setCompositionMode(
            self._composition_mode(self.settings.mode)
        )
        target_painter.drawImage(rect.topLeft(), stamp)
        target_painter.end()

    @staticmethod
    def _distance(a: QPointF, b: QPointF) -> float:
        return ((a.x() - b.x()) ** 2 + (a.y() - b.y()) ** 2) ** 0.5

    @staticmethod
    def _composition_mode(mode: BrushMode):
        mapping = {
            BrushMode.PAINT: QPainter.CompositionMode.CompositionMode_SourceOver,
            BrushMode.ERASE: QPainter.CompositionMode.CompositionMode_DestinationOut,
            BrushMode.DODGE: QPainter.CompositionMode.CompositionMode_Plus,
            BrushMode.BURN: QPainter.CompositionMode.CompositionMode_Multiply,
            BrushMode.SATURATE: QPainter.CompositionMode.CompositionMode_Saturation,
            BrushMode.DESATURATE: QPainter.CompositionMode.CompositionMode_ColorDodge,
        }
        return mapping.get(mode, QPainter.CompositionMode.CompositionMode_SourceOver)
