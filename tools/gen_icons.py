#!/usr/bin/env python3
"""Generate PWA / Apple-touch-icon PNGs (on-brand: green tile, dark 'W').

Writes apple-touch-icon (180), icon-192, icon-512 into both preview/ and
frontend/public/. iOS rounds the corners, so we render full-bleed green.

Usage: python tools/gen_icons.py
Requires: Pillow. Font: Arial Bold (falls back to PIL default if missing).
"""
from __future__ import annotations
import os
from PIL import Image, ImageDraw, ImageFont

GREEN = (52, 211, 153, 255)   # --acc.personal
DARK = (7, 9, 16, 255)        # --ink-950
FONT_CANDIDATES = ["C:/Windows/Fonts/arialbd.ttf", "/Library/Fonts/Arial Bold.ttf",
                   "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
TARGETS = {"apple-touch-icon.png": 180, "icon-192.png": 192, "icon-512.png": 512}
FOLDERS = ["preview", "frontend/public"]


def _font(size: int):
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def make(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), GREEN)
    d = ImageDraw.Draw(img)
    f = _font(int(size * 0.62))
    try:
        b = d.textbbox((0, 0), "W", font=f); w, h, ox, oy = b[2] - b[0], b[3] - b[1], b[0], b[1]
    except Exception:
        w, h = d.textsize("W", font=f); ox = oy = 0
    d.text(((size - w) / 2 - ox, (size - h) / 2 - oy), "W", font=f, fill=DARK)
    return img


if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for folder in FOLDERS:
        out = os.path.join(root, folder)
        os.makedirs(out, exist_ok=True)
        for name, sz in TARGETS.items():
            make(sz).save(os.path.join(out, name))
            print("wrote", folder + "/" + name, sz)
