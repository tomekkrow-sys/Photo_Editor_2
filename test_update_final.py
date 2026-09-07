#!/usr/bin/env python3
"""
Test script for final unified updater
"""
import sys
import os

# Add the current directory to Python path so we can import the module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from unified_updater_final import UpdateManager
    
    print("Creating update manager...")
    updater = UpdateManager()
    
    print(f"Current version: {updater.current_version}")
    print(f"Base URL: {updater.base_url}")
    print(f"Repo path: {updater.full_repo_path}")
    
    # Get latest version
    print("Checking for latest version...")
    latest = updater.get_latest_version()
    print(f"Latest version: {latest}")
    
    # Check if update needed
    if latest:
        is_newer = updater.is_version_newer(latest, updater.current_version)
        print(f"Is newer? {is_newer}")
    
    print("Test completed successfully!")
    
except Exception as e:
    print(f"Error during test: {e}")
    import traceback
    traceback.print_exc()