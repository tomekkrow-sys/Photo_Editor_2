#!/usr/bin/env python3
"""Color grading dialog with 3-way wheels for shadows, midtones, highlights."""
from __future__ import annotations
import math
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QRadialGradient
from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QSlider, QWidget, QGroupBox, QFormLayout, QDoubleSpinBox,
)


class ColorWheel(QWidget):
    """A draggable color wheel that returns an (R, G, B) tint."""
    color_changed = Signal(int, int, int)

    def __init__(self, label: str = "", parent=None):
        super().__init__(parent)
        self._label = label
        self._hue = 0.0       # 0..360
        self._sat = 0.0       # 0..1 (distance from center)
        self._dragging = False
        self.setFixedSize(180, 180)
        self.setCursor(Qt.CrossCursor)

    def _point_to_color(self, px, py):
        cx, cy = self.width() / 2, self.height() / 2
        dx = px - cx
        dy = py - cy
        r = min(cx, cy) - 4
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > r:
            dx = dx / dist * r
            dy = dy / dist * r
            dist = r
        self._sat = dist / r
        angle = math.atan2(dy, dx)
        self._hue = math.degrees(angle) % 360
        self.update()
        self._emit_color()

    def _emit_color(self):
        r, g, b = self._hsv_to_rgb(self._hue, self._sat)
        self.color_changed.emit(r, g, b)

    @staticmethod
    def _hsv_to_rgb(hue, sat):
        c = int(sat * 255)
        h = hue / 60.0
        x = int(c * (1 - abs(h % 2 - 1)))
        if h < 1:
            return c, x, 0
        elif h < 2:
            return x, c, 0
        elif h < 3:
            return 0, c, x
        elif h < 4:
            return 0, x, c
        elif h < 5:
            return x, 0, c
        else:
            return c, 0, x

    def set_rgb(self, r, g, b):
        # Convert RGB back to hue/sat
        rf, gf, bf = r / 255.0, g / 255.0, b / 255.0
        mx = max(rf, gf, bf)
        mn = min(rf, gf, bf)
        self._sat = mx - mn if mx > 0 else 0
        if self._sat == 0:
            self._hue = 0
        else:
            if mx == rf:
                self._hue = (60 * ((gf - bf) / self._sat)) % 360
            elif mx == gf:
                self._hue = (60 * ((bf - rf) / self._sat) + 120) % 360
            else:
                self._hue = (60 * ((rf - gf) / self._sat) + 240) % 360
        self.update()

    def get_rgb(self):
        if self._sat == 0:
            return None
        return self._hsv_to_rgb(self._hue, self._sat)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx, cy = self.width() / 2, self.height() / 2
        r = min(cx, cy) - 4

        # Draw wheel
        grad = QRadialGradient(cx, cy, r)
        for i in range(360):
            rf, gf, bf = [v / 255.0 for v in self._hsv_to_rgb(i, 1.0)]
            grad.setColorAt(i / 360.0, QColor(int(rf * 255), int(gf * 255), int(bf * 255)))
        grad.setColorAt(0.0, QColor(128, 128, 128))
        grad.setColorAt(1.0, QColor(int(self._hsv_to_rgb(self._hue, 1.0)[0]),
                                     int(self._hsv_to_rgb(self._hue, 1.0)[1]),
                                     int(self._hsv_to_rgb(self._hue, 1.0)[2])))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(grad))
        p.drawEllipse(4, 4, int(r * 2), int(r * 2))

        # Draw indicator
        angle = math.radians(self._hue)
        ix = cx + math.cos(angle) * self._sat * r
        iy = cy + math.sin(angle) * self._sat * r
        p.setPen(QPen(QColor("#FFFFFF"), 2))
        p.setBrush(QBrush(QColor(255, 255, 255, 100)))
        p.drawEllipse(int(ix) - 7, int(iy) - 7, 14, 14)

        # Label
        if self._label:
            p.setPen(QColor("#FFFFFF"))
            p.drawText(self.rect().adjusted(0, self.height() - 20, 0, 0),
                       Qt.AlignmentFlag.AlignHCenter, self._label)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._point_to_color(event.position().x(), event.position().y())

    def mouseMoveEvent(self, event):
        if self._dragging:
            self._point_to_color(event.position().x(), event.position().y())

    def mouseReleaseEvent(self, event):
        self._dragging = False

    def reset(self):
        self._hue = 0
        self._sat = 0
        self.update()
        self.color_changed.emit(128, 128, 128)


