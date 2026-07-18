#!/usr/bin/env python3
"""
Photo Editor 2.0

Canvas

Version: 0.3.3
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import (
    QDragEnterEvent,
    QDragMoveEvent,
    QDropEvent,
    QImage,
    QKeyEvent,
    QMouseEvent,
    QPixmap,
    QTransform,
    QWheelEvent,
)
from PySide6.QtWidgets import (
    QFileDialog,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
)

from core.adjustments import ImageAdjustments
from core.adjustment_settings import AdjustmentSettings
from core.crop_tool import CropTool
from core.history import ImageHistory
from core.image_document import ImageDocument
from core.image_loader import ImageLoader
from core.image_saver import ImageSaver


class Canvas(QGraphicsView):
    """Main image canvas."""

    image_loaded = Signal()
    zoom_changed = Signal(float)
    crop_mode_changed = Signal(bool)
    history_state_changed = Signal(bool, bool)

    ZOOM_STEP = 1.15

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.document = ImageDocument()
        self.history = ImageHistory()

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.image_item = QGraphicsPixmapItem()
        self.scene.addItem(self.image_item)

        self.crop_tool = CropTool(self.scene)
        self.crop_selection_enabled = False

        self._configure()

    def _configure(self) -> None:
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)

        self.setDragMode(
            QGraphicsView.DragMode.ScrollHandDrag
        )

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

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

        self.crop_tool.cancel()
        self.history.clear()
        self.document = document
        self.history.push(document.image)

        pixmap = QPixmap.fromImage(document.image)

        self.image_item.setPixmap(pixmap)

        self.scene.setSceneRect(
            self.image_item.boundingRect()
        )

        self.fit_to_window()
        self.image_loaded.emit()
        self._update_history_state()

        return True

    def save_image(
        self,
        file_path: str | Path | None = None,
    ) -> bool:
        """Save the current image to disk."""

        if not self.document.is_loaded or self.document.image is None:
            return False

        path = (
            Path(file_path)
            if file_path is not None
            else self.document.file_path
        )

        if path is None or not ImageSaver.can_save(path):
            return False

        if not ImageSaver.save(self.document.image, path):
            return False

        self.document.file_path = path
        self.document.file_name = path.name
        self.document.format = path.suffix.lower().lstrip(".")
        self.document.modified = False

        return True

    def set_crop_selection_enabled(self, enabled: bool) -> None:
        """Enable or disable rectangular crop selection mode."""

        if self.crop_selection_enabled == enabled:
            return

        self.crop_selection_enabled = enabled

        if enabled:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
        else:
            self.crop_tool.cancel()
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

        self.crop_mode_changed.emit(enabled)

    def apply_crop(self) -> bool:
        """Crop the current image to the active selection."""

        if (
            not self.document.is_loaded
            or not self.crop_tool.has_selection
            or self.document.image is None
        ):
            return False

        selection = self.crop_tool.selection_rect.intersected(
            self.image_item.sceneBoundingRect()
        )
        crop_rect = selection.toAlignedRect()

        if crop_rect.isEmpty():
            return False

        cropped_image = self.document.image.copy(crop_rect)

        if cropped_image.isNull():
            return False

        self.history.push(self.document.image)
        self.document.set_active_image(cropped_image)
        self.history.push(cropped_image)

        self.image_item.setPixmap(QPixmap.fromImage(cropped_image))
        self.scene.setSceneRect(self.image_item.boundingRect())

        self.crop_tool.cancel()
        self.set_crop_selection_enabled(False)
        self._update_history_state()

        return True

    def preview_adjustments(
        self,
        source_image: QImage,
        settings: AdjustmentSettings,
    ) -> bool:
        """Preview adjustments without changing history."""

        if source_image.isNull():
            return False


        image = ImageAdjustments.apply_settings(
            source_image,
            settings,
        )

        self._restore_image(image)

        return True

    def apply_adjustments(
        self,
        settings: AdjustmentSettings,
    ) -> bool:
        """Apply image adjustments."""

        if (
            not self.document.is_loaded
            or self.document.image is None
        ):
            return False

        image = ImageAdjustments.apply_settings(
            self.document.image,
            settings,
        )

        if settings.is_identity():
            return False

        self.history.push(image)
        self._restore_image(image)
        self._update_history_state()

        return True

    def resize_image(
        self,
        width: int,
        height: int,
    ) -> bool:
        """Resize the current image and add the result to history."""

        if (
            not self.document.is_loaded
            or self.document.image is None
            or width <= 0
            or height <= 0
        ):
            return False

        resized_image = self.document.image.scaled(
            width,
            height,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        if resized_image.isNull():
            return False

        self.history.push(resized_image)
        self._restore_image(resized_image)
        self._update_history_state()
        self.fit_to_window()

        return True

    def rotate_left(self) -> bool:
        """Rotate the current image 90 degrees counterclockwise."""

        return self._rotate_image(-90)

    def rotate_right(self) -> bool:
        """Rotate the current image 90 degrees clockwise."""

        return self._rotate_image(90)

    def _rotate_image(self, angle: int) -> bool:
        """Rotate the current image and add the result to history."""

        if (
            not self.document.is_loaded
            or self.document.image is None
        ):
            return False

        transform = QTransform()
        transform.rotate(angle)

        rotated_image = self.document.image.transformed(
            transform,
            Qt.TransformationMode.SmoothTransformation,
        )

        if rotated_image.isNull():
            return False

        self.history.push(rotated_image)
        self._restore_image(rotated_image)
        self._update_history_state()
        self.fit_to_window()

        return True

    def flip_horizontal(self) -> bool:
        """Flip the current image horizontally."""

        return self._flip_image(
            horizontal=True,
            vertical=False,
        )

    def flip_vertical(self) -> bool:
        """Flip the current image vertically."""

        return self._flip_image(
            horizontal=False,
            vertical=True,
        )

    def _flip_image(
        self,
        horizontal: bool,
        vertical: bool,
    ) -> bool:
        """Flip the current image and add the result to history."""

        if (
            not self.document.is_loaded
            or self.document.image is None
        ):
            return False

        flipped_image = self.document.image.mirrored(
            horizontal,
            vertical,
        )

        if flipped_image.isNull():
            return False

        self.history.push(flipped_image)
        self._restore_image(flipped_image)
        self._update_history_state()

        return True

    def undo(self, checked: bool = False) -> bool:
        if not self.document.is_loaded:
            return False

        image = self.history.undo()

        if image is None:
            return False

        self._restore_image(image)
        self._update_history_state()

        return True

    def redo(self, checked: bool = False) -> bool:
        if not self.document.is_loaded:
            return False

        image = self.history.redo()

        if image is None:
            return False

        self._restore_image(image)
        self._update_history_state()

        return True

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if (
            self.crop_selection_enabled
            and self.document.is_loaded
            and event.button() == Qt.MouseButton.LeftButton
        ):
            point = self.mapToScene(event.position().toPoint())
            image_bounds = self.image_item.sceneBoundingRect()

            self.setFocus()
            self.crop_tool.begin(point, image_bounds)
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.crop_selection_enabled and self.crop_tool.is_selecting:
            point = self.mapToScene(event.position().toPoint())
            self.crop_tool.update(
                point,
                self.image_item.sceneBoundingRect(),
            )
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if (
            self.crop_selection_enabled
            and self.crop_tool.is_selecting
            and event.button() == Qt.MouseButton.LeftButton
        ):
            point = self.mapToScene(event.position().toPoint())
            self.crop_tool.finish(
                point,
                self.image_item.sceneBoundingRect(),
            )
            event.accept()
            return

        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if (
            self.crop_selection_enabled
            and event.key() == Qt.Key.Key_Escape
        ):
            self.set_crop_selection_enabled(False)
            event.accept()
            return

        super().keyPressEvent(event)

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

    def _update_history_state(self) -> None:
        self.document.modified = self.history.can_undo
        self.history_state_changed.emit(
            self.history.can_undo,
            self.history.can_redo,
        )

    def _restore_image(self, image: QImage) -> None:
        self.document.image = image
        self.document.width = image.width()
        self.document.height = image.height()

        self.image_item.setPixmap(QPixmap.fromImage(image))
        self.scene.setSceneRect(self.image_item.boundingRect())

        self.crop_tool.cancel()
        self.set_crop_selection_enabled(False)

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