#!/usr/bin/env python3
"""assets/map.svg — every public repository, drawn as ground that was walked.

Cornifer's maps record where somebody has actually been, and leave the
unvisited parts blank. A commit history is the same record, so repositories
become chambers, domains become regions, and the current work — which is
private — is drawn as territory nobody has mapped.
"""
import json, math, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from theme import *

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "map.svg"
W, H = 1200, 640

# Hand-placed so the world reads as a cave system rather than a chart.
# name: (cx, cy, rx, ry, tint, label side)
PLACES = {
    "PERCEPTION":  (278, 252, 168, 96, "#2A4A52", "above"),
    "LANGUAGE":    (604, 206, 112, 68, "#3A3558", "above"),
    "AGENTS":      (846, 244,  96, 62, "#4A3A2E", "above"),
    "LEARNING":    (524, 406, 122, 70, "#2E4438", "below"),
    "FOUNDATIONS": (222, 442, 134, 78, "#37384A", "below"),
    "SILICON":     (792, 420,  74, 50, "#4A2E3A", "below"),
}
ROUTES = [("PERCEPTION", "LANGUAGE"), ("LANGUAGE", "AGENTS"),
          ("PERCEPTION", "FOUNDATIONS"), ("PERCEPTION", "LEARNING"),
          ("LEARNING", "LANGUAGE"), ("LEARNING", "SILICON"),
          ("AGENTS", "SILICON"), ("FOUNDATIONS", "LEARNING")]

UNMAPPED = ("M 1006 300 C 1120 288, 1162 348, 1142 420 "
            "C 1124 484, 1040 502, 998 462 C 962 426, 968 336, 1006 300 Z")

stats = json.loads((ROOT / "data" / "stats.json").read_text(encoding="utf-8"))
rng = random.Random(20260827)   # fixed, so the file changes only when data does


def scatter(cx, cy, rx, ry, n, gap=27):
    """Rejection-sample chamber positions inside a region's ellipse."""
    pts = []
    for _ in range(n * 400):
        if len(pts) == n:
            break
        a, rad = rng.random() * math.tau, math.sqrt(rng.random()) * 0.88
        x, y = cx + math.cos(a) * rx * rad, cy + math.sin(a) * ry * rad
        if all((x - px) ** 2 + (y - py) ** 2 > gap ** 2 for px, py in pts):
            pts.append((x, y))
    while len(pts) < n:                    # crowded region: relax the spacing
        a, rad = rng.random() * math.tau, math.sqrt(rng.random()) * 0.9
        pts.append((cx + math.cos(a) * rx * rad, cy + math.sin(a) * ry * rad))
    return pts


def span(pts):
    """Minimum spanning tree — corridors only where they shorten the walk."""
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


def corridor(a, b, bow=0.16):
    """A passage that wanders, because nothing down there runs straight."""
    (x1, y1), (x2, y2) = a, b
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    off = rng.uniform(-bow, bow)
    return (f"M {x1:.1f} {y1:.1f} Q {mx - dy * off:.1f} {my + dx * off:.1f} "
            f"{x2:.1f} {y2:.1f}")


def chamber(cx, cy, r, sides=7):
    pts = []
    for i in range(sides):
        a = math.tau * i / sides + rng.uniform(-0.13, 0.13)
        rr = r * rng.uniform(0.8, 1.2)
        pts.append(f"{cx + math.cos(a) * rr:.1f} {cy + math.sin(a) * rr:.1f}")
    return "M " + " L ".join(pts) + " Z"


svg = [head(W, H)]
svg.append(caps(72, 66, "The Map", size=23, track=6.5))
svg.append(prose(72, 96, "Ninety-two public repositories, laid out as ground "
                         "that was walked. Chamber size is commits."))
svg.append(f'<path d="M 72 118 L 1128 118" stroke="{BONE}" stroke-width="1.2" '
           f'opacity=".2" filter="url(#ink)"/>')

by_region = {}
for repo in stats["repo_list"]:
    by_region.setdefault(repo["region"], []).append(repo)

