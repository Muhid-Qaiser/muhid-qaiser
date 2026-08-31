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

# Traced from the line-art reference rather than estimated from it.
#
# Reading proportions off a row profile got me close twice and wrong twice, so
# this outline is the reference's own: every row of the drawing scanned for
# where its ink starts and ends, the boundary walked as one loop — down the
# outer left, round the bottom, up the outer right, then down into the notch
# and back — and simplified. It is a single closed path, which also settles
# the fill-rule holes that separate head and horn shapes used to punch.
#
# Box is 100 x 109.5 (h/w 1.10); the notch floor sits at y=44.6; the eyes are
# circles of r 9.45 at x 32.1 and 67.3, y 84, measured off the same drawing.
MASK = ("M 25.5 1 L 15 4.4 L 4.8 14.3 L 0.3 25.9 L 0.3 38.4 L 4.8 50.7 L 9.2 55.8 L 13.6 58.8 L 13.6 84.4 L 17.3 95.6 L 21.1 100.7 L 27.6 105.8 L 40.5 109.2 L 58.5 108.8 L 67.3 107.1 L 75.5 103.1 L 80.3 98.3 L 84 91.2 L 85.7 84 L 85.4 58.5 L 92.2 52.4 L 97.6 44.2 L 99.7 36.1 L 99.7 28.2 L 97.3 18.4 L 93.5 11.6 L 89.1 6.8 L 78.9 1.4 L 71.1 0 L 66.7 0.3 L 65 1.7 L 64.6 4.4 L 72.4 11.2 L 70.4 13.3 L 70.4 15.6 L 76.9 21.4 L 80.3 28.9 L 79.9 35 L 76.5 41.5 L 72.8 44.6 L 24.5 44.2 L 20.1 37.4 L 19 31.3 L 21.4 24.1 L 29.3 17.7 L 28.9 15 L 24.5 11.9 L 28.6 5.4 L 28.6 3.1 L 25.9 1 Z")

EYE_R, EYE_DX, EYE_CY = 9.45, 17.6, 84
EYE_CX = 49.7

# The failed seal, running the centre line between the eyes.
CRACK = "M 49 45 L 45 57 L 52 69 L 46 80 L 52 92 L 48 106"
BRANCH_A = "M 45 57 L 37 54"
BRANCH_B = "M 46 80 L 38 86"

DEFS = f"""
  <linearGradient id="shell" gradientUnits="userSpaceOnUse"
                  x1="12" y1="40" x2="76" y2="115">
    <stop offset="0%" stop-color="#FFFDF6"/>
    <stop offset="55%" stop-color="{BONE}"/>
    <stop offset="100%" stop-color="#B9BDC4"/>
  </linearGradient>"""

svg = [lantern(W, H)]
# A second light source behind the shell itself.
svg.append(lantern(W, H, cx=1020, cy=206, rx=340, ry=258))

svg.append('<g transform="translate(892,54) scale(2.68)">')
# Infection glowing through the shell. Blurred at this radius the mask's own
# outline is long gone, so the shape carrying the light may as well be the
# soft ellipse the blur was turning it into.
svg.append('  <ellipse cx="50" cy="58" rx="90" ry="96" fill="url(#sporeWarm)" opacity=".2"/>')
svg.append('  <g>')
# Horns first, so the head's edge sits over their bases and the join is clean.
svg.append(f'    <path d="{MASK}" fill="url(#shell)"/>')
# Eye voids. Nothing looks back out.
for sx in (-1, 1):
    svg.append(f'    <circle cx="{EYE_CX + sx*EYE_DX}" cy="{EYE_CY}" r="{EYE_R}" '
               f'fill="{VOID}"/>')
svg.append('  </g>')

# The breach: the dark cut first, then the light coming through it.
for path, w in ((CRACK, 0.7), (BRANCH_A, 0.45), (BRANCH_B, 0.45)):
    svg.append(f'  <path d="{path}" fill="none" stroke="#2A3040" stroke-width="{w}" '
               f'stroke-linecap="round" stroke-linejoin="round"/>')
svg.append('  <g style="mix-blend-mode:screen">')
for flt, width, op in (("glowWide", 7, .8), ("glowMed", 3.2, 1)):
    for path in (CRACK, BRANCH_A, BRANCH_B):
        svg.append(f'    <path d="{path}" fill="none" stroke="{INFECT}" '
                   f'stroke-width="{width}" stroke-linecap="round" '
                   f'stroke-linejoin="round" opacity="{op}" filter="url(#{flt})"/>')
svg.append('  </g>')
# Keep the bright fracture at the midpoint of its old pulse. Repainting the
# filtered breach continuously was expensive and the movement was too subtle
# to justify it beside the much clearer falling drops.
svg.append('  <g opacity=".78">')
for path, w in ((CRACK, 1.35), (BRANCH_A, 0.8), (BRANCH_B, 0.8)):
    svg.append(f'    <path d="{path}" fill="none" stroke="#FFD98A" stroke-width="{w}" '
               f'stroke-linecap="round" stroke-linejoin="round" '
               f'filter="url(#glow)"/>')
svg.append('  </g>')

svg.append('</g>')

# What got out. Amber is the profile's breach colour and this is the only
# place it is earned: the seal has failed, so the infection is leaving.
# Points sit on the fracture, low enough that a drop falls clear of the chin.
LEAK = [(49, 66), (46, 78), (51, 90), (47, 100), (49, 108)]
svg.append('<g transform="translate(892,54) scale(2.68)">')
for i, (lx, ly) in enumerate(LEAK):
    delay = -i * 1.45
    # One live drop communicates the failed seal; the other fracture points
    # stay as dim infection rather than independent animation timelines.
    motion = ('class="drip" opacity="0" '
              f'style="--fall:26px;animation-delay:{delay:.2f}s"'
              if i == 0 else 'opacity=".24"')
    svg.append(f'  <g {motion}>')
    svg.append(f'    <ellipse cx="{lx}" cy="{ly}" rx="2.1" ry="2.8" '
               f'fill="url(#sporeWarm)"/>')
    svg.append(f'    <ellipse cx="{lx}" cy="{ly}" rx="0.6" ry="0.95" '
               f'fill="#FFD98A"/>')
    svg.append('  </g>')
svg.append('</g>')

# Spores lifting out of the fracture.
svg.append(motes(996, 130, 80, 272, n=18, seed=11, fill=INFECT))

# ── Masthead lettering ────────────────────────────────────────────────────
svg.append(caps(MARGIN, 150, "Muhid Qaiser", size=64, track=9, glow=True))
svg.append(f'<path d="{wobble(MARGIN, 182, 660, 182, seed=7)}" fill="none" '
           f'stroke="{BONE}" stroke-width="1.4" opacity=".28"/>')

svg.append(prose(MARGIN, 222,
                 "AI Security  |  Computer Vision  |  Gen AI  |  Agentic AI",
                 size=24, fill=LUMEN, italic=False))

# The vessel's own inscription, typed out and repeated. It belongs under a
# cracked shell more than any line I could write.
svg.append(typeline(MARGIN, 332,
                    "No cost too great. No mind to think. "
                    "No will to break. No voice to cry suffering.",
                    size=26, cycle=15))

