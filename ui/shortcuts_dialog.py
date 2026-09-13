#!/usr/bin/env python3
from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QKeySequenceEdit,
    QMessageBox,
)
from PySide6.QtGui import QKeySequence
import json
from pathlib import Path


CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
SHORTCUTS_FILE = CONFIG_DIR / "shortcuts.json"

DEFAULT_SHORTCUTS = {
    "new": "Ctrl+N",
    "open": "Ctrl+O",
    "save": "Ctrl+S",
    "save_as": "Ctrl+Shift+S",
    "export": "Ctrl+E",
    "exit": "Ctrl+Q",
    "undo": "Ctrl+Z",
    "redo": "Ctrl+Y",
    "cut": "Ctrl+X",
    "copy": "Ctrl+C",
    "paste": "Ctrl+V",
    "delete": "Delete",
    "zoom_in": "Ctrl+Plus",
    "zoom_out": "Ctrl+Minus",
    "fit": "Ctrl+0",
    "actual_size": "Ctrl+1",
    "crop": "C",
    "spot": "S",
}


def load_shortcuts() -> dict:
    try:
        if SHORTCUTS_FILE.exists():
            data = json.loads(SHORTCUTS_FILE.read_text())
            merged = {**DEFAULT_SHORTCUTS, **data}
            return merged
    except Exception:
        pass
    return dict(DEFAULT_SHORTCUTS)


def save_shortcuts(shortcuts: dict) -> None:
    SHORTCUTS_FILE.write_text(json.dumps(shortcuts, indent=2))


class ShortcutsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Skróty klawiszowe")
        self.setMinimumSize(500, 500)
        self.shortcuts = load_shortcuts()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self.table = QTableWidget(len(self.shortcuts), 2)
        self.table.setHorizontalHeaderLabels(["Akcja", "Skrót"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)

        self.key_edits = {}
        for row, (action, key) in enumerate(self.shortcuts.items()):
            self.table.setItem(row, 0, QTableWidgetItem(action))
            editor = QKeySequenceEdit(QKeySequence(key))
            self.key_edits[action] = editor
            self.table.setCellWidget(row, 1, editor)

        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        reset_btn = QPushButton("Przywroć domyslne")
        reset_btn.clicked.connect(self._reset)
        save_btn = QPushButton("Zapisz")
        save_btn.clicked.connect(self._save)
        cancel_btn = QPushButton("Anuluj")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(reset_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def _reset(self):
        for action, editor in self.key_edits.items():
            editor.setKeySequence(QKeySequence(DEFAULT_SHORTCUTS.get(action, "")))

    def _save(self):
        new_shortcuts = {}
        for action, editor in self.key_edits.items():
            seq = editor.keySequence().toString()
            if seq:
                new_shortcuts[action] = seq
        save_shortcuts(new_shortcuts)
        self.shortcuts = new_shortcuts
        QMessageBox.information(self, "Zapisano", "Skróty zapisane. Zrestartuj aplikacje.")
        self.accept()
