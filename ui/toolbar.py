#!/usr/bin/env python3
"""
Photo Editor 2.0

Main Toolbar
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QToolBar


class ToolBar(QToolBar):
    """
    Main application toolbar.
    """

    def __init__(self, parent, actions):

        super().__init__("Main Toolbar", parent)

        self.actions = actions

        self.setMovable(True)
        self.setFloatable(False)

        self.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonIconOnly
        )

        self._build()

    def _build(self):

        #
        # FILE
        #

        self.addAction(self.actions.new)
        self.addAction(self.actions.open)
        self.addAction(self.actions.save)

        self.addSeparator()

        #
        # HISTORY
        #

        self.addAction(self.actions.undo)
        self.addAction(self.actions.redo)

        self.addSeparator()

        #
        # TOOLS
        #

        self.addAction(self.actions.move)
        self.addAction(self.actions.crop)

        self.addSeparator()

        self.addAction(self.actions.rectangle)
        self.addAction(self.actions.ellipse)

        self.addSeparator()

        #
        # VIEW
        #

        self.addAction(self.actions.zoom_in)
        self.addAction(self.actions.zoom_out)

        self.addAction(self.actions.fit)