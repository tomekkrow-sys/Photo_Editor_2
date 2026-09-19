#!/usr/bin/env python3
"""Fullscreen slideshow widget with transitions."""
from __future__ import annotations
import os
import random
from PySide6.QtCore import Qt, QTimer, QEasingCurve
from PySide6.QtGui import QPixmap, QKeyEvent
from PySide6.QtWidgets import QWidget, QLabel, QApplication

SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".tif", ".webp"}


class SlideshowWidget(QWidget):
    """Fullscreen slideshow with fade transitions."""

    def __init__(self, folder, interval=4, transition="fade",
                 loop=True, random_order=False, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setStyleSheet("background: black;")
        self.showFullScreen()

        self._folder = folder
        self._interval = interval * 1000
        self._transition = transition
        self._loop = loop
        self._random_order = random_order
        self._paused = False
        self._index = 0

        self._files = sorted([
            f for f in os.listdir(folder)
            if os.path.splitext(f)[1].lower() in SUPPORTED_EXTS
        ])
        if random_order:
            random.shuffle(self._files)

        if not self._files:
            lbl = QLabel("Brak zdjec w folderze", self)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("color: white; font-size: 20px;")
            return

        self._label_a = QLabel(self)
        self._label_b = QLabel(self)
        for lbl in (self._label_a, self._label_b):
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("background: black;")
        self._label_b.hide()

        self._counter = QLabel(self)
        self._counter.setStyleSheet(
            "color: #aaa; font-size: 13px; background: rgba(0,0,0,100); padding: 4px 10px;"
        )
        self._counter.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight
        )

        self._hint = QLabel(
            "Esc=wyjscie  <-/->=przelacz  Spacja=pauza", self
        )
        self._hint.setStyleSheet(
            "color: #888; font-size: 12px; background: rgba(0,0,0,140); padding: 6px;"
        )
        self._hint.setAlignment(
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter
        )
        self._hint_timer = QTimer(self)
        self._hint_timer.singleShot(3000, self._hint.hide)

        self._fade_timer = QTimer(self)
        self._fade_timer.timeout.connect(self._do_fade)
        self._fade_step = 0
        self._fade_steps = 20
        self._fade_new_idx = 0
        self._fading = False

        self._load_image(0)
        self._start_timer()

    def _load_image(self, idx):
        if not self._files:
            return
        idx = idx % len(self._files)
        self._index = idx
        path = os.path.join(self._folder, self._files[idx])
        pm = QPixmap(path)
        if pm.isNull():
            return
        screen = QApplication.primaryScreen().geometry()
        pm = pm.scaled(
            screen.size(), Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._label_a.setPixmap(pm)
        self._label_a.setGeometry(self.rect())
        self._label_a.show()
        self._label_a.raise_()
        self._counter.setText(f"{idx + 1} / {len(self._files)}")
        self._counter.adjustSize()
        self._counter.raise_()
        if self._hint.isVisible():
            self._hint.raise_()

    def _load_to_b(self, idx):
        if not self._files:
            return
        idx = idx % len(self._files)
        path = os.path.join(self._folder, self._files[idx])
        pm = QPixmap(path)
        if pm.isNull():
            return
        screen = QApplication.primaryScreen().geometry()
        pm = pm.scaled(
            screen.size(), Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._label_b.setPixmap(pm)
        self._label_b.setGeometry(self.rect())

    def _start_timer(self):
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._next)
        self._timer.start(self._interval)

    def _next(self):
        if self._paused or not self._files:
            return
        new_idx = self._index + 1
        if new_idx >= len(self._files):
            if self._loop:
                new_idx = 0
            else:
                self.close()
                return
        self._start_fade(new_idx)

    def _prev(self):
        if not self._files:
            return
        new_idx = self._index - 1
        if new_idx < 0:
            new_idx = len(self._files) - 1
        self._start_fade(new_idx)

    def _start_fade(self, new_idx):
        if self._fading:
            return
        self._fading = True
        self._fade_new_idx = new_idx
        self._fade_step = 0
        self._load_to_b(new_idx)
        self._label_b.setWindowOpacity(0.0)
        self._label_b.show()
        self._label_b.raise_()
        self._counter.raise_()
        self._fade_timer.start(20)

    def _do_fade(self):
        self._fade_step += 1
        t = min(self._fade_step / self._fade_steps, 1.0)
        self._label_b.setWindowOpacity(t)
        self._label_a.setWindowOpacity(1.0 - t)
        if t >= 1.0:
            self._fade_timer.stop()
            self._label_a.hide()
            self._label_a, self._label_b = self._label_b, self._label_a
            self._label_a.show()
            self._index = self._fade_new_idx
            self._counter.setText(f"{self._index + 1} / {len(self._files)}")
            self._counter.raise_()
            self._fading = False

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key == Qt.Key.Key_Escape:
            self.close()
        elif key == Qt.Key.Key_Space:
            self._paused = not self._paused
        elif key in (Qt.Key.Key_Right, Qt.Key.Key_Down):
            if not self._fading:
                self._next()
        elif key in (Qt.Key.Key_Left, Qt.Key.Key_Up):
            if not self._fading:
                self._prev()
        elif key == Qt.Key.Key_F or key == Qt.Key.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._next()
        elif event.button() == Qt.MouseButton.RightButton:
            self._prev()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._label_a.setGeometry(self.rect())
        self._label_b.setGeometry(self.rect())
        self._counter.adjustSize()
