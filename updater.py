# updater.py

import requests
import os
import sys
import subprocess
from pathlib import Path

def get_current_version():
    with open("version.txt", "r") as f:
        return f.read().strip()

def check_for_updates(repo_url="https://api.github.com/repos/user/repo/releases/latest"):
    try:
        response = requests.get(repo_url)
        latest_version = response.json()["tag_name"].lstrip("v")
        current_version = get_current_version()

        if latest_version > current_version:
            return True, latest_version
        else:
            return False, current_version
    except Exception as e:
        print(f"Error checking for updates: {e}")
        return False, current_version

def download_update(version):
    update_url = f"https://github.com/user/repo/releases/download/v{version}/app-update.zip"
    try:
        response = requests.get(update_url)
        with open(f"update/app-{version}.zip", "wb") as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"Error downloading update: {e}")
        return False

def install_update(version):
    # Tutaj można dodać logikę instalacji (np. rozpakowanie i nadpisanie plików)
    print(f"Installing version {version}...")
    # Przykład:
    # subprocess.run(["unzip", f"update/app-{version}.zip"])
    print("Update installed.")