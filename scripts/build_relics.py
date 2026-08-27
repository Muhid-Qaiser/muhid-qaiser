#!/usr/bin/env python3
"""assets/relic-*.svg — four things worth picking up.

Chosen by hand, not by star count: a published architecture, a vision model,
a delegating agent, and a frontier model rebuilt from nothing. Each card is
wrapped in a link in the README, so the whole tile is the target.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from theme import *

OUT = Path(__file__).resolve().parent.parent / "assets"
W, H = 600, 148

RELICS = [
    {"file": "teznet", "name": "TezNet", "tag": "published",
     "line": "A convolutional network for classifying optical coherence",
     "line2": "tomography scans. Published, with the official implementation.",
     "glyph": "scan"},
    {"file": "agrovq", "name": "AgroVQ-HybridNet", "tag": "vision · language",
     "line": "Visual question answering over crop imagery — a model that",
     "line2": "has to look at a field and answer a question about it.",
     "glyph": "leaf"},
    {"file": "crew", "name": "Hierarchical Multi-Doc RAG", "tag": "agents",
     "line": "A master agent that decomposes a question and delegates it to",
     "line2": "sub-agents. Building these is how you learn where they break.",
     "glyph": "tree"},
    {"file": "deepseek", "name": "DeepSeek from Scratch", "tag": "from scratch",
     "line": "The architecture rebuilt and trained in PyTorch from nothing,",
     "line2": "because reading the paper is not the same as running it.",
     "glyph": "layers"},
]


def glyph(kind, cx, cy):
    g = [f'<circle cx="{cx}" cy="{cy}" r="34" fill="#151D30"/>',
         f'<circle cx="{cx}" cy="{cy}" r="34" fill="none" stroke="{BONE}" '
         f'stroke-width="1.2" opacity=".38" filter="url(#ink)"/>']
    s = lambda d, col=BONE, w=2, op=.85: (
        f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" '
        f'stroke-linecap="round" opacity="{op}"/>')

    if kind == "scan":              # retinal layers, one of them lit
        for i, dy in enumerate((-13, -5, 3, 11)):
            col, op = (SOUL, 1) if i == 2 else ("#B4BDCE", .7)
            g.append(s(f"M {cx-19} {cy+dy} Q {cx} {cy+dy-6}, {cx+19} {cy+dy}",
                       col, 2.2, op))
    elif kind == "leaf":            # a leaf, and the eye that reads it
        g.append(s(f"M {cx-3} {cy+16} C {cx-20} {cy+2}, {cx-14} {cy-16}, "
                   f"{cx+6} {cy-17} C {cx+16} {cy+1}, {cx+8} {cy+14}, "
                   f"{cx-3} {cy+16} Z", "#B4BDCE", 2, .8))
        g.append(s(f"M {cx-3} {cy+16} L {cx+3} {cy-13}", "#B4BDCE", 1.6, .6))
        g.append(f'<circle cx="{cx+1}" cy="{cy-1}" r="4" fill="{SOUL}" '
                 f'filter="url(#glowMed)"/>')
    elif kind == "tree":            # one above, three below
        for dx in (-15, 0, 15):
            g.append(s(f"M {cx} {cy-9} L {cx+dx} {cy+12}", "#B4BDCE", 1.6, .6))
            g.append(f'<circle cx="{cx+dx}" cy="{cy+14}" r="4.2" '
                     f'fill="#B4BDCE" opacity=".8"/>')
        g.append(f'<circle cx="{cx}" cy="{cy-13}" r="6" fill="{SOUL}" '
                 f'filter="url(#glowMed)"/>')
    else:                           # layers stacked up from nothing
        for i, dy in enumerate((12, 4, -4, -12)):
            w = 26 - i * 4
            col, op = (SOUL, 1) if i == 3 else ("#B4BDCE", .72)
            g.append(f'<rect x="{cx-w/2}" y="{cy+dy-3}" width="{w}" height="5" '
                     f'rx="1.5" fill="{col}" opacity="{op}"/>')
    return "".join(g)


# A header strip so the section title stays in the same world as the figures.
hdr = [head(1200, 118)]
hdr.append(caps(72, 66, "Relics", size=23, track=6.5))
hdr.append(prose(72, 96, "Four things worth picking up. Chosen by hand, "
                         "not by star count."))
hdr.append(f'<path d="M 72 108 L 1128 108" stroke="{BONE}" stroke-width="1.2" '
           f'opacity=".2" filter="url(#ink)"/>')
hdr.append(tail())
(OUT / "relics-header.svg").write_text("\n".join(hdr), encoding="utf-8")
print("wrote relics-header.svg")

for r in RELICS:
    svg = [head(W, H)]
    svg.append(f'<rect x="3" y="3" width="{W-6}" height="{H-6}" rx="5" '
               f'fill="{CAVERN}" fill-opacity=".55" stroke="{BONE}" '
               f'stroke-width="1.3" stroke-opacity=".26" filter="url(#ink)"/>')
    svg.append(glyph(r["glyph"], 66, 74))
    svg.append(caps(122, 56, r["name"], size=16, track=3.6))
    svg.append(caps(122, 78, r["tag"], size=10, track=2.6, fill=SOUL))
    svg.append(prose(122, 102, r["line"], size=13.5))
    svg.append(prose(122, 122, r["line2"], size=13.5))
    svg.append(motes(40, 30, 520, 90, n=6, seed=len(r["name"])))
    svg.append(tail())
    path = OUT / f"relic-{r['file']}.svg"
    path.write_text("\n".join(svg), encoding="utf-8")
    print(f"wrote {path.name}")
