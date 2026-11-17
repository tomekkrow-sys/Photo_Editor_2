#!/usr/bin/env python3
from __future__ import annotations
import json
from core.adjustments import Adjustments
from core.paths import user_data_dir

# Katalog użytkownika (zapisywalny) — nie katalog instalacji (/opt).
PRESETS_DIR = user_data_dir() / "presets"
PRESETS_DIR.mkdir(parents=True, exist_ok=True)

def save_preset(name, adj):
    PRESETS_DIR.mkdir(parents=True, exist_ok=True)
    with open(PRESETS_DIR / f"{name}.json", "w", encoding="utf-8") as f:
        json.dump(adj.to_dict(), f, indent=2)

def load_preset(name):
    p = PRESETS_DIR / f"{name}.json"
    if not p.exists():
        return None
    with open(p, "r", encoding="utf-8") as f:
        return Adjustments.from_dict(json.load(f))

def delete_preset(name) -> bool:
    p = PRESETS_DIR / f"{name}.json"
    if not p.exists():
        return False
    p.unlink()
    return True

def list_presets():
    return sorted([p.stem for p in PRESETS_DIR.glob("*.json")])
