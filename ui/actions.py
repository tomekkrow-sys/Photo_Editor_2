#!/usr/bin/env python3
"""
Photo Editor 2.0
Action Manager
"""

from __future__ import annotations

from PySide6.QtGui import QAction

from config import shortcuts


class ActionManager:
    """Creates and stores all application actions."""

    def __init__(self, parent):
        self.parent = parent
        self._create_actions()

    def _create_actions(self):
        # FILE

        self.new = QAction("&Nowy", self.parent)
        self.new.setShortcut(shortcuts.NEW)

        self.open = QAction("&Otwórz...", self.parent)
        self.open.setShortcut(shortcuts.OPEN)

        self.save = QAction("&Zapisz", self.parent)
        self.save.setShortcut(shortcuts.SAVE)

        self.save_as = QAction("Zapisz &jako...", self.parent)
        self.save_as.setShortcut(shortcuts.SAVE_AS)

        self.export = QAction("&Eksport", self.parent)
        self.export.setShortcut(shortcuts.EXPORT)

        self.exit = QAction("&Zakończ", self.parent)
        self.exit.setShortcut(shortcuts.EXIT)

        # EDIT

        self.undo = QAction("&Cofnij", self.parent)
        self.undo.setShortcut(shortcuts.UNDO)
        self.undo.setEnabled(False)

        self.redo = QAction("&Ponów", self.parent)
        self.redo.setShortcut(shortcuts.REDO)
        self.redo.setEnabled(False)

        self.cut = QAction("&Wytnij", self.parent)
        self.cut.setShortcut(shortcuts.CUT)

        self.copy = QAction("&Kopiuj", self.parent)
        self.copy.setShortcut(shortcuts.COPY)

        self.paste = QAction("W&klej", self.parent)
        self.paste.setShortcut(shortcuts.PASTE)

        self.delete = QAction("&Usuń", self.parent)
        self.delete.setShortcut(shortcuts.DELETE)

        # VIEW

        self.zoom_in = QAction("Powiększ", self.parent)
        self.zoom_in.setShortcut(shortcuts.ZOOM_IN)

        self.zoom_out = QAction("Pomniejsz", self.parent)
        self.zoom_out.setShortcut(shortcuts.ZOOM_OUT)

        self.fit = QAction("Dopasuj", self.parent)
        self.fit.setShortcut(shortcuts.FIT)

        self.actual_size = QAction("100%", self.parent)
        self.actual_size.setShortcut(shortcuts.ACTUAL_SIZE)

        # IMAGE

        self.resize_image = QAction(
            "Zmień rozmiar...",
            self.parent,
        )

        self.rotate_left = QAction(
            "Obróć 90° w lewo",
            self.parent,
        )

        self.rotate_right = QAction(
            "Obróć 90° w prawo",
            self.parent,
        )

        self.flip_horizontal = QAction(
            "Odbij poziomo",
            self.parent,
        )

        self.flip_vertical = QAction(
            "Odbij pionowo",
            self.parent,
        )

        # TOOLS

        self.crop = QAction("Kadruj", self.parent)
        self.crop.setShortcut(shortcuts.CROP)
        self.crop.setCheckable(True)

        self.rectangle = QAction("Prostokąt", self.parent)
        self.rectangle.setShortcut(shortcuts.RECTANGLE)

        self.ellipse = QAction("Elipsa", self.parent)
        self.ellipse.setShortcut(shortcuts.ELLIPSE)

        self.move = QAction("Przesuń", self.parent)
        self.move.setShortcut(shortcuts.MOVE)