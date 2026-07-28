#!/usr/bin/env python3
"""Photo Editor 2.0 — Gradient Tool."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import (
    QColor,
    QImage,
    QLinearGradient,
    QPainter,
    QRadialGradient,
)


class GradientType(Enum):
    """Supported gradient shapes."""
    LINEAR = auto()
    RADIAL = auto()


class GradientBlend(Enum):
    """How gradient blends with the image."""
    NORMAL = "normal"
    MULTIPLY = "multiply"
    SCREEN = "screen"
    OVERLAY = "overlay"
    SOFT_LIGHT = "soft_light"


@dataclass
class GradientSettings:
    """Gradient configuration."""
    gradient_type: GradientType = GradientType.LINEAR
    blend_mode: GradientBlend = GradientBlend.NORMAL
    opacity: float = 1.0
    reverse: bool = False
    color1: QColor = None  # type: ignore
    color2: QColor = None  # type: ignore

    def __post_init__(self) -> None:
        if self.color1 is None:
            self.color1 = QColor("black")
        if self.color2 is None:
            self.color2 = QColor(Qt.GlobalColor.transparent)


class GradientTool:
    """Linear and radial gradient overlay tool."""

    def __init__(self) -> None:
        self.settings = GradientSettings()
        self._start_point: QPointF | None = None
        self._end_point: QPointF | None = None
        self._is_drawing = False

    @property
    def is_drawing(self) -> bool:
        return self._is_drawing

    def begin(self, point: QPointF) -> None:
        self._is_drawing = True
        self._start_point = point
        self._end_point = point

    def update(self, point: QPointF) -> None:
        if self._is_drawing:
            self._end_point = point

    def finish(self, target: QImage) -> QImage | None:
        if not self._is_drawing or self._start_point is None or self._end_point is None:
            return None
        self._is_drawing = False
        return self._apply(target)

    def cancel(self) -> None:
        self._is_drawing = False
        self._start_point = None
        self._end_point = None

    def _apply(self, target: QImage) -> QImage | None:
        if target.isNull() or self._start_point is None or self._end_point is None:
            return None
        mask = QImage(target.size(), QImage.Format.Format_ARGB32)
        mask.fill(Qt.GlobalColor.transparent)
        painter = QPainter(mask)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        c1 = self.settings.color1
        c2 = self.settings.color2
        if self.settings.reverse:
            c1, c2 = c2, c1
        if self.settings.gradient_type == GradientType.LINEAR:
            grad = QLinearGradient(self._start_point, self._end_point)
        else:
            dx = self._end_point.x() - self._start_point.x()
            dy = self._end_point.y() - self._start_point.y()
            radius = (dx * dx + dy * dy) ** 0.5
            grad = QRadialGradient(self._start_point, radius)
        grad.setColorAt(0.0, c1)
        grad.setColorAt(1.0, c2)
        painter.setBrush(grad)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(mask.rect())
        painter.end()
        result = target.copy()
        comp_painter = QPainter(result)
        comp_painter.setOpacity(self.settings.opacity)
        comp_painter.setCompositionMode(
            self._composition_mode(self.settings.blend_mode)
        )
        comp_painter.drawImage(0, 0, mask)
        comp_painter.end()
        return result

    @staticmethod
    def _composition_mode(mode: GradientBlend):
        mapping = {
            GradientBlend.NORMAL: QPainter.CompositionMode.CompositionMode_SourceOver,
            GradientBlend.MULTIPLY: QPainter.CompositionMode.CompositionMode_Multiply,
            GradientBlend.SCREEN: QPainter.CompositionMode.CompositionMode_Screen,
            GradientBlend.OVERLAY: QPainter.CompositionMode.CompositionMode_Overlay,
            GradientBlend.SOFT_LIGHT: QPainter.CompositionMode.CompositionMode_SoftLight,
        }
        return mapping.get(mode, QPainter.CompositionMode.CompositionMode_SourceOver)
