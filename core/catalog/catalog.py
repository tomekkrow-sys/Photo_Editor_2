#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path

from core.database.catalog_database import CatalogDatabase
from core.catalog.photo import Photo


class Catalog:
    """High-level interface to the photo catalog."""

    def __init__(self, database: CatalogDatabase) -> None:
        self._database = database

    def import_folder(self, folder: Path) -> int:
        return self._database.import_folder(folder)

    def photos(self) -> list[Photo]:
        return self._database.list_photos()

    def refresh(self) -> list[Photo]:
        return self.photos()
