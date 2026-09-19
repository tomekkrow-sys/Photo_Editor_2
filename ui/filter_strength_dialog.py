#!/usr/bin/env python3
"""Filter strength dialog - universal slider for filter intensity."""
from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QHBoxLayout, QLabel,
    QSlider, QVBoxLayout,
)
from config.i18n import t


class FilterStrengthDialog(QDialog):
    """Simple dialog with a strength slider for filter application."""

    def __init__(self, filter_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(filter_name)
        self.setMinimumWidth(320)
        self.setModal(True)

        lay = QVBoxLayout(self)

        # Filter name label
        name_lbl = QLabel(filter_name)
        name_lbl.setStyleSheet("font-weight: bold; font-size: 14px;")
        lay.addWidget(name_lbl)

        # Strength slider
        row = QHBoxLayout()
        row.addWidget(QLabel(t("filter_strength")))
        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setRange(1, 100)
        self._slider.setValue(75)
        self._slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._slider.setTickInterval(25)
        row.addWidget(self._slider)
        self._val = QLabel("75%")
        self._val.setFixedWidth(40)
        self._slider.valueChanged.connect(lambda v: self._val.setText(f"{v}%"))
        row.addWidget(self._val)
        lay.addLayout(row)

        # Blend info
        self._info = QLabel(t("filter_blend_info"))
        self._info.setStyleSheet("color: #888; font-size: 10px;")
        lay.addWidget(self._info)

        # Buttons
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        btns.button(QDialogButtonBox.StandardButton.Ok).setText(t("ok"))
        btns.button(QDialogButtonBox.StandardButton.Cancel).setText(t("cancel"))
        lay.addWidget(btns)

    def get_strength(self) -> float:
        return self._slider.value() / 100.0
