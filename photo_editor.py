#!/usr/bin/env python3
"""
Photo Editor 2.0
Main entry point.
"""

from __future__ import annotations

import logging
import os
import shutil
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication, QMessageBox
from core.database.catalog_database import CatalogDatabase
from core.catalog.catalog import Catalog

from config.version import APP_NAME, APP_VERSION
from ui.main_window import MainWindow
from core.crash_handler import install_exception_handler


ROOT_DIR = Path(__file__).resolve().parent


def _writable_dir(primary: Path, fallback_name: str) -> Path:
    try:
        primary.mkdir(parents=True, exist_ok=True)
        probe = primary / ".write_test"
        probe.touch()
        probe.unlink()
        return primary
    except OSError:
        fallback = Path.home() / ".local" / "share" / "Photo_Editor_2" / fallback_name
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


LOG_DIR = _writable_dir(ROOT_DIR / "logs", "logs")
LOG_FILE = LOG_DIR / "photo_editor.log"


def configure_logging() -> None:
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        encoding="utf-8",
    )
    logging.info("=" * 60)
    logging.info("Starting %s", APP_NAME)
    logging.info("Version %s", APP_VERSION)


def exception_hook(exc_type, exc_value, exc_traceback):
    logging.exception("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))
    QMessageBox.critical(None, APP_NAME, str(exc_value))


# ==============================================================
# AUTO-UPDATE  (runs download+install in background thread)
# ==============================================================

def _setup_auto_update(window) -> None:
    from PySide6.QtCore import QThread, Signal as QSignal

    class _UpdateChecker(QThread):
        result = QSignal(str, str)

        def run(self):
            try:
                import urllib.request, json
                from config.version import APP_VERSION as _cur

                cfg_path = ROOT_DIR / "config" / "updater_config.json"
                cfg = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}
                gh = cfg.get("github", {})
                api = gh.get("api_url", "https://api.github.com")
                owner = gh.get("owner", "tomekkrow-sys")
                repo = gh.get("repo", "Photo_Editor_2")
                url = f"{api}/repos/{owner}/{repo}/releases/latest"

                req = urllib.request.Request(url, headers={"User-Agent": "Photo-Editor-2"})
                resp = urllib.request.urlopen(req, timeout=15)
                data = json.loads(resp.read().decode())
                latest = data.get("tag_name", "").lstrip("v")

                cur_parts = [int(x) for x in _cur.split(".")]
                lat_parts = [int(x) for x in latest.split(".")]
                newer = False
                for i in range(min(len(cur_parts), len(lat_parts))):
                    if lat_parts[i] > cur_parts[i]:
                        newer = True
                        break
                    elif lat_parts[i] < cur_parts[i]:
                        break
                if newer:
                    self.result.emit(_cur, latest)
            except Exception as e:
                logging.warning("Update check failed: %s", e)

    class _UpdateInstaller(QThread):
        finished = QSignal(str, str)  # (status, message)

        def __init__(self, ver, parent=None):
            super().__init__(parent)
            self._ver = ver

        def run(self):
            import urllib.request, tempfile, platform, subprocess
            ver = self._ver
            system = platform.system().lower()

            assets = {
                "linux": f"photo-editor-2_{ver}_amd64.deb",
                "darwin": f"Photo_Editor_2-macos-v{ver}.zip",
                "windows": f"Photo_Editor_2-windows-v{ver}.zip",
            }
            filename = assets.get(system, assets["linux"])
            download_url = (
                f"https://github.com/tomekkrow-sys/Photo_Editor_2"
                f"/releases/download/v{ver}/{filename}"
            )

            try:
                tmp_dir = tempfile.mkdtemp(prefix="photo_editor_update_")
                download_path = os.path.join(tmp_dir, filename)
                logging.info("Update: downloading %s", download_url)
                urllib.request.urlretrieve(download_url, download_path)
                logging.info("Update: downloaded to %s (%d bytes)",
                             download_path, os.path.getsize(download_path))

                if system == "linux":
                    downloads = os.path.expanduser("~/Downloads")
                    os.makedirs(downloads, exist_ok=True)
                    dest = os.path.join(downloads, filename)
                    shutil.copy2(download_path, dest)
                    logging.info("Update: copied to %s", dest)

                    # Try pkexec first
                    try:
                        ret = subprocess.run(
                            ["pkexec", "dpkg", "-i", dest],
                            timeout=120,
                        )
                        if ret.returncode == 0:
                            logging.info("Update: pkexec succeeded")
                            self.finished.emit("ok", dest)
                            return
                        else:
                            logging.warning("Update: pkexec returned %d", ret.returncode)
                    except FileNotFoundError:
                        logging.warning("Update: pkexec not found")
                    except Exception as e:
                        logging.warning("Update: pkexec error: %s", e)

                    # Fallback: write script to ~/update_photo_editor.sh
                    script_path = os.path.expanduser("~/update_photo_editor.sh")
                    with open(script_path, "w") as f:
                        f.write(f"#!/bin/bash\n")
                        f.write(f"sudo dpkg -i \"{dest}\"\n")
                        f.write(f"RC=$?\n")
                        f.write(f"if [ $RC -ne 0 ]; then sudo apt-get install -f -y; fi\n")
                        f.write(f"echo ''\n")
                        f.write(f"echo 'Zainstalowano v{ver}. Zamknij i uruchom program ponownie.'\n")
                        f.write(f"read -p 'Enter aby zamknac...'\n")
                    os.chmod(script_path, 0o755)

                    self.finished.emit("manual",
                        f"Pobrano: {dest}\n\n"
                        f"Aby zainstalowac, otworz terminal i wklej:\n\n"
                        f"bash ~/update_photo_editor.sh\n\n"
                        f"lub recznie:\n"
                        f"sudo dpkg -i \"{dest}\"")
                    return

                self.finished.emit("ok", f"Pobrano: {download_path}")
            except Exception as e:
                logging.error("Update failed: %s", e, exc_info=True)
                self.finished.emit("error", str(e))

    def _on_check_done(cur, ver):
        if not ver:
            return
        from config.i18n import t
        ret = QMessageBox.information(
            window,
            t("check_updates"),
            f"Nowa wersja: v{ver}\nObecna: v{cur}\n\nPobrac i zainstalowac?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if ret != QMessageBox.StandardButton.Yes:
            return

        installer = _UpdateInstaller(ver, window)
        installer.finished.connect(_on_install_done)
        installer.start()

    def _on_install_done(status, message):
        if status == "error":
            QMessageBox.warning(window, "Aktualizacja",
                f"Blad: {message}\n\nPobierz recznie z GitHub.")
        else:
            QMessageBox.information(window, "Aktualizacja", message)

    _checker = _UpdateChecker()
    _checker.result.connect(_on_check_done)
    _checker.start()


# ==============================================================
# MAIN
# ==============================================================

def main() -> int:
    configure_logging()

    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    data_dir = _writable_dir(ROOT_DIR / "data", "data")
    database = CatalogDatabase(data_dir / "catalog.db")
    database.initialize()
    catalog = Catalog(database)

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    install_exception_handler(APP_VERSION)

    window = MainWindow(catalog)
    window.show()

    try:
        _setup_auto_update(window)
    except Exception as e:
        logging.warning("Auto-update setup failed: %s", e)

    logging.info("Application started")
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
