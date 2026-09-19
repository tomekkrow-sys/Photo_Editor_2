#!/usr/bin/env python3
from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QIntValidator
from PySide6.QtWidgets import (
    QColorDialog, QDialog, QFormLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSlider, QVBoxLayout,
    QFontComboBox, QComboBox, QGroupBox, QCheckBox,
)
from config.i18n import t


class TextToolDialog(QDialog):
    """Dialog for adding text overlay with shadow, outline, alignment."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("text_tool"))
        self.setMinimumWidth(450)
        self._color = QColor("white")
        self._shadow_color = QColor(0, 0, 0, 180)
        self._outline_color = QColor(0, 0, 0)
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        form = QFormLayout()

        # Text
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Wpisz tekst...")
        form.addRow(t("text_content"), self.text_input)

        # Font
        self.font_combo = QFontComboBox()
        form.addRow(t("text_font"), self.font_combo)

        # Size
        size_row = QHBoxLayout()
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(8, 400)
        self.size_slider.setValue(48)
        self.size_label = QLabel("48")
        self.size_slider.valueChanged.connect(lambda v: self.size_label.setText(str(v)))
        size_row.addWidget(self.size_slider)
        size_row.addWidget(self.size_label)
        form.addRow(t("text_size"), size_row)

        # Bold
        self.bold_btn = QPushButton(t("text_bold"))
        self.bold_btn.setCheckable(True)
        self.bold_btn.setChecked(False)
        form.addRow(t("text_style"), self.bold_btn)

        # Color
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

        # Alignment
        self.align_combo = QComboBox()
        self.align_combo.addItems(["Center", "Left", "Right", "Top-Left", "Top-Right", "Bottom-Left", "Bottom-Right"])
        form.addRow("Align:", self.align_combo)

        # Position
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

        lay.addLayout(form)

        # --- Shadow group ---
        shadow_grp = QGroupBox("Cień (Shadow)")
        shadow_grp.setCheckable(True)
        shadow_grp.setChecked(True)
        self._shadow_grp = shadow_grp
        slay = QFormLayout(shadow_grp)

        shadow_color_row = QHBoxLayout()
        self.shadow_color_btn = QPushButton()
        self.shadow_color_btn.setFixedSize(60, 24)
        self._update_shadow_btn()
        self.shadow_color_btn.clicked.connect(self._pick_shadow_color)
        shadow_color_row.addWidget(self.shadow_color_btn)
        self.shadow_opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.shadow_opacity_slider.setRange(0, 255)
        self.shadow_opacity_slider.setValue(180)
        self.shadow_opacity_label = QLabel("180")
        self.shadow_opacity_slider.valueChanged.connect(lambda v: self.shadow_opacity_label.setText(str(v)))
        shadow_color_row.addWidget(self.shadow_opacity_slider)
        shadow_color_row.addWidget(self.shadow_opacity_label)
        slay.addRow("Cień kolor:", shadow_color_row)

        shadow_off_row = QHBoxLayout()
        self.shadow_ox = QSlider(Qt.Orientation.Horizontal)
        self.shadow_ox.setRange(-50, 50)
        self.shadow_ox.setValue(3)
        self.shadow_ox_label = QLabel("3")
        self.shadow_ox.valueChanged.connect(lambda v: self.shadow_ox_label.setText(str(v)))
        shadow_off_row.addWidget(QLabel("X:"))
        shadow_off_row.addWidget(self.shadow_ox)
        shadow_off_row.addWidget(self.shadow_ox_label)
        self.shadow_oy = QSlider(Qt.Orientation.Horizontal)
        self.shadow_oy.setRange(-50, 50)
        self.shadow_oy.setValue(3)
        self.shadow_oy_label = QLabel("3")
        self.shadow_oy.valueChanged.connect(lambda v: self.shadow_oy_label.setText(str(v)))
        shadow_off_row.addWidget(QLabel("Y:"))
        shadow_off_row.addWidget(self.shadow_oy)
        shadow_off_row.addWidget(self.shadow_oy_label)
        slay.addRow("Offset:", shadow_off_row)

        lay.addWidget(shadow_grp)

        # --- Outline group ---
        outline_grp = QGroupBox("Kontur (Outline)")
        outline_grp.setCheckable(True)
        outline_grp.setChecked(False)
        self._outline_grp = outline_grp
        olay = QFormLayout(outline_grp)

        outline_color_row = QHBoxLayout()
        self.outline_color_btn = QPushButton()
        self.outline_color_btn.setFixedSize(60, 24)
        self._update_outline_btn()
        self.outline_color_btn.clicked.connect(self._pick_outline_color)
        outline_color_row.addWidget(self.outline_color_btn)
        self.outline_width_slider = QSlider(Qt.Orientation.Horizontal)
        self.outline_width_slider.setRange(1, 20)
        self.outline_width_slider.setValue(3)
        self.outline_width_label = QLabel("3")
        self.outline_width_slider.valueChanged.connect(lambda v: self.outline_width_label.setText(str(v)))
        outline_color_row.addWidget(QLabel("px:"))
        outline_color_row.addWidget(self.outline_width_slider)
        outline_color_row.addWidget(self.outline_width_label)
        olay.addRow("Kontur:", outline_color_row)

        lay.addWidget(outline_grp)

        # Buttons
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

    def _pick_shadow_color(self):
        c = QColorDialog.getColor(self._shadow_color, self, "Shadow color")
        if c.isValid():
            self._shadow_color = c
            c.setAlpha(self.shadow_opacity_slider.value())
            self._update_shadow_btn()

    def _update_shadow_btn(self):
        self.shadow_color_btn.setStyleSheet(
            f"background-color: rgba({self._shadow_color.red()},{self._shadow_color.green()},{self._shadow_color.blue()},{self.shadow_opacity_slider.value()}); "
            f"border: 1px solid #666;"
        )

    def _pick_outline_color(self):
        c = QColorDialog.getColor(self._outline_color, self, "Outline color")
        if c.isValid():
            self._outline_color = c
            self._update_outline_btn()

    def _update_outline_btn(self):
        self.outline_color_btn.setStyleSheet(
            f"background-color: {self._outline_color.name()}; border: 1px solid #666;"
        )

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
        idx = self.align_combo.currentIndex()
        return ["center", "left", "right", "topleft", "topright", "bottomleft", "bottomright"][idx]

    def get_shadow(self) -> dict | None:
        if not self._shadow_grp.isChecked():
            return None
        return {
            "color": (self._shadow_color.red(), self._shadow_color.green(), self._shadow_color.blue()),
            "opacity": self.shadow_opacity_slider.value() / 255.0,
            "offset_x": self.shadow_ox.value(),
            "offset_y": self.shadow_oy.value(),
        }

    def get_outline(self) -> dict | None:
        if not self._outline_grp.isChecked():
            return None
        return {
            "color": (self._outline_color.red(), self._outline_color.green(), self._outline_color.blue()),
            "width": self.outline_width_slider.value(),
        }
