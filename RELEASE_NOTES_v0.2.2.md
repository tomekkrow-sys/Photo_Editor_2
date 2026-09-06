# Photo Editor 2 - Update Manager Release

## Version 0.2.2

This release includes several bug fixes and performance improvements to the update manager system.

## Changes

- Fixed memory leak in the update verification process
- Improved error handling for network timeouts during downloads
- Optimized backup creation process to reduce execution time
- Enhanced logging for debugging update failures
- Added validation for update file integrity before installation
- Fixed issue with automatic updates not working when system time is incorrect

## New Features

1. **Enhanced Error Handling**:
   - More descriptive error messages for failed updates
   - Better handling of network connectivity issues
   - Improved user feedback during update processes

2. **Performance Improvements**:
   - Optimized backup creation algorithm
   - Reduced memory consumption during update verification
   - Faster file integrity checks

## Backward Compatibility

This update maintains strict backward compatibility with existing code:
- The `check_and_update()` function works exactly as before
- No changes required for existing Photo Editor 2 applications
- All existing workflows remain functional

## Installation

The update manager is included in the main application and runs automatically at startup.

To manually check for updates, run:

```python
from updater import check_and_update
result = check_and_update()
```

## Configuration

Update settings can be modified via `config/updater_config.json`:

```json
{
    "github": {
        "api_url": "https://api.github.com",
        "owner": "tomekkrow-sys",
        "repo": "Photo_Editor_2"
    },
    "update": {
        "check_interval_hours": 24,
        "backup_enabled": true,
        "auto_update": false,
        "background_updates": true
    }
}
```

## Requirements

- Python 3.6+
- PySide6>=6.5.0
- Pillow>=10.0.0
- rawpy>=0.18.0
- opencv-python-headless>=4.8.0
- gnupg>=0.5.0 (new requirement for this release)

This release improves the stability and reliability of Photo Editor 2's update system while maintaining existing functionality.