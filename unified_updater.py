#!/usr/bin/env python3
"""
Unified Update Manager for Photo Editor 2
"""

import sys
import os
import subprocess
import requests
import json
import hashlib
import base64
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
import gnupg  # For GPG signature verification

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

class UnifiedUpdateManager:
    """Unified update manager that consolidates functionality from both basic and advanced update managers"""
    
    def __init__(self, config_file="config/updater_config.json"):
        """
        Initialize the unified update manager
        
        Args:
            config_file (str): Path to configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
        self.gpg_home = os.path.join(os.path.dirname(__file__), "gpg_keys")
        
        # Ensure GPG keys directory exists
        os.makedirs(self.gpg_home, exist_ok=True)
        
    def _load_config(self):
        """Load configuration from file or use defaults"""
        default_config = {
            "github": {
                "owner": "tomekkrow-sys",
                "repo": "Photo_Editor_2",
                "api_url": "https://api.github.com"
            },
            "update_check_interval": 1800,  # 30 minutes in seconds
            "auto_update": True,
            "background_updates": True,
            "rollback_enabled": True,
            "version_pin_dependencies": True
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
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
    
    def _get_platform_info(self):
        """Detect platform and architecture information"""
        import platform
        
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        if system == "darwin":  # macOS
            platform_name = "macos"
        elif system == "windows":
            platform_name = "windows"
        else:  # linux and others
            platform_name = "linux"
            
        # Determine architecture
        if machine in ['arm64', 'aarch64']:
            arch = "arm64"
        elif machine in ['x86_64', 'amd64']:
            arch = "x64"
        else:
            arch = "unknown"
            
        return platform_name, arch
    
    def get_current_version(self):
        """
        Get the current version of the application from version.txt
        """
        try:
            with open("version.txt", "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return "0.0.0"
    
    def get_latest_version(self):
        """
        Get the latest version from GitHub releases
        """
        try:
            github_config = self.config.get("github", {})
            api_url = github_config.get("api_url", "https://api.github.com")
            owner = github_config.get("owner", "tomekkrow-sys")
            repo = github_config.get("repo", "Photo_Editor_2")
            
            response = requests.get(
                f"{api_url}/repos/{owner}/{repo}/releases/latest",
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
    
    def is_version_newer(self, current, latest):
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
    
    def _calculate_checksum(self, file_path, algorithm='sha256'):
        """
        Calculate checksum of a file
        
        Args:
            file_path (str): Path to the file
            algorithm (str): Hash algorithm to use
            
        Returns:
            str: Hexadecimal hash string
        """
        try:
            hash_obj = getattr(hashlib, algorithm)()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating checksum: {e}")
            return None
    
    def _verify_signature(self, file_path, signature_path):
        """
        Verify GPG signature of a file
        
        Args:
            file_path (str): Path to the file to verify
            signature_path (str): Path to the signature file
            
        Returns:
            bool: True if verification succeeds
        """
        try:
            # Initialize GPG
            gpg = gnupg.GPG(homedir=self.gpg_home)
            
            with open(signature_path, 'rb') as f:
                status = gpg.verify_file(f, file_path)
                
            logger.info(f"GPG signature verification: {status.valid}")
            return status.valid
        except Exception as e:
            logger.error(f"Error verifying GPG signature: {e}")
            return False
    
    def _download_with_verification(self, asset_url, expected_hash=None, signature_url=None):
        """
        Download a file with verification
        
        Args:
            asset_url (str): URL to download from
            expected_hash (str): Expected hash for verification
            signature_url (str): URL of signature file
            
        Returns:
            tuple: (temp_file_path, success)
        """
        try:
            # Download to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".tmp")
            temp_file.close()
            
            download_response = requests.get(asset_url, timeout=30)
            
            if download_response.status_code == 200:
                with open(temp_file.name, 'wb') as f:
                    f.write(download_response.content)
                
                # Verify content integrity if expected hash provided
                if expected_hash:
                    actual_hash = self._calculate_checksum(temp_file.name)
                    if actual_hash != expected_hash:
                        logger.error(f"Hash mismatch: expected {expected_hash}, got {actual_hash}")
                        os.unlink(temp_file.name)
                        return None, False
                
                # Verify GPG signature if available  
                if signature_url:
                    sig_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".sig")
                    sig_temp.close()
                    
                    try:
                        sig_response = requests.get(signature_url, timeout=30)
                        with open(sig_temp.name, 'wb') as f:
                            f.write(sig_response.content)
                        
                        if self._verify_signature(temp_file.name, sig_temp.name):
                            logger.info("File signature verified successfully")
                        else:
                            logger.error("File signature verification failed")
                            os.unlink(temp_file.name)
                            return None, False
                    finally:
                        os.unlink(sig_temp.name)
                
                logger.info(f"Downloaded file to {temp_file.name}")
                return temp_file.name, True
            else:
                logger.error(f"Failed to download file: {download_response.status_code}")
                return None, False
                
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return None, False
    
    def download_update(self, version, platform=None):
        """
        Download the update for the specified version and platform
        
        Args:
            version (str): Version to download
            platform (str): Platform name (overrides auto-detection)
            
        Returns:
            str: Path to downloaded file or None if error
        """
        try:
            # If no platform specified, detect automatically
            if not platform:
                platform_name, arch = self._get_platform_info()
                platform = f"{platform_name}-{arch}"
            
            github_config = self.config.get("github", {})
            api_url = github_config.get("api_url", "https://api.github.com")
            owner = github_config.get("owner", "tomekkrow-sys")
            repo = github_config.get("repo", "Photo_Editor_2")
            
            # Get release info
            response = requests.get(
                f"{api_url}/repos/{owner}/{repo}/releases/tags/v{version}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                assets = data.get("assets", [])
                
                # Find the correct asset for this platform
                asset_name = None
                asset_url = None
                expected_hash = None
                signature_url = None
                
                # Look for platform-specific asset or generic asset
                for asset in assets:
                    asset_filename = asset["name"].lower()
                    
                    if platform in asset_filename or "photo_editor_2" in asset_filename:
                        asset_name = asset["name"]
                        asset_url = asset["browser_download_url"]
                        
                        # Look for associated .sha256 and .sig files
                        for other_asset in assets:
                            if f"{asset_name}.sha256" == other_asset["name"]:
                                expected_hash = other_asset["browser_download_url"]
                            elif f"{asset_name}.sig" == other_asset["name"]:
                                signature_url = other_asset["browser_download_url"]
                        break
                
                if not asset_url:
                    logger.error("Could not find update asset for this platform")
                    return None
                
                # Download with verification
                logger.info(f"Downloading update {version}...")
                
                # Get expected hash value if available
                expected_hash_value = None
                try:
                    signature_response = requests.get(expected_hash, timeout=10)
                    expected_hash_value = signature_response.text.strip().split()[0]
                except:
                    pass  # Ignore error if hash file is unavailable
                
                downloaded_file, success = self._download_with_verification(
                    asset_url,
                    expected_hash_value,
                    signature_url
                )
                
                return downloaded_file if success else None
                
            logger.error("Could not fetch release information")
            return None
            
        except Exception as e:
            logger.error(f"Error downloading update: {e}")
            return None
    
    def _create_backup(self, backup_dir=None):
        """
        Create a backup of current application files
        
        Args:
            backup_dir (str): Directory to store backup (optional)
            
        Returns:
            str: Path to backup directory or None on error
        """
        try:
            if not backup_dir:
                backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
            os.makedirs(backup_dir, exist_ok=True)
            
            # Create backup of key files (you may want to customize this list)
            key_files = ["version.txt", "main.py", "requirements.txt"]
            for file_path in key_files:
                if os.path.exists(file_path):
                    shutil.copy2(file_path, backup_dir)
                    
            logger.info(f"Backup created: {backup_dir}")
            return backup_dir
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None
    
    def _rollback_update(self, backup_dir):
        """
        Rollback to previous version using backup
        
        Args:
            backup_dir (str): Directory containing backup files
        """
        try:
            if os.path.exists(backup_dir):
                # Restore files from backup
                for item in os.listdir(backup_dir):
                    source = os.path.join(backup_dir, item)
                    target = os.path.join(os.getcwd(), item)
                    shutil.copy2(source, target)
                
                logger.info(f"Update rolled back successfully using {backup_dir}")
            else:
                logger.warning("Backup directory not found, cannot rollback")
        except Exception as e:
            logger.error(f"Error during rollback: {e}")
    
    def install_update(self, update_file, target_dir=None, enable_rollback=True):
        """
        Install the downloaded update
        
        Args:
            update_file (str): Path to updated file
            target_dir (str): Target directory for installation (defaults to current)
            enable_rollback (bool): Whether to create backup before installing
            
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
                # Extract from the update or use actual version
                current_version = self.get_current_version()
                f.write(current_version)
            
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
        Check for updates and perform update if available
        
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
            if self.is_version_newer(current_version, latest_version):
                logger.info("You have a newer version than released!")
                return "no_update"
            elif current_version == latest_version:
                logger.info("Application is up to date")
                return "no_update"
            else:
                logger.info(f"New version available: {latest_version}")
                
                # For demo purposes, show what would be done
                if not auto_install:
                    return "update_available"
                
                # Download update
                platform_name, arch = self._get_platform_info()
                downloaded_file = self.download_update(latest_version, f"{platform_name}-{arch}")
                
                if downloaded_file:
                    logger.info("Installing update...")
                    
                    # Install the update
                    install_result = self.install_update(downloaded_file)
                    
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
                    
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            return "error"
    
    def start_background_update_checker(self):
        """
        Start the background thread to check for updates periodically
        
        Returns:
            threading.Thread: The background thread
        """
        def check_updates_background():
            """Background thread function to check for updates periodically"""
            while True:
                try:
                    logger.info("Checking for updates in background...")
                    result = self.check_and_update(auto_install=self.config.get("auto_update", True))
                    
                    if result == "updated":
                        logger.info("Update installed in background")
                        
                        # Optionally restart the application (not implemented here)
                        # Would require a system restart mechanism
                    elif result == "error":
                        logger.error("Error occurred during background update check")
                    
                    # Check for updates based on configured interval
                    check_interval = self.config.get("update_check_interval", 1800)
                    time.sleep(check_interval)
                    
                except Exception as e:
                    logger.error(f"Error in background update check: {e}")
                    # Wait before retrying after error
                    time.sleep(60)  # Wait 1 minute before retry
        
        if self.config.get("background_updates", True):
            update_thread = threading.Thread(target=check_updates_background, daemon=True)
            update_thread.start()
            logger.info("Background update checker started")
            
            return update_thread
        else:
            logger.info("Background updates disabled in configuration")
            return None
    
    def check_for_update(self):
        """
        Check for update and return detailed information
        
        Returns:
            dict: Update information
        """
        current_version = self.get_current_version()
        latest_version = self.get_latest_version()
        
        info = {
            "current_version": current_version,
            "latest_version": latest_version,
            "is_newer": False if not latest_version or not current_version else 
                       self.is_version_newer(current_version, latest_version),
            "is_up_to_date": current_version == latest_version,
            "update_available": False if not latest_version or not current_version else
                              (not self.is_version_newer(current_version, latest_version) and 
                               current_version != latest_version)
        }
        
        return info
    
    def update_requirements_txt(self, version):
        """
        Update requirements.txt with pinned versions for this release
        
        Args:
            version (str): Version of the release
        """
        try:
            # For this example, just add some pinned versions
            # In a real implementation, you'd extract these from the release assets or GitHub tags
            
            # Read current requirements
            if os.path.exists("requirements.txt"):
                with open("requirements.txt", "r") as f:
                    old_requirements = f.read().strip()
                
                logger.info("Updated requirements.txt would be pinned to specific versions")
                # Note: The exact implementation depends on how you extract these pinned versions from the release
            else:
                logger.warning("requirements.txt not found, could not update")
                
        except Exception as e:
            logger.error(f"Error updating requirements.txt: {e}")

def main():
    """
    Main function to demonstrate the unified updater
    """
    print("Initializing Unified Update Manager...")
    updater = UnifiedUpdateManager()
    
    # Check for updates
    result = updater.check_and_update(auto_install=False) 
    info = updater.check_for_update()
    
    print(f"Current Version: {info['current_version']}")
    print(f"Latest Version: {info['latest_version']}")
    print(f"Update Available: {info['update_available']}")
    
    if info['update_available']:
        print("New version is available!")
        
        # Optionally start background checker
        thread = updater.start_background_update_checker()
        print("Background update checker started!")
        
    else:
        print("Application is up to date!")

if __name__ == "__main__":
    main()