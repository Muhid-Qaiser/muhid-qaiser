#!/usr/bin/env python3
"""assets/map.svg — every public repository, drawn as Hallownest.

Cornifer draws rooms as rough boxes joined by corridors, tints each area its
own colour, and leaves unvisited ground blank. The layout here follows the
real geography: Foundations sits where Dirtmouth and the Forgotten Crossroads
do, because that is where everyone starts; Computer Vision takes Greenpath's
place in the west; Generative AI takes the City of Tears; and AI Security is
the Abyss at the bottom — the deepest part of the kingdom, and the one the map
refuses to draw, because that work is private.
"""
import json, math, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from theme import *

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "map.svg"
W, H = 1200, 880

# name: (x0, y0, x1, y1, tint, label side, the Hallownest area it stands in for)
AREAS = {
    "FOUNDATIONS":      (372, 170, 640, 274, "#4A4034", "above", "Dirtmouth"),
    "COMPUTER VISION":  ( 88, 300, 400, 566, "#2F5C3A", "above", "Greenpath"),
    "MACHINE LEARNING": (420, 332, 662, 488, "#6A5326", "below", "Fungal Wastes"),
    "GENERATIVE AI":    (700, 252, 884, 514, "#28466B", "below", "City of Tears"),
    "AGENTIC AI":       (912, 198, 1112, 342, "#5A2D4A", "above", "Crystal Peak"),
    "PARALLEL COMPUTE": (944, 394, 1104, 476, "#3A4250", "below", "Kingdom's Edge"),
}
ROUTES = [("FOUNDATIONS", "COMPUTER VISION"), ("FOUNDATIONS", "MACHINE LEARNING"),
          ("FOUNDATIONS", "AGENTIC AI"), ("COMPUTER VISION", "MACHINE LEARNING"),
          ("MACHINE LEARNING", "GENERATIVE AI"), ("AGENTIC AI", "GENERATIVE AI"),
          ("GENERATIVE AI", "PARALLEL COMPUTE")]

# The Abyss. Nothing is drawn inside it.
ABYSS = (430, 606, 800, 764)

stats = json.loads((ROOT / "data" / "stats.json").read_text(encoding="utf-8"))
rng = random.Random(20260827)   # fixed, so the file changes only when data does


def pack(x0, y0, x1, y1, repos):
    """Carve the area into irregular cells, then set a room inside each.

    Recursive subdivision is what gives a metroidvania map its look: rooms
    tile the space but no two are the same size, and nothing lines up into a
    grid. Bigger repositories are handed the bigger cells.
    """
    n = len(repos)
    cells = [(x0, y0, x1, y1)]
    while len(cells) < n:
        cells.sort(key=lambda c: -((c[2] - c[0]) * (c[3] - c[1])))
        cx0, cy0, cx1, cy1 = cells.pop(0)
        w, h = cx1 - cx0, cy1 - cy0
        if w > h * 1.15:
            sx = cx0 + w * rng.uniform(0.33, 0.67)
            cells += [(cx0, cy0, sx, cy1), (sx, cy0, cx1, cy1)]
        else:
            sy = cy0 + h * rng.uniform(0.33, 0.67)
            cells += [(cx0, cy0, cx1, sy), (cx0, sy, cx1, cy1)]

    cells.sort(key=lambda c: -((c[2] - c[0]) * (c[3] - c[1])))
    ranked = sorted(repos, key=lambda r: -r["commits"])
    rooms = []
    for cell, repo in zip(cells, ranked):
        cx0, cy0, cx1, cy1 = cell
        w, h = cx1 - cx0, cy1 - cy0
        padx = w * rng.uniform(0.20, 0.36)
        pady = h * rng.uniform(0.22, 0.40)
        rooms.append((cx0 + padx / 2, cy0 + pady / 2, w - padx, h - pady, repo))
    return rooms


def span(pts):
    """Minimum spanning tree — a corridor only where it shortens the walk."""
    if len(pts) < 2:
        return []
    inside, outside, edges = {0}, set(range(1, len(pts))), []
    while outside:
        i, j = min(((i, j) for i in inside for j in outside),
                   key=lambda e: (pts[e[0]][0] - pts[e[1]][0]) ** 2
                                 + (pts[e[0]][1] - pts[e[1]][1]) ** 2)
        edges.append((i, j))
        inside.add(j)
        outside.discard(j)
    return edges


def ortho(a, b):
    """Corridors in Hallownest turn square corners, never diagonals."""
    (x1, y1), (x2, y2) = a, b
    if rng.random() < 0.5:
        return f"M {x1:.1f} {y1:.1f} L {x2:.1f} {y1:.1f} L {x2:.1f} {y2:.1f}"
    return f"M {x1:.1f} {y1:.1f} L {x1:.1f} {y2:.1f} L {x2:.1f} {y2:.1f}"


svg = [head(W, H)]
svg.append(section("The Map", "Ninety-two public repositories, drawn as ground "
                                    "that was walked. Room size is commits."))

by_area = {}
for repo in stats["repo_list"]:
    by_area.setdefault(repo["region"], []).append(repo)

