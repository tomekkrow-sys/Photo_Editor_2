#!/usr/bin/env python3
"""Slideshow settings dialog."""
from __future__ import annotations
import os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFileDialog,
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QSlider, QVBoxLayout,
)
from config.i18n import t


class SlideshowDialog(QDialog):
    """Dialog for configuring slideshow."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Slideshow")
        self.setMinimumWidth(400)
        self._folder = ""
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)

        info = QLabel("Prezentacja zdjec z efektami przejsc")
        info.setStyleSheet("color: #ccc; font-size: 11px;")
        lay.addWidget(info)

        # Folder selection
        folder_row = QHBoxLayout()
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Wybierz folder...")
        self.folder_input.setReadOnly(True)
        folder_btn = QPushButton("Przegladaj...")
        folder_btn.clicked.connect(self._browse_folder)
        folder_row.addWidget(self.folder_input)
        folder_row.addWidget(folder_btn)
        lay.addLayout(folder_row)

        self.folder_info = QLabel("")
        self.folder_info.setStyleSheet("color: #aaa; font-size: 11px;")
        lay.addWidget(self.folder_info)

        # Interval
        int_row = QHBoxLayout()
        int_row.addWidget(QLabel("Czas (sek):"))
        self.interval_slider = QSlider(Qt.Orientation.Horizontal)
        self.interval_slider.setRange(1, 30)
        self.interval_slider.setValue(4)
        self.interval_label = QLabel("4")
        self.interval_slider.valueChanged.connect(
            lambda v: self.interval_label.setText(str(v))
        )
        int_row.addWidget(self.interval_slider)
        int_row.addWidget(self.interval_label)
        lay.addLayout(int_row)

        # Transition
        trans_row = QHBoxLayout()
        trans_row.addWidget(QLabel("Przejscie:"))
        self.trans_combo = QComboBox()
        self.trans_combo.addItems(["Fade", "Instant"])
        trans_row.addWidget(self.trans_combo)
        lay.addLayout(trans_row)

        # Options
        self.loop_check = QCheckBox("Petla (powtarzaj)")
        self.loop_check.setChecked(True)
        lay.addWidget(self.loop_check)

        self.random_check = QCheckBox("Losowa kolejnosc")
        self.random_check.setChecked(False)
        lay.addWidget(self.random_check)

        # Buttons
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self._on_accept)
        btns.rejected.connect(self.reject)
        btns.button(QDialogButtonBox.StandardButton.Ok).setText("Start")
        btns.button(QDialogButtonBox.StandardButton.Cancel).setText(t("cancel"))
        lay.addWidget(btns)

    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Wybierz folder ze zdjeciami")
        if folder:
            self._folder = folder
            self.folder_input.setText(folder)
            exts = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".tif", ".webp"}
            count = sum(
                1 for f in os.listdir(folder)
                if os.path.splitext(f)[1].lower() in exts
            )
            self.folder_info.setText(f"Znaleziono {count} zdjec")

    def _on_accept(self):
        if not self._folder:
            return
        self.accept()

    def get_folder(self):
        return self._folder

    def get_interval(self):
        return self.interval_slider.value()

    def get_transition(self):
        return "fade" if self.trans_combo.currentIndex() == 0 else "instant"

    def get_loop(self):
        return self.loop_check.isChecked()

    def get_random(self):
        return self.random_check.isChecked()
