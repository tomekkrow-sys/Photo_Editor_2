#!/usr/bin/env python3
"""Photo Editor 2.0 — HSL / Color Grading Panel."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class _HSLRow(QWidget):
    """Single HSL control row for a specific color channel."""

    valueChanged = Signal(int)

    def __init__(self, label: str, minimum: int = -100, maximum: int = 100, parent=None):
        super().__init__(parent)
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 2, 0, 2)

        self._label = QLabel(label)
        self._label.setFixedWidth(80)
        self._layout.addWidget(self._label)

        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setRange(minimum, maximum)
        self._slider.setValue(0)
        self._layout.addWidget(self._slider, 1)

        self._value_label = QLabel("0")
        self._value_label.setFixedWidth(36)
        self._value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._layout.addWidget(self._value_label)

        self._slider.valueChanged.connect(self._on_value_changed)

    @property
    def value(self) -> int:
        return self._slider.value()

    def _on_value_changed(self, v: int) -> None:
        self._value_label.setText(str(v))
        self.valueChanged.emit(v)

    def reset(self) -> None:
        self._slider.setValue(0)

    def set_value(self, v: int) -> None:
        self._slider.setValue(v)


class ColorGradingPanel(QWidget):
    """HSL / Color Grading controls for Shadows, Midtones, Highlights."""

    valuesChanged = Signal(dict)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._sliders_hsl: dict[str, dict[str, _HSLRow]] = {}
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        title = QLabel("<b>Kolor / HSL</b>")
        title.setStyleSheet("color: #FFFFFF; font-size: 13px; padding-bottom: 4px;")
        layout.addWidget(title)

        for section in ["Cienie", "Midtones", "Swiatla"]:
            section_layout = QVBoxLayout()
            section_title = QLabel(f"<b>{section}</b>")
            section_title.setStyleSheet("color: #888888; font-size: 12px;")
            section_layout.addWidget(section_title)

            hsl_layout = QHBoxLayout()
            hsl_layout.setContentsMargins(10, 2, 10, 2)

            for name, label in [
                ("hue", "Odcien"),
                ("saturation", "Nasycenie"),
                ("luminance", "Jasność"),
            ]:
                row = _HSLRow(label, minimum=-50, maximum=50)
                row._slider.valueChanged.connect(self._emit_change)
                if section not in self._sliders_hsl:
                    self._sliders_hsl[section] = {}
                self._sliders_hsl[section][name] = row
                hsl_layout.addWidget(row)

            section_layout.addLayout(hsl_layout)
            layout.addLayout(section_layout)

        reset_btn = QPushButton("Resetuj kolor")
        reset_btn.clicked.connect(self.reset)
        layout.addWidget(reset_btn)
        layout.addStretch()

        self._style_widget()

    def _emit_change(self) -> None:
        self.valuesChanged.emit(self.get_values())

    def get_values(self) -> dict[str, dict[str, float]]:
        result = {}
        for section, hsl_dict in self._sliders_hsl.items():
            result[section] = {k: float(v.value) for k, v in hsl_dict.items()}
        return result

    def set_values(self, values: dict[str, dict[str, float]]) -> None:
        for section, hsl_dict in values.items():
            if section in self._sliders_hsl:
                for name, val in hsl_dict.items():
                    if name in self._sliders_hsl[section]:
                        self._sliders_hsl[section][name].set_value(int(val))

    def reset(self) -> None:
        for section_dict in self._sliders_hsl.values():
            for row in section_dict.values():
                row.reset()
        self._emit_change()

    def _style_widget(self):
        self.setStyleSheet("""
            QWidget {
                background: #1E1E1E;
                color: #CCCCCC;
                font-family: "Segoe UI", "Ubuntu", sans-serif;
                font-size: 12px;
            }
            QLabel {
                color: #AAAAAA;
                padding: 2px 0px;
            }
            QSlider::groove:horizontal {
                height: 4px;
                background: #333333;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                width: 14px;
                height: 14px;
                margin: -5px 0;
                background: #4A9EFF;
                border-radius: 7px;
            }
            QSlider::handle:horizontal:hover {
                background: #88CCFF;
            }
            QSlider::sub-page:horizontal {
                background: #4A9EFF;
                border-radius: 2px;
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
