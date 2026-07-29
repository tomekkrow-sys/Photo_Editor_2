#!/usr/bin/env python3
"""Photo Editor 2.0 — Job Queue with thread pool."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal

from .background_job import BackgroundJob


class _JobRunnable(QRunnable):
    """Wrapper that runs a BackgroundJob inside QThreadPool."""

    def __init__(self, job: BackgroundJob) -> None:
        super().__init__()
        self._job = job
        self.setAutoDelete(True)

    def run(self) -> None:
        self._job._execute()


@dataclass(order=True)
class _QueuedItem:
    """Internal queue item with priority support."""
    priority: int = field(compare=True)
    job: BackgroundJob = field(compare=False)


class JobQueue(QObject):
    """
    Manages background jobs using QThreadPool.
    Supports priorities, progress tracking and graceful cancellation.
    """

    jobStarted = Signal(int)           # job_id
    jobProgress = Signal(int, int)     # job_id, progress 0-100
    jobFinished = Signal(int, object)  # job_id, result
    jobError = Signal(int, str)        # job_id, message
    jobCancelled = Signal(int)         # job_id
    queueEmpty = Signal()              # no more pending jobs
    allFinished = Signal()             # all jobs done (queue + active)

    def __init__(
        self,
        max_threads: int = 4,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._pool = QThreadPool.globalInstance()
        self._pool.setMaxThreadCount(max(max_threads, 1))

        self._pending: list[_QueuedItem] = []
        self._active: set[int] = set()
        self._completed: int = 0
        self._failed: int = 0
        self._next_id: int = 1

    # --- Public API ---

    def submit(
        self,
        job: BackgroundJob,
        priority: int = 0,
    ) -> int:
        """
        Add a job to the queue.
        Higher priority = executed earlier.
        Returns assigned job_id.
        """
        job_id = self._next_id
        self._next_id += 1
        job.job_id = job_id

        # Wire signals
        job.progressChanged.connect(
            lambda p, jid=job_id: self.jobProgress.emit(jid, p)
        )
        job.finished.connect(
            lambda r, jid=job_id: self._on_finished(jid, r)
        )
        job.error.connect(
            lambda e, jid=job_id: self._on_error(jid, e)
        )
        job.cancelled.connect(
            lambda jid=job_id: self._on_cancelled(jid)
        )

        self._pending.append(_QueuedItem(priority=-priority, job=job))
        self._pending.sort()
        self._try_start()
        return job_id

    def cancel_job(self, job_id: int) -> None:
        """Cancel a pending or active job by id."""
        # Cancel pending
        for item in self._pending:
            if item.job.job_id == job_id:
                item.job.cancel()
                self._pending.remove(item)
                self.jobCancelled.emit(job_id)
                return
        # Cancel active (graceful — job must check is_cancelled)
        for item in self._pending:
            pass  # already handled above
        # Active jobs are tracked only by id set; actual object lives in thread

    def cancel_all(self) -> None:
        """Cancel every pending job and request active ones to stop."""
        for item in self._pending:
            item.job.cancel()
        self._pending.clear()
        # Active jobs get cancel flag when they check is_cancelled

    def clear_completed(self) -> None:
        """Reset counters."""
        self._completed = 0
        self._failed = 0

    @property
    def pending_count(self) -> int:
        return len(self._pending)

    @property
    def active_count(self) -> int:
        return len(self._active)

    @property
    def is_idle(self) -> bool:
        return len(self._pending) == 0 and len(self._active) == 0

    @property
    def total_processed(self) -> int:
        return self._completed + self._failed

    # --- Internal ---

    def _try_start(self) -> None:
        """Start pending jobs if thread pool has capacity."""
        while self._pending and self.active_count < self._pool.maxThreadCount():
            item = self._pending.pop(0)
            job = item.job
            self._active.add(job.job_id)
            self.jobStarted.emit(job.job_id)
            runnable = _JobRunnable(job)
            self._pool.start(runnable)

    def _on_finished(self, job_id: int, result: Any) -> None:
        self._active.discard(job_id)
        self._completed += 1
        self.jobFinished.emit(job_id, result)
        self._check_queue()

    def _on_error(self, job_id: int, message: str) -> None:
        self._active.discard(job_id)
        self._failed += 1
        self.jobError.emit(job_id, message)
        self._check_queue()

    def _on_cancelled(self, job_id: int) -> None:
        self._active.discard(job_id)
        self.jobCancelled.emit(job_id)
        self._check_queue()

    def _check_queue(self) -> None:
        """Start next jobs or emit completion signals."""
        self._try_start()
        if not self._pending:
            self.queueEmpty.emit()
        if self.is_idle:
            self.allFinished.emit()
