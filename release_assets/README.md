# Photo Editor 2 v2.0.1 Release Assets

This directory contains all the necessary files for the Photo Editor 2 v2.0.1 release.

## Files included:

1. `photo-editor-2-linux-x86_64.tar.gz` - Linux 64-bit package
2. `photo-editor-2-windows-x64.zip` - Windows 64-bit package  
3. `photo-editor-2-macOS-x64.zip` - macOS 64-bit package
4. `version.txt` - Current version file (v2.0.1)
5. `update_manager_with_ui.py` - Updated manager with UI integration
6. `config/updater_config.json` - Configuration file for update manager

## Instructions for creating GitHub Release:

1. Create new release at: https://github.com/tomekkrow-sys/Photo_Editor_2/releases/new
2. Set Tag version to: `v2.0.1`
3. Release title: `Photo Editor 2 v2.0.1`
4. Add description:
   ```
   Photo Editor 2 v2.0.1 - Integrated Update Manager
   
   Features:
   - Added "Check for Updates" functionality
   - Added "Update Now" menu option
   - Fixed all previous update manager bugs
   - Improved version comparison logic
   - Platform-specific asset downloading
   ```
5. Upload the following files as assets:
   - `photo-editor-2-linux-x86_64.tar.gz`
   - `photo-editor-2-windows-x64.zip` 
   - `photo-editor-2-macOS-x64.zip`

## How to verify update manager works:

```bash
python3 update_manager_with_ui.py
```

This should show:
- Current version: 2.0.1
- Latest available: 2.0.1 (no updates)
- Update available: False

To test actual update functionality, set:
```python
from update_manager_with_ui import check_updates
result = check_updates()
print(result)
```