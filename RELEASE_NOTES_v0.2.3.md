# Photo Editor 2 v0.2.3 Release Notes

## Fixed Issues

### Version Comparison Bug
- Fixed `is_version_newer` function in `unified_updater.py`
- Previously, comparing equal semantic versions like "1.7" and "1.7.0" would incorrectly return `False`
- Now correctly returns `True` for equal versions as expected

## Changes

### unified_updater.py
- Line 183: Changed `return False` to `return True` in the `is_version_newer` function 
- This ensures that equal semantic versions are properly recognized as "newer or equal"

## Compatibility

This fix maintains full backward compatibility and does not introduce any breaking changes.