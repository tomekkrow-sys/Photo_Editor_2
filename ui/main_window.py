#!/usr/bin/env python3
"""Photo Editor 2.0 - Main Window."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from config.defaults import DEFAULT_WINDOW_HEIGHT, DEFAULT_WINDOW_WIDTH
from config.version import WINDOW_TITLE
from core.canvas import Canvas
from core.image_saver import ImageSaver
from ui.actions import ActionManager
from ui.menubar import MenuBar
from ui.statusbar import StatusBar
from ui.toolbar import ToolBar


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()

        self.actions = ActionManager(self)
        self.canvas = Canvas(self)
        self._save_target_created = False

        self._build_window()
        self._create_connections()

    def _build_window(self) -> None:
        self.setWindowTitle(WINDOW_TITLE)
        self.resize(
            DEFAULT_WINDOW_WIDTH,
            DEFAULT_WINDOW_HEIGHT,
        )

        self.setMenuBar(MenuBar(self, self.actions))
        self.addToolBar(ToolBar(self, self.actions))

        self.status_bar = StatusBar(self)
        self.setStatusBar(self.status_bar)

        self.setCentralWidget(self.canvas)
        self.status_bar.set_message("Gotowy")

    def _create_connections(self) -> None:
        self.actions.new.triggered.connect(
            self._new_document
        )
        self.actions.open.triggered.connect(
            self._open_image
        )
        self.actions.save.triggered.connect(
            self._save_image
        )
        self.actions.save_as.triggered.connect(
            self._save_image_as
        )
        self.actions.exit.triggered.connect(
            self.close
        )

        self.actions.zoom_in.triggered.connect(
            self.canvas.zoom_in
        )
        self.actions.zoom_out.triggered.connect(
            self.canvas.zoom_out
        )
        self.actions.fit.triggered.connect(
            self.canvas.fit_to_window
        )
        self.actions.actual_size.triggered.connect(
            self.canvas.actual_size
        )

        self.actions.undo.triggered.connect(
            self.canvas.undo
        )
        self.actions.redo.triggered.connect(
            self.canvas.redo
        )

        self.actions.rotate_left.triggered.connect(
            self.canvas.rotate_left
        )
        self.actions.rotate_right.triggered.connect(
            self.canvas.rotate_right
        )

        self.actions.flip_horizontal.triggered.connect(
            self.canvas.flip_horizontal
        )
        self.actions.flip_vertical.triggered.connect(
            self.canvas.flip_vertical
        )

        self.actions.crop.toggled.connect(
            self._handle_crop_action_toggled
        )

        self.canvas.image_loaded.connect(
            self._handle_image_loaded
        )
        self.canvas.zoom_changed.connect(
            self.status_bar.set_zoom
        )
        self.canvas.crop_mode_changed.connect(
            self.actions.crop.setChecked
        )
        self.canvas.history_state_changed.connect(
            self._update_history_actions
        )

        self._update_history_actions(False, False)

    def _confirm_discard_changes(self) -> bool:
        """Ask what to do with unsaved changes."""

        if not self.canvas.document.modified:
            return True

        answer = QMessageBox.warning(
            self,
            "Niezapisane zmiany",
            (
                "Obraz został zmodyfikowany.\n\n"
                "Czy chcesz zapisać zmiany?"
            ),
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )

        if answer == QMessageBox.StandardButton.Save:
            return self._save_image()

        if answer == QMessageBox.StandardButton.Discard:
            return True

        return False

    def _new_document(self) -> None:
        """Clear the current document."""

        if not self._confirm_discard_changes():
            return

        self.canvas.crop_tool.cancel()
        self.canvas.set_crop_selection_enabled(False)
        self.canvas.history.clear()
        self.canvas.document.clear()
        self.canvas.image_item.setPixmap(QPixmap())
        self.canvas.scene.setSceneRect(0, 0, 0, 0)
        self.canvas.resetTransform()

        self._save_target_created = False

        self._update_history_actions(False, False)
        self.status_bar.set_file_name("")
        self.status_bar.set_image_size(0, 0)
        self.status_bar.set_zoom(100.0)
        self.status_bar.set_message("Nowy dokument")

    def _open_image(self) -> None:
        """Open an image after checking for unsaved changes."""

        if not self._confirm_discard_changes():
            return

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Otwórz obraz",
            "",
            (
                "Obrazy (*.jpg *.jpeg *.png *.webp *.bmp "
                "*.tif *.tiff *.nef *.cr2 *.cr3 *.arw "
                "*.dng *.orf *.rw2 *.raf *.pef);;"
                "Wszystkie pliki (*)"
            ),
        )

        if filename:
            self.canvas.load_image(filename)

    def _save_image(self) -> bool:
        """Save safely without overwriting the original image."""

        document = self.canvas.document

        if not document.is_loaded:
            return False

        if (
            not self._save_target_created
            or document.file_path is None
            or not ImageSaver.can_save(document.file_path)
        ):
            return self._save_image_as()

        if self.canvas.save_image():
            self._update_status_bar()
            self.status_bar.set_message("Obraz zapisany")
            return True

        QMessageBox.warning(
            self,
            "Photo Editor 2.0",
            "Nie udało się zapisać obrazu.",
        )
        return False

    def _save_image_as(self) -> bool:
        """Save the current image under a new file name."""

        document = self.canvas.document

        if not document.is_loaded:
            return False

        suggested_path = self._suggest_save_path()

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Zapisz obraz jako",
            str(suggested_path),
            ImageSaver.file_dialog_filter(),
        )

        if not filename:
            return False

        if not ImageSaver.can_save(filename):
            QMessageBox.warning(
                self,
                "Nieobsługiwany format",
                (
                    "Nie można zapisać obrazu w tym formacie.\n\n"
                    "Formaty RAW, takie jak NEF, są tylko do odczytu.\n"
                    "Wybierz JPG, PNG, WebP, BMP lub TIFF."
                ),
            )
            return False

        if self.canvas.save_image(filename):
            self._save_target_created = True
            self._update_status_bar()
            self.status_bar.set_message("Obraz zapisany")
            return True

        QMessageBox.warning(
            self,
            "Photo Editor 2.0",
            "Nie udało się zapisać obrazu.",
        )
        return False

    def _suggest_save_path(self) -> Path:
        """Suggest a safe edited copy name."""

        document = self.canvas.document

        if document.file_path is None:
            return Path("image_edited.jpg")

        source = Path(document.file_path)
        suffix = source.suffix.lower()

        if not ImageSaver.can_save(source):
            suffix = ".jpg"

        return source.with_name(
            f"{source.stem}_edited{suffix}"
        )

    def _handle_image_loaded(self) -> None:
        """Reset safe-save state after loading an original image."""

        self._save_target_created = False
        self._update_status_bar()

    def _handle_crop_action_toggled(
        self,
        enabled: bool,
    ) -> None:
        if enabled:
            self.canvas.set_crop_selection_enabled(True)
            return

        if (
            self.canvas.crop_selection_enabled
            and self.canvas.crop_tool.has_selection
        ):
            if self.canvas.apply_crop():
                return

        self.canvas.set_crop_selection_enabled(False)

    def _update_status_bar(self) -> None:
        document = self.canvas.document

        self.status_bar.set_file_name(
            document.file_name
        )
        self.status_bar.set_image_size(
            document.width,
            document.height,
        )
        self.status_bar.set_message(
            "Obraz załadowany"
        )

    def _update_history_actions(
        self,
        can_undo: bool,
        can_redo: bool,
    ) -> None:
        self.actions.undo.setEnabled(can_undo)
        self.actions.redo.setEnabled(can_redo)

    def closeEvent(self, event) -> None:
        """Handle application closing."""

        if not self._confirm_discard_changes():
            event.ignore()
            return

        event.accept()