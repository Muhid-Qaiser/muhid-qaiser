#!/usr/bin/env python3
"""assets/shop-*.svg — the contact links, laid out as Sly's shelf.

A Hollow Knight shop row is an item icon in a bordered box, the item's name,
one line telling you what it does, and the cost on the far right. The cost
slot is the useful one here, so it holds the actual handle. Each row is
wrapped in a link in the README, so the whole shelf is clickable.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from theme import *

OUT = Path(__file__).resolve().parent.parent / "assets"
W, H = 1200, 122

WARES = [
    {"file": "linkedin", "name": "The Wanderer's Record", "icon": "tablet",
     "line": "Where the whole of it is written down — roles, dates, the long version.",
     "cost": "in/muhid-qaiser"},
    {"file": "medium", "name": "The Quill", "icon": "quill",
     "line": "Notes written up after the fact, on what broke and how.",
     "cost": "@muhid-qaiser"},
    {"file": "email", "name": "The Sealed Letter", "icon": "letter",
     "line": "The direct way. Carried by hand, answered the same.",
     "cost": "muhidqaiser02@gmail.com"},
]


def icon(kind, cx, cy):
    """Wares sit in a bordered box on the shelf, the way Sly displays them."""
    g = [f'<rect x="{cx-33}" y="{cy-33}" width="66" height="66" rx="6" '
         f'fill="#151D30"/>',
         f'<rect x="{cx-33}" y="{cy-33}" width="66" height="66" rx="6" fill="none" '
         f'stroke="{BONE}" stroke-width="1.3" opacity=".42" filter="url(#ink)"/>']
    s = lambda d, col="#CFD6E4", w=2, op=.9: (
        f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" '
        f'stroke-linecap="round" stroke-linejoin="round" opacity="{op}"/>')

    if kind == "tablet":            # a slab with a record cut into it
        g.append(s(f"M {cx-14} {cy-19} L {cx+14} {cy-19} L {cx+14} {cy+19} "
                   f"L {cx-14} {cy+19} Z", "#CFD6E4", 1.8, .85))
        for dy in (-9, -2, 5):
            g.append(s(f"M {cx-8} {cy+dy} L {cx+8} {cy+dy}", "#9AA6BC", 1.5, .75))
        g.append(s(f"M {cx-8} {cy+12} L {cx+2} {cy+12}", SOUL, 1.7, 1))
    elif kind == "quill":           # a feather, nib down
        g.append(s(f"M {cx+15} {cy-19} C {cx+2} {cy-14}, {cx-11} {cy+1}, "
                   f"{cx-15} {cy+18}", "#CFD6E4", 2, .9))
        g.append(s(f"M {cx+15} {cy-19} C {cx+11} {cy-4}, {cx+1} {cy+7}, "
                   f"{cx-15} {cy+18}", "#9AA6BC", 1.6, .7))
        g.append(f'<circle cx="{cx-15}" cy="{cy+18}" r="3" fill="{SOUL}" '
                 f'filter="url(#glowMed)"/>')
    else:                           # a folded letter, still sealed
        g.append(s(f"M {cx-18} {cy-13} L {cx+18} {cy-13} L {cx+18} {cy+13} "
                   f"L {cx-18} {cy+13} Z", "#CFD6E4", 1.8, .85))
        g.append(s(f"M {cx-18} {cy-13} L {cx} {cy+2} L {cx+18} {cy-13}",
                   "#9AA6BC", 1.5, .75))
        g.append(f'<circle cx="{cx}" cy="{cy+9}" r="4.5" fill="{SOUL}" '
                 f'filter="url(#glowMed)"/>')
    return "".join(g)


def geo(cx, cy):
    """The Geo mark, small, where the price would sit."""
    return (f'<path d="M {cx} {cy-6} L {cx+5} {cy} L {cx} {cy+6} L {cx-5} {cy} Z" '
            f'fill="none" stroke="{ASH}" stroke-width="1.4" opacity=".8"/>')


hdr = [head(1200, 118)]
hdr.append(section("Wares", "Three ways to reach me. Take whichever you need."))
hdr.append(tail())
(OUT / "shop-header.svg").write_text("\n".join(hdr), encoding="utf-8")
print("wrote shop-header.svg")

for w in WARES:
    svg = [head(W, H, lantern=False)]
    svg.append(f'<rect x="{MARGIN}" y="6" width="{1200 - MARGIN*2}" height="{H-12}" '
               f'rx="5" fill="{CAVERN}" fill-opacity=".5" stroke="{BONE}" '
               f'stroke-width="1.3" stroke-opacity=".22" filter="url(#ink)"/>')
    svg.append(icon(w["icon"], MARGIN + 56, H / 2))
    svg.append(caps(MARGIN + 116, 52, w["name"], size=16, track=3.8, glow=True))
    svg.append(prose(MARGIN + 116, 80, w["line"], size=14))
    # Right-anchored, so the Geo mark is placed off the measured text width.
    width = len(w["cost"]) * (12 * 0.68 + 2.2)
    svg.append(geo(1128 - width - 22, 58))
    svg.append(caps(1128, 63, w["cost"], size=12, track=2.2, fill=SOUL,
                    anchor="end", glow=True))
    svg.append(motes(MARGIN + 40, 20, 900, 80, n=6, seed=len(w["name"])))
    svg.append(tail())
    path = OUT / f"shop-{w['file']}.svg"
    path.write_text("\n".join(svg), encoding="utf-8")
    print(f"wrote {path.name}")
