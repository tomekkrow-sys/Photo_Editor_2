#!/usr/bin/env python3
"""
Photo Editor 2.0

Catalog database
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from core.catalog.photo import Photo


class CatalogDatabase:
    """Photo catalog database."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.connection = sqlite3.connect(database_path)

    def initialize(self) -> None:
        """Create database schema."""

        cursor = self.connection.cursor()

        cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                folder_id INTEGER,
                filename TEXT NOT NULL,
                full_path TEXT NOT NULL UNIQUE,

                width INTEGER,
                height INTEGER,

                rating INTEGER DEFAULT 0,
                flag INTEGER DEFAULT 0,

                imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY(folder_id)
                    REFERENCES folders(id)
            );
            """
        )

        self.connection.commit()


    def import_folder(self, folder: Path) -> int:
        """Import all supported images from a folder."""

        from core.catalog.importer import CatalogImporter

        importer = CatalogImporter(self)
        return importer.import_folder(folder)


    def list_photos(self) -> list[dict]:
        """Return all imported photos."""

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                filename,
                full_path,
                rating,
                flag
            FROM photos
            ORDER BY filename
            """
        )

        rows = cursor.fetchall()

        return [
            Photo(
                id=row[0],
                filename=row[1],
                full_path=Path(row[2]),
                rating=row[3],
                flag=row[4],
            )
            for row in rows
        ]

    def close(self) -> None:
        self.connection.close()
