#!/usr/bin/env python3
"""
Photo Editor 2.0
Menu Bar
"""

from __future__ import annotations

from PySide6.QtWidgets import QMenuBar


class MenuBar(QMenuBar):
    """Main application menu."""

    def __init__(self, parent, actions):
        super().__init__(parent)

        self.actions = actions
        self._build()

    def _build(self):
        # FILE

        file_menu = self.addMenu("&Plik")

        file_menu.addAction(self.actions.new)
        file_menu.addAction(self.actions.open)

        file_menu.addSeparator()

        file_menu.addAction(self.actions.save)
        file_menu.addAction(self.actions.save_as)

        file_menu.addSeparator()

        file_menu.addAction(self.actions.export)

        file_menu.addSeparator()

        file_menu.addAction(self.actions.exit)

        # EDIT

        edit_menu = self.addMenu("&Edycja")

        edit_menu.addAction(self.actions.undo)
        edit_menu.addAction(self.actions.redo)

        edit_menu.addSeparator()

        edit_menu.addAction(self.actions.cut)
        edit_menu.addAction(self.actions.copy)
        edit_menu.addAction(self.actions.paste)

        edit_menu.addSeparator()

        edit_menu.addAction(self.actions.delete)

        # IMAGE

        image_menu = self.addMenu("&Obraz")

        image_menu.addAction(self.actions.rotate_left)
        image_menu.addAction(self.actions.rotate_right)

        # FILTERS

        self.addMenu("&Filtry")

        # VIEW

        view_menu = self.addMenu("&Widok")

        view_menu.addAction(self.actions.zoom_in)
        view_menu.addAction(self.actions.zoom_out)

        view_menu.addSeparator()

        view_menu.addAction(self.actions.fit)
        view_menu.addAction(self.actions.actual_size)

        # TOOLS

        tools_menu = self.addMenu("&Narzędzia")

        tools_menu.addAction(self.actions.move)
        tools_menu.addAction(self.actions.crop)

        tools_menu.addSeparator()

        tools_menu.addAction(self.actions.rectangle)
        tools_menu.addAction(self.actions.ellipse)

        # HELP

        self.addMenu("&Pomoc")