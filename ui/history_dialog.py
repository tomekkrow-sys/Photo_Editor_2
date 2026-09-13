#!/usr/bin/env python3
from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QSplitter, QWidget,
)
from PIL import Image
import numpy as np


class HistoryDialog(QDialog):
    def __init__(self, parent, history):
        super().__init__(parent)
        self.setWindowTitle("Historia edycji")
        self.setMinimumSize(600, 400)
        self.history = history
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        info = QLabel("Historia zmian obrazu (Ctrl+Z = cofnij, Ctrl+Y = ponow)")
        info.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(info)

        self.history_list = QListWidget()
        self.history_list.currentRowChanged.connect(self._on_select)

        # Populate from history (EditHistory uses _undo list)
        stack = self.history._undo if hasattr(self.history, '_undo') else []
        if stack:
            for i, item in enumerate(stack):
                desc = f"Krok {i + 1}"
                if hasattr(item, 'width') and hasattr(item, 'height'):
                    desc += f" - {item.width}x{item.height}"
                self.history_list.addItem(QListWidgetItem(desc))
        else:
            self.history_list.addItem(QListWidgetItem("(brak historii)"))

        # Preview
        self.preview = QLabel()
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumHeight(250)
        self.preview.setStyleSheet("border: 1px solid #444; background: #1a1a1a;")

        layout.addWidget(self.history_list)
        layout.addWidget(self.preview)

        btn_layout = QHBoxLayout()
        close_btn = QPushButton("Zamknij")
        close_btn.clicked.connect(self.accept)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def _on_select(self, row):
        stack = self.history._undo if hasattr(self.history, '_undo') else []
        if 0 <= row < len(stack):
            item = stack[row]
            if isinstance(item, Image.Image):
                preview = item.copy()
                preview.thumbnail((500, 400))
                data = preview.convert("RGB").tobytes()
                qimg = QImage(data, preview.width, preview.height, QImage.Format.Format_RGB888)
                self.preview.setPixmap(QPixmap.fromImage(qimg))
