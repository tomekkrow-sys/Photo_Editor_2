#!/usr/bin/env python3
from __future__ import annotations
from PySide6.QtWidgets import QLabel, QStatusBar
from config.i18n import t, I18n

class StatusBar(QStatusBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.zoom_label = QLabel("100%")
        self.size_label = QLabel("0 x 0")
        self.format_label = QLabel("---")
        self.msg_label = QLabel(t("status_ready"))
        self.addPermanentWidget(self.zoom_label)
        self.addPermanentWidget(self.size_label)
        self.addPermanentWidget(self.format_label)
        self.addWidget(self.msg_label)
        I18n.get().on_change(self._rebuild)

    def _rebuild(self, lang=None):
        self.msg_label.setText(t("status_ready"))
