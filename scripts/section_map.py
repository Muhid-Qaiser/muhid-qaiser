#!/usr/bin/env python3
"""The map section — every public repository, drawn as Hallownest.

Modelled on the in-game world map rather than on a chart. Each area is one
continuous rectilinear silhouette with a stepped edge, filled near-black,
outlined in its own glowing colour, and captioned inside itself — Greenpath
green, the City of Tears blue, Crystal Peak pink. The areas interlock.

The layout keeps the real geography, so the substitutions carry meaning:
Foundations sits where Dirtmouth and the Forgotten Crossroads do, because that
is where everyone starts. Computer Vision takes Greenpath's place in the west.
Generative AI is the City of Tears. AI Security is the Abyss at the bottom of
the kingdom — the deepest ground, and the only area the map leaves unlit,
because that work is private.
"""
import json, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from theme import *

ROOT = Path(__file__).resolve().parent.parent
W, H = 1200, 820

# Every outline is orthogonal — Hallownest's areas step, they never slope.
AREAS = {
    # Dirtmouth and the Crossroads: wide, shallow, with a bay along the bottom
    # that Machine Learning fills from below.
    "FOUNDATIONS": {
        "poly": [(340, 196), (380, 196), (380, 168), (520, 168), (520, 160),
                 (600, 160), (600, 188), (660, 188), (660, 168), (700, 168),
                 (700, 240), (672, 240), (672, 268), (700, 268), (700, 300),
                 (560, 300), (560, 272), (460, 272), (460, 300), (400, 300),
                 (400, 268), (340, 268)],
        "colour": "#C6C9D6", "label": (520, 224), "lines": ["Foundations"],
    },
    # Greenpath: the widest ground on the map, stepping down to the south-west.
    "COMPUTER VISION": {
        "poly": [(60, 268), (140, 268), (140, 240), (340, 240), (340, 268),
                 (400, 268), (400, 320), (372, 320), (372, 368), (400, 368),
                 (400, 440), (348, 440), (348, 412), (300, 412), (300, 468),
                 (332, 468), (332, 532), (240, 532), (240, 560), (160, 560),
                 (160, 516), (96, 516), (96, 468), (60, 468)],
        "colour": "#86D96F", "label": (214, 330), "lines": ["Computer", "Vision"],
    },
    # Fungal Wastes: rises into Foundations' bay, drops toward the Abyss.
    "MACHINE LEARNING": {
        "poly": [(400, 300), (460, 300), (460, 272), (560, 272), (560, 300),
                 (700, 300), (700, 348), (672, 348), (672, 396), (700, 396),
                 (700, 460), (660, 460), (660, 512), (692, 512), (692, 568),
                 (600, 568), (600, 600), (500, 600), (500, 556), (452, 556),
                 (452, 508), (420, 508), (420, 440), (400, 440)],
        "colour": "#C9C271", "label": (548, 416), "lines": ["Machine", "Learning"],
    },
    # The City of Tears: the tall capital, notched along its eastern wall.
    "GENERATIVE AI": {
        "poly": [(720, 300), (1010, 300), (1010, 360), (980, 360), (980, 412), (1010, 412),
                 (1010, 500), (968, 500), (968, 544), (1010, 544), (1010, 580),
                 (880, 580), (880, 548), (800, 548), (800, 580), (720, 580),
                 (720, 520), (748, 520), (748, 468), (720, 468)],
        "colour": "#74ADEC", "label": (856, 398), "lines": ["Generative", "AI"],
    },
    # Crystal Peak: high in the east, its floor toothed where it meets the City.
    "AGENTIC AI": {
        "poly": [(750, 190), (790, 190), (790, 158), (920, 158), (920, 182),
                 (975, 182), (975, 250), (940, 250), (940, 288), (858, 288),
                 (858, 258), (806, 258), (806, 288), (750, 288)],
        "colour": "#E28FCB", "label": (866, 186), "lines": ["Agentic", "AI"],
    },
    # Kingdom's Edge: narrow, far out, barely joined to anything.
    "PARALLEL COMPUTE": {
        "poly": [(1030, 340), (1070, 340), (1070, 312), (1150, 312),
                 (1150, 420), (1122, 420), (1122, 460), (1150, 460),
                 (1150, 520), (1080, 520), (1080, 488), (1030, 488)],
        "colour": "#E8874A", "label": (1090, 360), "lines": ["Parallel", "Compute"],
        "size": 11,
    },
}

