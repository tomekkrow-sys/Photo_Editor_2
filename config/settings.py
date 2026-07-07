#!/usr/bin/env python3
"""
Photo Editor 2.0
Application settings manager.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSettings

from config.version import APP_NAME, ORGANIZATION


class Settings:
    """
    Wrapper around Qt QSettings.
    """

    def __init__(self) -> None:

        self._settings = QSettings(
            ORGANIZATION,
            APP_NAME,
        )

    def value(self, key: str, default=None):

        return self._settings.value(key, default)

    def set_value(self, key: str, value) -> None:

        self._settings.setValue(key, value)

    def contains(self, key: str) -> bool:

        return self._settings.contains(key)

    def remove(self, key: str) -> None:

        self._settings.remove(key)

    def sync(self) -> None:

        self._settings.sync()

    @property
    def file_path(self) -> Path:

        return Path(self._settings.fileName())