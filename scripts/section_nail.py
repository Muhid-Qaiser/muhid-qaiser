#!/usr/bin/env python3
"""The nail section: turning points, not years.

Five forgings of the Nail, each a hand-picked turning point rather than a
date; the years live in the Ledger. Brightness steps up evenly at each
forging mark and so does the light the blade throws, so the Pure Nail is
the brightest thing above the fold. After it there is nothing left to
forge; growth from here is the Nail Arts.
"""
import math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from theme import *

W = 1200

NAIL_H = 430
STAGES = [
    ("Old Nail",        "foundation"),
    ("Sharpened",       "machine learning"),
    ("Channelled",      "computer vision"),
    ("Coiled",          "gen AI, agentic AI"),
    ("Pure Nail",       "AI security"),
]
# Each forging is a discrete step in brightness: the blade goes from dull
# iron at the grip to lit steel at the tip. Stops are doubled so the steps
# are hard edges, not a ramp: a forging is an event, not a drift.
STEPS = ["#3A4658", "#66748C", "#95A3BA", "#D4DBE6", "#FFFFFF"]
# and the light each segment throws grows with it, in the same steps
GLOW = [.08, .31, .54, .77, 1.0]
gstops = "".join(
    f'<stop offset="{i/5:.2f}" stop-color="{SOUL}" stop-opacity="{g}"/>'
    f'<stop offset="{(i+1)/5:.2f}" stop-color="{SOUL}" stop-opacity="{g}"/>'
    for i, g in enumerate(GLOW))
stops = "".join(
    f'<stop offset="{i/5:.2f}" stop-color="{c}"/><stop offset="{(i+1)/5:.2f}" stop-color="{c}"/>'
    for i, c in enumerate(STEPS))
NAIL_DEFS = ""

BX0, BX1, BY = 200, 1128, 262       # blade from guard to tip, centreline
SEG = (BX1 - 40 - BX0) / 5           # last 40px is the point itself
NAIL_DEFS = (f'<linearGradient id="forge" gradientUnits="userSpaceOnUse" '
             f'x1="{BX0}" y1="0" x2="{BX0+SEG*5}" y2="0">{stops}</linearGradient>'
             f'<linearGradient id="forgeGlow" gradientUnits="userSpaceOnUse" '
             f'x1="{BX0}" y1="0" x2="{BX0+SEG*5}" y2="0">{gstops}</linearGradient>')

def nail():
    out = []
    # grip and guard, in the same carved ink as everything else
    out.append(f'<rect x="118" y="{BY-6}" width="66" height="12" rx="3" fill="{STONE}" '
               f'stroke="{BONE}" stroke-width="1" opacity=".9"/>')
    out.append(f'<path d="M 184 {BY-24} L 200 {BY-8} L 200 {BY+8} L 184 {BY+24} L 178 {BY} Z" '
               f'fill="{CAVERN}" stroke="{BONE}" stroke-width="1.2" opacity=".95"/>')
    blade = (f'M {BX0} {BY-11} L {BX1-40} {BY-8} L {BX1} {BY} '
             f'L {BX1-40} {BY+8} L {BX0} {BY+11} Z')
    # light off the blade grows with each forging: the same blade shape, filled with a
    # stepped-opacity gradient and blurred once wide and once tight. Two filter passes.
    out.append(f'<path d="{blade}" fill="url(#forgeGlow)" opacity=".9" filter="url(#glowWideT)"/>')
    out.append(f'<path d="{blade}" fill="url(#forgeGlow)" opacity=".9" filter="url(#glowMedT)"/>')
    out.append(f'<path d="{blade}" fill="url(#forge)" stroke="{BONE}" stroke-width=".8" opacity=".95"/>')
    # fuller line down the blade
    out.append(f'<path d="M {BX0+8} {BY} L {BX0+SEG*4} {BY}" stroke="{VOID}" stroke-width="1" opacity=".22"/>')
    # forging marks: four, at the segment boundaries. Pale Ore went in here.
    for k in range(1, 5):
        x = BX0 + SEG * k
        out.append(f'<path d="M {x} {BY-17} L {x+5} {BY-11} L {x} {BY-5} L {x-5} {BY-11} Z" '
                   f'fill="{SOUL}" opacity=".9"/>')
        out.append(f'<path d="M {x} {BY-11} L {x} {BY+11}" stroke="{VOID}" stroke-width="1.2" opacity=".7"/>')
    # stage names above, turning points below. Past stages unlit; the current one lit.
    for i, (name, turn) in enumerate(STAGES):
        cx = BX0 + SEG * (i + .5)
        lit = i == len(STAGES) - 1
        out.append(caps(cx, BY - 46, name, size=15, track=2.2,
                        fill=LUMEN if lit else ASH, anchor="middle", glow=lit,
                        opacity=1 if lit else .85))
        out.append(prose(cx, BY + 52, turn, size=15, anchor="middle",
                         fill=SOUL if lit else ASH, opacity=.95 if lit else .8))
    return "".join(out)

nail_svg = [lantern(W, NAIL_H), section("The Nail"), nail(),
            footnote("Nothing left to forge. Now, the arts.", 400)]

H, svg, DEFS = NAIL_H, nail_svg, NAIL_DEFS
