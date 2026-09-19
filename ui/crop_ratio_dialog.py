#!/usr/bin/env python3
"""Crop by aspect ratio dialog."""
from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QLabel, QVBoxLayout,
)
from config.i18n import t


RATIOS = [
    ("16:9", 16, 9),
    ("4:3", 4, 3),
    ("3:2", 3, 2),
    ("1:1", 1, 1),
    ("2:3", 2, 3),
    ("9:16", 9, 16),
]


class CropRatioDialog(QDialog):
    def __init__(self, img_w: int, img_h: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("crop_ratio"))
        self.setMinimumWidth(280)
        self.setModal(True)
        self._img_w = img_w
        self._img_h = img_h
        self._rw = img_w
        self._rh = img_h

        lay = QVBoxLayout(self)

        lay.addWidget(QLabel(t("crop_ratio_choose")))

        self._combo = QComboBox()
        for name, rw, rh in RATIOS:
            self._combo.addItem(name, (rw, rh))
        self._combo.currentIndexChanged.connect(self._update_preview)
        lay.addWidget(self._combo)

        self._info = QLabel()
        lay.addWidget(self._info)
        self._update_preview()

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        btns.button(QDialogButtonBox.StandardButton.Ok).setText(t("ok"))
        btns.button(QDialogButtonBox.StandardButton.Cancel).setText(t("cancel"))
        lay.addWidget(btns)

    def _update_preview(self):
        idx = self._combo.currentIndex()
        _, rw, rh = RATIOS[idx]
        # Calculate crop to fill the ratio
        ratio = rw / rh
        cur_ratio = self._img_w / self._img_h
        if ratio > cur_ratio:
            new_w = self._img_w
            new_h = int(self._img_w / ratio)
        else:
            new_h = self._img_h
            new_w = int(self._img_h * ratio)
        self._rw = new_w
        self._rh = new_h
        self._info.setText(f"{new_w} x {new_h} px")

    def get_size(self) -> tuple[int, int]:
        return self._rw, self._rh
