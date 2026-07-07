#!/usr/bin/env python3
"""
Photo Editor 2.0

Status Bar
"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QStatusBar


class StatusBar(QStatusBar):

    def __init__(self, parent):

        super().__init__(parent)

        self.zoom = QLabel("100%")

        self.size = QLabel("0 × 0")

        self.format = QLabel("---")

        self.message = QLabel("Ready")

        self.addPermanentWidget(self.zoom)

        self.addPermanentWidget(self.size)

        self.addPermanentWidget(self.format)

        self.addWidget(self.message)