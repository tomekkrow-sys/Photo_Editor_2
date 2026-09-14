#!/usr/bin/env python3
"""Perspective correction dialog."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QFormLayout, QSpinBox,
)
from config.i18n import t


class PerspectiveDialog(QDialog):
    """Dialog for perspective correction with 4-point adjustment."""

    def __init__(self, img_width: int, img_height: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("perspective"))
        self.setMinimumWidth(380)
        self.img_w = img_width
        self.img_h = img_height
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel(t("perspective_hint")))

        form = QFormLayout()

        # Top-left
        tl_row = QHBoxLayout()
        self.tl_x = QSpinBox(); self.tl_x.setRange(0, 99999); self.tl_x.setValue(0)
        self.tl_y = QSpinBox(); self.tl_y.setRange(0, 99999); self.tl_y.setValue(0)
        tl_row.addWidget(QLabel("X:")); tl_row.addWidget(self.tl_x)
        tl_row.addWidget(QLabel("Y:")); tl_row.addWidget(self.tl_y)
        form.addRow(t("perspective_topleft"), tl_row)

        # Top-right
        tr_row = QHBoxLayout()
        self.tr_x = QSpinBox(); self.tr_x.setRange(0, 99999); self.tr_x.setValue(self.img_w)
        self.tr_y = QSpinBox(); self.tr_y.setRange(0, 99999); self.tr_y.setValue(0)
        tr_row.addWidget(QLabel("X:")); tr_row.addWidget(self.tr_x)
        tr_row.addWidget(QLabel("Y:")); tr_row.addWidget(self.tr_y)
        form.addRow(t("perspective_topright"), tr_row)

        # Bottom-right
        br_row = QHBoxLayout()
        self.br_x = QSpinBox(); self.br_x.setRange(0, 99999); self.br_x.setValue(self.img_w)
        self.br_y = QSpinBox(); self.br_y.setRange(0, 99999); self.br_y.setValue(self.img_h)
        br_row.addWidget(QLabel("X:")); br_row.addWidget(self.br_x)
        br_row.addWidget(QLabel("Y:")); br_row.addWidget(self.br_y)
        form.addRow(t("perspective_bottomright"), br_row)

        # Bottom-left
        bl_row = QHBoxLayout()
        self.bl_x = QSpinBox(); self.bl_x.setRange(0, 99999); self.bl_x.setValue(0)
        self.bl_y = QSpinBox(); self.bl_y.setRange(0, 99999); self.bl_y.setValue(self.img_h)
        bl_row.addWidget(QLabel("X:")); bl_row.addWidget(self.bl_x)
        bl_row.addWidget(QLabel("Y:")); bl_row.addWidget(self.bl_y)
        form.addRow(t("perspective_bottomleft"), bl_row)

        lay.addLayout(form)

        btn_row = QHBoxLayout()
        ok = QPushButton(t("ok"))
        ok.clicked.connect(self.accept)
        cancel = QPushButton(t("cancel"))
        cancel.clicked.connect(self.reject)
        btn_row.addWidget(ok)
        btn_row.addWidget(cancel)
        lay.addLayout(btn_row)

    def get_corners(self) -> list:
        return [
            (self.tl_x.value(), self.tl_y.value()),
            (self.tr_x.value(), self.tr_y.value()),
            (self.br_x.value(), self.br_y.value()),
            (self.bl_x.value(), self.bl_y.value()),
        ]
