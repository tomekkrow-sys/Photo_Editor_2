#!/usr/bin/env python3
from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QFileDialog,
    QFormLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSlider, QSpinBox, QVBoxLayout, QWidget,
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
"""

class ExportDialog(QDialog):
    def __init__(self, parent=None, orig_width=0, orig_height=0, default_name="export"):
        super().__init__(parent)
        self.setWindowTitle("Eksportuj zdjecie")
        self.setMinimumWidth(420)
        self.setStyleSheet(DARK_STYLE)
        self._orig_w = orig_width
        self._orig_h = orig_height
        self._default_name = default_name
        self._build_ui()
        self._estimate_size()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(10)

        # Sciezka
        path_row = QWidget()
        pr = QHBoxLayout(path_row)
        pr.setContentsMargins(0, 0, 0, 0)
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Wybierz plik wyjsciowy...")
        pr.addWidget(self.path_edit)
        browse = QPushButton("Przegladaj...")
        browse.clicked.connect(self._on_browse)
        pr.addWidget(browse)
        lay.addWidget(path_row)

        # Format
        form = QFormLayout()
        form.setSpacing(8)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "JPEG", "TIFF"])
        self.format_combo.currentTextChanged.connect(self._on_format_changed)
        form.addRow("Format:", self.format_combo)

        # Jakosc JPEG
        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(95)
        self.quality_label = QLabel("95")
        self.quality_slider.valueChanged.connect(self._on_quality)
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
        self.scale_spin.valueChanged.connect(self._on_scale)
        form.addRow("Skalowanie:", self.scale_spin)

        # Rozmiar wyjsciowy
        self.out_size_label = QLabel(f"{self._orig_w} x {self._orig_h}")
        form.addRow("Rozmiar:", self.out_size_label)

        # Szacunkowy rozmiar pliku
        self.file_size_label = QLabel("~ --")
        self.file_size_label.setStyleSheet("color: #4A9EFF; font-weight: bold;")
        form.addRow("Szac. rozmiar:", self.file_size_label)

        lay.addLayout(form)
        lay.addStretch()

        # Przyciski
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        btns.button(QDialogButtonBox.StandardButton.Ok).setText("Eksportuj")
        btns.button(QDialogButtonBox.StandardButton.Cancel).setText("Anuluj")
        lay.addWidget(btns)

    def _on_browse(self):
        fmt = self.format_combo.currentText().lower()
        ext_map = {"png": "PNG (*.png)", "jpeg": "JPEG (*.jpg *.jpeg)", "tiff": "TIFF (*.tiff)"}
        ext = ext_map.get(fmt, "*.png")
        p, _ = QFileDialog.getSaveFileName(self, "Zapisz jako", self._default_name, ext)
        if p:
            p = self._fix_extension(p)
            self.path_edit.setText(p)
            self._estimate_size()

    def _fix_extension(self, path):
        fmt = self.format_combo.currentText().lower()
        ext_map = {"png": ".png", "jpeg": ".jpg", "tiff": ".tiff"}
        wanted = ext_map.get(fmt, ".png")
        path = str(path)
        lower = path.lower()
        for e in [".png", ".jpg", ".jpeg", ".tiff"]:
            if lower.endswith(e):
                return path[:-len(e)] + wanted
        return path + wanted

    def _on_format_changed(self, fmt):
        self.quality_slider.setEnabled(fmt == "JPEG")
        # Aktualizuj rozszerzenie w polu tekstowym jesli jest juz sciezka
        p = self.path_edit.text()
        if p:
            self.path_edit.setText(self._fix_extension(p))
        self._estimate_size()

    def _on_quality(self, v):
        self.quality_label.setText(str(v))
        self._estimate_size()

    def _on_scale(self):
        w = int(self._orig_w * self.scale_spin.value() / 100)
        h = int(self._orig_h * self.scale_spin.value() / 100)
        self.out_size_label.setText(f"{w} x {h}")
        self._estimate_size()

    def _estimate_size(self):
        if self._orig_w == 0 or self._orig_h == 0:
            self.file_size_label.setText("~ --")
            return
        fmt = self.format_combo.currentText()
        scale = self.scale_spin.value() / 100
        px = self._orig_w * self._orig_h * scale * scale
        if fmt == "PNG":
            mb = px * 3 / (1024 * 1024) * 0.6
        elif fmt == "JPEG":
            q = self.quality_slider.value()
            mb = px * 3 / (1024 * 1024) * (q / 250.0)
        else:
            mb = px * 3 / (1024 * 1024)
        if mb < 1:
            self.file_size_label.setText(f"~ {mb*1024:.0f} KB")
        else:
            self.file_size_label.setText(f"~ {mb:.1f} MB")

    def get_path(self):
        return self.path_edit.text()

    def get_format(self):
        return self.format_combo.currentText()

    def get_quality(self):
        return self.quality_slider.value()

    def get_scale(self):
        return self.scale_spin.value() / 100.0
