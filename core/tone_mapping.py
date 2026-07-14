#!/usr/bin/env python3
"""Tone mapping operations for Photo Editor."""

from __future__ import annotations

import numpy as np


class ToneMapping:
    """Tone mapping operations.

    Wszystkie operacje związane ze światłem trafiają tutaj:
    - Exposure
    - Gamma
    - Highlights
    - Shadows
    - Whites
    - Blacks
    """

    @staticmethod
    def apply(
        rgb: np.ndarray,
        settings,
    ) -> np.ndarray:
        """Apply all tone adjustments."""

        if settings.exposure != 0:
            factor = 2.0 ** (settings.exposure / 100.0)

            rgb = (
                255.0
                * (
                    1.0
                    - np.power(
                        1.0 - rgb / 255.0,
                        factor,
                    )
                )
            )

        return rgb
