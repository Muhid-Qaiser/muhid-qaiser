#!/usr/bin/env python3
"""assets/journal.svg — the Hunter's Journal.

A red-team log and a bestiary are the same document: a record of things you
have fought, what they do, and where they get in. Each entry names the
boundary it crosses, because that is the only part that matters.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from theme import *

W = 1200
OUT = Path(__file__).resolve().parent.parent / "assets" / "journal.svg"

ENTRIES = [
    {
        "name": "The Injected Instruction",
        "boundary": "instruction",
        "lines": [
            "Hides in text the model was only asked to read. It speaks in the "
            "operator's voice, and is believed.",
            "Nothing is forced open. The shell is asked politely, and it obliges.",
        ],
        "sigil": "inject",
    },
    {
        "name": "The Borrowed Hand",
        "boundary": "action",
        "lines": [
            "Waits for a model that can act rather than only answer. It never "
            "argues with the guard.",
            "It waits for the guard to reach for a tool, and then guides the hand.",
        ],
        "sigil": "hand",
    },
    {
        "name": "The Poisoned Pixel",
        "boundary": "perception",
        "lines": [
            "Eldest of the three. A change too small for any eye, and the "
            "classifier names the wrong thing —",
            "more certain than it was before. Everything I hunt now is a "
            "variation on it.",
        ],
        "sigil": "pixel",
    },
]


def sigil(kind, cx, cy):
    """An inked mark per entry. Exactly one stroke in each is amber: the way in."""
    g = [f'<circle cx="{cx}" cy="{cy}" r="46" fill="#151D30"/>',
         f'<circle cx="{cx}" cy="{cy}" r="46" fill="none" stroke="{BONE}" '
         f'stroke-width="1.4" opacity=".45" filter="url(#ink)"/>']
    b = lambda d, col=BONE, w=2.6, op=.95: (
        f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" '
        f'stroke-linecap="round" opacity="{op}"/>')

    if kind == "inject":
        # Lines of text the model was told to read. One of them gives an order.
        for i, dy in enumerate((-16, 0, 16)):
            if i == 1:
                continue
            g.append(b(f"M {cx-21} {cy+dy} L {cx+15} {cy+dy}", "#B4BDCE", 2.6, .85))
        g.append(b(f"M {cx-25} {cy} L {cx+27} {cy}", INFECT, 3.6, 1))
        g.append(f'<circle cx="{cx+27}" cy="{cy}" r="4.2" fill="{INFECT}" '
                 f'filter="url(#glowMed)"/>')
    elif kind == "hand":
        # A nail, and the amber curve that turns it.
        g.append(b(f"M {cx-6} {cy-28} L {cx-6} {cy+14}", BONE, 4, .95))
        g.append(b(f"M {cx-18} {cy+14} L {cx+6} {cy+14}", BONE, 3, .9))
        g.append(b(f"M {cx-6} {cy+14} L {cx-6} {cy+27}", "#B4BDCE", 2.4, .8))
        g.append(b(f"M {cx+24} {cy+16} C {cx+28} {cy-8}, {cx+14} {cy-26}, "
                   f"{cx+2} {cy-27}", INFECT, 3, 1))
        g.append(b(f"M {cx+2} {cy-27} L {cx+12} {cy-31} M {cx+2} {cy-27} "
                   f"L {cx+10} {cy-19}", INFECT, 2.6, 1))
    else:
        # A grid, with one cell moved. That is the whole attack.
        for r in range(4):
            for c in range(4):
                if (r, c) == (2, 1):
                    continue
                g.append(f'<rect x="{cx-24+c*13}" y="{cy-24+r*13}" width="8" '
                         f'height="8" fill="#B4BDCE" opacity=".72"/>')
        g.append(f'<rect x="{cx-24+1*13+4}" y="{cy-24+2*13-3}" width="10" height="10" '
                 f'fill="{INFECT}" filter="url(#glowMed)"/>')
    return "".join(g)


TOP, STEP = 150, 152
H = TOP + STEP * len(ENTRIES) + 34

svg = [head(W, H)]
svg.append('<ellipse cx="600" cy="300" rx="640" ry="380" fill="url(#lantern)" '
           'opacity=".55"/>')

svg.append(caps(72, 66, "The Hunter's Journal", size=23, track=6.5))
svg.append(prose(72, 96, "Three things I hunt. Each one crosses a boundary "
                         "somebody believed was closed."))
svg.append(f'<path d="M 72 118 L 1128 118" stroke="{BONE}" stroke-width="1.2" '
           f'opacity=".2" filter="url(#ink)"/>')

for i, e in enumerate(ENTRIES):
    y = TOP + i * STEP
    svg.append(sigil(e["sigil"], 118, y + 50))
    svg.append(caps(200, y + 28, e["name"], size=17.5, track=5))
    svg.append(caps(1128, y + 28, f"boundary · {e['boundary']}", size=11,
                    track=3, fill=SOUL, anchor="end"))
    svg.append(f'<path d="M {216 + len(e["name"]) * 12.6} {y + 24} L 966 {y + 24}" '
               f'stroke="{BONE}" stroke-width="1" opacity=".13" '
               f'stroke-dasharray="1 6" stroke-linecap="round"/>')
    for j, line in enumerate(e["lines"]):
        svg.append(prose(200, y + 62 + j * 25, line, size=14.5))
    if i < len(ENTRIES) - 1:
        svg.append(f'<path d="M 200 {y + 124} L 1128 {y + 124}" stroke="{BONE}" '
                   f'stroke-width="1" opacity=".11" filter="url(#ink)"/>')

svg.append(motes(90, 150, 1020, 400, n=20, seed=5))
svg.append(vignette(W, H))
svg.append(tail())

OUT.write_text("\n".join(svg), encoding="utf-8")
print(f"wrote {OUT} ({W}x{H})")
