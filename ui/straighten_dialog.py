#!/usr/bin/env python3
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QSlider,
)


class StraightenDialog(QDialog):
    """Angle picker for horizon straightening (-45..+45 degrees)."""

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setWindowTitle("Wyprostuj horyzont")

        layout = QFormLayout(self)

        row = QHBoxLayout()
        self.angle_slider = QSlider(Qt.Orientation.Horizontal)
        self.angle_slider.setRange(-450, 450)
        self.angle_slider.setValue(0)
        self.angle_label = QLabel("0.0°")
        self.angle_slider.valueChanged.connect(
            lambda v: self.angle_label.setText(f"{v / 10:.1f}°")
        )
        row.addWidget(self.angle_slider)
        row.addWidget(self.angle_label)
        layout.addRow("Kat (w lewo +):", row)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_angle(self) -> float:
        return self.angle_slider.value() / 10.0
