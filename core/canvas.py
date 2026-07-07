#!/usr/bin/env python3
"""
Photo Editor 2.0

Canvas widget.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QImage,
    QPixmap,
)

from PySide6.QtWidgets import (
    QFileDialog,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
)


class Canvas(QGraphicsView):
    """
    Main image canvas.
    """

    def __init__(self, parent=None):

        super().__init__(parent)

        self.scene = QGraphicsScene(self)

        self.setScene(self.scene)

        self.image_item = QGraphicsPixmapItem()

        self.scene.addItem(self.image_item)

        self.current_file: Path | None = None

        self.zoom_factor = 1.0

        self._configure()

    def _configure(self):

        self.setRenderHints(
            self.renderHints()
        )

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

    # --------------------------------------------------

    def open_image(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.webp)"
        )

        if not filename:
            return

        image = QImage(filename)

        if image.isNull():
            return

        self.current_file = Path(filename)

        pixmap = QPixmap.fromImage(image)

        self.image_item.setPixmap(pixmap)

        self.scene.setSceneRect(
            pixmap.rect()
        )

        self.fitInView(
            self.image_item,
            Qt.AspectRatioMode.KeepAspectRatio
        )

        self.zoom_factor = 1.0

    # --------------------------------------------------

    def wheelEvent(self, event):

        factor = 1.15

        if event.angleDelta().y() > 0:

            self.scale(
                factor,
                factor,
            )

            self.zoom_factor *= factor

        else:

            self.scale(
                1 / factor,
                1 / factor,
            )

            self.zoom_factor /= factor