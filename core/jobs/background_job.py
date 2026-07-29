#!/usr/bin/env python3
"""Photo Editor 2.0 — Background Job base class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from PySide6.QtCore import QObject, Signal


class BackgroundJob(QObject, ABC):
    """
    Abstract base for a background task.
    Runs inside QThreadPool via QRunnable wrapper.
    Emits signals for progress and lifecycle.
    """

    progressChanged = Signal(int)      # 0-100
    finished = Signal(object)          # result payload
    error = Signal(str)                # error message
    cancelled = Signal()

    def __init__(self, job_id: int = 0, payload: Any = None, parent=None) -> None:
        super().__init__(parent)
        self.job_id = job_id
        self.payload = payload
        self._cancelled = False

    @property
    def is_cancelled(self) -> bool:
        return self._cancelled

    def cancel(self) -> None:
        """Request graceful cancellation."""
        self._cancelled = True

    @abstractmethod
    def run(self) -> Any:
        """
        Override with the actual work.
        Should periodically check self.is_cancelled.
        Can call self.set_progress() to report status.
        Returns a result object passed to finished signal.
        """
        ...

    def set_progress(self, value: int) -> None:
        """Emit progress (clamped 0-100)."""
        self.progressChanged.emit(max(0, min(100, value)))

    def _execute(self) -> None:
        """Internal executor — do not override."""
        if self._cancelled:
            self.cancelled.emit()
            return
        try:
            result = self.run()
            if not self._cancelled:
                self.finished.emit(result)
        except Exception as exc:
            if not self._cancelled:
                self.error.emit(str(exc))
