"""Tests for preset save/load roundtrip."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import core.preset_manager as preset_manager
from core.adjustments import Adjustments


class PresetManagerTests(unittest.TestCase):
    """Verify presets can be saved and loaded back."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self._original_dir = preset_manager.PRESETS_DIR
        preset_manager.PRESETS_DIR = Path(self.tmp.name)

    def tearDown(self) -> None:
        preset_manager.PRESETS_DIR = self._original_dir
        self.tmp.cleanup()

    def test_save_load_roundtrip(self) -> None:
        adj = Adjustments()
        adj.exposure = 1.5
        adj.contrast = -20.0
        adj.saturation = 30.0

        preset_manager.save_preset("moj", adj)
        loaded = preset_manager.load_preset("moj")

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.exposure, 1.5)
        self.assertEqual(loaded.contrast, -20.0)
        self.assertEqual(loaded.saturation, 30.0)
        self.assertEqual(loaded.tint, 0.0)

    def test_load_missing_returns_none(self) -> None:
        self.assertIsNone(preset_manager.load_preset("nie_ma"))

    def test_load_ignores_unknown_keys(self) -> None:
        preset_file = Path(self.tmp.name) / "stary.json"
        preset_file.write_text(
            '{"exposure": 2.0, "usunieta_opcja": 99}', encoding="utf-8"
        )

        loaded = preset_manager.load_preset("stary")

        self.assertEqual(loaded.exposure, 2.0)

    def test_list_presets(self) -> None:
        preset_manager.save_preset("b", Adjustments())
        preset_manager.save_preset("a", Adjustments())

        self.assertEqual(preset_manager.list_presets(), ["a", "b"])


if __name__ == "__main__":
    unittest.main()
