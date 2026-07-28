#!/usr/bin/env python3
"""Backward compatibility shim for core.image.image_loader."""

from __future__ import annotations

from core.image.image_loader import ImageLoader

# Expose class for old imports: from core.image_loader import ImageLoader
__all__ = ["ImageLoader", "load_image", "SUPPORTED_FORMATS", "can_load", "is_supported"]

# Function wrappers for old API
def load_image(file_path: str):
    """Backward compat: load image via ImageLoader."""
    return ImageLoader.load(file_path)

def can_load(file_path: str) -> bool:
    """Backward compat: check if file can be loaded."""
    return ImageLoader.can_load(file_path)

def is_supported(file_path: str) -> bool:
    """Backward compat: check if format is supported."""
    return ImageLoader.is_supported(file_path)

# Constants
SUPPORTED_FORMATS = ImageLoader.SUPPORTED_EXTENSIONS
