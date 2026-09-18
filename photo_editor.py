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
            result = QSignal(str, str)  # (current_version, latest_version) or ("","") 

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
                        self.result.emit(current, latest)
                    else:
                        self.result.emit("", "")
                except Exception as e:
                    logging.warning("Update check failed: %s", e)
                    self.result.emit("", "")

        def _on_update_result(cur, ver):
            if not ver:
                return
            from PySide6.QtWidgets import QMessageBox, QProgressDialog
            from PySide6.QtCore import Qt
            from config.i18n import t

            ret = QMessageBox.information(
                window,
                t("check_updates"),
                f"Nowa wersja: v{ver}\nObecna: v{cur}\n\nPobrac i zainstalowac?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if ret != QMessageBox.StandardButton.Yes:
                return

            import platform
            system = platform.system().lower()
            import urllib.request
            import tempfile
            import subprocess

            # Find the right asset
            assets = {
                "linux": f"photo-editor-2_{ver}_amd64.deb",
                "darwin": f"Photo_Editor_2-macos-{ver}.zip",
                "windows": f"Photo_Editor_2-windows-{ver}.zip",
            }
            filename = assets.get(system, assets["linux"])
            download_url = f"https://github.com/tomekkrow-sys/Photo_Editor_2/releases/download/v{ver}/{filename}"

            try:
                progress = QProgressDialog(f"Pobieranie v{ver}...", "Anuluj", 0, 0, window)
                progress.setWindowTitle("Aktualizacja")
                progress.setWindowModality(Qt.WindowModality.WindowModal)
                progress.show()

                tmp_dir = tempfile.mkdtemp(prefix="photo_editor_update_")
                download_path = os.path.join(tmp_dir, filename)
                urllib.request.urlretrieve(download_url, download_path)

                progress.close()

                if system == "linux":
                    ret2 = subprocess.run(
                        ["pkexec", "dpkg", "-i", download_path],
                        capture_output=True, text=True
                    )
                    if ret2.returncode == 0:
                        QMessageBox.information(window, "Aktualizacja",
                            f"Zainstalowano v{ver}. Uruchom ponownie program.")
                    else:
                        # Fallback without pkexec
                        QMessageBox.information(window, "Aktualizacja",
                            f"Pobrano: {download_path}\n\nUruchom:\nsudo dpkg -i {download_path}")
                else:
                    QMessageBox.information(window, "Aktualizacja",
                        f"Pobrano: {download_path}")

            except Exception as e:
                logging.error("Update download failed: %s", e)
                QMessageBox.warning(window, "Aktualizacja",
                    f"Blad pobierania: {e}\n\nPobierz recznie:\n{download_url}")

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