# The Abyss, drawn but never lit.
ABYSS = {
    "poly": [(380, 640), (470, 640), (470, 620), (560, 620), (560, 600),
             (700, 600), (700, 620), (900, 620), (900, 680), (860, 680),
             (860, 720), (900, 720), (900, 752), (700, 752), (700, 724),
             (600, 724), (600, 752), (440, 752), (440, 712), (380, 712)],
    "label": (650, 664),
}

stats = json.loads((ROOT / "data" / "stats.json").read_text(encoding="utf-8"))
rng = random.Random(20260827)   # fixed, so the file changes only when data does


def path_of(poly):
    first, *rest = poly
    return (f"M {first[0]} {first[1]} "
            + " ".join(f"L {x} {y}" for x, y in rest) + " Z")


def inside(px, py, poly):
    """Ray casting, so interior marks land inside the silhouette."""
    hit = False
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        if (y1 > py) != (y2 > py) and px < x1 + (py - y1) / (y2 - y1) * (x2 - x1):
            hit = not hit
    return hit


def bounds(poly):
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    return min(xs), min(ys), max(xs), max(ys)


def rooms_in(poly, n, keep_clear):
    """One small mark per repository, the way the Forgotten Crossroads shows
    its mapped rooms. Rejection-sampled, and kept off the caption."""
    x0, y0, x1, y1 = bounds(poly)
    cx, cy, cw, ch = keep_clear
    out = []
    for _ in range(n * 900):
        if len(out) == n:
            break
        w, h = rng.uniform(9, 20), rng.uniform(7, 13)
        px, py = rng.uniform(x0 + 8, x1 - 8 - w), rng.uniform(y0 + 8, y1 - 8 - h)
        # Every corner must sit inside, or the mark straddles a wall.
        if not all(inside(px + dx, py + dy, poly)
                   for dx in (-3, w + 3) for dy in (-3, h + 3)):
            continue
        if abs(px + w / 2 - cx) < cw / 2 + w and abs(py + h / 2 - cy) < ch / 2 + h:
            continue
        if any(abs(px - ox) < ow + 7 and abs(py - oy) < oh + 7
               for ox, oy, ow, oh in out):
            continue
        out.append((px, py, w, h))
    return out


by_area = {}
for repo in stats["repo_list"]:
    by_area.setdefault(repo["region"], []).append(repo)

DEFS = "".join(
    f'<clipPath id="clip{i}"><path d="{path_of(a["poly"])}"/></clipPath>'
    for i, a in enumerate(list(AREAS.values()) + [ABYSS]))

svg = []
# Read from the data, never spelled out — the total moves on its own.
svg.append(section("The Map"))

# The way down from Dirtmouth is a well, so the band above Foundations is not
# empty space — it is the descent. Drawn from above this section's own origin
# so the beam crosses the gap the masthead leaves, and the spores inside it
# drift up toward the opening.
for i, (name, area) in enumerate(AREAS.items()):
    poly, colour = area["poly"], area["colour"]
    d = path_of(poly)
    x0, y0, x1, y1 = bounds(poly)
    repos = by_area.get(name, [])

    svg.append(f'<path d="{d}" fill="#0B1019"/>')
    svg.append(f'<g clip-path="url(#clip{i})"><rect x="{x0}" y="{y0}" '
               f'width="{x1-x0}" height="{y1-y0}" filter="url(#grain)" '
               f'opacity=".16"/></g>')
    # A breath of the area's own colour, pooling inside its walls.
    svg.append(f'<g clip-path="url(#clip{i})"><path d="{d}" fill="{colour}" '
               f'opacity=".08" filter="url(#glowWide)"/></g>')

    lines, (lx, ly) = area["lines"], area["label"]
    size = area.get("size", 17)
    clear = (lx, ly + (len(lines) - 1) * 13, 200, 40 + (len(lines) - 1) * 26)
    svg.append(f'<g clip-path="url(#clip{i})" filter="url(#ink)">')
    for px, py, w, h in rooms_in(poly, len(repos), clear):
        svg.append(f'  <rect x="{px:.1f}" y="{py:.1f}" width="{w:.1f}" '
                   f'height="{h:.1f}" fill="none" stroke="{colour}" '
                   f'stroke-width="1" opacity=".28"/>')
    svg.append('</g>')

    # The wall: a wide bloom under a crisp line, both roughened.
    svg.append(f'<path class="lit" d="{d}" fill="none" stroke="{colour}" '
               f'stroke-width="7" filter="url(#glowMed)" opacity=".3" '
               f'style="animation-delay:-{i * 2.3:.1f}s"/>')
    # Each area takes the light in turn, so the kingdom is never lit all at
    # once — the closest thing to a hover state an <img> can carry.
    svg.append(f'<path class="lit" d="{d}" fill="none" stroke="{colour}" '
               f'stroke-width="2" filter="url(#ink)" '
               f'style="animation-delay:-{i * 2.3:.1f}s"/>')

    for j, line in enumerate(lines):
        svg.append(caps(lx, ly + j * 37, line, size=size + 7, track=1.8,
                        anchor="middle", glow=True))
    svg.append(prose(lx, ly + len(lines) * 37 - 8, f"{len(repos)} repositories",
                     size=21 if "size" not in area else 15,
                     anchor="middle", opacity=.9))

