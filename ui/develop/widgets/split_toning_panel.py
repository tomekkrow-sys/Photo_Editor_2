#!/usr/bin/env python3
"""Photo Editor 2.0 — Split Toning Panel."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class _SplitToneRow(QWidget):
    """Split Toning row: Hue/Sat for Shadows and Highlights."""

    valueChanged = Signal(dict)

    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 2, 0, 2)

        self._label = QLabel(label)
        self._label.setFixedWidth(80)
        self._layout.addWidget(self._label)

        self._hue_slider = QSlider(Qt.Orientation.Horizontal)
        self._hue_slider.setRange(0, 360)
        self._hue_slider.setValue(180)
        self._layout.addWidget(self._hue_slider, 1)

        self._hue_label = QLabel("180")
        self._hue_label.setFixedWidth(36)
        self._hue_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._layout.addWidget(self._hue_label)

        self._sat_slider = QSlider(Qt.Orientation.Horizontal)
        self._sat_slider.setRange(0, 100)
        self._sat_slider.setValue(50)
        self._layout.addWidget(self._sat_slider, 1)

        self._sat_label = QLabel("50")
        self._sat_label.setFixedWidth(36)
        self._sat_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._layout.addWidget(self._sat_label)

        self._hue_slider.valueChanged.connect(self._on_value_changed)
        self._sat_slider.valueChanged.connect(self._on_value_changed)

    @property
    def hue(self) -> int:
        return self._hue_slider.value()

    @property
    def saturation(self) -> int:
        return self._sat_slider.value()

    def _on_value_changed(self) -> None:
        self._hue_label.setText(str(self._hue_slider.value()))
        self._sat_label.setText(str(self._sat_slider.value()))
        self.valueChanged.emit({"hue": self.hue, "sat": self.saturation})

    def reset(self) -> None:
        self._hue_slider.setValue(180)
        self._sat_slider.setValue(50)
        self._on_value_changed()

    def set_values(self, hue: int, sat: int) -> None:
        self._hue_slider.setValue(hue)
        self._sat_slider.setValue(sat)
        self._on_value_changed()


class SplitToningPanel(QWidget):
    """Split Toning controls: Shadows and Highlights hue/saturation."""

    valuesChanged = Signal(dict)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._shadows_row = _SplitToneRow("Cienie")
        self._highlights_row = _SplitToneRow("Swiatla")
        self._balance_slider = QSlider(Qt.Orientation.Horizontal)
        self._balance_slider.setRange(-100, 100)
        self._balance_slider.setValue(0)

        self._shadows_row.valueChanged.connect(self._emit_change)
        self._highlights_row.valueChanged.connect(self._emit_change)
        self._balance_slider.valueChanged.connect(self._emit_change)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        title = QLabel("<b>Split Toning</b>")
        title.setStyleSheet("color: #FFFFFF; font-size: 13px; padding-bottom: 4px;")
        layout.addWidget(title)

        layout.addWidget(self._shadows_row)
        layout.addWidget(self._highlights_row)

        balance_layout = QHBoxLayout()
        balance_layout.addWidget(QLabel("Balans"))
        balance_layout.addWidget(self._balance_slider)
        self._balance_label = QLabel("0")
        self._balance_label.setFixedWidth(36)
        self._balance_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        balance_layout.addWidget(self._balance_label)
        layout.addLayout(balance_layout)

        reset_btn = QPushButton("Resetuj Split Toning")
        reset_btn.clicked.connect(self.reset)
        layout.addWidget(reset_btn)
        layout.addStretch()

        self._style_widget()

    def _emit_change(self) -> None:
        self.valuesChanged.emit(self.get_values())

    def get_values(self) -> dict:
        return {
            "shadows": {"hue": self._shadows_row.hue, "sat": self._shadows_row.saturation},
            "highlights": {"hue": self._highlights_row.hue, "sat": self._highlights_row.saturation},
            "balance": self._balance_slider.value(),
        }

    def set_values(self, values: dict) -> None:
        if "shadows" in values:
            self._shadows_row.set_values(values["shadows"]["hue"], values["shadows"]["sat"])
        if "highlights" in values:
            self._highlights_row.set_values(values["highlights"]["hue"], values["highlights"]["sat"])
        if "balance" in values:
            self._balance_slider.setValue(values["balance"])
            self._balance_label.setText(str(values["balance"]))

    def reset(self) -> None:
        self._shadows_row.reset()
        self._highlights_row.reset()
        self._balance_slider.setValue(0)
        self._balance_label.setText("0")
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
                background: #FF9800;
                border-radius: 7px;
            }
            QSlider::handle:horizontal:hover {
                background: #FFB74D;
            }
            QSlider::sub-page:horizontal {
                background: #FF9800;
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
