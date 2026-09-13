#!/usr/bin/env python3
from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QComboBox, QFileDialog, QListWidget, QListWidgetItem,
    QSplitter, QWidget, QSpinBox,
)
from PIL import Image
import numpy as np


class LayersDialog(QDialog):
    def __init__(self, parent, base_image: Image.Image):
        super().__init__(parent)
        self.setWindowTitle("Warstwy")
        self.setMinimumSize(700, 500)
        self.base = base_image.copy()
        self.layers = []  # list of (Image, opacity, mode)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Layer list
        self.layer_list = QListWidget()
        self.layer_list.currentRowChanged.connect(self._on_select)

        # Controls
        ctrl_layout = QHBoxLayout()

        add_btn = QPushButton("Dodaj warstwe")
        add_btn.clicked.connect(self._add_layer)
        remove_btn = QPushButton("Usun")
        remove_btn.clicked.connect(self._remove_layer)
        up_btn = QPushButton("W gore")
        up_btn.clicked.connect(self._move_up)
        down_btn = QPushButton("W dol")
        down_btn.clicked.connect(self._move_down)

        ctrl_layout.addWidget(add_btn)
        ctrl_layout.addWidget(remove_btn)
        ctrl_layout.addWidget(up_btn)
        ctrl_layout.addWidget(down_btn)

        # Opacity slider
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Przezroczystosc:"))
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self._on_opacity)
        self.opacity_label = QLabel("100%")
        self.opacity_slider.valueChanged.connect(lambda v: self.opacity_label.setText(f"{v}%"))
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_label)

        # Blend mode
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Tryb mieszania:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Nakładanie", "Mnożenie", "Ekran", "Ciemniejszy", "Jasniejszy"])
        self.mode_combo.currentIndexChanged.connect(self._on_mode)
        mode_layout.addWidget(self.mode_combo)

        # Preview
        self.preview = QLabel()
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumHeight(200)

        layout.addWidget(self.layer_list)
        layout.addLayout(ctrl_layout)
        layout.addLayout(opacity_layout)
        layout.addLayout(mode_layout)
        layout.addWidget(self.preview)

        # OK / Cancel
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("Zastosuj")
        ok_btn.clicked.connect(self._apply)
        cancel_btn = QPushButton("Anuluj")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self._update_preview()

    def _add_layer(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Wybierz warstwe", "",
            "Obrazy (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        if path:
            img = Image.open(path).convert("RGBA")
            self.layers.append((img, 100, "overlay"))
            self.layer_list.addItem(f"Warstwa {len(self.layers)}: {Path(path).name}")
            self._update_preview()

    def _remove_layer(self):
        row = self.layer_list.currentRow()
        if 0 <= row < len(self.layers):
            self.layers.pop(row)
            self.layer_list.takeItem(row)
            self._update_preview()

    def _move_up(self):
        row = self.layer_list.currentRow()
        if row > 0:
            self.layers[row], self.layers[row - 1] = self.layers[row - 1], self.layers[row]
            item = self.layer_list.takeItem(row)
            self.layer_list.insertItem(row - 1, item)
            self.layer_list.setCurrentRow(row - 1)

    def _move_down(self):
        row = self.layer_list.currentRow()
        if 0 <= row < len(self.layers) - 1:
            self.layers[row], self.layers[row + 1] = self.layers[row + 1], self.layers[row]
            item = self.layer_list.takeItem(row)
            self.layer_list.insertItem(row + 1, item)
            self.layer_list.setCurrentRow(row + 1)

    def _on_select(self, row):
        if 0 <= row < len(self.layers):
            _, opacity, mode = self.layers[row]
            self.opacity_slider.setValue(opacity)
            modes = ["overlay", "multiply", "screen", "darken", "lighten"]
            idx = modes.index(mode) if mode in modes else 0
            self.mode_combo.setCurrentIndex(idx)

    def _on_opacity(self, value):
        row = self.layer_list.currentRow()
        if 0 <= row < len(self.layers):
            img, _, mode = self.layers[row]
            self.layers[row] = (img, value, mode)

    def _on_mode(self, index):
        row = self.layer_list.currentRow()
        modes = ["overlay", "multiply", "screen", "darken", "lighten"]
        if 0 <= row < len(self.layers):
            img, opacity, _ = self.layers[row]
            self.layers[row] = (img, opacity, modes[index])

    def _composite(self, base: Image.Image, layer: Image.Image, opacity: int, mode: str) -> Image.Image:
        """Composite a layer onto base image."""
        base = base.convert("RGBA")
        layer = layer.copy()
        # Resize layer to match base
        if layer.size != base.size:
            layer = layer.resize(base.size, Image.Resampling.LANCZOS)
        # Apply opacity
        alpha = layer.split()[3]
        alpha = alpha.point(lambda p: int(p * opacity / 100))
        layer.putalpha(alpha)
        # Composite
        if mode == "overlay":
            return Image.alpha_composite(base, layer)
        elif mode == "multiply":
            result = Image.composite(
                Image.new("RGBA", base.size, (0, 0, 0, 255)),
                layer, layer.split()[3]
            )
            return Image.alpha_composite(base, result)
        else:
            return Image.alpha_composite(base, layer)

    def _update_preview(self):
        result = self.base.copy()
        for img, opacity, mode in self.layers:
            result = self._composite(result, img, opacity, mode)
        # Create preview pixmap
        preview = result.copy()
        preview.thumbnail((400, 300))
        data = preview.convert("RGB").tobytes()
        qimg = QImage(data, preview.width, preview.height, QImage.Format.Format_RGB888)
        self.preview.setPixmap(QPixmap.fromImage(qimg))

    def _apply(self):
        result = self.base.copy()
        for img, opacity, mode in self.layers:
            result = self._composite(result, img, opacity, mode)
        self._result = result.convert("RGB")
        self.accept()

    def get_result(self) -> Image.Image | None:
        return getattr(self, "_result", None)
