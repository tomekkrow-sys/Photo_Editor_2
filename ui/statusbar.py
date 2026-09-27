#!/usr/bin/env python3
from __future__ import annotations
from PySide6.QtWidgets import QLabel, QStatusBar, QProgressBar
from config.i18n import t, I18n

class StatusBar(QStatusBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.zoom_label = QLabel("100%")
        self.size_label = QLabel("0 x 0")
        self.format_label = QLabel("---")
        self.msg_label = QLabel(t("status_ready"))
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(150)

        self.addPermanentWidget(self.progress_bar)
        self.addPermanentWidget(self.zoom_label)
        self.addPermanentWidget(self.size_label)
        self.addPermanentWidget(self.format_label)
        self.addWidget(self.msg_label)
        I18n.get().on_change(self._rebuild)

    def show_progress(self, min_val=0, max_val=100):
        self.progress_bar.setRange(min_val, max_val)
        self.progress_bar.setValue(min_val)
        self.progress_bar.setVisible(True)

    def set_progress(self, val):
        self.progress_bar.setValue(val)

    def hide_progress(self):
        self.progress_bar.setVisible(False)

    def _rebuild(self, lang=None):
        self.msg_label.setText(t("status_ready"))
