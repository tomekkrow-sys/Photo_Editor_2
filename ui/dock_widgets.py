"""Dock widgets used by the application."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDockWidget, QWidget


class DockWidget(QDockWidget):
    """Base dock widget used by editor panels."""

    def __init__(self, title: str, widget: QWidget, parent=None) -> None:
        super().__init__(title, parent)

        self.setWidget(widget)
        self.setAllowedAreas(
            Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea
        )
