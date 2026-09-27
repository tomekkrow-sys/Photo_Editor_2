#!/usr/bin/env python3
"""Photo Editor 2.0 — Lens Corrections Panel."""

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

    def reset(self) -> None:
        self._slider.setValue(0)

    def set_value(self, v: int) -> None:
        self._slider.setValue(v)


class LensPanel(QWidget):
    """Lens corrections: Distortion, Vignette, Chromatic Aberration."""

    valuesChanged = Signal(dict)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._sliders: dict[str, _SliderRow] = {}
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        title = QLabel("<b>Korekcja obiektywu</b>")
        title.setStyleSheet("color: #4A9EFF; font-size: 11px; padding-bottom: 4px; letter-spacing: 1px;")
        layout.addWidget(title)

        for name, label in [
            ("distortion", "Dystorsja"),
            ("lens_vignette", "Winietowanie"),
            ("chromatic_aberration", "Aberracja chromat."),
        ]:
            row = _SliderRow(label)
            row._slider.valueChanged.connect(self._emit_change)
            self._sliders[name] = row
            layout.addWidget(row)

        reset_btn = QPushButton("Resetuj korekcje")
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
        pass  # Uses global theme
