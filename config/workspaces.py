#!/usr/bin/env python3
"""
Application workspaces.
"""

from enum import Enum


class Workspace(Enum):
    LIBRARY = "library"
    DEVELOP = "develop"
    EXPORT = "export"
