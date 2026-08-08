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
        self.setFixedHeight(36)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.setStyleSheet("""
            QToolBar { background: #252526; border-bottom: 1px solid #333; spacing: 2px; padding: 2px 8px; }
            QToolButton { color: #CCCCCC; background: transparent; border: none; padding: 4px 10px; font-size: 11px; }
            QToolButton:hover { background: #3C3C3C; border-radius: 3px; }
            QToolButton:pressed { background: #4A9EFF; color: white; }
        """)
        self._build()
    def _build(self):
        self.addAction(self.actions.open)
        self.addAction(self.actions.save)
        self.addAction(self.actions.export)
        self.addSeparator()
        self.addAction(self.actions.crop)
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
