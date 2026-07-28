#!/usr/bin/env python3
"""Photo Editor 2.0 — Spot / Clone Stamp Tool."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QImage, QPainter, QRadialGradient


class SpotMode(Enum):
    """Spot removal modes."""
    CLONE = auto()
    HEAL = auto()


@dataclass
class SpotSettings:
    """Spot tool configuration."""
    size: float = 20.0
    hardness: float = 0.5
    opacity: float = 1.0
    mode: SpotMode = SpotMode.HEAL
    sample_all_layers: bool = False
    aligned: bool = True


class SpotTool:
    """Clone stamp / healing brush for retouching."""

    def __init__(self) -> None:
        self.settings = SpotSettings()
        self._source_point: QPointF | None = None
        self._last_paint_point: QPointF | None = None
        self._offset: QPointF = QPointF(0, 0)
        self._is_sampling = False
        self._is_painting = False
        self._sample_image: QImage | None = None

    @property
    def is_sampling(self) -> bool:
        return self._is_sampling

    @property
    def is_painting(self) -> bool:
        return self._is_painting

    def set_sample_source(self, point: QPointF, image: QImage) -> None:
        self._source_point = point
        self._sample_image = image.copy()
        self._offset = QPointF(0, 0)

    def begin_paint(self, point: QPointF, target: QImage) -> None:
        if self._source_point is None or self._sample_image is None:
            return
        self._is_painting = True
        self._last_paint_point = point
        if not self.settings.aligned:
            self._offset = QPointF(
                self._source_point.x() - point.x(),
                self._source_point.y() - point.y(),
            )
        self._stamp(point, target)

    def update_paint(self, point: QPointF, target: QImage) -> None:
        if not self._is_painting or self._last_paint_point is None:
            return
        distance = ((point.x() - self._last_paint_point.x()) ** 2 +
                    (point.y() - self._last_paint_point.y()) ** 2) ** 0.5
        spacing = self.settings.size * 0.25
        if distance < spacing:
            return
        steps = int(distance / spacing)
        for i in range(1, steps + 1):
            t = i / steps
            interp = QPointF(
                self._last_paint_point.x() + (point.x() - self._last_paint_point.x()) * t,
                self._last_paint_point.y() + (point.y() - self._last_paint_point.y()) * t,
            )
            self._stamp(interp, target)
        self._last_paint_point = point

    def finish_paint(self) -> None:
        self._is_painting = False
        self._last_paint_point = None

    def cancel(self) -> None:
        self._is_painting = False
        self._is_sampling = False
        self._last_paint_point = None

    def _stamp(self, point: QPointF, target: QImage) -> None:
        if target.isNull() or self._sample_image is None or self._sample_image.isNull():
            return
        r = self.settings.size / 2
        stamp_rect = target.rect().intersected(
            target.rect().adjusted(
                int(point.x() - r), int(point.y() - r),
                int(point.x() + r), int(point.y() + r),
            )
        )
        if stamp_rect.isEmpty():
            return
        if self.settings.aligned:
            src_point = QPointF(
                point.x() + (self._source_point.x() - self._last_paint_point.x()),
                point.y() + (self._source_point.y() - self._last_paint_point.y()),
            ) if self._last_paint_point else self._source_point
        else:
            src_point = QPointF(point.x() + self._offset.x(), point.y() + self._offset.y())
        src_rect = self._sample_image.rect().intersected(
            self._sample_image.rect().adjusted(
                int(src_point.x() - r), int(src_point.y() - r),
                int(src_point.x() + r), int(src_point.y() + r),
            )
        )
        if src_rect.isEmpty():
            return
        patch = self._sample_image.copy(src_rect)
        if self.settings.mode == SpotMode.HEAL:
            dest_patch = target.copy(stamp_rect)
            patch = self._blend_heal(patch, dest_patch)
        patch = self._apply_soft_edge(patch, r)
        painter = QPainter(target)
        painter.setOpacity(self.settings.opacity)
        painter.drawImage(stamp_rect.topLeft(), patch)
        painter.end()

    def _blend_heal(self, source: QImage, dest: QImage) -> QImage:
        result = source.copy()
        painter = QPainter(result)
        painter.setOpacity(0.5)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Overlay)
        painter.drawImage(0, 0, dest)
        painter.end()
        return result

    def _apply_soft_edge(self, image: QImage, radius: float) -> QImage:
        mask = QImage(image.size(), QImage.Format.Format_ARGB32)
        mask.fill(Qt.GlobalColor.transparent)
        painter = QPainter(mask)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx, cy = image.width() / 2, image.height() / 2
        grad = QRadialGradient(QPointF(cx, cy), radius)
        grad.setColorAt(0.0, QColor(255, 255, 255, 255))
        fade = self.settings.hardness
        grad.setColorAt(fade, QColor(255, 255, 255, 255))
        grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setBrush(grad)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(mask.rect())
        painter.end()
        result = image.copy()
        mask_painter = QPainter(result)
        mask_painter.setCompositionMode(
            QPainter.CompositionMode.CompositionMode_DestinationIn
        )
        mask_painter.drawImage(0, 0, mask)
        mask_painter.end()
        return result
