#!/usr/bin/env python3
from __future__ import annotations
from PySide6.QtWidgets import QLabel, QStatusBar

class StatusBar(QStatusBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.setStyleSheet("QStatusBar { background: #252526; color: #AAAAAA; border-top: 1px solid #333; } QLabel { color: #AAAAAA; }")
        self.zoom_label = QLabel("100%")
        self.size_label = QLabel("0 × 0")
        self.format_label = QLabel("---")
        self.msg_label = QLabel("Ready")
        self.addPermanentWidget(self.zoom_label)
        self.addPermanentWidget(self.size_label)
        self.addPermanentWidget(self.format_label)
        self.addWidget(self.msg_label)
