#!/usr/bin/env python3
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSlider,
)

from core.filters import WATERMARK_POSITIONS


class WatermarkDialog(QDialog):
    """Text watermark settings (text, position, opacity)."""

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setWindowTitle("Znak wodny")

        layout = QFormLayout(self)

        self.text_edit = QLineEdit()
        self.text_edit.setPlaceholderText("np. (c) Jan Kowalski 2026")
        layout.addRow("Tekst:", self.text_edit)

        self.position_combo = QComboBox()
        self.position_combo.addItems(WATERMARK_POSITIONS)
        self.position_combo.setCurrentText("Prawy dolny rog")
        layout.addRow("Pozycja:", self.position_combo)

        row = QHBoxLayout()
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(10, 100)
        self.opacity_slider.setValue(60)
        self.opacity_label = QLabel("60%")
        self.opacity_slider.valueChanged.connect(
            lambda v: self.opacity_label.setText(f"{v}%")
        )
        row.addWidget(self.opacity_slider)
        row.addWidget(self.opacity_label)
        layout.addRow("Krycie:", row)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_text(self) -> str:
        return self.text_edit.text().strip()

    def get_position(self) -> str:
        return self.position_combo.currentText()

    def get_opacity(self) -> float:
        return self.opacity_slider.value() / 100.0
