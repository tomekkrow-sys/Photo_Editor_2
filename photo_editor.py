#!/usr/bin/env python3
"""
Photo Editor 2.0

Main entry point.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication, QMessageBox
from core.database.catalog_database import CatalogDatabase
from core.catalog.catalog import Catalog

from config.version import (
    APP_NAME,
    APP_VERSION,
)

from ui.main_window import MainWindow
from core.crash_handler import install_exception_handler


# ==========================================================
# DIRECTORIES
# ==========================================================

ROOT_DIR = Path(__file__).resolve().parent


def _writable_dir(primary: Path, fallback_name: str) -> Path:
    """Return a writable directory (falls back to user data dir)."""

    try:
        primary.mkdir(parents=True, exist_ok=True)
        probe = primary / ".write_test"
        probe.touch()
        probe.unlink()
        return primary
    except OSError:
        fallback = (
            Path.home() / ".local" / "share" / "Photo_Editor_2" / fallback_name
        )
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


LOG_DIR = _writable_dir(ROOT_DIR / "logs", "logs")

LOG_FILE = LOG_DIR / "photo_editor.log"


# ==========================================================
# LOGGING
# ==========================================================

def configure_logging() -> None:
    """
    Configure application logging.
    """

    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        encoding="utf-8",
    )

    logging.info("=" * 60)
    logging.info("Starting %s", APP_NAME)
    logging.info("Version %s", APP_VERSION)


# ==========================================================
# EXCEPTION HANDLER
# ==========================================================

def exception_hook(exc_type, exc_value, exc_traceback):

    logging.exception(
        "Unhandled exception",
        exc_info=(exc_type, exc_value, exc_traceback),
    )

    QMessageBox.critical(
        None,
        APP_NAME,
        str(exc_value),
    )


# ==========================================================
# MAIN
# ==========================================================

def main() -> int:

    configure_logging()

    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    data_dir = _writable_dir(ROOT_DIR / "data", "data")

    database = CatalogDatabase(
        data_dir / "catalog.db"
    )
    database.initialize()

    catalog = Catalog(database)

    app = QApplication(sys.argv)

    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    install_exception_handler(APP_VERSION)

    window = MainWindow(catalog)

    window.show()

    # --- Auto-update check in background ---
    try:
        from PySide6.QtCore import QThread, Signal as QSignal

        class _UpdateChecker(QThread):
            result = QSignal(str)

            def run(self):
                try:
                    import urllib.request
                    import json
                    from config.version import APP_VERSION as _cur
                    from pathlib import Path as _P
                    cfg_path = _P(__file__).resolve().parent / "config" / "updater_config.json"
                    if cfg_path.exists():
                        cfg = json.loads(cfg_path.read_text())
                    else:
                        cfg = {}
                    gh = cfg.get("github", {})
                    url = f"{gh.get('api_url', 'https://api.github.com')}/repos/{gh.get('owner', 'tomekkrow-sys')}/{gh.get('repo', 'Photo_Editor_2')}/releases/latest"
                    req = urllib.request.Request(url, headers={"User-Agent": "Photo-Editor-2"})
                    resp = urllib.request.urlopen(req, timeout=10)
                    data = json.loads(resp.read().decode())
                    latest = data.get("tag_name", "").lstrip("v")
                    current = _cur
                    cur_parts = [int(x) for x in current.split(".")]
                    lat_parts = [int(x) for x in latest.split(".")]
                    newer = False
                    for i in range(min(len(cur_parts), len(lat_parts))):
                        if lat_parts[i] > cur_parts[i]:
                            newer = True
                            break
                        elif lat_parts[i] < cur_parts[i]:
                            break
                    if newer:
                        self.result.emit(latest)
                    else:
                        self.result.emit("")
                except Exception:
                    self.result.emit("")

        def _on_update_result(ver):
            if ver:
                from PySide6.QtWidgets import QMessageBox
                from config.i18n import t
                ret = QMessageBox.information(
                    window,
                    t("check_updates"),
                    f"Nowa wersja: v{ver}\nObecna: v{_APP_VERSION}\n\nOtworzyc strone pobierania?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if ret == QMessageBox.StandardButton.Yes:
                    import webbrowser
                    webbrowser.open(f"https://github.com/tomekkrow-sys/Photo_Editor_2/releases/tag/v{ver}")

        _checker = _UpdateChecker()
        _checker.result.connect(_on_update_result)
        _checker.start()
    except Exception:
        pass

    logging.info("Application started")

    return app.exec()


# ==========================================================
# START
# ==========================================================

if __name__ == "__main__":
    raise SystemExit(main())