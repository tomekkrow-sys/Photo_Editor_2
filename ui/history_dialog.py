#!/usr/bin/env python3
"""Visual History Dialog with thumbnails for Photo Editor 2."""
from __future__ import annotations
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QPushButton, QSplitter, QWidget, QSizePolicy,
)
from config.i18n import t


def pil_to_qimage_small(img, max_size=120):
    """Convert PIL image to QImage, resized."""
    if img is None:
        return QImage()
    w, h = img.size
    if w > max_size or h > max_size:
        ratio = min(max_size / w, max_size / h)
        new_w = int(w * ratio)
        new_h = int(h * ratio)
        img = img.resize((new_w, new_h))
    rgb = img.convert("RGB")
    data = rgb.tobytes()
    qimg = QImage(data, rgb.width, rgb.height, 3 * rgb.width, QImage.Format.Format_RGB888)
    return qimg.copy()


class HistoryDialog(QDialog):
    """Visual history dialog showing operations with thumbnails."""

    def __init__(self, history, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("history"))
        self.setMinimumSize(600, 400)
        self._history = history
        self._selected_index = -1
        self._result = None
        self._build_ui()
        self._populate()

    def _build_ui(self):
        lay = QVBoxLayout(self)

        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: list of operations
        left = QWidget()
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(0, 0, 0, 0)
        left_lay.addWidget(QLabel(t("history")))

        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(80, 60))
        self.list_widget.currentRowChanged.connect(self._on_select)
        left_lay.addWidget(self.list_widget)
        splitter.addWidget(left)

        # Right: preview
        right = QWidget()
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(0, 0, 0, 0)

        self.preview_label = QLabel("Wybierz operacje z listy")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(300, 250)
        self.preview_label.setStyleSheet("background: #1a1a1a; border: 1px solid #333;")
        right_lay.addWidget(self.preview_label)

        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_lay.addWidget(self.info_label)

        splitter.addWidget(right)
        splitter.setSizes([200, 400])
        lay.addWidget(splitter)

        # Buttons
        btn_layout = QHBoxLayout()

        self._undo_to_btn = QPushButton(t("history_undo_to"))
        self._undo_to_btn.setEnabled(False)
        self._undo_to_btn.clicked.connect(self._on_undo_to)
        btn_layout.addWidget(self._undo_to_btn)

        btn_layout.addStretch()

        close_btn = QPushButton(t("ok"))
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        lay.addLayout(btn_layout)

    def _populate(self):
        self.list_widget.clear()

        # Add current state
        if hasattr(self._history, '_undo') and self._history._undo:
            current_item = QListWidgetItem(">>> " + t("history_current"))
            current_item.setData(Qt.ItemDataRole.UserRole, -1)
            current_item.setFlags(current_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self.list_widget.addItem(current_item)

            # Add undo stack (newest first)
            names = self._history._names
            for i in range(len(self._history._undo) - 1, -1, -1):
                name = names[i] if i < len(names) else f"Krok {i + 1}"
                item = QListWidgetItem(name)
                item.setData(Qt.ItemDataRole.UserRole, i)

                # Add thumbnail
                state = self._history._undo[i]
                if state is not None:
                    thumb = EditHistory.make_thumbnail(state, (80, 60))
                    if thumb is not None:
                        qimg = pil_to_qimage_small(thumb, 80)
                        if not qimg.isNull():
                            item.setIcon(QPixmap.fromImage(qimg))

                self.list_widget.addItem(item)

        # Select current
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def _on_select(self, row):
        if row < 0:
            return
        item = self.list_widget.item(row)
        if item is None:
            return
        idx = item.data(Qt.ItemDataRole.UserRole)
        self._selected_index = idx

        if idx == -1:
            self.preview_label.setText("Aktualny stan")
            self.info_label.setText("")
            self._undo_to_btn.setEnabled(False)
            return

        state = self._history.get_state(idx)
        if state is not None:
            qimg = pil_to_qimage_small(state, 400)
            if not qimg.isNull():
                self.preview_label.setPixmap(QPixmap.fromImage(qimg))
            self.info_label.setText(f"{item.text()}  |  {state.width}x{state.height}")
            self._undo_to_btn.setEnabled(True)
        else:
            self.preview_label.setText("Brak podgladu")
            self._undo_to_btn.setEnabled(False)

    def _on_undo_to(self):
        if self._selected_index >= 0:
            self._result = self._selected_index
            self.accept()

    def get_target_index(self) -> int | None:
        """Return the index the user wants to undo to, or None."""
        return self._result


# Avoid circular import
from core.history import EditHistory
