# Photo Editor 2 Update Manager

Unified Update Manager for Photo Editor 2 application, handling version retrieval, checking, downloading, and installing updates from GitHub repositories.

## Features

- Fetch current version from `version.txt`
- Check for latest releases on GitHub
- Download updates for specific platforms
- Install updates automatically 
- Support for semantic versioning comparison
- Configurable via JSON configuration file
- Backup and rollback capabilities
- Background update checking support

## Configuration

The manager uses a JSON configuration file at `config/updater_config.json`:

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

## Usage

### Basic usage:
```python
from unified_updater import UpdateManager

# Create manager instance (loads configuration automatically)
updater = UpdateManager()

# Check and optionally update
status = updater.check_and_update()
print(f"Update status: {status}")

# Or check latest version only
latest_version = updater.get_latest_version()
print(f"Latest version: {latest_version}")
```

### Direct update:
```python
# Download and install latest update
updater.download_update(latest_version, platform_arch)
updater.install_update(downloaded_file, target_dir, latest_version)
```

## Supported Platforms

- Linux (x86_64, arm64)
- Windows (x86, x64)
- macOS (Intel, Apple Silicon)

## Version Comparison

The manager implements semantic versioning comparison that handles:
- Standard versions: 1.0.0, 2.1.3
- Pre-release versions: 1.0.0-alpha, 2.1.0-beta.2
- Build metadata suffixes

## Repository Structure

```
.
├── config/
│   └── updater_config.json     # Update configuration
├── unified_updater.py          # Main update manager
├── version.txt                 # Current application version
└── update_manager.log          # Update logs
```

## Requirements

- Python 3.7+
- requests library
- json module (built-in)

## Installation

Extract the archive `photo-editor-2-update-manager-complete.tar.gz` to get all necessary files:

```bash
tar -xzf photo-editor-2-update-manager-complete.tar.gz
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create feature branch 
3. Commit changes
4. Push to branch
5. Create pull request