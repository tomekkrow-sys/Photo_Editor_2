#!/usr/bin/env python3
from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QSpinBox,
)


class ResizeDialog(QDialog):
    """Dialog for resizing the image with optional aspect-ratio lock."""

    def __init__(self, parent, width: int, height: int) -> None:
        super().__init__(parent)
        self.setWindowTitle("Zmien rozmiar")
        self._ratio = width / height

        layout = QFormLayout(self)

        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 20000)
        self.width_spin.setValue(width)

        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 20000)
        self.height_spin.setValue(height)

        self.lock = QCheckBox("Zachowaj proporcje")
        self.lock.setChecked(True)

        layout.addRow("Szerokosc:", self.width_spin)
        layout.addRow("Wysokosc:", self.height_spin)
        layout.addRow(self.lock)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.width_spin.valueChanged.connect(self._on_width)
        self.height_spin.valueChanged.connect(self._on_height)

    def _on_width(self, value: int) -> None:
        if self.lock.isChecked():
            self.height_spin.blockSignals(True)
            self.height_spin.setValue(max(1, round(value / self._ratio)))
            self.height_spin.blockSignals(False)

    def _on_height(self, value: int) -> None:
        if self.lock.isChecked():
            self.width_spin.blockSignals(True)
            self.width_spin.setValue(max(1, round(value * self._ratio)))
            self.width_spin.blockSignals(False)

    def get_size(self) -> tuple[int, int]:
        return self.width_spin.value(), self.height_spin.value()
