#!/usr/bin/env python3
"""Photo Editor 2.0 — Export Presets manager."""

from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)


DEFAULT_PRESETS = [
    {
        "name": "JPG Web",
        "format": "JPG",
        "quality": 85,
        "resize": 1920,
        "keep_original_size": False,
    },
    {
        "name": "JPG High Quality",
        "format": "JPG",
        "quality": 95,
        "resize": 4096,
        "keep_original_size": True,
    },
    {
        "name": "PNG Lossless",
        "format": "PNG",
        "quality": 100,
        "resize": None,
        "keep_original_size": True,
    },
    {
        "name": "TIFF Edit",
        "format": "TIFF",
        "quality": 100,
        "resize": None,
        "keep_original_size": True,
    },
]


class PresetManager:
    """Export preset manager."""

    PRESETS_DIR = Path("export_presets")

    @classmethod
    def load_presets(cls) -> list[dict]:
        presets = []
        presets_file = cls.PRESETS_DIR / "presets.json"
        if presets_file.exists():
            with open(presets_file) as f:
                presets.extend(json.load(f))
        presets.extend(DEFAULT_PRESETS)
        return presets

    @classmethod
    def save_preset(cls, preset: dict) -> None:
        cls.PRESETS_DIR.mkdir(exist_ok=True)
        presets_file = cls.PRESETS_DIR / "presets.json"
        presets = cls.load_presets()
        presets = [p for p in presets if p["name"] != preset["name"]]
        presets.append(preset)
        with open(presets_file, "w") as f:
            json.dump(presets, f, indent=2)

    @classmethod
    def delete_preset(cls, name: str) -> None:
        presets_file = cls.PRESETS_DIR / "presets.json"
        if presets_file.exists():
            with open(presets_file) as f:
                presets = json.load(f)
            presets = [p for p in presets if p["name"] != name]
            with open(presets_file, "w") as f:
                json.dump(presets, f, indent=2)


class ExportPresetDialog(QDialog):
    """Export preset configuration dialog."""

    def __init__(self, parent=None, preset: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Konfiguracja presetsu eksportu")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        form = QFormLayout()
        self._name_edit = preset.get("name", "Nowy preset")
        self._name_input = self._create_name_input(preset)
        form.addRow("Nazwa:", self._name_input)
        layout.addLayout(form)

        self._format_group = self._create_format_group(preset)
        layout.addWidget(self._format_group)

        self._resize_group = self._create_resize_group(preset)
        layout.addWidget(self._resize_group)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._preset = preset or {}

    def _create_name_input(self, preset: dict | None) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self._name_input = self._name_input if hasattr(self, "_name_input") else preset.get("name", "Nowy preset")
        return widget

    def _create_format_group(self, preset: dict | None) -> QGroupBox:
        group = QGroupBox("Format")
        layout = QFormLayout(group)

        self._format_combo = preset.get("format", "JPG")
        self._format_combo = self._create_format_combo(preset)
        layout.addRow("Format:", self._format_combo)

        self._quality_slider = preset.get("quality", 85)
        self._quality_slider = self._create_quality_slider(preset)
        layout.addRow("Jakość:", self._quality_slider)

        return group

    def _create_format_combo(self, preset: dict) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        formats = ["JPG", "PNG", "TIFF"]
        self._format_combo = preset.get("format", "JPG")
        return widget

    def _create_quality_slider(self, preset: dict) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self._quality_slider = preset.get("quality", 85)
        return widget

    def _create_resize_group(self, preset: dict | None) -> QGroupBox:
        group = QGroupBox("Zmiana rozmiaru")
        layout = QFormLayout(group)

        self._resize_check = preset.get("resize", 1920)
        self._resize_check = self._create_resize_check(preset)
        layout.addRow("Maks. szerokość:", self._resize_check)

        self._keep_original_check = preset.get("keep_original_size", False)
        self._keep_original_check = self._create_keep_original_check(preset)
        layout.addRow("Oryginalny rozmiar:", self._keep_original_check)

        return group

    def _create_resize_check(self, preset: dict) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self._resize_check = preset.get("resize", 1920)
        return widget

    def _create_keep_original_check(self, preset: dict) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self._keep_original_check = preset.get("keep_original_size", False)
        return widget

    def get_preset(self) -> dict:
        return {
            "name": self._name_input if isinstance(self._name_input, str) else "Nowy preset",
            "format": self._format_combo if isinstance(self._format_combo, str) else "JPG",
            "quality": self._quality_slider if isinstance(self._quality_slider, int) else 85,
            "resize": self._resize_check if isinstance(self._resize_check, int) else 1920,
            "keep_original_size": self._keep_original_check if isinstance(self._keep_original_check, bool) else False,
        }


class PresetListWidget(QListWidget):
    """Widget showing list of export presets."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)

    def load_presets(self) -> None:
        self.clear()
        presets = PresetManager.load_presets()
        for preset in presets:
            item = QListWidgetItem(preset["name"])
            item.setData(32, preset)
            self.addItem(item)

    def get_selected_preset(self) -> dict | None:
        item = self.currentItem()
        return item.data(32) if item else None

    def get_all_presets(self) -> list[dict]:
        return [self.item(i).data(32) for i in range(self.count())]
