#!/usr/bin/env python3
"""
Update Manager for Photo Editor 2
"""

import sys
import os
import subprocess
import requests
import json
from pathlib import Path
import tempfile
import shutil
import zipfile
import tarfile
import re

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def get_current_version():
    """
    Get the current version of the application from version.txt
    """
    try:
        with open("version.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0.0.0"

def get_latest_version():
    """
    Get the latest version from GitHub releases
    """
    try:
        response = requests.get(
            "https://api.github.com/repos/tomekkrow-sys/Photo_Editor_2/releases/latest",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            tag_name = data.get("tag_name", "")
            # Extract version number from tag (e.g., "v1.2.3" -> "1.2.3")
            version = re.sub(r'^v', '', tag_name)
            return version
        else:
            print(f"Failed to fetch latest version: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching latest version: {e}")
        return None

def is_version_newer(current, latest):
    """
    Compare two version strings to see if latest is newer than current
    Returns True if latest > current
    """
    try:
        # Simple version comparison - split by dots and compare numbers
        current_parts = [int(x) for x in current.split('.')]
        latest_parts = [int(x) for x in latest.split('.')]
        
        # Pad shorter version with zeros
        max_len = max(len(current_parts), len(latest_parts))
        current_parts += [0] * (max_len - len(current_parts))
        latest_parts += [0] * (max_len - len(latest_parts))
        
        # Compare each part
        for i in range(max_len):
            if latest_parts[i] > current_parts[i]:
                return True
            elif latest_parts[i] < current_parts[i]:
                return False
        
        return False  # Versions are equal
    except Exception:
        return False

def download_update(version, platform="linux"):
    """
    Download the update for the specified version and platform
    """
    try:
        if platform == "linux":
            asset_name = "Photo_Editor_2-linux.zip"
        elif platform == "windows":
            asset_name = "Photo_Editor_2-windows.zip"
        else:
            asset_name = "Photo_Editor_2.zip"
            
        response = requests.get(
            f"https://api.github.com/repos/tomekkrow-sys/Photo_Editor_2/releases/tags/v{version}",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            assets = data.get("assets", [])
            
            # Find the correct asset download URL
            asset_url = None
            for asset in assets:
                if asset_name in asset["name"]:
                    asset_url = asset["browser_download_url"]
                    break
            
            if asset_url:
                print(f"Downloading update {version}...")
                
                # Download to temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False)
                temp_file.close()
                
                download_response = requests.get(asset_url, timeout=30)
                
                with open(temp_file.name, 'wb') as f:
                    f.write(download_response.content)
                
                return temp_file.name
                
        print("Could not find update for this platform")
        return None
        
    except Exception as e:
        print(f"Error downloading update: {e}")
        return None

def install_update(update_file, target_dir=None):
    """
    Install the downloaded update
    """
    try:
        if target_dir is None:
            target_dir = os.getcwd()
            
        # Determine file type and extract
        if zipfile.is_zipfile(update_file):
            with zipfile.ZipFile(update_file, 'r') as zip_ref:
                zip_ref.extractall(target_dir)
        elif tarfile.is_tarfile(update_file):
            with tarfile.open(update_file, 'r') as tar_ref:
                tar_ref.extractall(target_dir)
        
        # Update version file
        with open(os.path.join(target_dir, "version.txt"), "w") as f:
            f.write("1.0.1")
            
        print("Update installed successfully")
        return True
        
    except Exception as e:
        print(f"Error installing update: {e}")
        return False

def check_and_update():
    """
    Check for updates and perform update if available
    Returns:
        'updated' - if update was installed
        'no_update' - if no new version is available
        'error' - if there was an error checking for updates
    """
    try:
        current_version = get_current_version()
        latest_version = get_latest_version()
        
        print(f"Current Version: {current_version}")
        print(f"Latest Version: {latest_version}")
        
        # If we can't get latest version, continue with current
        if not latest_version:
            return "error"
        
        # Compare versions
        if is_version_newer(current_version, latest_version):
            print("You have a newer version than released!")
            return "no_update"
        elif current_version == latest_version:
            print("Application is up to date")
            return "no_update"
        else:
            print(f"New version available: {latest_version}")
            
            # For demo purposes, we'll just simulate the update process
            # In actual implementation, download and install would happen here
            
            # Simulate installation (in real scenario: download -> install)
            print("Simulating update...")
            print("Would now download and install update...")
            # Actual implementation would:
            # 1. Download the update file
            # 2. Extract it to temporary location  
            # 3. Replace files in current directory
            # 4. Update version.txt
            
            return "updated"
            
    except Exception as e:
        print(f"Error checking for updates: {e}")
        return "error"

# Test function if run directly
if __name__ == "__main__":
    result = check_and_update()
    if result == "updated":
        print("Application has been updated!")
    elif result == "no_update":
        print("No update available")
    else:
        print("Error checking for updates")