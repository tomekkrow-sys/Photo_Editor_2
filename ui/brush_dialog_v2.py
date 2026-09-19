#!/usr/bin/env python3
"""Brush settings dialog v2 - full control over correction brush."""
from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog, QDialog, QFormLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QVBoxLayout, QGroupBox,
    QComboBox, QDoubleSpinBox,
)
from config.i18n import t


class BrushDialogV2(QDialog):
    """Full brush settings dialog for correction brush v2."""

    MODES = [
        ("Rozjasnianie (Dodge)", "dodge"),
        ("Przyciemnianie (Burn)", "burn"),
        ("Nasycenie (Saturate)", "saturate"),
        ("Odbarwienie (Desaturate)", "desaturate"),
        ("Korekcja temperatury (Warm)", "warm"),
        ("Korekcja temperatury (Cool)", "cool"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pedzel korekcyjny v2")
        self.setMinimumWidth(380)
        self._color = QColor("white")
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)

        info = QLabel("Ustawienia pedzla korekcyjnego. Lewy przycisk = aktywny, prawy = odwrotny.")
        info.setStyleSheet("color: #aaa; font-size: 11px;")
        lay.addWidget(info)

        form = QFormLayout()

        # Mode
        self.mode_combo = QComboBox()
        for name, _ in self.MODES:
            self.mode_combo.addItem(name)
        form.addRow("Tryb:", self.mode_combo)

        # Size
        size_row = QHBoxLayout()
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(4, 300)
        self.size_slider.setValue(40)
        self.size_label = QLabel("40")
        self.size_slider.valueChanged.connect(lambda v: self.size_label.setText(str(v)))
        size_row.addWidget(self.size_slider)
        size_row.addWidget(self.size_label)
        form.addRow("Rozmiar:", size_row)

        # Hardness
        hard_row = QHBoxLayout()
        self.hard_slider = QSlider(Qt.Orientation.Horizontal)
        self.hard_slider.setRange(0, 100)
        self.hard_slider.setValue(80)
        self.hard_label = QLabel("80%")
        self.hard_slider.valueChanged.connect(lambda v: self.hard_label.setText(f"{v}%"))
        hard_row.addWidget(self.hard_slider)
        hard_row.addWidget(self.hard_label)
        form.addRow("Twardosc:", hard_row)

        # Opacity
        op_row = QHBoxLayout()
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(1, 100)
        self.opacity_slider.setValue(25)
        self.opacity_label = QLabel("25%")
        self.opacity_slider.valueChanged.connect(lambda v: self.opacity_label.setText(f"{v}%"))
        op_row.addWidget(self.opacity_slider)
        op_row.addWidget(self.opacity_label)
        form.addRow("Krycie:", op_row)

        # Flow
        flow_row = QHBoxLayout()
        self.flow_slider = QSlider(Qt.Orientation.Horizontal)
        self.flow_slider.setRange(1, 100)
        self.flow_slider.setValue(100)
        self.flow_label = QLabel("100%")
        self.flow_slider.valueChanged.connect(lambda v: self.flow_label.setText(f"{v}%"))
        flow_row.addWidget(self.flow_slider)
        flow_row.addWidget(self.flow_label)
        form.addRow("Przeplyw:", flow_row)

        # Spacing
        space_row = QHBoxLayout()
        self.spacing_slider = QSlider(Qt.Orientation.Horizontal)
        self.spacing_slider.setRange(5, 100)
        self.spacing_slider.setValue(25)
        self.spacing_label = QLabel("25%")
        self.spacing_slider.valueChanged.connect(lambda v: self.spacing_label.setText(f"{v}%"))
        space_row.addWidget(self.spacing_slider)
        space_row.addWidget(self.spacing_label)
        form.addRow("Odstep:", space_row)

        # Strength (applied to each stroke)
        str_row = QHBoxLayout()
        self.strength_slider = QSlider(Qt.Orientation.Horizontal)
        self.strength_slider.setRange(5, 200)
        self.strength_slider.setValue(100)
        self.strength_label = QLabel("100%")
        self.strength_slider.valueChanged.connect(lambda v: self.strength_label.setText(f"{v}%"))
        str_row.addWidget(self.strength_slider)
        str_row.addWidget(self.strength_label)
        form.addRow("Sila efektu:", str_row)

        lay.addLayout(form)

        # Buttons
        btn_row = QHBoxLayout()
        ok = QPushButton(t("ok"))
        ok.clicked.connect(self.accept)
        cancel = QPushButton(t("cancel"))
        cancel.clicked.connect(self.reject)
        btn_row.addWidget(ok)
        btn_row.addWidget(cancel)
        lay.addLayout(btn_row)

    def get_mode(self) -> str:
        idx = self.mode_combo.currentIndex()
        return self.MODES[idx][1]

    def get_size(self) -> int:
        return self.size_slider.value()

    def get_hardness(self) -> float:
        return self.hard_slider.value() / 100.0

    def get_opacity(self) -> float:
        return self.opacity_slider.value() / 100.0

    def get_flow(self) -> float:
        return self.flow_slider.value() / 100.0

    def get_spacing(self) -> float:
        return self.spacing_slider.value() / 100.0

    def get_strength(self) -> float:
        return self.strength_slider.value() / 100.0
