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

        if settings.gamma != 0:
            gamma = 2.0 ** (settings.gamma / 100.0)

            rgb = (
                np.power(
                    np.clip(
                        rgb / 255.0,
                        0.0,
                        1.0,
                    ),
                    1.0 / gamma,
                )
                * 255.0
            )

        if settings.highlights != 0:
            amount = settings.highlights / 100.0

            luminance = (
                rgb[:, :, 0] * 0.2126
                + rgb[:, :, 1] * 0.7152
                + rgb[:, :, 2] * 0.0722
            )

            mask = (luminance > 128.0).astype(np.float32)

            factor = 1.0 - amount * (
                (luminance - 128.0) / 127.0
            )

            factor = np.clip(
                factor,
                0.2,
                5.0,
            )

            rgb *= (
                1.0
                + (factor - 1.0)[:, :, np.newaxis] * mask[:, :, np.newaxis]
            )

        if settings.shadows != 0:
            amount = settings.shadows / 100.0

            luminance = (
                rgb[:, :, 0] * 0.2126
                + rgb[:, :, 1] * 0.7152
                + rgb[:, :, 2] * 0.0722
            )

            mask = np.clip(
                (128.0 - luminance) / 128.0,
                0.0,
                1.0,
            )

            rgb += (
                amount
                * 80.0
                * mask[:, :, np.newaxis]
            )

        if settings.whites != 0:
            amount = settings.whites / 100.0

            luminance = (
                rgb[:, :, 0] * 0.2126
                + rgb[:, :, 1] * 0.7152
                + rgb[:, :, 2] * 0.0722
            )

            mask = np.clip(
                (luminance - 192.0) / 63.0,
                0.0,
                1.0,
            )

            rgb += (
                amount
                * 80.0
                * mask[:, :, np.newaxis]
            )


        if settings.blacks != 0:
            amount = settings.blacks / 100.0

            luminance = (
                rgb[:, :, 0] * 0.2126
                + rgb[:, :, 1] * 0.7152
                + rgb[:, :, 2] * 0.0722
            )

            mask = np.clip(
                (64.0 - luminance) / 64.0,
                0.0,
                1.0,
            )

            rgb -= (
                amount
                * 80.0
                * mask[:, :, np.newaxis]
            )

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
