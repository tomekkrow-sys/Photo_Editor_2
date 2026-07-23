from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtWidgets import (
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
)


class ImageView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)

        scene = QGraphicsScene(self)
        self.setScene(scene)

        self._item = QGraphicsPixmapItem()
        scene.addItem(self._item)

        self.setBackgroundBrush(Qt.darkGray)

        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

    def set_pixmap(self, pixmap: QPixmap):
        self._item.setPixmap(pixmap)
        self.scene().setSceneRect(self._item.boundingRect())

        if not pixmap.isNull():
            self.fitInView(self._item, Qt.KeepAspectRatio)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        if not self._item.pixmap().isNull():
            self.fitInView(self._item, Qt.KeepAspectRatio)
