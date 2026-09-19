#!/usr/bin/env python3
"""Smart crop dialog - auto-detect best crop region with ratio selection."""
from __future__ import annotations
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QLabel, QVBoxLayout,
    QHBoxLayout, QProgressBar, QCheckBox,
)
from core.filters import smart_crop, smart_crop_auto
from core.pipeline import pil_to_qpixmap
from config.i18n import t


class _SmartCropWorker(QThread):
    """Background thread for smart crop computation."""
    result = Signal(object)
    progress = Signal(str)

    def __init__(self, img, ratio=None):
        super().__init__()
        self._img = img
        self._ratio = ratio

    def run(self):
        self.progress.emit("Analizuje obraz...")
        if self._ratio is None:
            result = smart_crop_auto(self._img)
        else:
            result = smart_crop(self._img, ratio=self._ratio)
        self.result.emit(result)


RATIOS = [
    ("Auto", None),
    ("16:9", 16/9),
    ("4:3", 4/3),
    ("3:2", 3/2),
    ("1:1", 1.0),
    ("2:3", 2/3),
    ("9:16", 9/16),
]


class SmartCropDialog(QDialog):
    """Smart crop dialog with preview and ratio selection."""

    def __init__(self, img, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Smart Crop")
        self.setMinimumWidth(500)
        self._img = img
        self._result = None
        self._worker = None
        self._build_ui()
        self._run_crop()

    def _build_ui(self):
        lay = QVBoxLayout(self)

        info = QLabel("Automatyczne kadrowanie — analiza zawartosci obrazu")
        info.setStyleSheet("color: #ccc; font-size: 11px;")
        lay.addWidget(info)

        # Ratio selection
        ratio_row = QHBoxLayout()
        ratio_row.addWidget(QLabel("Proporcje:"))
        self.ratio_combo = QComboBox()
        for name, _ in RATIOS:
            self.ratio_combo.addItem(name)
        self.ratio_combo.currentIndexChanged.connect(self._on_ratio_changed)
        ratio_row.addWidget(self.ratio_combo)
        lay.addLayout(ratio_row)

        # Preview
        self.preview_label = QLabel("Przetwarzanie...")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(300)
        self.preview_label.setStyleSheet("background: #1a1a1a; border: 1px solid #333;")
        lay.addWidget(self.preview_label)

        # Info
        self.info_label = QLabel("")
        lay.addWidget(self.info_label)

        # Progress
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # indeterminate
        self.progress.setVisible(False)
        lay.addWidget(self.progress)

        # Buttons
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        btns.button(QDialogButtonBox.StandardButton.Ok).setText(t("ok"))
        btns.button(QDialogButtonBox.StandardButton.Cancel).setText(t("cancel"))
        lay.addWidget(btns)

    def _on_ratio_changed(self, idx):
        self._run_crop()

    def _run_crop(self):
        if self._worker and self._worker.isRunning():
            self._worker.terminate()
        self.progress.setVisible(True)
        idx = self.ratio_combo.currentIndex()
        ratio = RATIOS[idx][1]
        self._worker = _SmartCropWorker(self._img, ratio)
        self._worker.result.connect(self._on_result)
        self._worker.start()

    def _on_result(self, result):
        self._result = result
        self.progress.setVisible(False)
        # Show preview
        pm = pil_to_qpixmap(result)
        scaled = pm.scaled(
            self.preview_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.preview_label.setPixmap(scaled)
        self.info_label.setText(f"Wynik: {result.width} x {result.height} px (oryginal: {self._img.width} x {self._img.height})")

    def get_result(self):
        return self._result