# Each area's colour wash, laid down before anything is drawn on top of it.
for name, (x0, y0, x1, y1, tint, _, _) in AREAS.items():
    svg.append(f'<ellipse cx="{(x0+x1)/2}" cy="{(y0+y1)/2}" '
               f'rx="{(x1-x0)/2 + 54}" ry="{(y1-y0)/2 + 46}" fill="{tint}" '
               f'opacity=".3" filter="url(#glowWide)"/>')

placed = {}
for name, (x0, y0, x1, y1, *_rest) in AREAS.items():
    repos = sorted(by_area.get(name, []), key=lambda r: -r["commits"])
    placed[name] = pack(x0, y0, x1, y1, repos)


def centre(room):
    x, y, w, h, _ = room
    return (x + w / 2, y + h / 2)


# Corridors first, so the rooms sit on top and hide the joins.
svg.append(f'<g filter="url(#ink)" fill="none" stroke="{BONE}" opacity=".4" '
           f'stroke-width="1.4" stroke-linecap="square">')
for rooms in placed.values():
    pts = [centre(r) for r in rooms]
    for i, j in span(pts):
        svg.append(f'  <path d="{ortho(pts[i], pts[j])}"/>')
svg.append('</g>')

# The long passages between areas.
svg.append(f'<g filter="url(#ink)" fill="none" stroke="{BONE}" opacity=".32" '
           f'stroke-width="1.6" stroke-linecap="square" stroke-dasharray="8 7">')
for a, b in ROUTES:
    pair = min(((centre(ra), centre(rb)) for ra in placed[a] for rb in placed[b]),
               key=lambda e: (e[0][0] - e[1][0]) ** 2 + (e[0][1] - e[1][1]) ** 2)
    svg.append(f'  <path d="{ortho(*pair)}"/>')
# Two roads run down into the Abyss and stop being drawn.
ax0, ay0, ax1, ay1 = ABYSS
for area, target in (("GENERATIVE AI", (ax1 - 40, ay0 - 6)),
                     ("COMPUTER VISION", (ax0 + 40, ay0 - 6))):
    low = max((centre(r) for r in placed[area]), key=lambda p: p[1])
    svg.append(f'  <path d="{ortho(low, target)}" opacity=".62"/>')
svg.append('</g>')

# Rooms.
for name, rooms in placed.items():
    svg.append('<g filter="url(#bloomSoft)">')
    for x, y, w, h, repo in rooms:
        svg.append(f'  <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" '
                   f'height="{h:.1f}" rx="2.5" fill="#141C2E" fill-opacity=".95" '
                   f'stroke="{BONE}" stroke-width="1.3" stroke-opacity=".6"/>')
        if repo["stars"]:                  # somebody else found this one
            cx, cy = x + w / 2, y + h / 2
            svg.append(f'  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.6" '
                       f'fill="{SOUL}" filter="url(#glowMed)"/>')
    svg.append('</g>')

# ── The Abyss ─────────────────────────────────────────────────────────────
svg.append(f'<rect x="{ax0}" y="{ay0}" width="{ax1-ax0}" height="{ay1-ay0}" '
           f'rx="14" fill="#03060B"/>')
svg.append(f'<ellipse cx="{(ax0+ax1)/2}" cy="{ay1-20}" rx="150" ry="54" '
           f'fill="{SOUL}" opacity=".09" filter="url(#glowWide)"/>')
svg.append(f'<rect x="{ax0}" y="{ay0}" width="{ax1-ax0}" height="{ay1-ay0}" '
           f'rx="14" fill="none" stroke="{SOUL}" stroke-width="1.5" '
           f'opacity=".4" stroke-dasharray="4 10" stroke-linecap="round" '
           f'filter="url(#ink)"/>')
svg.append(motes(ax0 + 24, ay0 + 20, ax1 - ax0 - 48, ay1 - ay0 - 40, n=18, seed=31))
svg.append(caps((ax0 + ax1) / 2, ay0 + 74, "AI Security", size=15, track=5,
                fill=SOUL, anchor="middle", glow=True))
svg.append(prose((ax0 + ax1) / 2, ay0 + 98, "unmapped — the work is private",
                 size=13, anchor="middle"))

# ── Area names ────────────────────────────────────────────────────────────
for name, (x0, y0, x1, y1, tint, where, stand_in) in AREAS.items():
    cx = (x0 + x1) / 2
    ly = y0 - 34 if where == "above" else y1 + 40
    svg.append(caps(cx, ly, name, size=14, track=4.4, anchor="middle",
                    opacity=.92, glow=True))
    svg.append(prose(cx, ly + 19, f"{len(by_area.get(name, []))} rooms", size=12,
                     anchor="middle", opacity=.78))

svg.append(footnote("Areas are inferred from repository names and descriptions, "
                    "and laid out after Hallownest — Foundations where Dirtmouth "
                    "stands, Computer Vision in Greenpath's place, AI Security "
                    "in the Abyss.", 836))
svg.append(vignette(W, H))
svg.append(tail())

OUT.write_text("\n".join(svg), encoding="utf-8")
print(f"wrote {OUT} ({W}x{H})  {sum(len(v) for v in placed.values())} rooms")
