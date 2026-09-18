#!/usr/bin/env python3
"""Brightness / Contrast / Saturation / Temperature / Tint dialog."""
from __future__ import annotations
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSlider,
    QPushButton, QWidget, QGridLayout,
)
from config.i18n import t


class _SliderRow(QWidget):
    value_changed = Signal(int)

    def __init__(self, label: str, min_val: int = -100, max_val: int = 100,
                 parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self._lbl = QLabel(label)
        self._lbl.setFixedWidth(100)
        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setRange(min_val, max_val)
        self._slider.setValue(0)
        self._val_lbl = QLabel("0")
        self._val_lbl.setFixedWidth(40)
        self._val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        lay.addWidget(self._lbl)
        lay.addWidget(self._slider)
        lay.addWidget(self._val_lbl)
        self._slider.valueChanged.connect(self._on_change)

    def _on_change(self, v):
        self._val_lbl.setText(str(v))
        self.value_changed.emit(v)

    def value(self) -> int:
        return self._slider.value()

    def set_value(self, v: int):
        self._slider.setValue(v)


class AdjustDialog(QDialog):
    """Modal dialog with sliders for brightness, contrast, saturation, etc."""

    def __init__(self, parent=None, brightness=0, contrast=0, saturation=0,
                 temperature=0, tint=0):
        super().__init__(parent)
        self.setWindowTitle(t("adjust_title"))
        self.setMinimumWidth(420)
        self.setModal(True)

        layout = QVBoxLayout(self)

        self.sliders: dict[str, _SliderRow] = {}
        keys = [
            ("brightness", "brightness"),
            ("contrast", "contrast"),
            ("saturation", "saturation"),
            ("temperature", "temperature"),
            ("tint", "tint"),
        ]
        for key, label_key in keys:
            row = _SliderRow(t(label_key))
            row.set_value(locals()[key])
            row.value_changed.connect(lambda v, k=key: self._on_slider(k, v))
            self.sliders[key] = row
            layout.addWidget(row)

        # Buttons
        btn_layout = QHBoxLayout()
        reset_btn = QPushButton(t("reset_all"))
        reset_btn.clicked.connect(self._on_reset)
        btn_layout.addWidget(reset_btn)

        btn_layout.addStretch()

        ok_btn = QPushButton(t("ok"))
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)

        cancel_btn = QPushButton(t("cancel"))
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def _on_slider(self, key, value):
        pass  # live preview handled by caller if needed

    def _on_reset(self):
        for row in self.sliders.values():
            row.set_value(0)

    def get_values(self) -> dict[str, int]:
        return {k: row.value() for k, row in self.sliders.items()}
