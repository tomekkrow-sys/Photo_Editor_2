#!/usr/bin/env python3
"""Rotate by arbitrary angle dialog."""
from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSlider,
    QPushButton, QComboBox, QWidget, QSpinBox, QDoubleSpinBox,
)
from config.i18n import t


class RotateDialog(QDialog):
    """Modal dialog for rotating image by custom angle."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("rotate_custom"))
        self.setMinimumWidth(350)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Angle slider + spinbox
        angle_row = QHBoxLayout()
        angle_row.addWidget(QLabel(t("rotate_angle")))
        self._angle_slider = QSlider(Qt.Orientation.Horizontal)
        self._angle_slider.setRange(-180, 180)
        self._angle_slider.setValue(0)
        self._angle_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._angle_slider.setTickInterval(15)
        angle_row.addWidget(self._angle_slider)
        self._angle_spin = QDoubleSpinBox()
        self._angle_spin.setRange(-180.0, 180.0)
        self._angle_spin.setSingleStep(0.5)
        self._angle_spin.setSuffix("\u00b0")
        angle_row.addWidget(self._angle_spin)
        self._angle_slider.valueChanged.connect(
            lambda v: self._angle_spin.setValue(v))
        self._angle_spin.valueChanged.connect(
            lambda v: self._angle_slider.setValue(int(v)))
        layout.addLayout(angle_row)

        # Expand checkbox
        from PySide6.QtWidgets import QCheckBox
        self._expand_cb = QCheckBox(t("rotate_expand"))
        self._expand_cb.setChecked(True)
        layout.addWidget(self._expand_cb)

        # Buttons
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton(t("ok"))
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)

        cancel_btn = QPushButton(t("cancel"))
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def get_angle(self) -> float:
        return self._angle_spin.value()

    def expand(self) -> bool:
        return self._expand_cb.isChecked()
