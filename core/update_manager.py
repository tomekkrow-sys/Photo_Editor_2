#!/usr/bin/env python3
from __future__ import annotations

import json
import logging
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

from config.version import APP_VERSION, APP_NAME

GITHUB_REPO = "tomekkrow-sys/Photo_Editor_2"
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
GITHUB_DOWNLOAD = f"https://github.com/{GITHUB_REPO}/releases/download"


def _parse_version(v: str) -> tuple[int, ...]:
    v = v.strip().lstrip("v")
    parts = []
    for p in v.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            break
    return tuple(parts) if parts else (0,)


def check_for_update() -> dict | None:
    try:
        req = Request(GITHUB_API, headers={"Accept": "application/vnd.github.v3+json"})
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        tag = data.get("tag_name", "")
        latest_version = _parse_version(tag)
        current_version = _parse_version(APP_VERSION)

        if not tag or latest_version <= current_version:
            return None

        body = data.get("body", "")
        assets = []
        for a in data.get("assets", []):
            assets.append({
                "name": a["name"],
                "url": a["browser_download_url"],
                "size": a.get("size", 0),
            })

        return {
            "version": tag.lstrip("v"),
            "tag": tag,
            "notes": body,
            "assets": assets,
        }
    except Exception as e:
        logging.error("Update check failed: %s", e)
        return None


def _detect_asset(assets: list[dict]) -> dict | None:
    system = platform.system().lower()
    for a in assets:
        name = a["name"].lower()
        if system == "linux" and name.endswith(".zip") and "windows" not in name:
            return a
        if system == "linux" and name.endswith(".deb"):
            return a
        if system == "windows" and name.endswith(".zip") and "windows" in name:
            return a
        if system == "windows" and name.endswith(".exe"):
            return a
    for a in assets:
        if a["name"].lower().endswith(".zip"):
            return a
    return None


def download_and_install(asset: dict, progress_callback=None) -> bool:
    try:
        url = asset["url"]
        name = asset["name"]
        is_zip = name.lower().endswith(".zip")
        is_deb = name.lower().endswith(".deb")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            download_path = tmpdir / name

            logging.info("Downloading update: %s", url)
            if progress_callback:
                progress_callback("Pobieranie...", 0)

            req = Request(url, headers={"Accept": "application/octet-stream"})
            with urlopen(req, timeout=120) as resp:
                total = int(resp.headers.get("Content-Length", 0))
                downloaded = 0
                chunk_size = 65536
                with open(download_path, "wb") as f:
                    while True:
                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total > 0:
                            pct = int(downloaded * 100 / total)
                            progress_callback("Pobieranie...", pct)

            if progress_callback:
                progress_callback("Instalowanie...", 90)

            root_dir = Path(__file__).resolve().parent.parent

            if is_deb:
                result = subprocess.run(
                    ["dpkg", "-i", str(download_path)],
                    capture_output=True, text=True, timeout=60,
                )
                if result.returncode != 0:
                    logging.error("dpkg failed: %s", result.stderr)
                    return False

            elif is_zip:
                extract_dir = tmpdir / "extracted"
                with zipfile.ZipFile(download_path, "r") as zf:
                    zf.extractall(extract_dir)

                app_dir = extract_dir / "Photo_Editor_2"
                if not app_dir.exists():
                    for d in extract_dir.iterdir():
                        if d.is_dir() and (d / "photo_editor.py").exists():
                            app_dir = d
                            break

                if not app_dir.exists():
                    logging.error("Cannot find app dir in zip")
                    return False

                update_files = [
                    "photo_editor.py", "requirements.txt", "run.sh",
                    "config", "core", "ui", "plugins",
                ]
                for item in update_files:
                    src = app_dir / item
                    dst = root_dir / item
                    if src.exists():
                        if src.is_dir():
                            if dst.exists():
                                shutil.rmtree(dst)
                            shutil.copytree(src, dst)
                        else:
                            shutil.copy2(src, dst)

            if progress_callback:
                progress_callback("Gotowe!", 100)

            logging.info("Update installed successfully")
            return True

    except Exception as e:
        logging.error("Update install failed: %s", e)
        return False


def restart_app():
    root_dir = Path(__file__).resolve().parent.parent
    run_sh = root_dir / "run.sh"
    if run_sh.exists():
        subprocess.Popen(
            ["/bin/bash", str(run_sh)],
            cwd=str(root_dir),
            start_new_session=True,
        )
    else:
        subprocess.Popen(
            [sys.executable, str(root_dir / "photo_editor.py")],
            cwd=str(root_dir),
            start_new_session=True,
        )
    os._exit(0)
