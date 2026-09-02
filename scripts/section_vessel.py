#!/usr/bin/env python3
"""The quiet masthead: one name, one role line, one broken shell."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from theme import *

W, H = 1200, 300
DEFS = ""

# A measured Knight shell silhouette. Keeping it as one path makes the mark
# crisp at every README width without introducing a raster asset.
MASK = (
    "M 25.5 1 L 15 4.4 L 4.8 14.3 L 0.3 25.9 L 0.3 38.4 "
    "L 4.8 50.7 L 9.2 55.8 L 13.6 58.8 L 13.6 84.4 L 17.3 95.6 "
    "L 21.1 100.7 L 27.6 105.8 L 40.5 109.2 L 58.5 108.8 "
    "L 67.3 107.1 L 75.5 103.1 L 80.3 98.3 L 84 91.2 L 85.7 84 "
    "L 85.4 58.5 L 92.2 52.4 L 97.6 44.2 L 99.7 36.1 L 99.7 28.2 "
    "L 97.3 18.4 L 93.5 11.6 L 89.1 6.8 L 78.9 1.4 L 71.1 0 "
    "L 66.7 0.3 L 65 1.7 L 64.6 4.4 L 72.4 11.2 L 70.4 13.3 "
    "L 70.4 15.6 L 76.9 21.4 L 80.3 28.9 L 79.9 35 L 76.5 41.5 "
    "L 72.8 44.6 L 24.5 44.2 L 20.1 37.4 L 19 31.3 L 21.4 24.1 "
    "L 29.3 17.7 L 28.9 15 L 24.5 11.9 L 28.6 5.4 L 28.6 3.1 Z"
)
CRACKS = (
    "M 49 45 L 45 57 L 52 69 L 46 80 L 52 92 L 48 106",
    "M 45 57 L 37 54",
    "M 46 80 L 38 86",
)

svg = []

# Title block. No glow, typing cursor or decorative particles: the game gets
# its authority from scale and empty space rather than constant motion.
svg.append(caps(72, 132, "Muhid Qaiser", size=62, track=7.2, fill=BONE))
svg.append(f'<path d="{wobble(72, 170, 724, 170, amp=.65, seed=7)}" '
           f'fill="none" stroke="{BONE}" stroke-width="1.2" opacity=".34"/>')
svg.append('<path d="M 390 164 l 7 6 -7 6 -7 -6 Z" fill="none" '
           f'stroke="{BONE}" stroke-width="1" opacity=".52"/>')
svg.append(prose(72, 218,
                 "AI Security  |  Computer Vision  |  Gen AI  |  Agentic AI",
                 size=23, fill=BONE, italic=False, opacity=.92))

# One shell, kept deliberately flat like the game's menu portraits.
svg.append('<g transform="translate(952,28) scale(1.62)">')
svg.append(f'<path d="{MASK}" fill="{BONE}"/>')
svg.append(f'<path d="{MASK}" fill="none" stroke="#AEB5BF" '
           'stroke-width="1.2" opacity=".55"/>')
for sx in (-1, 1):
    svg.append(f'<circle cx="{49.7 + sx * 17.6:.1f}" cy="84" r="9.45" '
               f'fill="{VOID}"/>')
for path in CRACKS:
    svg.append(f'<path d="{path}" fill="none" stroke="#454E5D" '
               'stroke-width="1" stroke-linecap="round" '
               'stroke-linejoin="round"/>')
svg.append('</g>')
