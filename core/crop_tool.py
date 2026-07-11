#!/usr/bin/env python3
"""Rectangular crop selection tool."""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsScene

from config.colors import SELECTION_BORDER


class CropTool:
    """Manages a rectangular selection displayed in a graphics scene."""

    def __init__(self, scene: QGraphicsScene) -> None:
        self._selection_item = QGraphicsRectItem()
        self._selection_item.setZValue(1)
        self._selection_item.setBrush(Qt.BrushStyle.NoBrush)

        pen = QPen(QColor(SELECTION_BORDER), 2)
        pen.setCosmetic(True)
        self._selection_item.setPen(pen)
        self._selection_item.hide()

        scene.addItem(self._selection_item)

        self._start_point: QPointF | None = None

    @property
    def is_selecting(self) -> bool:
        return self._start_point is not None

    @property
    def selection_rect(self) -> QRectF:
        """Return the current selection in scene/image coordinates."""

        return self._selection_item.rect()

    @property
    def has_selection(self) -> bool:
        return (
            self._selection_item.isVisible()
            and not self.selection_rect.isNull()
        )

    def begin(self, point: QPointF, image_bounds: QRectF) -> None:
        """Begin a selection at a point constrained to the image."""

        self._start_point = self._clamp_point(point, image_bounds)
        self._selection_item.setRect(
            QRectF(self._start_point, self._start_point)
        )
        self._selection_item.show()

    def update(self, point: QPointF, image_bounds: QRectF) -> None:
        """Update the selection rectangle within image bounds."""

        if self._start_point is None:
            return

        end_point = self._clamp_point(point, image_bounds)
        selection = QRectF(self._start_point, end_point).normalized()

        self._selection_item.setRect(
            selection.intersected(image_bounds)
        )

    def finish(self, point: QPointF, image_bounds: QRectF) -> None:
        """Finish the current selection."""

        self.update(point, image_bounds)
        self._start_point = None

    def cancel(self) -> None:
        """Remove the current selection."""

        self._start_point = None
        self._selection_item.setRect(QRectF())
        self._selection_item.hide()

    @staticmethod
    def _clamp_point(point: QPointF, bounds: QRectF) -> QPointF:
        return QPointF(
            min(max(point.x(), bounds.left()), bounds.right()),
            min(max(point.y(), bounds.top()), bounds.bottom()),
        )
