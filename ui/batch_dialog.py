#!/usr/bin/env python3
from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QFileDialog,
    QFormLayout, QHBoxLayout, QLabel, QLineEdit,
    QProgressBar, QPushButton, QSlider, QSpinBox,
    QVBoxLayout, QWidget,
)

DARK_STYLE = """
QDialog { background: #1E1E1E; color: #CCCCCC; }
QLabel { color: #CCCCCC; font-size: 11px; }
QLineEdit { background: #2A2A2A; color: #FFFFFF; border: 1px solid #444; padding: 4px; }
QComboBox { background: #2A2A2A; color: #FFFFFF; border: 1px solid #444; padding: 4px; }
QSlider::groove:horizontal { height: 4px; background: #333; border-radius: 2px; }
QSlider::handle:horizontal { width: 14px; background: #4A9EFF; border-radius: 7px; margin: -5px 0; }
QSlider::sub-page:horizontal { background: #4A9EFF; }
QSpinBox { background: #2A2A2A; color: #FFFFFF; border: 1px solid #444; padding: 4px; }
QPushButton { background: #333; color: #FFF; border: 1px solid #444; padding: 6px 16px; border-radius: 3px; }
QPushButton:hover { background: #444; }
QPushButton:default { background: #2E7D32; }
QProgressBar { border: 1px solid #444; background: #2A2A2A; text-align: center; color: white; }
QProgressBar::chunk { background: #4A9EFF; }
"""

class BatchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Konwerter folderu")
        self.setMinimumWidth(450)
        self.setStyleSheet(DARK_STYLE)
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(10)

        # Folder wejsciowy
        in_row = QWidget()
        ir = QHBoxLayout(in_row)
        ir.setContentsMargins(0, 0, 0, 0)
        self.in_edit = QLineEdit()
        self.in_edit.setPlaceholderText("Folder ze zdjeciami...")
        ir.addWidget(self.in_edit)
        btn = QPushButton("Przegladaj...")
        btn.clicked.connect(self._on_browse_in)
        ir.addWidget(btn)
        lay.addWidget(in_row)

        # Folder wyjsciowy
        out_row = QWidget()
        or_ = QHBoxLayout(out_row)
        or_.setContentsMargins(0, 0, 0, 0)
        self.out_edit = QLineEdit()
        self.out_edit.setPlaceholderText("Folder wyjsciowy...")
        or_.addWidget(self.out_edit)
        btn2 = QPushButton("Przegladaj...")
        btn2.clicked.connect(self._on_browse_out)
        or_.addWidget(btn2)
        lay.addWidget(out_row)

        # Format
        form = QFormLayout()
        form.setSpacing(8)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["JPEG", "PNG", "TIFF"])
        self.format_combo.currentTextChanged.connect(self._on_format_changed)
        form.addRow("Format:", self.format_combo)

        # Jakosc JPEG
        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(95)
        self.quality_label = QLabel("95")
        self.quality_slider.valueChanged.connect(lambda v: self.quality_label.setText(str(v)))
        qrow = QWidget()
        qr = QHBoxLayout(qrow)
        qr.setContentsMargins(0, 0, 0, 0)
        qr.addWidget(self.quality_slider)
        qr.addWidget(self.quality_label)
        form.addRow("Jakosc JPEG:", qrow)

        # Skalowanie
        self.scale_spin = QSpinBox()
        self.scale_spin.setRange(10, 200)
        self.scale_spin.setValue(100)
        self.scale_spin.setSuffix("%")
        form.addRow("Skalowanie:", self.scale_spin)

        # Suffix
        self.suffix_edit = QLineEdit("_edit")
        self.suffix_edit.setPlaceholderText("_edit")
        form.addRow("Suffix nazwy:", self.suffix_edit)

        lay.addLayout(form)

        # Progress
        self.progress = QProgressBar()
        self.progress.setValue(0)
        lay.addWidget(self.progress)
        self.status_label = QLabel("Gotowy")
        lay.addWidget(self.status_label)
        lay.addStretch()

        # Przyciski
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        btns.button(QDialogButtonBox.StandardButton.Ok).setText("Eksportuj wszystko")
        btns.button(QDialogButtonBox.StandardButton.Cancel).setText("Anuluj")
        lay.addWidget(btns)

    def _on_browse_in(self):
        p = QFileDialog.getExistingDirectory(self, "Folder ze zdjeciami")
        if p:
            self.in_edit.setText(p)

    def _on_browse_out(self):
        p = QFileDialog.getExistingDirectory(self, "Folder wyjsciowy")
        if p:
            self.out_edit.setText(p)

    def _on_format_changed(self, fmt):
        self.quality_slider.setEnabled(fmt == "JPEG")

    def set_progress(self, current, total):
        self.progress.setMaximum(total)
        self.progress.setValue(current)
        self.status_label.setText(f"Przetwarzanie {current}/{total}...")

    def get_input_dir(self):
        return self.in_edit.text()

    def get_output_dir(self):
        return self.out_edit.text()

    def get_format(self):
        return self.format_combo.currentText()

    def get_quality(self):
        return self.quality_slider.value()

    def get_scale(self):
        return self.scale_spin.value() / 100.0

    def get_suffix(self):
        return self.suffix_edit.text().strip()
