#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  UI Theme Engine — SovereignOS Dynamic Styling, Palettes & Adaptive Themes
#  File: ui_theme_engine.py
#===============================================================================

import time
import uuid
import json
import numpy as np
from typing import Dict, Any, Optional

class UIThemeEngine:
    """
    Provides:
      • dynamic theme generation
      • palette blending
      • adaptive contrast modeling
      • dark/light mode switching
      • kernel-driven UI styling
    """

    def __init__(self):
        self.themes: Dict[str, Dict[str, Any]] = {}
        self.active_theme: Optional[str] = None

    #---------------------------------------------------------------------------
    #  REGISTER THEME
    #---------------------------------------------------------------------------
    def register_theme(self, name: str, data: Dict[str, Any]):
        self.themes[name] = data
        if not self.active_theme:
            self.active_theme = name

    #---------------------------------------------------------------------------
    #  SET ACTIVE THEME
    #---------------------------------------------------------------------------
    def activate(self, name: str):
        if name in self.themes:
            self.active_theme = name

    #---------------------------------------------------------------------------
    #  GET ACTIVE THEME
    #---------------------------------------------------------------------------
    def get_active(self) -> Optional[Dict[str, Any]]:
        if not self.active_theme:
            return None
        return self.themes.get(self.active_theme)

    #---------------------------------------------------------------------------
    #  PALETTE BLENDING
    #---------------------------------------------------------------------------
    def _blend(self, c1: str, c2: str, t: float) -> str:
        def hex_to_rgb(h):
            h = h.lstrip("#")
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

        def rgb_to_hex(r, g, b):
            return "#{:02X}{:02X}{:02X}".format(r, g, b)

        r1, g1, b1 = hex_to_rgb(c1)
        r2, g2, b2 = hex_to_rgb(c2)

        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)

        return rgb_to_hex(r, g, b)

    #---------------------------------------------------------------------------
    #  ADAPTIVE CONTRAST
    #---------------------------------------------------------------------------
    def _contrast(self, color: str) -> str:
        h = color.lstrip("#")
        r, g, b = [int(h[i:i+2], 16) for i in (0, 2, 4)]
        luminance = (0.299*r + 0.587*g + 0.114*b) / 255
        return "#000000" if luminance > 0.5 else "#FFFFFF"

    #---------------------------------------------------------------------------
    #  GENERATE VARIANT
    #---------------------------------------------------------------------------
    def variant(self, base: str, intensity: float = 0.5) -> Dict[str, str]:
        if base not in self.themes:
            return {}

        theme = self.themes[base]
        primary = theme.get("primary", "#000000")
        secondary = theme.get("secondary", "#FFFFFF")

        t = max(0.0, min(1.0, intensity + np.random.normal(0, 0.05)))

        blended = self._blend(primary, secondary, t)

        return {
            "primary": blended,
            "secondary": self._contrast(blended),
            "accent": self._blend(blended, "#FF4081", 0.25),
            "background": self._blend(blended, "#FFFFFF", 0.85)
        }

    #---------------------------------------------------------------------------
    #  EXPORT ACTIVE THEME
    #---------------------------------------------------------------------------
    def export(self) -> Dict[str, Any]:
        theme = self.get_active()
        if not theme:
            return {}

        return {
            "theme_id": f"THM-{uuid.uuid4().hex[:10].upper()}",
            "timestamp": time.time(),
            "theme": json.dumps(theme)
        }

#===============================================================================
#  END OF FILE — ui_theme_engine.py
#===============================================================================
