#!/usr/bin/env python3
"""
Simple test to verify version comparison works correctly.
This simulates what would happen in check_and_update function.
"""

import os
import sys

# Add parent directory to path so we can import the module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the module that was modified
from unified_updater import UnifiedUpdateManager

# Create an instance of updater manager  
updater = UnifiedUpdateManager()

test_cases = [
    ("1.7", "1.7.0"),  # Should be equal (our main issue case) 
    ("1.0.0", "1.0.1"),  # Should detect newer version available
    ("1.0.1", "1.0.0"),  # Should detect older version
    ("1.7.0", "1.7"),    # Should be equal  
    ("2.10.5", "2.9.10"), # Should detect newer version 
]

print("Testing version comparison logic:")
print("=" * 50)

for current, latest in test_cases:
    is_newer = updater.is_version_newer(current, latest)
    print(f"Comparing '{current}' vs '{latest}':")
    print(f"  is_version_newer('{current}', '{latest}') = {is_newer}")
    
    # Test the check logic
    if is_newer: 
        result = "newer version exists (should not trigger update)"
    elif current == latest:
        result = "versions are equal"
    else:
        result = "older version (should trigger update)"
        
    print(f"  Result: {result}")
    print()