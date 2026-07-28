#!/usr/bin/env python3
"""Photo Editor 2.0 — Effects Panel."""

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


class _SliderRow(QWidget):
    def __init__(self, label: str, minimum: int = 0, maximum: int = 100, parent=None):
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

    def reset(self) -> None:
        self._slider.setValue(0)

    def set_value(self, v: int) -> None:
        self._slider.setValue(v)


class EffectsPanel(QWidget):
    """Creative effects: Vignette, Dehaze, Grain."""

    valuesChanged = Signal(dict)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._sliders: dict[str, _SliderRow] = {}
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        title = QLabel("<b>Efekty</b>")
        title.setStyleSheet("color: #FFFFFF; font-size: 13px; padding-bottom: 4px;")
        layout.addWidget(title)

        for name, label in [
            ("vignette", "Winietowanie"),
            ("dehaze", "Usuwanie mgly"),
            ("grain", "Ziarno"),
        ]:
            row = _SliderRow(label, minimum=0, maximum=100)
            row._slider.valueChanged.connect(self._emit_change)
            self._sliders[name] = row
            layout.addWidget(row)

        reset_btn = QPushButton("Resetuj efekty")
        reset_btn.clicked.connect(self.reset)
        layout.addWidget(reset_btn)
        layout.addStretch()

        self._style_widget()

    def _emit_change(self) -> None:
        self.valuesChanged.emit(self.get_values())

    def get_values(self) -> dict[str, float]:
        return {k: float(v.value) for k, v in self._sliders.items()}

    def set_values(self, values: dict[str, float]) -> None:
        for k, v in values.items():
            if k in self._sliders:
                self._sliders[k].set_value(int(v))

    def reset(self) -> None:
        for row in self._sliders.values():
            row.reset()
        self.valuesChanged.emit(self.get_values())

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
                background: #888888;
                border-radius: 7px;
            }
            QSlider::handle:horizontal:hover {
                background: #AAAAAA;
            }
            QSlider::sub-page:horizontal {
                background: #555555;
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
