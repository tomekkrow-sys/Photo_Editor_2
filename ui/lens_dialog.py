#!/usr/bin/env python3
"""Lens correction dialog."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QFormLayout,
)
from config.i18n import t


class LensCorrectionDialog(QDialog):
    """Dialog for lens distortion and vignette correction."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("lens_correction"))
        self.setMinimumWidth(420)
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        form = QFormLayout()

        self.k1 = self._mk_slider(-100, 100, 0)
        form.addRow("K1 (radial):", self.k1)
        self.k2 = self._mk_slider(-100, 100, 0)
        form.addRow("K2 (radial):", self.k2)
        self.k3 = self._mk_slider(-100, 100, 0)
        form.addRow("K3 (radial):", self.k3)
        self.p1 = self._mk_slider(-100, 100, 0)
        form.addRow("P1 (tangential):", self.p1)
        self.p2 = self._mk_slider(-100, 100, 0)
        form.addRow("P2 (tangential):", self.p2)

        lay.addLayout(form)

        btn_row = QHBoxLayout()
        ok = QPushButton(t("ok"))
        ok.clicked.connect(self.accept)
        cancel = QPushButton(t("cancel"))
        cancel.clicked.connect(self.reject)
        btn_row.addWidget(ok)
        btn_row.addWidget(cancel)
        lay.addLayout(btn_row)

    def _mk_slider(self, mn, mx, default):
        row = QHBoxLayout()
        sl = QSlider(Qt.Orientation.Horizontal)
        sl.setRange(mn, mx)
        sl.setValue(default)
        lbl = QLabel(str(default / 10.0))
        sl.valueChanged.connect(lambda v: lbl.setText(f"{v / 10.0:.1f}"))
        row.addWidget(sl)
        row.addWidget(lbl)
        return sl

    def get_values(self) -> dict:
        return {
            "k1": self.k1.value() / 10.0,
            "k2": self.k2.value() / 10.0,
            "k3": self.k3.value() / 10.0,
            "p1": self.p1.value() / 10.0,
            "p2": self.p2.value() / 10.0,
        }
