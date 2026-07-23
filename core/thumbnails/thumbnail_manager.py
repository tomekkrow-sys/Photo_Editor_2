from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from PySide6.QtGui import QIcon, QImageReader, QPixmap
from PySide6.QtCore import QSize


class ThumbnailWorkerSignals(QObject):
    finished = Signal(str, QIcon)


class ThumbnailWorker(QRunnable):
    WIDTH = 180
    HEIGHT = 120

    def __init__(self, filename: str):
        super().__init__()

        self.filename = filename
        self.signals = ThumbnailWorkerSignals()

    def run(self):
        reader = QImageReader(self.filename)
        reader.setScaledSize(QSize(self.WIDTH, self.HEIGHT))

        image = reader.read()

        if image.isNull():
            return

        icon = QIcon(QPixmap.fromImage(image))
        self.signals.finished.emit(self.filename, icon)


class ThumbnailManager(QObject):
    CACHE_DIR = Path.home() / ".cache" / "PhotoEditor2" / "thumbnails"

    thumbnail_ready = Signal(str, QIcon)

    def __init__(self):
        super().__init__()

        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)

        self.pool = QThreadPool.globalInstance()
        self.cache: dict[str, QIcon] = {}
        self.pending: set[str] = set()

    def get(self, filename: Path) -> QIcon | None:
        key = str(filename)

        if key in self.cache:
            return self.cache[key]

        if key in self.pending:
            return None

        self.pending.add(key)

        worker = ThumbnailWorker(key)

        worker.signals.finished.connect(self._finished)

        self.pool.start(worker)

        return None

    def _finished(self, filename: str, icon: QIcon):
        self.pending.discard(filename)
        self.cache[filename] = icon
        self.thumbnail_ready.emit(filename, icon)


# Współdzielona instancja dla całej aplikacji.
thumbnail_manager = ThumbnailManager()
