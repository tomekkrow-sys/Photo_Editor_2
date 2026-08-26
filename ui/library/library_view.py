#!/usr/bin/env python3
"""Photo Editor 2.0 — Library View with rating, filter, search."""

from __future__ import annotations

from PySide6.QtCore import Qt, QSortFilterProxyModel, Signal, QThreadPool
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDockWidget,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class PhotoGridItem(QFrame):
    """Single item in the photo grid."""

    selected = Signal()
    doubleClicked = Signal()

    def __init__(self, photo, parent=None):
        super().__init__(parent)
        self.photo = photo
        self._rating = 0
        self._is_selected = False
        self._is_rejected = False

        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self.thumb_label = QLabel()
        self.thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.thumb_label)

        self.filename_label = QLabel(photo.stem)
        self.filename_label.setStyleSheet("color: #CCCCCC; font-size: 11px;")
        layout.addWidget(self.filename_label)

        self._update_style()

    def set_pixmap(self, pixmap: QPixmap) -> None:
        scaled = pixmap.scaled(180, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.thumb_label.setPixmap(scaled)

    def set_rating(self, rating: int) -> None:
        self._rating = rating
        self._update_style()

    def toggle_select(self) -> None:
        self._is_selected = not self._is_selected
        self._update_style()
        self.selected.emit()

    def _update_style(self) -> None:
        if self._is_selected:
            self.setStyleSheet("""
                QFrame {
                    background: #2A2A3A;
                    border: 2px solid #4A9EFF;
                    border-radius: 4px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background: #1E1E1E;
                    border: 2px solid #333333;
                    border-radius: 4px;
                }
            """)

        if self._is_rejected:
            self.setStyleSheet(self.styleSheet().replace("border-radius: 4px;", "border-radius: 4px; opacity: 0.6;"))


class LibraryView(QWidget):
    """Library view with grid layout, filters, and search."""

    photo_selected = Signal(object)
    photo_double_clicked = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._photos: list = []
        self._filter_vendor = "Wszystkie"
        self._filter_rating = 0
        self._search_text = ""
        self._thread_pool = QThreadPool()

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        toolbar = self._build_toolbar()
        layout.addWidget(toolbar)

        self._grid_widget = QWidget()
        self._grid_layout = QGridLayout(self._grid_widget)
        self._grid_layout.setSpacing(8)
        layout.addWidget(self._grid_widget)

        self._update_grid()

    def _build_toolbar(self) -> QWidget:
        toolbar = QWidget()
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(8, 4, 8, 4)

        search = QLineEdit()
        search.setPlaceholderText("Szukaj...")
        search.textChanged.connect(self._on_search_changed)
        layout.addWidget(search)

        vendor_combo = QComboBox()
        vendor_combo.addItem("Wszystkie")
        vendor_combo.currentTextChanged.connect(self._on_vendor_changed)
        layout.addWidget(vendor_combo)

        rating_combo = QComboBox()
        rating_combo.addItem("Wszystkie")
        for i in range(1, 6):
            rating_combo.addItem(f"{i} ★")
        rating_combo.currentIndexChanged.connect(self._on_rating_changed)
        layout.addWidget(rating_combo)

        flags_layout = QHBoxLayout()
        flags_layout.addWidget(QLabel("Oznaczenia:"))

        self._picked_check = QCheckBox("Wybrane")
        self._picked_check.setChecked(True)
        self._picked_check.stateChanged.connect(lambda: self._update_grid())
        flags_layout.addWidget(self._picked_check)

        self._rejected_check = QCheckBox("Odrzucone")
        self._rejected_check.setChecked(True)
        self._rejected_check.stateChanged.connect(lambda: self._update_grid())
        flags_layout.addWidget(self._rejected_check)

        layout.addLayout(flags_layout)
        layout.addStretch()

        return toolbar

    def set_photos(self, photos: list) -> None:
        self._photos = photos
        self._update_grid()

    def _update_grid(self) -> None:
        for i in reversed(range(self._grid_layout.count())):
            widget = self._grid_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        row, col = 0, 0
        for photo in self._photos:
            if not self._matches_filters(photo):
                continue

            item = PhotoGridItem(photo)
            item.set_pixmap(QPixmap(str(photo.full_path)))
            item.selected.connect(lambda p=photo: self.photo_selected.emit(p))
            item.doubleClicked.connect(lambda p=photo: self.photo_double_clicked.emit(p))
            item.doubleClicked.connect(lambda p=photo: self.photo_double_clicked.emit(p))
            item.doubleClicked.connect(lambda: self._on_item_double_clicked(item))
            item.mousePressEvent = lambda e, item=item: self._on_item_click(e, item)

            self._grid_layout.addWidget(item, row, col)

            col += 1
            if col > 4:
                col = 0
                row += 1

    def _matches_filters(self, photo) -> bool:
        if self._filter_vendor != "Wszystkie":
            if hasattr(photo, "vendor") and photo.vendor != self._filter_vendor:
                return False

        if self._filter_rating > 0:
            if hasattr(photo, "rating") and photo.rating != self._filter_rating:
                return False

        if self._search_text:
            text_lower = self._search_text.lower()
            if text_lower not in photo.stem.lower():
                return False

        return True

    def _on_search_changed(self, text: str) -> None:
        self._search_text = text
        self._update_grid()

    def _on_vendor_changed(self, vendor: str) -> None:
        self._filter_vendor = vendor
        self._update_grid()

    def _on_rating_changed(self, index: int) -> None:
        self._filter_rating = index
        self._update_grid()

    def _on_item_click(self, event, item: PhotoGridItem) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            item.toggle_select()

    def _on_item_double_clicked(self, item: PhotoGridItem) -> None:
        self.photo_double_clicked.emit(item.photo)


class LibraryPanel(QDockWidget):
    """Dockable library panel."""

    def __init__(self, title: str = "Biblioteka", parent=None):
        super().__init__(title, parent)

        self.library_view = LibraryView()
        self.setWidget(self.library_view)

        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
