#!/usr/bin/env python3
"""
Photo Editor 2.0

Canvas

Version: 0.3.2
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import (
    QDragEnterEvent,
    QDragMoveEvent,
    QDropEvent,
    QPixmap,
    QWheelEvent,
)
from PySide6.QtWidgets import (
    QFileDialog,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
)

from core.image_document import ImageDocument
from core.image_loader import ImageLoader


class Canvas(QGraphicsView):
    """Main image canvas."""

    image_loaded = Signal()
    zoom_changed = Signal(float)

    ZOOM_STEP = 1.15

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.document = ImageDocument()

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.image_item = QGraphicsPixmapItem()
        self.scene.addItem(self.image_item)

        self._configure()

    def _configure(self) -> None:
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)

        self.setDragMode(
            QGraphicsView.DragMode.ScrollHandDrag
        )

        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )

        self.setResizeAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )

        self.setBackgroundBrush(
            Qt.GlobalColor.darkGray
        )

    def open_image(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Otwórz obraz",
            "",
            ImageLoader.file_dialog_filter(),
        )

        if filename:
            self.load_image(filename)

    def load_image(
        self,
        file_path: str | Path,
    ) -> bool:
        try:
            document = ImageLoader.load(file_path)
        except (FileNotFoundError, ValueError):
            return False

        self.document = document

        pixmap = QPixmap.fromImage(document.image)

        self.image_item.setPixmap(pixmap)

        self.scene.setSceneRect(
            self.image_item.boundingRect()
        )

        self.fit_to_window()
        self.image_loaded.emit()

        return True

    def _event_has_supported_image(
        self,
        event: QDragEnterEvent | QDragMoveEvent,
    ) -> bool:
        mime_data = event.mimeData()

        if not mime_data.hasUrls():
            return False

        for url in mime_data.urls():
            if not url.isLocalFile():
                continue

            if ImageLoader.can_load(url.toLocalFile()):
                return True

        return False

    def dragEnterEvent(
        self,
        event: QDragEnterEvent,
    ) -> None:
        if self._event_has_supported_image(event):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(
        self,
        event: QDragMoveEvent,
    ) -> None:
        if self._event_has_supported_image(event):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(
        self,
        event: QDropEvent,
    ) -> None:
        if not event.mimeData().hasUrls():
            event.ignore()
            return

        for url in event.mimeData().urls():
            if not url.isLocalFile():
                continue

            if self.load_image(url.toLocalFile()):
                event.acceptProposedAction()
                return

        event.ignore()

    def zoom_in(self) -> None:
        if not self.document.is_loaded:
            return

        self.scale(
            self.ZOOM_STEP,
            self.ZOOM_STEP,
        )

        self._update_zoom()

    def zoom_out(self) -> None:
        if not self.document.is_loaded:
            return

        factor = 1.0 / self.ZOOM_STEP

        self.scale(
            factor,
            factor,
        )

        self._update_zoom()

    def actual_size(self) -> None:
        """Display the image at a 1:1 scale."""

        if not self.document.is_loaded:
            return

        self.resetTransform()
        self._update_zoom()

    def fit_to_window(self) -> None:
        """Fit the image into the available viewport."""

        if not self.document.is_loaded:
            return

        self.resetTransform()

        if not self.image_item.pixmap().isNull():
            self.fitInView(
                self.image_item,
                Qt.AspectRatioMode.KeepAspectRatio,
            )

        self._update_zoom()

    def _update_zoom(self) -> None:
        zoom = self.transform().m11() * 100.0

        self.document.zoom = zoom
        self.zoom_changed.emit(zoom)

    def wheelEvent(
        self,
        event: QWheelEvent,
    ) -> None:
        if (
            not self.document.is_loaded
            or not event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            super().wheelEvent(event)
            return

        delta = event.angleDelta().y()

        if delta > 0:
            self.zoom_in()
        elif delta < 0:
            self.zoom_out()
        else:
            super().wheelEvent(event)
            return

        event.accept()
