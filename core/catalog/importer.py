#!/usr/bin/env python3
"""
Photo Editor 2.0

Catalog Importer
"""

from __future__ import annotations

from pathlib import Path

from core.database.catalog_database import CatalogDatabase


SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".tif",
    ".tiff",
    ".bmp",
    ".webp",
    ".dng",
    ".nef",
    ".cr2",
    ".cr3",
    ".arw",
    ".raf",
    ".rw2",
    ".orf",
    ".pef",
}


class CatalogImporter:
    """Imports folders into the catalog."""

    def __init__(self, database: CatalogDatabase) -> None:
        self.database = database

    def import_folder(self, folder: Path) -> int:
        """Import all supported images from a folder."""

        folder = folder.resolve()

        cur = self.database.connection.cursor()

        cur.execute(
            """
            INSERT OR IGNORE INTO folders(path)
            VALUES(?)
            """,
            (str(folder),),
        )

        self.database.connection.commit()

        cur.execute(
            """
            SELECT id
            FROM folders
            WHERE path=?
            """,
            (str(folder),),
        )

        folder_id = cur.fetchone()[0]

        imported = 0

        for file in sorted(folder.rglob("*")):

            if not file.is_file():
                continue

            if file.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            cur.execute(
                """
                INSERT OR IGNORE INTO photos(
                    folder_id,
                    filename,
                    full_path
                )
                VALUES(?,?,?)
                """,
                (
                    folder_id,
                    file.name,
                    str(file),
                ),
            )

            if cur.rowcount:
                imported += 1

        self.database.connection.commit()

        return imported
