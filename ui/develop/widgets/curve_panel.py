#!/usr/bin/env python3
"""Photo Editor 2.0 — Tone Curve Panel with Point Curve and Color Wheels."""

from __future__ import annotations

from math import atan2

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class PointCurveWidget(QWidget):
    """Interactive point-based tone curve (RGB or Gray)."""

    curveChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._points: list[tuple[int, int]] = [
            (0, 0), (32, 32), (64, 64), (96, 96),
            (128, 128), (160, 160), (192, 192), (224, 224), (255, 255)
        ]
        self._dragging_point: int | None = None
        self._min_value = 0
        self._max_value = 255

        self.setMinimumSize(200, 200)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        painter.fillRect(self.rect(), QColor("#1E1E1E"))

        grid_color = QColor("#333333")
        pen = QPen(grid_color, 1)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)

        for i in range(0, 256, 64):
            x = int(i / 255 * width)
            y = int(i / 255 * height)
            painter.drawLine(x, 0, x, height)
            painter.drawLine(0, y, width, y)

        curve_color = QColor("#4A9EFF")
        pen = QPen(curve_color, 3)
        painter.setPen(pen)

        points_scaled = [
            (int(x / 255 * width), int((255 - y) / 255 * height))
            for x, y in self._points
        ]

        painter.drawPolyline(points_scaled)

        for i, (px, py) in enumerate(points_scaled):
            is_end = i == 0 or i == len(points_scaled) - 1
            if is_end:
                radius = 8
            else:
                radius = 6

            painter.setBrush(QColor("#FFFFFF") if i == self._dragging_point else QColor("#888888"))
            painter.drawEllipse(px - radius, py - radius, radius * 2, radius * 2)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._start_drag(event.position().x(), event.position().y())

    def mouseMoveEvent(self, event):
        if self._dragging_point is not None:
            self._update_point(event.position().x(), event.position().y())
            self.curveChanged.emit()
            self.update()

    def mouseReleaseEvent(self, event):
        if self._dragging_point is not None:
            self._end_drag(event.position().x(), event.position().y())
            self.curveChanged.emit()

    def _start_drag(self, x: float, y: float):
        width = self.width()
        height = self.height()

        for i, (px, py) in enumerate(self._points):
            screen_x = int(px / 255 * width)
            screen_y = int((255 - py) / 255 * height)
            dist = ((x - screen_x) ** 2 + (y - screen_y) ** 2) ** 0.5
            if dist < 15:
                self._dragging_point = i
                break

    def _update_point(self, x: float, y: float):
        if self._dragging_point is None:
            return

        width = self.width()
        height = self.height()

        x = max(0, min(x, width))
        y = max(0, min(y, height))

        self._points[self._dragging_point] = (
            int(x / width * 255),
            int(255 - y / height * 255)
        )

    def _end_drag(self, x: float, y: float):
        self._update_point(x, y)
        self._dragging_point = None

    def get_curve_points(self) -> list[tuple[int, int]]:
        return self._points.copy()

    def set_curve_points(self, points: list[tuple[int, int]]) -> None:
        self._points = points.copy()
        self.update()


