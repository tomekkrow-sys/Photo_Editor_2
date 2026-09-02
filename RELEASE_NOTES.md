# Photo Editor 2 Update Manager Release

## Version 1.0.1

This release introduces a unified update manager that combines the functionality of both basic and advanced update managers with enhanced security features.

## Changes

- Implemented `UnifiedUpdateManager` class that consolidates functionality from both previous managers
- Added GPG signature verification for updates
- Enhanced integrity checks using hash validation
- Improved backup creation before updates
- Maintained full backward compatibility with existing `check_and_update()` function
- Added detailed logging and error handling

## New Features

1. **GPG Signature Verification**:
   - Updated releases can be verified with GPG signatures
   - Enhanced security for update distribution

2. **Enhanced Integrity Check**:
   - Added SHA256 hash verification for downloaded files
   - Ensures file integrity during download and installation

3. **Improved Backup System**:
   - Automatic backup creation before updates
   - Configurable backup settings in `updater_config.json`

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

This release enhances the security and reliability of Photo Editor 2's update system while maintaining existing functionality.