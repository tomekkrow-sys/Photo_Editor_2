#!/usr/bin/env python3
"""Comprehensive test for update system version comparison (0.6.8 -> 0.6.9)."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unified_updater import UpdateManager

def test_update_transition():
    manager = UpdateManager()
    
    # Test transition from 0.6.9 to 0.7.0
    current = "0.6.9"
    latest = "0.7.0"
    
    newer = manager.is_version_newer(latest, current)
    print(f"Is latest '{latest}' newer than current '{current}'? {newer}")
    assert newer is True, "0.7.0 should be considered newer than 0.6.9"
    
    # Test reverse (current 0.6.9, latest 0.6.8)
    newer_rev = manager.is_version_newer(current, latest)
    print(f"Is current '{current}' newer than latest '{latest}'? {newer_rev}")
    assert newer_rev is False, "0.6.8 should NOT be considered newer than 0.6.9"
    
    # Test equal versions (0.6.8 vs 0.6.8)
    equal = manager.is_version_newer("0.6.8", "0.6.8")
    print(f"Is '0.6.8' newer than '0.6.8'? {equal}")
    assert equal is False, "Equal versions should return False for is_version_newer"

    print("All update system tests passed successfully!")

if __name__ == "__main__":
    test_update_transition()
