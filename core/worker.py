#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from PySide6.QtCore import QThread, Signal
from PIL import Image
import rawpy
from core.pipeline import apply_adjustments_arr, arr_to_pil

class PipelineWorker(QThread):
    finished = Signal(object)
    def __init__(self, parent=None):
        super().__init__(parent)
        self._arr = None
        self._adj = None
    def set_job(self, arr, adj):
        self._arr = arr
        self._adj = adj
    def run(self):
        if self._arr is None or self._adj is None:
            self.finished.emit(None)
            return
        out = apply_adjustments_arr(self._arr, self._adj)
        pil = arr_to_pil(out)
        self.finished.emit(pil)


class ImageLoaderWorker(QThread):
    """Asynchronous worker for loading images and RAW files into PIL Image in background thread."""
    finished = Signal(object, object)  # (path, pil_image_or_none)
    error = Signal(object, str)        # (path, error_message)

    RAW_EXTS = {".nef", ".cr2", ".cr3", ".arw", ".dng", ".orf", ".rw2", ".raf", ".pef"}

    def __init__(self, path: Path | str, parent=None):
        super().__init__(parent)
        self.path = Path(path)

    def run(self):
        try:
            path = self.path
            orientation = 1
            try:
                with Image.open(path) as tmp:
                    exif = tmp.getexif()
                    if exif:
                        orientation = exif.get(274, 1)
            except Exception:
                pass

            if path.suffix.lower() in self.RAW_EXTS:
                with rawpy.imread(str(path)) as raw:
                    rgb = raw.postprocess(
                        use_camera_wb=True,
                        no_auto_bright=False,
                        output_bps=8,
                    )
                img = Image.fromarray(rgb)
            else:
                img = Image.open(path)
                img.load()

            if orientation == 3:
                img = img.rotate(180, expand=True)
            elif orientation == 6:
                img = img.rotate(270, expand=True)
            elif orientation == 8:
                img = img.rotate(90, expand=True)

            if img.mode in ("RGBA", "P"):
                img = img.convert("RGBA").convert("RGB")
            elif img.mode != "RGB":
                img = img.convert("RGB")

            self.finished.emit(path, img)
        except Exception as e:
            self.error.emit(self.path, str(e))
