#!/usr/bin/env python3
"""Photo Editor 2.0 — Crop Tool (enhanced)."""

from __future__ import annotations

from enum import Enum
from typing import Self

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import (
    QGraphicsLineItem,
    QGraphicsRectItem,
    QGraphicsScene,
)

from config.colors import SELECTION_BORDER


class CropRatio(Enum):
    """Predefined crop aspect ratios."""
    FREE = "free"
    ORIGINAL = "original"
    SQUARE = "1:1"
    RATIO_4_3 = "4:3"
    RATIO_3_2 = "3:2"
    RATIO_16_9 = "16:9"
    RATIO_5_4 = "5:4"
    RATIO_2_3 = "2:3"
    RATIO_9_16 = "9:16"

    @property
    def value_tuple(self) -> tuple[float, float] | None:
        """Return (width, height) ratio or None for free/original."""
        mapping = {
            CropRatio.SQUARE: (1.0, 1.0),
            CropRatio.RATIO_4_3: (4.0, 3.0),
            CropRatio.RATIO_3_2: (3.0, 2.0),
            CropRatio.RATIO_16_9: (16.0, 9.0),
            CropRatio.RATIO_5_4: (5.0, 4.0),
            CropRatio.RATIO_2_3: (2.0, 3.0),
            CropRatio.RATIO_9_16: (9.0, 16.0),
        }
        return mapping.get(self)


class CropTool:
    """
    Enhanced rectangular crop selection with:
    - aspect ratio locking
    - rule-of-thirds overlay
    - straighten (rotation) support
    """

    def __init__(self, scene: QGraphicsScene) -> None:
        self._scene = scene

        # Main selection rect
        self._selection_item = QGraphicsRectItem()
        self._selection_item.setZValue(10)
        self._selection_item.setBrush(Qt.BrushStyle.NoBrush)
        pen = QPen(QColor(SELECTION_BORDER), 2)
        pen.setCosmetic(True)
        self._selection_item.setPen(pen)
        self._selection_item.hide()
        scene.addItem(self._selection_item)

        # Rule-of-thirds grid lines
        self._grid_lines: list[QGraphicsLineItem] = []
        grid_pen = QPen(QColor(255, 255, 255, 120), 1)
        grid_pen.setCosmetic(True)
        grid_pen.setStyle(Qt.PenStyle.DashLine)
        for _ in range(4):
            line = QGraphicsLineItem()
            line.setZValue(11)
            line.setPen(grid_pen)
            line.hide()
            scene.addItem(line)
            self._grid_lines.append(line)

        self._start_point: QPointF | None = None
        self._ratio: CropRatio = CropRatio.FREE
        self._angle: float = 0.0
        self._image_bounds: QRectF = QRectF()

    @property
    def is_selecting(self) -> bool:
        return self._start_point is not None

    @property
    def selection_rect(self) -> QRectF:
        return self._selection_item.rect()

    @property
    def has_selection(self) -> bool:
        return (
            self._selection_item.isVisible()
            and not self.selection_rect.isNull()
            and self.selection_rect.width() > 4
            and self.selection_rect.height() > 4
        )

    @property
    def ratio(self) -> CropRatio:
        return self._ratio

    @ratio.setter
    def ratio(self, value: CropRatio) -> None:
        self._ratio = value
        if self.has_selection:
            self._apply_ratio_constraint()

    @property
    def straighten_angle(self) -> float:
        return self._angle

    @straighten_angle.setter
    def straighten_angle(self, value: float) -> None:
        self._angle = max(-45.0, min(45.0, value))

    def begin(self, point: QPointF, image_bounds: QRectF) -> None:
        self._image_bounds = image_bounds
        self._start_point = self._clamp_point(point, image_bounds)
        self._selection_item.setRect(
            QRectF(self._start_point, self._start_point)
        )
        self._selection_item.show()
        self._update_grid()

    def update(self, point: QPointF, image_bounds: QRectF) -> None:
        if self._start_point is None:
            return
        self._image_bounds = image_bounds
        end_point = self._clamp_point(point, image_bounds)
        raw_rect = QRectF(self._start_point, end_point).normalized()
        constrained = raw_rect.intersected(image_bounds)
        self._selection_item.setRect(constrained)
        self._apply_ratio_constraint()
        self._update_grid()

    def finish(self, point: QPointF, image_bounds: QRectF) -> None:
        self.update(point, image_bounds)
        self._start_point = None

    def cancel(self) -> None:
        self._start_point = None
        self._selection_item.setRect(QRectF())
        self._selection_item.hide()
        for line in self._grid_lines:
            line.hide()

    def _apply_ratio_constraint(self) -> None:
        if self._ratio in (CropRatio.FREE, CropRatio.ORIGINAL):
            return
        ratio = self._ratio.value_tuple
        if ratio is None:
            return
        rw, rh = ratio
        rect = self._selection_item.rect()
        if rect.isNull():
            return
        current_ratio = rect.width() / rect.height()
        target_ratio = rw / rh
        if current_ratio > target_ratio:
            new_width = rect.height() * target_ratio
            delta = (rect.width() - new_width) / 2
            rect.adjust(delta, 0, -delta, 0)
        else:
            new_height = rect.width() / target_ratio
            delta = (rect.height() - new_height) / 2
            rect.adjust(0, delta, 0, -delta)
        rect = rect.intersected(self._image_bounds)
        self._selection_item.setRect(rect)

    def _update_grid(self) -> None:
        rect = self._selection_item.rect()
        if rect.isNull() or not self._selection_item.isVisible():
            for line in self._grid_lines:
                line.hide()
            return
        x1, y1 = rect.left(), rect.top()
        x2, y2 = rect.right(), rect.bottom()
        w3, h3 = rect.width() / 3, rect.height() / 3
        coords = [
            (x1 + w3, y1, x1 + w3, y2),
            (x1 + 2 * w3, y1, x1 + 2 * w3, y2),
            (x1, y1 + h3, x2, y1 + h3),
            (x1, y1 + 2 * h3, x2, y1 + 2 * h3),
        ]
        for line, (x1l, y1l, x2l, y2l) in zip(self._grid_lines, coords):
            line.setLine(x1l, y1l, x2l, y2l)
            line.show()

    @staticmethod
    def _clamp_point(point: QPointF, bounds: QRectF) -> QPointF:
        return QPointF(
            min(max(point.x(), bounds.left()), bounds.right()),
            min(max(point.y(), bounds.top()), bounds.bottom()),
        )
