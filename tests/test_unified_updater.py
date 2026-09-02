#!/usr/bin/env python3
"""
Test suite for the Unified Update Manager
"""

import unittest
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

# Add the project root to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

from unified_updater import UnifiedUpdateManager


class TestUnifiedUpdateManager(unittest.TestCase):
    """Test cases for UnifiedUpdateManager"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.old_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create version.txt file for testing
        with open("version.txt", "w") as f:
            f.write("1.0.0")
        
        # Create a mock config file
        config_content = '''
{
    "github": {
        "owner": "tomekkrow-sys",
        "repo": "Photo_Editor_2",
        "api_url": "https://api.github.com"
    },
    "update_check_interval": 1800,
    "auto_update": true,
    "background_updates": true
}
'''
        with open("config/updater_config.json", "w") as f:
            f.write(config_content)
        
        # Initialize the updater manager for testing
        self.updater = UnifiedUpdateManager()
    
    def tearDown(self):
        """Clean up after each test method."""
        os.chdir(self.old_cwd)
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_get_current_version(self):
        """Test getting current version from version.txt"""
        version = self.updater.get_current_version()
        self.assertEqual(version, "1.0.0")
    
    def test_get_current_version_file_missing(self):
        """Test getting version when version.txt is missing"""
        # Remove the version.txt file
        os.remove("version.txt")
        version = self.updater.get_current_version()
        self.assertEqual(version, "0.0.0")
    
    def test_version_comparison_newer(self):
        """Test version comparison - newer version"""
        result = self.updater.is_version_newer("1.0.0", "1.0.1")
        self.assertTrue(result)
    
    def test_version_comparison_older(self):
        """Test version comparison - older version"""
        result = self.updater.is_version_newer("1.0.1", "1.0.0")
        self.assertFalse(result)
    
    def test_version_comparison_equal(self):
        """Test version comparison - equal versions"""
        result = self.updater.is_version_newer("1.0.0", "1.0.0")
        self.assertFalse(result)
    
    def test_version_comparison_complex(self):
        """Test version comparison with complex version numbers"""
        result = self.updater.is_version_newer("2.10.5", "2.9.10")
        self.assertTrue(result)  # 2.10.5 > 2.9.10
    
    @patch('requests.get')
    def test_get_latest_version_success(self, mock_get):
        """Test getting latest version successfully"""
        # Mock response for GitHub API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tag_name": "v1.0.1",
            "name": "Photo Editor 2 v1.0.1"
        }
        mock_get.return_value = mock_response
        
        version = self.updater.get_latest_version()
        self.assertEqual(version, "1.0.1")
    
    @patch('requests.get')
    def test_get_latest_version_failure(self, mock_get):
        """Test getting latest version when API fails"""
        # Mock response for GitHub API - error
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        version = self.updater.get_latest_version()
        self.assertIsNone(version)
    
    def test_config_loading(self):
        """Test that configuration is loaded properly"""
        self.assertEqual(self.updater.config["github"]["owner"], "tomekkrow-sys")
        self.assertEqual(self.updater.config["update_check_interval"], 1800)
        self.assertTrue(self.updater.config["auto_update"])
    
    def test_platform_detection(self):
        """Test platform detection logic"""
        platform_name, arch = self.updater._get_platform_info()
        # Just make sure it returns something reasonable
        self.assertIn(platform_name, ["linux", "windows", "macos"])
        self.assertIn(arch, ["x64", "arm64", "unknown"])
    
    def test_calculate_checksum(self):
        """Test checksum calculation"""
        # Create a test file
        with open("test_file.txt", "w") as f:
            f.write("This is a test file for checksum calculation.")
        
        checksum = self.updater._calculate_checksum("test_file.txt")
        self.assertIsNotNone(checksum)
        self.assertIsInstance(checksum, str)
        self.assertTrue(len(checksum) > 0)
    
    @patch('unified_updater.os.path.exists')
    @patch('unified_updater.shutil.copy2')
    def test_create_backup_success(self, mock_copy, mock_exists):
        """Test creating backup successfully"""
        mock_exists.return_value = True
        backup_dir = self.updater._create_backup("test_backup")
        
        # Ensure we get a backup directory path
        self.assertIsNotNone(backup_dir)
    
    @patch('unified_updater.os.path.exists')
    @patch('unified_updater.shutil.copy2')  
    def test_create_backup_failure(self, mock_copy, mock_exists):
        """Test creating backup when it fails"""
        mock_exists.return_value = False
        mock_copy.side_effect = Exception("Copy error")
        
        backup_dir = self.updater._create_backup("test_backup")
        # Method should return None on failure
        self.assertIsNone(backup_dir)
    
    def test_check_for_update(self):
        """Test checking for updates and getting update info"""
        # Set up mock responses using the same approach as in the main class  
        def mock_get_side_effect(url, timeout=None):
            # Mock GitHub API call to return latest version
            response = MagicMock()
            if url.endswith('releases/latest'):
                response.status_code = 200
                response.json.return_value = {
                    "tag_name": "v1.0.1",
                    "name": "Photo Editor 2 v1.0.1"
                }
            elif url.endswith('releases/tags/v1.0.1'):
                response.status_code = 200
                response.json.return_value = {
                    "assets": []
                }
            else:
                response.status_code = 404
            return response
            
        with patch('requests.get', side_effect=mock_get_side_effect):
            info = self.updater.check_for_update()
            
            # Verify the information returned
            self.assertEqual(info["current_version"], "1.0.0")
            self.assertEqual(info["latest_version"], "1.0.1")
            self.assertTrue(info["update_available"])
            self.assertFalse(info["is_up_to_date"])
            self.assertFalse(info["is_newer"])


if __name__ == '__main__':
    unittest.main()