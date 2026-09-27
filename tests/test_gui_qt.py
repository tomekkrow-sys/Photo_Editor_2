"""GUI tests using pytest-qt and qtbot."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PIL import Image
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from core.worker import ImageLoaderWorker


def test_main_window_creation(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    assert window is not None
    window.close()


def test_status_bar_progress(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    
    sb = window.statusBar()
    sb.show_progress(0, 100)
    assert sb.progress_bar.isVisible()
    
    sb.set_progress(50)
    assert sb.progress_bar.value() == 50
    
    sb.hide_progress()
    assert not sb.progress_bar.isVisible()
    window.close()


def test_image_loader_worker_integration(qtbot):
    with tempfile.TemporaryDirectory() as temp_dir:
        img_path = Path(temp_dir) / "test.png"
        Image.new("RGB", (30, 20), (255, 0, 0)).save(img_path)

        window = MainWindow()
        qtbot.addWidget(window)

        loaded_data = []
        worker = ImageLoaderWorker(img_path, window)
        worker.finished.connect(lambda p, img: loaded_data.append(img))

        with qtbot.waitSignal(worker.finished, timeout=5000):
            worker.start()

        assert len(loaded_data) == 1
        assert loaded_data[0] is not None
        assert loaded_data[0].size == (30, 20)
        window.close()