# Atmospheric wash first, so every chamber sits on its region's colour.
for name, (cx, cy, rx, ry, tint, _) in PLACES.items():
    svg.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx + 62}" ry="{ry + 54}" '
               f'fill="{tint}" opacity=".26" filter="url(#glowWide)"/>')

placed = {}
for name, (cx, cy, rx, ry, tint, _) in PLACES.items():
    repos = sorted(by_region.get(name, []), key=lambda r: -r["commits"])
    placed[name] = list(zip(scatter(cx, cy, rx, ry, len(repos)), repos))

# Region-to-region routes sit under everything else.
svg.append(f'<g filter="url(#ink)" fill="none" stroke="{BONE}" opacity=".3" '
           f'stroke-width="1.5" stroke-linecap="round" stroke-dasharray="7 7">')
for a, b in ROUTES:
    pair = min(((pa, pb) for pa, _ in placed[a] for pb, _ in placed[b]),
               key=lambda e: (e[0][0] - e[1][0]) ** 2 + (e[0][1] - e[1][1]) ** 2)
    svg.append(f'  <path d="{corridor(pair[0], pair[1], 0.09)}"/>')
# One passage runs on toward the private work and stops being drawn.
edge = min((p for p, _ in placed["AGENTS"]), key=lambda p: -p[0])
svg.append(f'  <path d="{corridor(edge, (1002, 350), 0.05)}" opacity=".55"/>')
svg.append('</g>')

for name, entries in placed.items():
    pts = [p for p, _ in entries]
    svg.append(f'<g filter="url(#ink)" fill="none" stroke="{BONE}" opacity=".34" '
               f'stroke-width="1.3" stroke-linecap="round">')
    for i, j in span(pts):
        svg.append(f'  <path d="{corridor(pts[i], pts[j])}"/>')
    svg.append('</g>')

    svg.append('<g filter="url(#ink)">')
    for (x, y), repo in entries:
        r = 5.4 + math.sqrt(min(repo["commits"], 30)) * 2.6
        svg.append(f'  <path d="{chamber(x, y, r)}" fill="{CAVERN}" '
                   f'stroke="{BONE}" stroke-width="1.25" stroke-opacity=".62"/>')
        if repo["stars"]:                  # somebody else found this one
            svg.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{r * .42:.1f}" '
                       f'fill="{SOUL}" filter="url(#glowMed)"/>')
    svg.append('</g>')

for name, (cx, cy, rx, ry, tint, where) in PLACES.items():
    ly = cy - ry - 24 if where == "above" else cy + ry + 32
    svg.append(caps(cx, ly, name, size=12.5, track=4, anchor="middle", opacity=.9))
    svg.append(prose(cx, ly + 18, f"{len(by_region.get(name, []))} chambers",
                     size=12, anchor="middle", opacity=.8))

# The part that is not drawn: the current work is private, so it stays blank.
svg.append(f'<path d="{UNMAPPED}" fill="{SOUL}" opacity=".05" filter="url(#ink)"/>')
svg.append(f'<path d="{UNMAPPED}" fill="none" stroke="{SOUL}" stroke-width="1.5" '
           f'opacity=".45" stroke-dasharray="4 9" stroke-linecap="round" '
           f'filter="url(#ink)"/>')
svg.append(motes(1010, 322, 96, 146, n=12, seed=31))
svg.append(caps(1054, 378, "Red team", size=12.5, track=4, fill=SOUL,
                anchor="middle"))
svg.append(prose(1054, 398, "unmapped", size=12, anchor="middle"))

svg.append(f'<path d="M 72 566 L 1128 566" stroke="{BONE}" stroke-width="1" '
           f'opacity=".14" filter="url(#ink)"/>')
svg.append(prose(72, 596, "Regions are inferred from repository names and "
                          "descriptions. The red-team work is not public, so "
                          "there is nothing there to draw.", size=13, opacity=.85))
svg.append(vignette(W, H))
svg.append(tail())

OUT.write_text("\n".join(svg), encoding="utf-8")
print(f"wrote {OUT} ({W}x{H})  {sum(len(v) for v in by_region.values())} chambers")
