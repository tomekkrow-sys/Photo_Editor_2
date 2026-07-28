#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from core.adjustments import Adjustments

PRESETS_DIR = Path(__file__).resolve().parent.parent / "presets"
PRESETS_DIR.mkdir(exist_ok=True)

def save_preset(name, adj):
    with open(PRESETS_DIR / f"{name}.json", "w", encoding="utf-8") as f:
        json.dump(adj.to_dict(), f, indent=2)

def load_preset(name):
    p = PRESETS_DIR / f"{name}.json"
    if not p.exists():
        return None
    with open(p, "r", encoding="utf-8") as f:
        return Adjustments.from_dict(json.load(f))

def list_presets():
    return sorted([p.stem for p in PRESETS_DIR.glob("*.json")])
