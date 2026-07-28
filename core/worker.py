#!/usr/bin/env python3
from __future__ import annotations
from PySide6.QtCore import QThread, Signal
from core.pipeline import apply_adjustments_arr, arr_to_pil, pil_to_cv
from core.adjustments import Adjustments

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