class ColorWheelWidget(QWidget):
    """Color wheel for Color Grading (shadows/midtones/highlights)."""

    colorChanged = Signal(QColor)

    def __init__(self, label: str = "", parent=None):
        super().__init__(parent)
        self._label = label
        self._color = QColor(128, 128, 128)
        self._angle = 0.0
        self._radius = 0
        self._min_size = 120

        self.setCursor(Qt.CursorShape.CrossCursor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        size = min(self.width(), self._min_size)
        center = self.width() // 2, self.height() // 2

        painter.setBrush(self._color)
        painter.setPen(QPen(QColor("#CCCCCC"), 2))
        painter.drawEllipse(
            center[0] - size // 2,
            center[1] - size // 2,
            size,
            size,
        )

        if self._label:
            painter.setPen(QColor("#FFFFFF"))
            painter.drawText(
                center[0] - 40,
                center[1] + size // 2 + 20,
                80,
                20,
                Qt.AlignmentFlag.AlignCenter,
                self._label,
            )

    def mousePressEvent(self, event):
        self._angle = self._compute_angle(event.position().x(), event.position().y())
        self._color = self._angle_to_color(self._angle)
        self.colorChanged.emit(self._color)
        self.update()

    def mouseMoveEvent(self, event):
        self._angle = self._compute_angle(event.position().x(), event.position().y())
        self._color = self._angle_to_color(self._angle)
        self.colorChanged.emit(self._color)
        self.update()

    def _compute_angle(self, x: float, y: float) -> float:
        center_x, center_y = self.width() // 2, self.height() // 2
        dx = x - center_x
        dy = y - center_y
        angle = (180 / 3.14159) * atan2(dy, dx)
        return angle + 180 if angle < 0 else angle

    def _angle_to_color(self, angle: float) -> QColor:
        hue = int(angle)
        return QColor.fromHsv(hue, 128, 200)

    def color(self) -> QColor:
        return self._color

    def set_color(self, color: QColor) -> None:
        self._color = color
        self._angle = color.hue()
        self.update()


class ToneCurvePanel(QWidget):
    """Tone Curve panel with Point Curve and Color Wheels."""

    valuesChanged = Signal(dict)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._curve_widget = PointCurveWidget()
        self._shadows_wheel = ColorWheelWidget("Cienie")
        self._midtones_wheel = ColorWheelWidget("Midtones")
        self._highlights_wheel = ColorWheelWidget("Swiatla")

        self._curve_widget.curveChanged.connect(self._emit_change)
        self._shadows_wheel.colorChanged.connect(self._emit_change)
        self._midtones_wheel.colorChanged.connect(self._emit_change)
        self._highlights_wheel.colorChanged.connect(self._emit_change)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        title = QLabel("<b>Tone Curve</b>")
        title.setStyleSheet("color: #FFFFFF; font-size: 13px; padding-bottom: 4px;")
        layout.addWidget(title)

        layout.addWidget(self._curve_widget)

        wheels_layout = QHBoxLayout()
        wheels_layout.addWidget(self._shadows_wheel)
        wheels_layout.addWidget(self._midtones_wheel)
        wheels_layout.addWidget(self._highlights_wheel)
        layout.addLayout(wheels_layout)

        reset_btn = QPushButton("Resetuj tone curve")
        reset_btn.clicked.connect(self.reset)
        layout.addWidget(reset_btn)
        layout.addStretch()

        self._style_widget()

    def _emit_change(self) -> None:
        self.valuesChanged.emit(self.get_values())

    def get_values(self) -> dict:
        return {
            "point_curve": self._curve_widget.get_curve_points(),
            "shadows_color": self._shadows_wheel.color(),
            "midtones_color": self._midtones_wheel.color(),
            "highlights_color": self._highlights_wheel.color(),
        }

    def set_values(self, values: dict) -> None:
        if "point_curve" in values:
            self._curve_widget.set_curve_points(values["point_curve"])
        if "shadows_color" in values:
            self._shadows_wheel.set_color(values["shadows_color"])
        if "midtones_color" in values:
            self._midtones_wheel.set_color(values["midtones_color"])
        if "highlights_color" in values:
            self._highlights_wheel.set_color(values["highlights_color"])

    def reset(self) -> None:
        self._curve_widget.set_curve_points([
            (0, 0), (32, 32), (64, 64), (96, 96),
            (128, 128), (160, 160), (192, 192), (224, 224), (255, 255)
        ])
        self._shadows_wheel.set_color(QColor(128, 128, 128))
        self._midtones_wheel.set_color(QColor(128, 128, 128))
        self._highlights_wheel.set_color(QColor(128, 128, 128))
        self._emit_change()

    def _style_widget(self):
        self.setStyleSheet("""
            QWidget {
                background: #1E1E1E;
                color: #CCCCCC;
                font-family: "Segoe UI", "Ubuntu", sans-serif;
                font-size: 12px;
            }
            QPushButton {
                background: #333333;
                border: 1px solid #444444;
                padding: 4px 12px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background: #444444;
            }
        """)


