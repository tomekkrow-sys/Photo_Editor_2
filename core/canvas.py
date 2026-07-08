#!/usr/bin/env python3
"""
Photo Editor 2.0

Canvas

Version: 0.2.0
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import (
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
    """
    Main image canvas.
    """

    image_loaded = Signal()

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
                "Images (*.png *.jpg *.jpeg "
                "*.bmp *.tif *.tiff *.webp)"
            ),
        )

        if not filename:
            return

        image = QImage(filename)

        if image.isNull():
            return

        self.document.clear()

        self.document.image = image
        self.document.original_image = image.copy()

        self.document.file_path = Path(filename)
        self.document.file_name = Path(filename).name

        self.document.width = image.width()
        self.document.height = image.height()

        pixmap = QPixmap.fromImage(image)

        self.image_item.setPixmap(pixmap)

        self.scene.setSceneRect(
            self.image_item.boundingRect()
        )

        self.resetTransform()

        self.fitInView(
            self.image_item,
            Qt.AspectRatioMode.KeepAspectRatio,
        )

        self.document.zoom = 100.0

        self.image_loaded.emit()

    def wheelEvent(
        self,
        event: QWheelEvent,
    ) -> None:

        if event.angleDelta().y() > 0:
            factor = self.ZOOM_STEP
        else:
            factor = 1.0 / self.ZOOM_STEP

        self.scale(factor, factor)

        self.document.zoom *= factor