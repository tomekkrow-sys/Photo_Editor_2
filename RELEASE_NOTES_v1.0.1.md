# Photo Editor 2 v1.0.1 Release Notes

## What's New

- Added update manager functionality
- Implemented automatic check for new updates
- Added ability to download and install application updates
- Core application now supports self-update mechanism

## Changes

- Added `updater.py` module with update checking functionality
- Added `main.py` that integrates the update manager into the main flow  
- Created `version.txt` file to track current application version
- Updated project structure with new modules needed for updates

## Installation

The application can now automatically check for and install updates. Simply run the application normally and it will check for available updates on startup.

## Notes

This release introduces the core functionality for self-updating the application. Future releases will focus on improving the update experience and adding more features related to software distribution.