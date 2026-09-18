#!/usr/bin/env python3
"""Selective Edit Dialog - choose filter to apply to selected area."""
from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QFormLayout,
    QLabel, QSlider, QVBoxLayout, QSpinBox, QCheckBox, QWidget, QHBoxLayout,
)
from config.i18n import t

FILTERS = [
    ("blur", "blur"),
    ("sharpen", "sharpen"),
    ("black_white", "black_white"),
    ("sepia", "sepia"),
    ("negative", "negative"),
    ("vignette", "vignette"),
    ("emboss", "emboss"),
    ("brightness", "brightness"),
    ("contrast", "contrast"),
    ("saturation", "saturation"),
    ("pixelate", "pixelate"),
    ("denoise", "denoise"),
    ("hdr", "hdr"),
    ("cartoon", "cartoon"),
    ("thermal", "thermal"),
]


class SelectEditDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("select_edit"))
        self.setMinimumWidth(350)
        self.setModal(True)

        lay = QVBoxLayout(self)

        form = QFormLayout()
        form.setSpacing(8)

        self.filter_combo = QComboBox()
        for key, label_key in FILTERS:
            self.filter_combo.addItem(t(label_key), key)
        form.addRow(t("select_filter") + ":", self.filter_combo)

        # Params
        self.intensity_slider = QSlider(Qt.Orientation.Horizontal)
        self.intensity_slider.setRange(1, 100)
        self.intensity_slider.setValue(50)
        self.intensity_label = QLabel("50")
        self.intensity_slider.valueChanged.connect(lambda v: self.intensity_label.setText(str(v)))
        int_row = QHBoxLayout()
        int_row.addWidget(self.intensity_slider)
        int_row.addWidget(self.intensity_label)
        form.addRow(t("select_intensity") + ":", int_row)

        self.feather_slider = QSlider(Qt.Orientation.Horizontal)
        self.feather_slider.setRange(0, 50)
        self.feather_slider.setValue(5)
        self.feather_label = QLabel("5")
        self.feather_slider.valueChanged.connect(lambda v: self.feather_label.setText(str(v)))
        f_row = QHBoxLayout()
        f_row.addWidget(self.feather_slider)
        f_row.addWidget(self.feather_label)
        form.addRow(t("select_feather") + ":", f_row)

        lay.addLayout(form)

        # Buttons
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        btns.button(QDialogButtonBox.StandardButton.Ok).setText(t("ok"))
        btns.button(QDialogButtonBox.StandardButton.Cancel).setText(t("cancel"))
        lay.addWidget(btns)

    def get_filter(self) -> str:
        return self.filter_combo.currentData()

    def get_intensity(self) -> int:
        return self.intensity_slider.value()

    def get_feather(self) -> int:
        return self.feather_slider.value()
