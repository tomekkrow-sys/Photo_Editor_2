#!/usr/bin/env python3
"""
Photo Editor 2.0

Status Bar

Version: 0.2.0
"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QStatusBar


class StatusBar(QStatusBar):
    """
    Main application status bar.
    """

    def __init__(self, parent=None) -> None:

        super().__init__(parent)

        self.file_name = QLabel("Brak pliku")
        self.image_size = QLabel("0 × 0")
        self.zoom = QLabel("100%")
        self.message = QLabel("Gotowy")

        self.addWidget(self.message)
        self.addPermanentWidget(self.file_name)
        self.addPermanentWidget(self.image_size)
        self.addPermanentWidget(self.zoom)

    def set_file_name(self, name: str) -> None:
        self.file_name.setText(name)

    def set_image_size(self, width: int, height: int) -> None:
        self.image_size.setText(f"{width} × {height}")

    def set_zoom(self, zoom: float) -> None:
        self.zoom.setText(f"{zoom:.0f}%")

    def set_message(self, text: str) -> None:
        self.showMessage(text)