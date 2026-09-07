#!/usr/bin/env python3
"""
Unified Updater Manager for Photo Editor 2
Handles version retrieval, checking, downloading, and installing updates.
"""

import os
import sys
import json
import logging
import requests
import platform
import tarfile
import zipfile
import shutil
import tempfile
from pathlib import Path
from datetime import datetime
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('update_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UpdateManager:
    def __init__(self, config_file="config/updater_config.json", app_name="Photo Editor 2"):
        """
        Initialize the Update Manager.
        
        Args:
            config_file (str): Path to configuration file
            app_name (str): Name of the application for version retrieval
        """
        self.app_name = app_name
        self.config_file = config_file
        
        # Load config with defaults
        self.config = self._load_config()
        self.base_url = "https://api.github.com/repos/username/repo/releases"
        
        # Version information
        self.current_version = self.get_current_version()
        try:
            with open("version.txt", "r") as f:
                self.current_version = f.read().strip()
        except FileNotFoundError:
            self.current_version = "1.0.0"  # Default version

    def _load_config(self):
        """Load configuration from file or use defaults."""
        default_config = {
            "base_url": "https://api.github.com/repos/username/repo/releases",
            "update_interval_days": 7,
            "check_on_startup": True,
            "auto_install": False,
            "rollback_enabled": True
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with default values
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            else:
                # Create config file with defaults
                os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=4)
                return default_config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return default_config

    def get_current_version(self):
        """Get the current version from version.txt file."""
        try:
            with open("version.txt", "r") as f:
                version = f.read().strip()
            return version
        except FileNotFoundError:
            logger.warning("version.txt not found, using default version 1.0.0")
            return "1.0.0"

    def get_latest_version(self, repository="username/repo"):
        """Get the latest version from GitHub releases."""
        try:
            # Get the latest release from GitHub
            response = requests.get(f"https://api.github.com/repos/{repository}/releases/latest", timeout=10)
            if response.status_code == 200:
                latest_release = response.json()
                latest_version = latest_release['tag_name'].lstrip('v')  # Remove 'v' prefix if present
                logger.info(f"Latest version from GitHub: {latest_version}")
                return latest_version
            else:
                logger.warning(f"Failed to get latest version. Status code: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error fetching latest version from GitHub: {e}")
            return None

    def is_version_newer(self, version1, version2):
        """
        Compare two version strings.
        
        Args:
            version1 (str): First version string
            version2 (str): Second version string
            
        Returns:
            bool: True if version1 > version2
        """
        # Split version strings into components
        v1_parts = [int(x) for x in version1.split('.')]
        v2_parts = [int(x) for x in version2.split('.')]
        
        # Pad the shorter version with zeros
        max_len = max(len(v1_parts), len(v2_parts))
        v1_parts.extend([0] * (max_len - len(v1_parts)))
        v2_parts.extend([0] * (max_len - len(v2_parts)))
        
        # Compare each component
        for i in range(max_len):
            if v1_parts[i] > v2_parts[i]:
                return True
            elif v1_parts[i] < v2_parts[i]:
                return False
        
        # Versions are equal
        return False

    def _get_platform_info(self):
        """Get platform and architecture information."""
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        # Map platform names
        if system == "linux":
            platform_name = "linux"
        elif system == "darwin":
            platform_name = "macos"
        elif system == "windows":
            platform_name = "windows"
        else:
            platform_name = "unknown"
            
        # Map architecture
        if machine in ["x86_64", "amd64"]:
            arch = "x64"
        elif machine in ["arm64", "aarch64"]:
            arch = "arm64"
        else:
            arch = "unknown"
            
        return platform_name, arch

    def _create_backup(self):
        """Create a backup of current installation."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join("backup", f"backup_{timestamp}")
            os.makedirs(backup_dir, exist_ok=True)
            
            # Copy essential files
            for root, dirs, files in os.walk(os.getcwd()):
                for file in files:
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(src_path, os.getcwd())
                    dst_path = os.path.join(backup_dir, rel_path)
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    shutil.copy2(src_path, dst_path)
            
            logger.info(f"Backup created successfully to {backup_dir}")
            return backup_dir
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None

    def _rollback_update(self, backup_dir):
        """Rollback to previous version using backup."""
        try:
            # Check if backup exists
            if not os.path.exists(backup_dir):
                logger.warning("Backup directory does not exist")
                return False
                
            # Create current folder backup in case of rollback failure
            temp_backup = os.path.join(os.getcwd(), "temp_rollback")
            shutil.copytree(os.getcwd(), temp_backup)
            
            # Remove existing content and restore from backup
            for root, dirs, files in os.walk(os.getcwd()):
                for file in files:
                    if not root.endswith("backup"):
                        os.remove(os.path.join(root, file))
                
            # Restore backup content
            for root, dirs, files in os.walk(backup_dir):
                for file in files:
                    src_path = os.path.join(backup_dir, root, file)
                    dst_path = os.path.join(os.getcwd(), os.path.relpath(src_path, backup_dir))
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    shutil.copy2(src_path, dst_path)
            
            # Clean up temp
            if os.path.exists(temp_backup):
                shutil.rmtree(temp_backup)
                
            logger.info("Update rolled back successfully")
            return True
        except Exception as e:
            logger.error(f"Error during rollback: {e}")
            return False

    def download_update(self, version, platform_arch):
        """
        Download update file for specified version and platform.
        
        Args:
            version (str): Version to download
            platform_arch (str): Target platform architecture
            
        Returns:
            str: Path to downloaded file or None if failed
        """
        try:
            # Try multiple formats for the release asset
            filename = f"photo-editor-2_v{version}_{platform_arch}.tar.gz"
            
            logger.info(f"Attempting download of {filename}")
            
            # GitHub API endpoint for releases
            response = requests.get(
                f"https://api.github.com/repos/username/repo/releases/tags/v{version}",
                timeout=30
            )
            
            if response.status_code == 200:
                release_info = response.json()
                
                # Find the correct asset for our platform
                for asset in release_info['assets']:
                    if filename in asset['name']:
                        download_url = asset['browser_download_url']
                        
                        # Download file to temporary location
                        temp_dir = tempfile.gettempdir()
                        download_path = os.path.join(temp_dir, filename)
    
                        logger.info(f"Downloading update from {download_url}")
                        
                        response = requests.get(download_url, timeout=30)
                        
                        if response.status_code == 200:
                            with open(download_path, 'wb') as f:
                                f.write(response.content)
                            logger.info(f"Update downloaded successfully to {download_path}")
                            return download_path
                        break
                    
            logger.error("Could not find suitable update asset")
            return None
            
        except Exception as e:
            logger.error(f"Error downloading update: {e}")
            return None

    def install_update(self, update_file, target_dir=None, enable_rollback=True, latest_version=None):
        """
        Install the downloaded update.
        
        Args:
            update_file (str): Path to updated file
            target_dir (str): Target directory for installation (defaults to current)
            enable_rollback (bool): Whether to create backup before installing
            latest_version (str): The version we're updating to
            
        Returns:
            bool: True if installation succeeded
        """
        try:
            if target_dir is None:
                target_dir = os.getcwd()
            
            # Create backup if enabled
            backup_dir = None
            if enable_rollback:
                backup_dir = self._create_backup()
            
            # Determine file type and extract
            if zipfile.is_zipfile(update_file):
                with zipfile.ZipFile(update_file, 'r') as zip_ref:
                    zip_ref.extractall(target_dir)
            elif tarfile.is_tarfile(update_file):
                with tarfile.open(update_file, 'r') as tar_ref:
                    tar_ref.extractall(target_dir)
            
            # Update version file
            with open(os.path.join(target_dir, "version.txt"), "w") as f:
                # Write the new version that we're installing 
                f.write(latest_version)
            
            logger.info("Update installed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error installing update: {e}")
            
            # If there was an error during installation and we have a backup, rollback
            if enable_rollback and backup_dir:
                logger.info("Rolling back to previous version due to installation error")
                self._rollback_update(backup_dir)
                
            return False

    def check_and_update(self, auto_install=True):
        """
        Check for updates and perform update if available.
        
        Args:
            auto_install (bool): Whether to automatically install update
            
        Returns:
            str: Status ('updated', 'no_update', 'error')
        """
        try:
            current_version = self.get_current_version()
            latest_version = self.get_latest_version()
            
            logger.info(f"Current Version: {current_version}")
            logger.info(f"Latest Version: {latest_version}")
            
            # If we can't get latest version, continue with current
            if not latest_version:
                return "error"
            
            # Compare versions  
            if self.is_version_newer(latest_version, current_version):
                logger.info("New version available")
                # For demo purposes, show what would be done
                if not auto_install:
                    return "update_available"
                
                # Download update
                platform_name, arch = self._get_platform_info()
                downloaded_file = self.download_update(latest_version, f"{platform_name}-{arch}")
                
                if downloaded_file:
                    logger.info("Installing update...")
                    
                    # Install the update
                    install_result = self.install_update(downloaded_file, latest_version=latest_version)
                    
                    if install_result:
                        logger.info("Update installed successfully!")
                        # Clean up download file
                        os.unlink(downloaded_file)
                        return "updated"
                    else:
                        logger.error("Failed to install update")
                        
                        # Clean up download file on failure
                        os.unlink(downloaded_file) 
                        return "error"
                else:
                    logger.error("Failed to download update")
                    return "error"
            elif current_version == latest_version:
                logger.info("Application is up to date")
                return "no_update"
            else:
                logger.info("You have a newer version than released!")
                return "no_update"
                
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            return "error"

    def start_background_update_checker(self):
        """Start background update checker (scheduled task)."""
        # This would be implemented in a scheduled task or daemon
        pass

    def run_update_check(self):
        """Run update check immediately."""
        status = self.check_and_update()
        if status == "updated":
            logger.info("Update completed successfully")
        elif status == "no_update":
            logger.info("No updates available")
        elif status == "update_available":
            logger.info("Update is available (but not automatically applied)")
        else:
            logger.error(f"Error during update check: {status}")

def main():
    """Main entry point for the updater."""
    try:
        manager = UpdateManager()
        manager.run_update_check()
    except Exception as e:
        logger.error(f"Critical error in main execution: {e}")

if __name__ == "__main__":
    main()