# ── The Abyss ─────────────────────────────────────────────────────────────
d = path_of(ABYSS["poly"])
ax0, ay0, ax1, ay1 = bounds(ABYSS["poly"])
svg.append(f'<path d="{d}" fill="#03060B"/>')
svg.append(f'<g clip-path="url(#clip{len(AREAS)})"><rect x="{ax0}" y="{ay0}" '
           f'width="{ax1-ax0}" height="{ay1-ay0}" filter="url(#grain)" '
           f'opacity=".1"/></g>')
svg.append(f'<ellipse cx="{(ax0+ax1)/2}" cy="{ay1-24}" rx="170" ry="56" '
           f'fill="{SOUL}" opacity=".08" filter="url(#glowWide)"/>')
ABYSS_EDGE = "#243247"
svg.append(f'<path d="{d}" fill="none" stroke="{ABYSS_EDGE}" stroke-width="2.4" '
           f'opacity=".95" stroke-dasharray="5 9" filter="url(#ink)"/>')
# What the Abyss actually looks like: a floor of dead vessels, so the dark
# is full of small pale eyes looking back up out of it. Rejection-sampled so
# no pair straddles a wall, and kept clear of the caption.
_rng = random.Random(5150)
cap_x, cap_y = ABYSS["label"]
_eyes = []
while len(_eyes) < 22:
    ex = _rng.uniform(ax0 + 16, ax1 - 16)
    ey = _rng.uniform(ay0 + 14, ay1 - 14)
    if not inside(ex, ey, ABYSS["poly"]):
        continue
    if abs(ex - cap_x) < 190 and abs(ey - cap_y - 8) < 40:   # off the caption
        continue
    if any((ex - px) ** 2 + (ey - py) ** 2 < 30 ** 2 for px, py, _ in _eyes):
        continue
    _eyes.append((ex, ey, _rng.uniform(1.4, 2.5)))
for i, (ex, ey, er) in enumerate(_eyes):
    gap, tilt = er * 2.5, _rng.uniform(-8, 8)
    svg.append(f'<g class="breathe" style="animation-delay:-{i*0.7:.1f}s" '
               f'transform="rotate({tilt:.0f} {ex:.0f} {ey:.0f})">'
               f'<ellipse cx="{ex-gap:.1f}" cy="{ey:.1f}" rx="{er:.1f}" '
               f'ry="{er*1.35:.1f}" fill="#DCF4F8" filter="url(#bloomSoft)"/>'
               f'<ellipse cx="{ex+gap:.1f}" cy="{ey:.1f}" rx="{er:.1f}" '
               f'ry="{er*1.35:.1f}" fill="#DCF4F8" filter="url(#bloomSoft)"/></g>')

svg.append(motes(ax0 + 30, ay0 + 20, ax1 - ax0 - 60, ay1 - ay0 - 40, n=12, seed=31))
lx, ly = ABYSS["label"]
svg.append(caps(lx, ly, "AI Security", size=29, track=1.8, fill=SOUL,
                anchor="middle", glow=True))

