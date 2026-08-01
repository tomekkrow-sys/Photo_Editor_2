#!/usr/bin/env python3
"""Photo Editor 2.0 — Export Manager."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QImage

from core.image_saver import ImageSaver
from core.image_processor import ImageProcessor

from .export_job import ExportFormat, ExportJob, ExportState


class ExportManager(QObject):
    """
    Manages a queue of export jobs.
    Emits signals for progress tracking in UI.
    """

    jobStarted = Signal(int)          # job index
    jobProgress = Signal(int, int)    # job index, progress 0-100
    jobCompleted = Signal(int)        # job index
    jobFailed = Signal(int, str)      # job index, error message
    queueFinished = Signal()          # all jobs done
    totalProgress = Signal(int)       # overall progress 0-100

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._jobs: list[ExportJob] = []
        self._current_index: int = -1
        self._cancelled: bool = False

    # --- Queue management ---

    def add_job(self, job: ExportJob) -> int:
        """Add a job to the queue. Returns the job index."""
        self._jobs.append(job)
        return len(self._jobs) - 1

    def remove_job(self, index: int) -> None:
        """Remove a job by index if it hasn't started yet."""
        if 0 <= index < len(self._jobs):
            if self._jobs[index].is_pending:
                self._jobs.pop(index)

    def clear_queue(self) -> None:
        """Remove all pending jobs."""
        self._jobs = [j for j in self._jobs if not j.is_pending]
        self._current_index = -1

    @property
    def jobs(self) -> list[ExportJob]:
        """Return a copy of the job list."""
        return self._jobs.copy()

    @property
    def pending_count(self) -> int:
        return sum(1 for j in self._jobs if j.is_pending)

    @property
    def completed_count(self) -> int:
        return sum(1 for j in self._jobs if j.is_completed)

    @property
    def failed_count(self) -> int:
        return sum(1 for j in self._jobs if j.is_failed)

    @property
    def total_count(self) -> int:
        return len(self._jobs)

    @property
    def is_running(self) -> bool:
        return any(j.is_running for j in self._jobs)

    # --- Execution ---

    def run_all(self) -> None:
        """Execute all pending jobs synchronously (blocking)."""
        self._cancelled = False
        pending = [i for i, j in enumerate(self._jobs) if j.is_pending]

        if not pending:
            self.queueFinished.emit()
            return

        total = len(pending)
        for step, idx in enumerate(pending):
            if self._cancelled:
                self._jobs[idx].mark_cancelled()
                continue
            self._run_single(idx)
            overall = int((step + 1) / total * 100)
            self.totalProgress.emit(overall)

        self.queueFinished.emit()

    def cancel(self) -> None:
        """Cancel after the current job finishes."""
        self._cancelled = True

    # --- Internal ---

    def _run_single(self, index: int) -> None:
        """Execute one export job."""
        job = self._jobs[index]
        job.reset()
        job.state = ExportState.RUNNING
        self._current_index = index
        self.jobStarted.emit(index)

        try:
            # Validate
            if job.image is None:
                raise ValueError("Brak obrazu do eksportu")
            if not isinstance(job.image, QImage) or job.image.isNull():
                raise ValueError("Obraz jest pusty lub nieprawidlowy")

            # Determine output path
            dest = job.destination_path
            if dest.suffix.lower() != job.file_extension:
                dest = dest.with_suffix(job.file_extension)

            # Ensure directory exists
            dest.parent.mkdir(parents=True, exist_ok=True)

            # Apply develop settings if needed
            image = job.image
            if job.apply_develop and not job.develop_settings.is_identity():
                # TODO: integrate with render pipeline for full develop
                pass

            # Resize if needed
            if job.max_width > 0 or job.max_height > 0:
                w = job.max_width if job.max_width > 0 else image.width()
                h = job.max_height if job.max_height > 0 else image.height()
                scaled = ImageProcessor.resize(image, w, h)
                if scaled is not None:
                    image = scaled

            self.jobProgress.emit(index, 50)

            # Save
            if not ImageSaver.can_save(dest):
                raise ValueError(f"Nieobslugiwany format: {dest.suffix}")

            # For JPEG/WebP, quality is handled by QImage.save
            saved = image.save(str(dest), quality=job.quality)
            if not saved:
                raise RuntimeError("Nie udalo sie zapisac pliku")

            job.mark_completed()
            self.jobCompleted.emit(index)

        except Exception as exc:
            job.mark_failed(str(exc))
            self.jobFailed.emit(index, str(exc))

    # --- Utility ---

    @staticmethod
    def create_job_from_path(
        source: str | Path,
        destination: str | Path,
        image: QImage,
        fmt: ExportFormat = ExportFormat.JPEG,
        quality: int = 95,
    ) -> ExportJob:
        """Factory: create a simple export job."""
        return ExportJob(
            source_path=Path(source),
            destination_path=Path(destination),
            image=image,
            format=fmt,
            quality=quality,
        )

    @staticmethod
    def build_destination(
        source: Path,
        output_dir: Path,
        suffix: str | None = None,
    ) -> Path:
        """Build destination path preserving filename with optional new suffix."""
        name = source.stem
        if suffix:
            return output_dir / f"{name}{suffix}"
        return output_dir / source.name
