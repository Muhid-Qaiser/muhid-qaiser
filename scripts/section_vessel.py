#!/usr/bin/env python3
"""The masthead section — the vessel, and the name.

A vessel is a shell built to hold something that must not get out. The seal on
this one has failed and the light inside is escaping. That is the whole job
description, so it is the whole picture.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from theme import *

W, H = 1200, 420

# Redrawn from the game's The_Knight_Front sprite rather than from memory.
# Measured off it: the head is a rounded rectangle wider than it is tall
# (47x38, aspect 1.24) — not the tapering oval this used to be — the horns
# span 1.45x the head's width and take the top half of the silhouette, and the
# eyes are large circles at ±0.65 of the head's half-width, 0.71 of the way
# down, each 0.35 of the head's width.
#
# Local box is 290 x 318, head centred on x=145.
HEAD = (
    "M 45 212 "
    "C 45 176, 63 155, 103 153 L 187 153 C 227 155, 245 176, 245 212 "
    "C 245 256, 238 300, 216 326 C 200 341, 176 347, 145 347 "
    "C 114 347, 90 341, 74 326 C 52 300, 45 256, 45 212 Z"
)
# Two crescents: out and up from the head's shoulders, tips curling back in.
HORN_L = ("M 68 178 C 38 152, 8 120, 6 82 C 5 56, 17 42, 31 52 "
          "C 41 96, 75 136, 110 154 Z")
HORN_R = ("M 222 178 C 252 152, 282 120, 284 82 C 285 56, 273 42, 259 52 "
          "C 249 96, 215 136, 180 154 Z")
MASK = HEAD + " " + HORN_L + " " + HORN_R

EYE_R, EYE_DX, EYE_CY = 32, 60, 262

# The failed seal, running the centre line between the eyes.
CRACK = "M 145 155 L 137 188 L 152 220 L 139 254 L 151 290 L 145 332"
BRANCH_A = "M 137 188 L 116 180"
BRANCH_B = "M 139 250 L 120 262"

DEFS = f"""
  <linearGradient id="shell" gradientUnits="userSpaceOnUse"
                  x1="40" y1="0" x2="210" y2="318">
    <stop offset="0%" stop-color="#FFFDF6"/>
    <stop offset="55%" stop-color="{BONE}"/>
    <stop offset="100%" stop-color="#B9BDC4"/>
  </linearGradient>"""

svg = [lantern(W, H)]
# A second light source behind the shell itself.
svg.append(lantern(W, H, cx=978, cy=200, rx=330, ry=250))

svg.append('<g transform="translate(862,6) scale(1.06)">')
svg.append(f'  <path d="{MASK}" fill="{INFECT}" opacity=".16" filter="url(#glowWide)"/>')
svg.append('  <g filter="url(#inkSoft)">')
# Horns first, so the head's edge sits over their bases and the join is clean.
for piece in (HORN_L, HORN_R, HEAD):
    svg.append(f'    <path d="{piece}" fill="url(#shell)"/>')
# Eye voids. Nothing looks back out.
for sx in (-1, 1):
    svg.append(f'    <circle cx="{145 + sx*EYE_DX}" cy="{EYE_CY}" r="{EYE_R}" '
               f'fill="{VOID}"/>')
svg.append('  </g>')

# The breach: the dark cut first, then the light coming through it.
for path, w in ((CRACK, 3.4), (BRANCH_A, 2.2), (BRANCH_B, 2.2)):
    svg.append(f'  <path d="{path}" fill="none" stroke="#2A3040" stroke-width="{w}" '
               f'stroke-linecap="round" stroke-linejoin="round"/>')
svg.append('  <g style="mix-blend-mode:screen">')
for flt, width, op in (("glowWide", 16, .75), ("glowMed", 7, .95)):
    for path in (CRACK, BRANCH_A, BRANCH_B):
        svg.append(f'    <path d="{path}" fill="none" stroke="{INFECT}" '
                   f'stroke-width="{width}" stroke-linecap="round" '
                   f'stroke-linejoin="round" opacity="{op}" filter="url(#{flt})"/>')
svg.append('  </g>')
for path, w in ((CRACK, 2.8), (BRANCH_A, 1.6), (BRANCH_B, 1.6)):
    svg.append(f'  <path d="{path}" fill="none" stroke="#FFD98A" stroke-width="{w}" '
               f'stroke-linecap="round" stroke-linejoin="round" '
               f'filter="url(#glow)" class="breathe"/>')

svg.append('</g>')

# What got out. Amber is the profile's breach colour and this is the only
# place it is earned: the seal has failed, so the infection is leaving.
# Points sit on the fracture, low enough that a drop falls clear of the chin.
LEAK = [(146, 206), (140, 244), (150, 278), (143, 310), (146, 336)]
svg.append('<g transform="translate(862,6) scale(1.06)">')
for i, (lx, ly) in enumerate(LEAK):
    delay = -i * 1.45
    svg.append(f'  <ellipse class="drip" cx="{lx}" cy="{ly}" rx="3.1" ry="4.3" '
               f'fill="{INFECT}" filter="url(#glowMed)" opacity="0" '
               f'style="animation-delay:{delay:.2f}s"/>')
    svg.append(f'  <ellipse class="drip" cx="{lx}" cy="{ly}" rx="1.7" ry="2.6" '
               f'fill="#FFD98A" opacity="0" '
               f'style="animation-delay:{delay:.2f}s"/>')
svg.append('</g>')

# Spores lifting out of the fracture.
svg.append(motes(996, 130, 80, 272, n=18, seed=11, fill=INFECT))

# ── Masthead lettering ────────────────────────────────────────────────────
svg.append(caps(MARGIN, 158, "Muhid Qaiser", size=46, track=9, glow=True))
svg.append(f'<path d="M {MARGIN} 182 L 536 182" stroke="{BONE}" stroke-width="1.4" '
           f'opacity=".28" filter="url(#ink)"/>')

svg.append(prose(MARGIN, 221,
                 "AI Security Engineer. I red-team large language models "
                 "and the agents built on them.",
                 size=19, fill=BONE, italic=False))
svg.append(prose(MARGIN, 253,
                 "Before this, computer vision — where adversarial examples "
                 "were first found.", size=17))
svg.append(prose(MARGIN, 279,
                 "The method did not change when the input became language.", size=17))

svg.append(f'<path d="M {MARGIN + 1} 315 L {MARGIN + 1} 351" stroke="{SOUL}" '
           f'stroke-width="2" opacity=".75" filter="url(#bloomSoft)"/>')
svg.append(caps(MARGIN + 20, 330, "A vessel is only as good as its seal",
                size=13.5, track=3, fill=SOUL, glow=True))
svg.append(prose(MARGIN + 20, 353, "Islamabad, Pakistan", size=15))
