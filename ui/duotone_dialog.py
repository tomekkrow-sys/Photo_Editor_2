#!/usr/bin/env python3
"""Duotone custom color dialog."""
from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog, QDialog, QDialogButtonBox, QHBoxLayout,
    QLabel, QPushButton, QVBoxLayout,
)
from config.i18n import t


class DuotoneDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Duotone")
        self.setMinimumWidth(300)
        self.setModal(True)

        self._color1 = QColor("#FF6B35")
        self._color2 = QColor("#004E89")

        lay = QVBoxLayout(self)

        # Color 1
        row1 = QHBoxLayout()
        row1.addWidget(QLabel(t("duotone_color1")))
        self._btn1 = QPushButton()
        self._btn1.setFixedSize(80, 30)
        self._btn1.setStyleSheet(f"background: {self._color1.name()}; border: 1px solid #666;")
        self._btn1.clicked.connect(self._pick1)
        row1.addWidget(self._btn1)
        row1.addStretch()
        lay.addLayout(row1)

        # Color 2
        row2 = QHBoxLayout()
        row2.addWidget(QLabel(t("duotone_color2")))
        self._btn2 = QPushButton()
        self._btn2.setFixedSize(80, 30)
        self._btn2.setStyleSheet(f"background: {self._color2.name()}; border: 1px solid #666;")
        self._btn2.clicked.connect(self._pick2)
        row2.addWidget(self._btn2)
        row2.addStretch()
        lay.addLayout(row2)

        # Preview strip
        self._preview = QLabel()
        self._preview.setFixedHeight(30)
        self._update_preview()
        lay.addWidget(self._preview)

        # Buttons
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        btns.button(QDialogButtonBox.StandardButton.Ok).setText(t("ok"))
        btns.button(QDialogButtonBox.StandardButton.Cancel).setText(t("cancel"))
        lay.addWidget(btns)

    def _pick1(self):
        c = QColorDialog.getColor(self._color1, self)
        if c.isValid():
            self._color1 = c
            self._btn1.setStyleSheet(f"background: {c.name()}; border: 1px solid #666;")
            self._update_preview()

    def _pick2(self):
        c = QColorDialog.getColor(self._color2, self)
        if c.isValid():
            self._color2 = c
            self._btn2.setStyleSheet(f"background: {c.name()}; border: 1px solid #666;")
            self._update_preview()

    def _update_preview(self):
        self._preview.setStyleSheet(
            f"background: qlineargradient(x1:0, x2:1, stop:0 {self._color1.name()}, stop:1 {self._color2.name()});"
            f"border: 1px solid #444;"
        )

    def get_colors(self) -> tuple[str, str]:
        return self._color1.name(), self._color2.name()
