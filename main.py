#!/usr/bin/env python3
"""
Photo Editor 2 - Main Application with Update Manager
"""

import sys
import os
import subprocess
from pathlib import Path

# Add the current directory to Python path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from updater import check_and_update

def main():
    """
    Main application entry point
    """
    print("Starting Photo Editor 2...")
    
    # Check for updates before running the main application
    update_result = check_and_update()
    
    if update_result == "updated":
        print("Application updated successfully. Restarting...")
        # Restart the application
        subprocess.Popen([sys.executable, __file__])
        sys.exit(0)
    elif update_result == "error":
        print("Error checking for updates. Continuing with current version...")
    
    # Continue with normal application startup
    print("Running Photo Editor 2 with current version")
    # Here would go the actual application code
    # For now, we'll just simulate it
    try:
        # This is where the main application logic would be
        import photo_editor
        
        # Run the actual app
        photo_editor.main()
    except ImportError:
        print("Photo editor module not found. Running demo mode.")
        print("This is a demo version of Photo Editor 2")

if __name__ == "__main__":
    main()