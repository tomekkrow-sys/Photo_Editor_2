"""Unit tests for background workers (ImageLoaderWorker, PipelineWorker)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from PIL import Image as PILImage
from PySide6.QtCore import QCoreApplication

from core.worker import ImageLoaderWorker, PipelineWorker
from core.adjustments import Adjustments
import numpy as np


class WorkerTests(unittest.TestCase):
    """Verify asynchronous workers functionality."""

    @classmethod
    def setUpClass(cls):
        # Ensure QCoreApplication exists for signals/threads if needed
        if not QCoreApplication.instance():
            cls.app = QCoreApplication([])

    def test_image_loader_worker_success(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.png"
            img = PILImage.new("RGB", (10, 10), color="red")
            img.save(path)

            loaded_result = []
            error_result = []

            worker = ImageLoaderWorker(path)
            worker.finished.connect(lambda p, im: loaded_result.append((p, im)))
            worker.error.connect(lambda p, err: error_result.append((p, err)))

            worker.start()
            worker.wait(5000)

            self.assertEqual(len(error_result), 0)
            self.assertEqual(len(loaded_result), 1)
            self.assertEqual(loaded_result[0][0], path)
            self.assertIsNotNone(loaded_result[0][1])
            self.assertEqual(loaded_result[0][1].size, (10, 10))

    def test_image_loader_worker_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nonexistent.png"

            loaded_result = []
            error_result = []

            worker = ImageLoaderWorker(path)
            worker.finished.connect(lambda p, im: loaded_result.append((p, im)))
            worker.error.connect(lambda p, err: error_result.append((p, err)))

            worker.start()
            worker.wait(5000)

            self.assertEqual(len(loaded_result), 0)
            self.assertEqual(len(error_result), 1)
            self.assertEqual(error_result[0][0], path)

    def test_pipeline_worker(self):
        arr = np.zeros((100, 100, 3), dtype=np.uint8)
        adj = Adjustments()

        results = []
        worker = PipelineWorker()
        worker.set_job(arr, adj)
        worker.finished.connect(lambda res: results.append(res))

        worker.start()
        worker.wait(5000)

        self.assertEqual(len(results), 1)
        self.assertIsNotNone(results[0])


if __name__ == "__main__":
    unittest.main()
