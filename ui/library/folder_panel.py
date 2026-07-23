from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QListWidget


class FolderPanel(QListWidget):
    """Lista zaimportowanych folderów."""

    folder_selected = Signal(Path)

    def load_folders(self, folders: list[Path]) -> None:
        self.clear()

        for folder in folders:
            self.addItem(str(folder))

    def mouseDoubleClickEvent(self, event):
        item = self.currentItem()

        if item is not None:
            self.folder_selected.emit(Path(item.text()))

        super().mouseDoubleClickEvent(event)
