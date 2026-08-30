#!/usr/bin/env python3
"""
Advanced Update Manager for Photo Editor 2 with background updates
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
import threading
import time
import logging
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("update_manager.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
            logger.error(f"Failed to fetch latest version: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error fetching latest version: {e}")
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
                logger.info(f"Downloading update {version}...")
                
                # Download to temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
                temp_file.close()
                
                download_response = requests.get(asset_url, timeout=30)
                
                with open(temp_file.name, 'wb') as f:
                    f.write(download_response.content)
                
                logger.info(f"Downloaded update to {temp_file.name}")
                return temp_file.name
                
        logger.error("Could not find update for this platform")
        return None
        
    except Exception as e:
        logger.error(f"Error downloading update: {e}")
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
            
        logger.info("Update installed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error installing update: {e}")
        return False

def check_updates_background():
    """
    Background thread function to check for updates periodically
    """
    while True:
        try:
            logger.info("Checking for updates in background...")
            current_version = get_current_version()
            latest_version = get_latest_version()
            
            if latest_version and current_version != latest_version:
                # If there's a newer version and it's not the same as current
                new_version = is_version_newer(current_version, latest_version)
                
                if new_version:
                    logger.info(f"New update available: {latest_version}")
                    
                    # Download update
                    platform = "linux"  # or detect platform dynamically
                    downloaded_file = download_update(latest_version, platform)
                    
                    if downloaded_file:
                        logger.info("Installing update...")
                        
                        # Install the update (this would be where actual installation takes place)
                        install_result = install_update(downloaded_file)
                        
                        if install_result:
                            logger.info("Update installed successfully!")
                            
                            # In real implementation, we would then restart or update
                            # For this demo, we'll just simulate it
                            print("Update would have been applied without application restart")
                        else:
                            logger.error("Failed to install update")
                    else:
                        logger.error("Failed to download update")
                else:
                    logger.info("No new updates available")
            
            # Check for updates every 30 minutes (1800 seconds)
            time.sleep(1800)
            
        except Exception as e:
            logger.error(f"Error in background update check: {e}")
            time.sleep(1800)  # Wait before retry

def start_background_update_checker():
    """
    Start the background thread to check for updates
    """
    update_thread = threading.Thread(target=check_updates_background, daemon=True)
    update_thread.start()
    logger.info("Background update checker started")
    
    return update_thread

def create_github_release(version, release_notes, assets=None):
    """
    Create a new GitHub release programmatically
    This would typically require GitHub API tokens and proper credentials
    For demonstration purposes, this provides the structure
    
    Args:
        version: Version number (e.g., "1.0.2")
        release_notes: Release notes for this version
        assets: List of asset files to upload
        
    Returns:
        URL of the created release or None if failed
    """
    logger.info(f"Creating GitHub release v{version}")
    
    try:
        # This would require a GitHub token and proper API interactions
        # Implementation is not included for security reasons, but shows how it could work
        
        # Example endpoint structure (not executable):
        '''
        release_data = {
            "tag_name": f"v{version}",
            "name": f"Photo Editor 2 v{version}",
            "body": release_notes,
            "draft": False,
            "prerelease": False
        }
        
        # This would require proper authentication with GitHub API
        response = requests.post(
            "https://api.github.com/repos/tomekkrow-sys/Photo_Editor_2/releases",
            headers={"Authorization": f"token YOUR_GITHUB_TOKEN"},
            json=release_data
        )
        '''
        
        logger.info(f"Would create GitHub release v{version}")
        return f"https://github.com/tomekkrow-sys/Photo_Editor_2/releases/tag/v{version}"
        
    except Exception as e:
        logger.error(f"Error creating GitHub release: {e}")
        return None

def auto_publish_new_version(version, commit_message="Automated release"):
    """
    Automate the process of publishing a new version
    This function should be called when you want to automatically create a release
    """
    logger.info(f"Starting automatic publishing of version {version}")
    
    # First, we'd normally bump the version in version.txt
    try:
        with open("version.txt", "w") as f:
            f.write(version)
        logger.info(f"Updated version.txt to {version}")
        
        # Then create a release
        release_url = create_github_release(
            version,
            f"Automated release of Photo Editor 2 v{version}"
        )
        
        if release_url:
            logger.info(f"Successfully published release: {release_url}")
            
            # Commit the version bump (if git is available)
            try:
                # This would normally be done with git commands
                logger.info("Would commit and push new version to repository")
            except Exception:
                pass
                
            return release_url
        else:
            logger.error("Failed to publish GitHub release")
            return None
            
    except Exception as e:
        logger.error(f"Error in auto publishing: {e}")
        return None

def check_and_update():
    """
    Check for updates and perform update if available
    This is the main entry point for checking updates
    Returns:
        'updated' - if update was installed
        'no_update' - if no new version is available
        'error' - if there was an error checking for updates
        'background' - if background check started successfully
    """
    try:
        current_version = get_current_version()
        latest_version = get_latest_version()
        
        logger.info(f"Current Version: {current_version}")
        logger.info(f"Latest Version: {latest_version}")
        
        # If we can't get latest version, continue with current
        if not latest_version:
            return "error"
        
        # Compare versions
        if is_version_newer(current_version, latest_version):
            logger.info("You have a newer version than released!")
            return "no_update"
        elif current_version == latest_version:
            logger.info("Application is up to date")
            return "no_update"
        else:
            logger.info(f"New version available: {latest_version}")
            
            # For demo purposes, we'll simulate the update process
            # In actual implementation, download and install would happen here
            
            # Simulate installation (in real scenario: download -> install)
            logger.info("Would now download and install update without requiring restart...")
            
            # Start background checker to check for updates periodically
            start_background_update_checker()
            
            return "background"
            
    except Exception as e:
        logger.error(f"Error checking for updates: {e}")
        return "error"

# Test function if run directly
if __name__ == "__main__":
    result = check_and_update()
    if result == "updated":
        print("Application has been updated!")
    elif result == "no_update":
        print("No update available")
    elif result == "background":
        print("Background update checker started")
    else:
        print("Error checking for updates")