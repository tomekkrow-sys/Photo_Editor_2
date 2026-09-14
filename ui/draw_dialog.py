#!/usr/bin/env python3
"""Freehand drawing tool settings dialog."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog, QDialog, QFormLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QVBoxLayout,
)
from config.i18n import t


class DrawToolDialog(QDialog):
    """Dialog for configuring the freehand drawing tool."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("draw_tool"))
        self.setMinimumWidth(350)
        self._color = QColor("red")
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        form = QFormLayout()

        size_row = QHBoxLayout()
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(1, 100)
        self.size_slider.setValue(10)
        self.size_label = QLabel("10")
        self.size_slider.valueChanged.connect(lambda v: self.size_label.setText(str(v)))
        size_row.addWidget(self.size_slider)
        size_row.addWidget(self.size_label)
        form.addRow(t("draw_size"), size_row)

        color_row = QHBoxLayout()
        self.color_btn = QPushButton(t("draw_color"))
        self.color_btn.setStyleSheet(f"background-color: {self._color.name()}; color: white; padding: 6px;")
        self.color_btn.clicked.connect(self._pick_color)
        color_row.addWidget(self.color_btn)

        opacity_row = QHBoxLayout()
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(1, 100)
        self.opacity_slider.setValue(100)
        self.opacity_label = QLabel("100%")
        self.opacity_slider.valueChanged.connect(lambda v: self.opacity_label.setText(f"{v}%"))
        opacity_row.addWidget(self.opacity_slider)
        opacity_row.addWidget(self.opacity_label)
        form.addRow(t("draw_opacity"), opacity_row)

        form.addRow(t("draw_color_label"), color_row)

        lay.addLayout(form)

        btn_row = QHBoxLayout()
        ok = QPushButton(t("ok"))
        ok.clicked.connect(self.accept)
        cancel = QPushButton(t("cancel"))
        cancel.clicked.connect(self.reject)
        btn_row.addWidget(ok)
        btn_row.addWidget(cancel)
        lay.addLayout(btn_row)

    def _pick_color(self):
        c = QColorDialog.getColor(self._color, self, t("draw_color"))
        if c.isValid():
            self._color = c
            self.color_btn.setStyleSheet(f"background-color: {c.name()}; color: white; padding: 6px;")

    def get_size(self) -> float:
        return float(self.size_slider.value())

    def get_color(self) -> QColor:
        return self._color

    def get_opacity(self) -> float:
        return self.opacity_slider.value() / 100.0
