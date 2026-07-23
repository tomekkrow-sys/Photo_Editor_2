#!/usr/bin/env python3

from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QListView,
    QVBoxLayout,
    QWidget,
)

from core.catalog.photo import Photo
from core.thumbnails.thumbnail_cache import ThumbnailCache
from ui.library.photo_list_model import PhotoListModel


class LibraryPanel(QWidget):
    """Panel biblioteki zdjęć."""

    photo_selected = Signal(Photo)

    THUMB_WIDTH = 180
    THUMB_HEIGHT = 120

    def __init__(self, parent=None):
        super().__init__(parent)

        self.thumbnail_cache = ThumbnailCache()

        self.model = PhotoListModel(self)

        self.view = QListView()

        self.view.setModel(self.model)

        self.view.setViewMode(QListView.IconMode)
        self.view.setFlow(QListView.LeftToRight)
        self.view.setResizeMode(QListView.Adjust)
        self.view.setWrapping(True)
        self.view.setMovement(QListView.Static)

        self.view.setIconSize(QSize(self.THUMB_WIDTH, self.THUMB_HEIGHT))
        self.view.setGridSize(QSize(200, 170))
        self.view.setSpacing(10)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)

        self.view.doubleClicked.connect(self._item_activated)

    def load_photos(self, photos: list[Photo]) -> None:
        seen: set[str] = set()
        filtered: list[Photo] = []

        for photo in photos:
            if photo.stem in seen:
                continue
            seen.add(photo.stem)
            filtered.append(photo)

        self.model.set_photos(filtered)

    def _item_activated(self, index) -> None:
        photo = index.data(Qt.UserRole)
        self.photo_selected.emit(photo)