class ColorGradingDialog(QDialog):
    """Color grading dialog with 3 wheels."""

    def __init__(self, parent=None, shadows=None, midtones=None, highlights=None):
        super().__init__(parent)
        self.setWindowTitle("Color Grading")
        self.setMinimumWidth(620)
        self._build_ui(shadows, midtones, highlights)

    def _build_ui(self, shadows, midtones, highlights):
        lay = QVBoxLayout(self)

        title = QLabel("Przeciagaj kolory na kolach — cienie, srodki, swiatla")
        title.setStyleSheet("color: #ccc; font-size: 11px;")
        lay.addWidget(title)

        wheels_row = QHBoxLayout()

        # Shadows
        self.shadow_wheel = ColorWheel("SHADOWS")
        if shadows:
            self.shadow_wheel.set_rgb(*shadows)
        self.shadow_wheel.color_changed.connect(self._on_shadow)
        wheels_row.addWidget(self.shadow_wheel)

        # Midtones
        self.mid_wheel = ColorWheel("MIDTONES")
        if midtones:
            self.mid_wheel.set_rgb(*midtones)
        self.mid_wheel.color_changed.connect(self._on_mid)
        wheels_row.addWidget(self.mid_wheel)

        # Highlights
        self.hi_wheel = ColorWheel("HIGHLIGHTS")
        if highlights:
            self.hi_wheel.set_rgb(*highlights)
        self.hi_wheel.color_changed.connect(self._on_hi)
        wheels_row.addWidget(self.hi_wheel)

        lay.addLayout(wheels_row)

        # Info labels
        info_row = QHBoxLayout()
        self.shadow_info = QLabel("")
        self.shadow_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mid_info = QLabel("")
        self.mid_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hi_info = QLabel("")
        self.hi_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_row.addWidget(self.shadow_info)
        info_row.addWidget(self.mid_info)
        info_row.addWidget(self.hi_info)
        lay.addLayout(info_row)

        # Intensity slider
        int_row = QHBoxLayout()
        int_row.addWidget(QLabel("Intensywnosc:"))
        self.intensity_slider = QSlider(Qt.Orientation.Horizontal)
        self.intensity_slider.setRange(10, 100)
        self.intensity_slider.setValue(30)
        self.intensity_label = QLabel("30%")
        self.intensity_slider.valueChanged.connect(lambda v: self.intensity_label.setText(f"{v}%"))
        int_row.addWidget(self.intensity_slider)
        int_row.addWidget(self.intensity_label)
        lay.addLayout(int_row)

        # Buttons
        btn_row = QHBoxLayout()
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self._reset_all)
        ok = QPushButton("OK")
        ok.clicked.connect(self.accept)
        cancel = QPushButton("Anuluj")
        cancel.clicked.connect(self.reject)
        btn_row.addWidget(reset_btn)
        btn_row.addWidget(ok)
        btn_row.addWidget(cancel)
        lay.addLayout(btn_row)

        self._on_shadow(128, 128, 128)
        self._on_mid(128, 128, 128)
        self._on_hi(128, 128, 128)

    def _on_shadow(self, r, g, b):
        self.shadow_info.setText(f"Cienie: ({r}, {g}, {b})")

    def _on_mid(self, r, g, b):
        self.mid_info.setText(f"Srodki: ({r}, {g}, {b})")

    def _on_hi(self, r, g, b):
        self.hi_info.setText(f"Swiatla: ({r}, {g}, {b})")

    def _reset_all(self):
        self.shadow_wheel.reset()
        self.mid_wheel.reset()
        self.hi_wheel.reset()

    def get_shadows(self):
        c = self.shadow_wheel.get_rgb()
        return c if c else None

    def get_midtones(self):
        c = self.mid_wheel.get_rgb()
        return c if c else None

    def get_highlights(self):
        c = self.hi_wheel.get_rgb()
        return c if c else None

    def get_intensity(self) -> float:
        return self.intensity_slider.value() / 100.0
