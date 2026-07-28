#!/usr/bin/env python3
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Adjustments:
    exposure:    float = 0.0
    contrast:    float = 0.0
    highlights:  float = 0.0
    shadows:     float = 0.0
    whites:      float = 0.0
    blacks:      float = 0.0
    temperature: float = 0.0
    tint:        float = 0.0
    saturation:  float = 0.0
    vibrance:    float = 0.0
    sharpness:   float = 0.0
    clarity:     float = 0.0

    def copy(self):
        return Adjustments(**self.to_dict())

    def to_dict(self):
        return {
            "exposure": self.exposure, "contrast": self.contrast,
            "highlights": self.highlights, "shadows": self.shadows,
            "whites": self.whites, "blacks": self.blacks,
            "temperature": self.temperature, "tint": self.tint,
            "saturation": self.saturation, "vibrance": self.vibrance,
            "sharpness": self.sharpness, "clarity": self.clarity,
        }

    def reset(self):
        self.exposure = self.contrast = self.highlights = self.shadows = 0.0
        self.whites = self.blacks = self.temperature = self.tint = 0.0
        self.saturation = self.vibrance = self.sharpness = self.clarity = 0.0
