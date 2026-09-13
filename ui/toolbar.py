#!/usr/bin/env python3
from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QToolBar

class ToolBar(QToolBar):
    def __init__(self, parent, actions):
        super().__init__("Main Toolbar", parent)
        self.actions = actions
        self.setMovable(False)
        self.setFloatable(False)
        self.setFixedHeight(40)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self._build()
    def _build(self):
        self.addAction(self.actions.open)
        self.addAction(self.actions.save)
        self.addAction(self.actions.export)
        self.addSeparator()
        self.addAction(self.actions.crop)
        self.addAction(self.actions.spot)
        self.addAction(self.actions.brush)
        self.addSeparator()
        self.addAction(self.actions.rotate_left)
        self.addAction(self.actions.rotate_right)
        self.addAction(self.actions.flip_h)
        self.addAction(self.actions.flip_v)
        self.addSeparator()
        self.addAction(self.actions.before_after)
        self.addSeparator()
        self.addAction(self.actions.pencil)
        self.addAction(self.actions.black_white)
        self.addSeparator()
        self.addAction(self.actions.batch)
        self.addSeparator()
        self.addAction(self.actions.zoom_in)
        self.addAction(self.actions.zoom_out)
        self.addAction(self.actions.fit)
