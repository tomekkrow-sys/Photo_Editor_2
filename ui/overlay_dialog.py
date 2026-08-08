#!/usr/bin/env python3
from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QSlider,
)
from PySide6.QtCore import Qt

from core.filters import BLEND_MODES


class OverlayDialog(QDialog):
    """Settings for overlaying an image as a layer (opacity + blend mode)."""

    def __init__(self, parent, name: str) -> None:
        super().__init__(parent)
        self.setWindowTitle("Naloz warstwe: " + name)

        layout = QFormLayout(self)

        row = QHBoxLayout()
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_label = QLabel("100%")
        self.opacity_slider.valueChanged.connect(
            lambda v: self.opacity_label.setText(f"{v}%")
        )
        row.addWidget(self.opacity_slider)
        row.addWidget(self.opacity_label)
        layout.addRow("Krycie:", row)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(BLEND_MODES)
        layout.addRow("Tryb mieszania:", self.mode_combo)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_opacity(self) -> float:
        return self.opacity_slider.value() / 100.0

    def get_mode(self) -> str:
        return self.mode_combo.currentText()
