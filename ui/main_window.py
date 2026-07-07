#!/usr/bin/env python3
"""
Main Window
"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QMainWindow

from config.defaults import (
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
)

from config.version import WINDOW_TITLE

from ui.actions import ActionManager
from ui.menubar import MenuBar
from ui.statusbar import StatusBar
from ui.toolbar import ToolBar


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.actions = ActionManager(self)

        self._build_ui()

    def _build_ui(self):

        self.setWindowTitle(WINDOW_TITLE)

        self.resize(
            DEFAULT_WINDOW_WIDTH,
            DEFAULT_WINDOW_HEIGHT,
        )

        #
        # Menu
        #

        self.setMenuBar(
            MenuBar(self, self.actions)
        )

        #
        # Toolbar
        #

        self.addToolBar(
            ToolBar(self, self.actions)
        )

        #
        # StatusBar
        #

        self.setStatusBar(
            StatusBar(self)
        )

        #
        # Canvas (tymczasowy)
        #

        label = QLabel(
            "Photo Editor 2.0\n\nCanvas będzie dodany w następnym etapie."
        )

        label.setStyleSheet(
            """
            font-size:20px;
            """
        )

        self.setCentralWidget(label)

        self.statusBar().showMessage(
            "Program uruchomiony."
        )