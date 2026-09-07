#!/usr/bin/env python3
"""
Enhanced Update Manager with UI integration for Photo Editor 2
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
    def __init__(self, config_file="config/updater_config.json"):
        """
        Initialize the update manager with configuration.
        """
        self.config_file = config_file
        self.config = self._load_config()
        self.current_version = self._get_current_version()
        
        # Extract GitHub configuration
        self.owner = self.config.get('github', {}).get('owner', 'tomekkrow-sys')
        self.repo = self.config.get('github', {}).get('repo', 'Photo_Editor_2')
        self.base_url = self.config.get('github', {}).get('api_url', 'https://api.github.com')
        
        # Set up full repo path for API calls
        self.full_repo_path = f"{self.owner}/{self.repo}"
        
        # Initialize update settings from config
        self.check_interval_hours = self.config.get('update', {}).get('check_interval_hours', 24)
        self.backup_enabled = self.config.get('update', {}).get('backup_enabled', True)
        self.auto_update = self.config.get('update', {}).get('auto_update', False)
        self.background_updates = self.config.get('update', {}).get('background_updates', True)

    def _load_config(self):
        """Load configuration from file or use defaults."""
        default_config = {
            "github": {
                "api_url": "https://api.github.com",
                "owner": "tomekkrow-sys",
                "repo": "Photo_Editor_2"
            },
            "update": {
                "check_interval_hours": 24,
                "backup_enabled": True,
                "auto_update": False,
                "background_updates": True
            }
        }

        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    # Merge defaults with user config
                    for key, value in default_config.items():
                        if key not in user_config:
                            user_config[key] = value
                        elif isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                if sub_key not in user_config[key]:
                                    user_config[key][sub_key] = sub_value
                    return user_config
            else:
                logger.info("Configuration file not found, using defaults")
                return default_config
                
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return default_config

    def _get_current_version(self):
        """Get current version from version.txt file."""
        try:
            with open("version.txt", "r") as f:
                version = f.read().strip()
                logger.info(f"Current version: {version}")
                return version
        except Exception as e:
            logger.error(f"Error reading version.txt: {e}")
            return "0.0.0"

    def get_latest_version(self):
        """Get the latest version from GitHub releases."""
        try:
            # GitHub API endpoint for releases
            url = f"{self.base_url}/repos/{self.full_repo_path}/releases/latest"
            
            logger.info(f"Checking for latest release at {url}")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                latest_release = response.json()
                
                # Check if tag_name exists in the response
                if 'tag_name' not in latest_release:
                    logger.warning("Release response does not contain tag_name")
                    return None
                    
                version = latest_release['tag_name'].lstrip('v')
                logger.info(f"Latest version from GitHub: {version}")
                return version
                
            elif response.status_code == 404:
                logger.error("GitHub repository or release not found")
                return None
            else:
                logger.error(f"Error fetching latest release: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting latest version from GitHub: {e}")
            return None

    def is_version_newer(self, new_version, current_version):
        """Compare versions to determine if update is needed."""
        try:
            # Simple semantic version comparison
            def version_tuple(version_str):
                # Handle pre-release and build metadata
                version_str = version_str.split('+')[0]  # Remove build metadata
                version_str = version_str.split('-')[0]  # Remove pre-release
                return tuple(map(int, (version_str.split('.'))))

            new_tuple = version_tuple(new_version)
            current_tuple = version_tuple(current_version)
            
            return new_tuple > current_tuple
            
        except Exception as e:
            logger.error(f"Error comparing versions: {e}")
            return False

    def check_for_updates(self):
        """Check if updates are available."""
        latest_version = self.get_latest_version()
        
        if not latest_version:
            logger.warning("Could not determine latest version")
            return {
                "update_available": False,
                "current_version": self.current_version,
                "latest_version": None,
                "message": "Could not check for updates"
            }
            
        is_newer = self.is_version_newer(latest_version, self.current_version)
        
        if is_newer:
            logger.info(f"Update available: {self.current_version} -> {latest_version}")
            return {
                "update_available": True,
                "current_version": self.current_version,
                "latest_version": latest_version,
                "message": f"New version {latest_version} is available"
            }
        else:
            logger.info(f"No updates available. Current version: {self.current_version}")
            return {
                "update_available": False,
                "current_version": self.current_version,
                "latest_version": latest_version,
                "message": "No updates available"
            }

    def get_platform_asset(self, version):
        """Get platform-specific asset from release."""
        try:
            # GitHub API endpoint for specific release
            url = f"{self.base_url}/repos/{self.full_repo_path}/releases/tags/v{version}"
            
            logger.info(f"Getting assets from {url}")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                release_info = response.json()
                
                # Get platform-specific asset based on OS
                platform_name = platform.system().lower()
                arch = platform.machine().lower()
                
                logger.info(f"Platform: {platform_name}, Architecture: {arch}")
                
                for asset in release_info.get('assets', []):
                    asset_name = asset['name'].lower()
                    
                    # Match platform-specific assets
                    if (platform_name == 'linux' and ('linux' in asset_name or 'ubuntu' in asset_name or 'debian' in asset_name)) or \
                       (platform_name == 'windows' and ('win' in asset_name or 'windows' in asset_name or '.exe' in asset_name)) or \
                       (platform_name == 'darwin' and ('mac' in asset_name or 'osx' in asset_name or 'darwin' in asset_name)):
                        
                        # Prefer x86_64 architecture if available
                        if 'x86_64' in asset_name or '64bit' in asset_name:
                            logger.info(f"Found platform-specific asset: {asset['name']}")
                            return asset
                        elif arch == 'x86_64' and ('amd64' in asset_name or 'x64' in asset_name):
                            logger.info(f"Found platform-specific asset: {asset['name']}")
                            return asset
            
            logger.warning("No matching platform asset found")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving platform asset: {e}")
            return None

    def download_update(self, version, asset=None):
        """Download update file from GitHub."""
        try:
            if not asset:
                asset = self.get_platform_asset(version)
                
            if not asset:
                logger.warning("No asset found for download")
                return None
                
            logger.info(f"Downloading update: {asset['browser_download_url']}")
            
            # Make download request
            response = requests.get(asset['browser_download_url'], timeout=60, stream=True)
            
            if response.status_code == 200:
                # Create temporary file
                temp_dir = tempfile.mkdtemp()
                file_path = os.path.join(temp_dir, asset['name'])
                
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            
                logger.info(f"Update downloaded successfully to {file_path}")
                return file_path
            else:
                logger.error(f"Error downloading update: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error downloading update: {e}")
            return None

    def install_update(self, update_file, target_dir=None):
        """Install update from downloaded file."""
        try:
            if not target_dir:
                target_dir = os.getcwd()
                
            logger.info(f"Installing update to {target_dir}")
            
            # Extract and install based on file type
            if update_file.endswith('.tar.gz') or update_file.endswith('.tgz'):
                with tarfile.open(update_file, 'r:gz') as tar:
                    tar.extractall(path=target_dir)
                    
            elif update_file.endswith('.zip'):
                with zipfile.ZipFile(update_file, 'r') as zip_ref:
                    zip_ref.extractall(path=target_dir)
                    
            else:
                logger.error("Unsupported file type for installation")
                return False
                
            logger.info("Update installed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error installing update: {e}")
            return False

    def check_and_update(self):
        """Main function to check and install updates."""
        # Check for updates
        update_info = self.check_for_updates()
        
        if not update_info["update_available"]:
            return update_info
            
        # If update available and auto-update is enabled, download and install automatically
        if self.auto_update:
            logger.info("Auto-update enabled, downloading and installing...")
            
            # Download update
            downloaded_file = self.download_update(update_info["latest_version"])
            
            if downloaded_file:
                success = self.install_update(downloaded_file)
                return {
                    "update_available": True,
                    "current_version": self.current_version,
                    "latest_version": update_info["latest_version"],
                    "installed": success,
                    "message": f"Update to {update_info['latest_version']} {'successful' if success else 'failed'}"
                }
            else:
                return {
                    "update_available": True,
                    "current_version": self.current_version,
                    "latest_version": update_info["latest_version"],
                    "installed": False,
                    "message": "Failed to download update"
                }
        else:
            # Return info for UI to show update availability
            return update_info

    def get_update_status(self):
        """Get current update status."""
        return self.check_for_updates()

# Additional functions for UI integration
def check_updates():
    """Function to be called from UI to check updates."""
    try:
        manager = UpdateManager()
        return manager.check_and_update()
    except Exception as e:
        logger.error(f"Error checking updates: {e}")
        return {
            "update_available": False,
            "current_version": "unknown",
            "latest_version": None,
            "message": f"Error checking updates: {str(e)}"
        }

def update_now():
    """Function to be called from UI to install updates."""
    try:
        manager = UpdateManager()
        # Force manual update
        manager.auto_update = True
        return manager.check_and_update()
    except Exception as e:
        logger.error(f"Error updating: {e}")
        return {
            "update_available": False,
            "current_version": "unknown",
            "latest_version": None,
            "message": f"Error during update: {str(e)}"
        }

if __name__ == "__main__":
    # Example usage
    print("Photo Editor 2 Update Manager")
    print("=" * 40)
    
    manager = UpdateManager()
    
    # Show current status
    status = manager.get_update_status()
    print(f"Current version: {status['current_version']}")
    print(f"Latest available: {status['latest_version']}")
    print(f"Update available: {status['update_available']}")
    
    if status['update_available']:
        print("Update is possible!")
    else:
        print("No need to update.")