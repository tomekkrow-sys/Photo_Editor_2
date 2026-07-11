#!/usr/bin/env python3
"""
Photo Editor 2.0

Canvas

Version: 0.3.2
"""

from __future__ import annotations

from pathlib import Path

import rawpy

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import (
    QDragEnterEvent,
    QDragMoveEvent,
    QDropEvent,
    QImage,
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


class Canvas(QGraphicsView):
    """Main image canvas."""

    image_loaded = Signal()

    ZOOM_STEP = 1.15

    STANDARD_EXTENSIONS = {
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".tif",
        ".tiff",
        ".webp",
    }

    RAW_EXTENSIONS = {
        ".nef",
        ".cr2",
        ".cr3",
        ".arw",
        ".dng",
        ".orf",
        ".rw2",
        ".raf",
        ".pef",
    }

    SUPPORTED_EXTENSIONS = (
        STANDARD_EXTENSIONS | RAW_EXTENSIONS
    )

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
            (
                "Wszystkie obsługiwane obrazy "
                "(*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.webp "
                "*.nef *.cr2 *.cr3 *.arw *.dng *.orf *.rw2 "
                "*.raf *.pef);;"
                "Obrazy (*.png *.jpg *.jpeg *.bmp "
                "*.tif *.tiff *.webp);;"
                "RAW (*.nef *.cr2 *.cr3 *.arw *.dng "
                "*.orf *.rw2 *.raf *.pef)"
            ),
        )

        if filename:
            self.load_image(filename)

    def load_image(
        self,
        file_path: str | Path,
    ) -> bool:
        path = Path(file_path)

        if not path.is_file():
            return False

        extension = path.suffix.lower()

        if extension not in self.SUPPORTED_EXTENSIONS:
            return False

        if extension in self.RAW_EXTENSIONS:
            image = self._load_raw_image(path)
        else:
            image = QImage(str(path))

        if image.isNull():
            return False

        self.document.clear()

        self.document.image = image
        self.document.original_image = image.copy()
        self.document.file_path = path
        self.document.file_name = path.name
        self.document.width = image.width()
        self.document.height = image.height()
        self.document.format = extension.lstrip(".")
        self.document.modified = False

        pixmap = QPixmap.fromImage(image)

        self.image_item.setPixmap(pixmap)

        self.scene.setSceneRect(
            self.image_item.boundingRect()
        )

        self.reset_zoom()
        self.image_loaded.emit()

        return True

    @staticmethod
    def _load_raw_image(path: Path) -> QImage:
        try:
            with rawpy.imread(str(path)) as raw:
                rgb = raw.postprocess(
                    use_camera_wb=True,
                    no_auto_bright=False,
                    output_bps=8,
                )

            height, width, channels = rgb.shape

            if channels != 3:
                return QImage()

            bytes_per_line = width * channels

            image = QImage(
                rgb.data,
                width,
                height,
                bytes_per_line,
                QImage.Format.Format_RGB888,
            )

            return image.copy()

        except (
            rawpy.LibRawError,
            OSError,
            ValueError,
        ):
            return QImage()

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

            path = Path(url.toLocalFile())

            if (
                path.is_file()
                and path.suffix.lower()
                in self.SUPPORTED_EXTENSIONS
            ):
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

        self.document.zoom *= self.ZOOM_STEP

    def zoom_out(self) -> None:
        if not self.document.is_loaded:
            return

        factor = 1.0 / self.ZOOM_STEP

        self.scale(
            factor,
            factor,
        )

        self.document.zoom *= factor

    def reset_zoom(self) -> None:
        self.resetTransform()

        if not self.image_item.pixmap().isNull():
            self.fitInView(
                self.image_item,
                Qt.AspectRatioMode.KeepAspectRatio,
            )

        self.document.zoom = 100.0

    def wheelEvent(
        self,
        event: QWheelEvent,
    ) -> None:
        if not self.document.is_loaded:
            super().wheelEvent(event)
            return

        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()

        event.accept()