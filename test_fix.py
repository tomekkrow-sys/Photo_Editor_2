#!/usr/bin/env python3

# Simple test to verify our version comparison fix
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unified_updater import UpdateManager

def test_version_comparison():
    manager = UpdateManager()
    
    # Test the specific cases mentioned in the issue
    result1 = manager.is_version_newer("1.7", "1.7.0")
    result2 = manager.is_version_newer("1.7.0", "1.7")
    
    print(f"is_version_newer('1.7', '1.7.0') = {result1}")
    print(f"is_version_newer('1.7.0', '1.7') = {result2}")
    
    # Test other cases to make sure we didn't break anything
    result3 = manager.is_version_newer("1.8", "1.7")
    result4 = manager.is_version_newer("1.7", "1.8")
    result5 = manager.is_version_newer("2.0.0", "1.9.9")
    
    print(f"is_version_newer('1.8', '1.7') = {result3}")
    print(f"is_version_newer('1.7', '1.8') = {result4}")
    print(f"is_version_newer('2.0.0', '1.9.9') = {result5}")
    
    # Test pre-release versions
    result6 = manager.is_version_newer("1.7.0-alpha", "1.7.0")
    result7 = manager.is_version_newer("1.7.0", "1.7.0-alpha")
    
    print(f"is_version_newer('1.7.0-alpha', '1.7.0') = {result6}")
    print(f"is_version_newer('1.7.0', '1.7.0-alpha') = {result7}")

if __name__ == "__main__":
    test_version_comparison()