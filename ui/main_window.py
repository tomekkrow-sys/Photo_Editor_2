#!/usr/bin/env python3
"""
Photo Editor 2.0

Main Window

Version: 0.2.1
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QMainWindow,
    QMessageBox,
)

from config.defaults import (
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
)
from config.version import WINDOW_TITLE
from core.canvas import Canvas
from ui.actions import ActionManager
from ui.menubar import MenuBar
from ui.statusbar import StatusBar
from ui.toolbar import ToolBar


class MainWindow(QMainWindow):
    """
    Main application window.
    """

    def __init__(self) -> None:

        super().__init__()

        self.actions = ActionManager(self)
        self.canvas = Canvas(self)

        self._build_window()
        self._create_connections()

    def _build_window(self) -> None:

        self.setWindowTitle(WINDOW_TITLE)

        self.resize(
            DEFAULT_WINDOW_WIDTH,
            DEFAULT_WINDOW_HEIGHT,
        )

        self.setMenuBar(
            MenuBar(
                self,
                self.actions,
            )
        )

        self.addToolBar(
            ToolBar(
                self,
                self.actions,
            )
        )

        self.status_bar = StatusBar(self)
        self.setStatusBar(self.status_bar)

        self.setCentralWidget(self.canvas)

        self.status_bar.set_message("Gotowy")

    def _create_connections(self) -> None:

        self.actions.open.triggered.connect(
            self.canvas.open_image
        )

        self.actions.exit.triggered.connect(
            self.close
        )

        self.actions.zoom_in.triggered.connect(
            self.canvas.zoom_in
        )

        self.actions.zoom_out.triggered.connect(
            self.canvas.zoom_out
        )

        self.actions.fit.triggered.connect(
            self.canvas.fit_to_window
        )

        self.actions.actual_size.triggered.connect(
            self.canvas.actual_size
        )

        self.actions.crop.toggled.connect(
            self._handle_crop_action_toggled
        )

        self.canvas.image_loaded.connect(
            self._update_status_bar
        )

        self.canvas.zoom_changed.connect(
            self.status_bar.set_zoom
        )

        self.canvas.crop_mode_changed.connect(
            self.actions.crop.setChecked
        )

    def _handle_crop_action_toggled(self, enabled: bool) -> None:

        if enabled:
            self.canvas.set_crop_selection_enabled(True)
            return

        if self.canvas.crop_selection_enabled and self.canvas.crop_tool.has_selection:
            if self.canvas.apply_crop():
                return

        self.canvas.set_crop_selection_enabled(False)

    def _update_status_bar(self) -> None:

        document = self.canvas.document

        self.status_bar.set_file_name(
            document.file_name
        )

        self.status_bar.set_image_size(
            document.width,
            document.height,
        )

        self.status_bar.set_message(
            "Obraz załadowany"
        )

    def closeEvent(self, event) -> None:

        if self.canvas.document.modified:

            answer = QMessageBox.question(
                self,
                "Photo Editor 2.0",
                (
                    "Obraz został zmodyfikowany.\n\n"
                    "Na pewno zamknąć program?"
                ),
            )

            if answer != QMessageBox.StandardButton.Yes:

                event.ignore()
                return

        event.accept()
