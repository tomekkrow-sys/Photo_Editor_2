#!/usr/bin/env python3
from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QIntValidator
from PySide6.QtWidgets import (
    QColorDialog, QDialog, QFormLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSlider, QVBoxLayout,
    QFontComboBox, QComboBox,
)
from config.i18n import t


class TextToolDialog(QDialog):
    """Dialog for adding text overlay to an image."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("text_tool"))
        self.setMinimumWidth(400)
        self._color = QColor("white")
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)

        form = QFormLayout()

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Wpisz tekst...")
        form.addRow(t("text_content"), self.text_input)

        self.font_combo = QFontComboBox()
        form.addRow(t("text_font"), self.font_combo)

        size_row = QHBoxLayout()
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(8, 200)
        self.size_slider.setValue(48)
        self.size_label = QLabel("48")
        self.size_slider.valueChanged.connect(lambda v: self.size_label.setText(str(v)))
        size_row.addWidget(self.size_slider)
        size_row.addWidget(self.size_label)
        form.addRow(t("text_size"), size_row)

        self.bold_btn = QPushButton(t("text_bold"))
        self.bold_btn.setCheckable(True)
        self.bold_btn.setChecked(False)
        form.addRow(t("text_style"), self.bold_btn)

        color_row = QHBoxLayout()
        self.color_btn = QPushButton(t("text_color"))
        self.color_btn.setStyleSheet(f"background-color: {self._color.name()}; color: white; padding: 6px;")
        self.color_btn.clicked.connect(self._pick_color)
        color_row.addWidget(self.color_btn)

        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_label = QLabel("100%")
        self.opacity_slider.valueChanged.connect(lambda v: self.opacity_label.setText(f"{v}%"))
        color_row.addWidget(self.opacity_slider)
        color_row.addWidget(self.opacity_label)
        form.addRow(t("text_opacity"), color_row)

        pos_row = QHBoxLayout()
        self.pos_x = QLineEdit("0")
        self.pos_x.setValidator(QIntValidator(0, 99999))
        self.pos_y = QLineEdit("0")
        self.pos_y.setValidator(QIntValidator(0, 99999))
        pos_row.addWidget(QLabel("X:"))
        pos_row.addWidget(self.pos_x)
        pos_row.addWidget(QLabel("Y:"))
        pos_row.addWidget(self.pos_y)
        form.addRow(t("text_position"), pos_row)

        self.anchor_combo = QComboBox()
        self.anchor_combo.addItems([t("text_anchor_center"), t("text_anchor_topleft"), t("text_anchor_bottomright")])
        form.addRow(t("text_anchor"), self.anchor_combo)

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
        c = QColorDialog.getColor(self._color, self, t("text_color"))
        if c.isValid():
            self._color = c
            self.color_btn.setStyleSheet(f"background-color: {c.name()}; color: white; padding: 6px;")

    def get_text(self) -> str:
        return self.text_input.text()

    def get_font(self) -> QFont:
        f = self.font_combo.currentFont()
        f.setPixelSize(self.size_slider.value())
        f.setBold(self.bold_btn.isChecked())
        return f

    def get_color(self) -> QColor:
        return self._color

    def get_opacity(self) -> float:
        return self.opacity_slider.value() / 100.0

    def get_position(self) -> tuple:
        try:
            x = int(self.pos_x.text() or "0")
        except ValueError:
            x = 0
        try:
            y = int(self.pos_y.text() or "0")
        except ValueError:
            y = 0
        return x, y

    def get_anchor(self) -> str:
        idx = self.anchor_combo.currentIndex()
        return ["center", "topleft", "bottomright"][idx]
