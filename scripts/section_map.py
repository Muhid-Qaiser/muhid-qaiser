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

It always rains in the City of Tears. The Knight stands at the edge of the
Abyss with the compass ping. Pins mark repositories the way the game marks
its map: Cornifer's red for pushed this year, a shop for starred, a bench
for built from scratch. Pins never stand on a caption.
"""
import json, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from theme import *
import section_vessel as SV

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
                 (1150, 580), (1080, 580), (1080, 548), (1030, 548)],
        "colour": "#E8874A", "label": (1090, 380), "lines": ["Parallel", "Compute"],
        "size": 11,
    },
}

# The Abyss, drawn but never lit.
ABYSS = {
    "poly": [(380, 640), (470, 640), (470, 620), (560, 620), (560, 600),
             (700, 600), (700, 620), (900, 620), (900, 680), (860, 680),
             (860, 720), (900, 720), (900, 752), (700, 752), (700, 724),
             (600, 724), (600, 752), (440, 752), (440, 712), (380, 712)],
    "label": (650, 686),
}

stats = json.loads((ROOT / "data" / "stats.json").read_text(encoding="utf-8"))
rng = random.Random(20260827)   # fixed, so the file changes only when data does


# The soft band around each wall used to be a 7px stroke under a 6px Gaussian
# — one filter buffer per region, and by measurement the single most
# expensive thing in the file. Concentric strokes lay down the same profile
# with plain geometry. The opacities compose to 0.467 at the centre, which is
# where a 6px blur of a 7px stroke peaks, and the widths step down
# geometrically so the edge falls off smoothly instead of banding.
BLOOM = ((46, .042), (34, .058), (24, .080), (16, .105), (10, .135), (6, .170))


def path_of(poly, rough=0.0):
    """Emit the outline, optionally with the corners nudged.

    `rough` bakes in the wobble the ink filter used to add at paint time. The
    jitter is drawn from a fixed seed, so the file only changes when the data
    does."""
    if rough:
        jr = random.Random(4242)
        poly = [(x + jr.uniform(-rough, rough), y + jr.uniform(-rough, rough))
                for x, y in poly]
    first, *rest = poly
    return (f"M {first[0]:.1f} {first[1]:.1f} "
            + " ".join(f"L {x:.1f} {y:.1f}" for x, y in rest) + " Z")


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
    # The Abyss no longer needs one: its grain was folded into the map-wide
    # pass, which is the only thing that ever clipped to it.
    f'<clipPath id="clip{i}"><path d="{path_of(a["poly"])}"/></clipPath>'
    for i, a in enumerate(AREAS.values())
) + "".join(
    # Bare geometry for the wall bloom to reference. It carries no stroke of
    # its own on purpose: a presentation attribute on the referenced element
    # beats the one on <use>, so giving this a width would render all six
    # bloom layers at that width and the falloff would collapse into a band.
    f'<path id="w{i}" d="{path_of(a["poly"])}"/>'
    for i, a in enumerate(AREAS.values()))

def rain_path(poly, period=40, col=30, seed=1201):
    # It always rains in the City of Tears. One path of short strokes on a
    # lattice whose rows repeat every 40px, so sliding it 80px and starting
    # over is seamless. One element, one stroke pass per step: no pattern
    # tile to rasterise, and the region's own clip does the cutting.
    rr = random.Random(seed)
    x0, y0, x1, y1 = bounds(poly)
    segs = []
    x = x0 + 8
    while x < x1 - 4:
        phase, length = rr.uniform(0, period), rr.uniform(9, 15)
        y = y0 - 2 * period + phase
        while y < y1:
            segs.append(f'M {x:.0f} {y:.0f} v {length:.0f}')
            y += period
        x += col + rr.uniform(-6, 6)
    return ' '.join(segs)

# Pins, as the game colours them: a bench is where you sit down and rebuild,
# so the builds from scratch get the bench; a shop is where Geo changes hands,
# so the starred repositories get the shop; Cornifer is wherever the map is
# still being drawn, so the repositories pushed this year get his pin. A
# repository gets one pin, the most recent claim first.
NOW_YEAR = max(r["pushed"][:4] for r in stats["repo_list"])
PIN = {
    "cornifer": ("#E8705C", "M -1.7 1.7 L 1.9 -1.9 M 0.4 -1.9 L 1.9 -1.9 L 1.9 -0.4"),
    "shop":     (BONE,      "M 0 -2 L 2 0 L 0 2 L -2 0 Z"),
    "bench":    ("#7FB8FF", "M -2.4 -0.3 L 2.4 -0.3 M -1.6 -0.3 L -1.6 1.8 M 1.6 -0.3 L 1.6 1.8"),
}
PIN_LEGEND = (("cornifer", "mapped this year"), ("shop", "starred"), ("bench", "built from scratch"))


def kind_of(repo):
    if repo["pushed"][:4] == NOW_YEAR:
        return "cornifer"
    if repo.get("stars"):
        return "shop"
    if repo.get("scratch"):
        return "bench"
    return None


def pin(x, y, kind):
    colour, mark = PIN[kind]
    return (f'<circle cx="{x:.1f}" cy="{y-9:.1f}" r="3.8" fill="{colour}"/>'
            f'<path d="{mark}" transform="translate({x:.1f},{y-9:.1f})" fill="none" '
            f'stroke="{VOID}" stroke-width=".9" stroke-linecap="round"/>'
            f'<path d="M {x:.1f} {y-5:.1f} L {x:.1f} {y+2:.1f}" stroke="{colour}" stroke-width="1.4"/>')

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
    # A breath of the area's own colour. This used to be a blurred copy
    # clipped to its own outline, so the blur only softened an edge that the
    # clip then cut off — a flat tint is indistinguishable and free.
    svg.append(f'<path d="{d}" fill="{colour}" opacity=".07"/>')

    lines, (lx, ly) = area["lines"], area["label"]
    size = area.get("size", 17)
    clear = (lx, ly + (len(lines) - 1) * 13, 200, 40 + (len(lines) - 1) * 26)
    svg.append(f'<g clip-path="url(#clip{i})">')
    if name == "GENERATIVE AI":
        svg.append(f'  <path class="rain" d="{rain_path(poly)}" stroke="{SOUL}" '
                   f'stroke-width="1" opacity=".38" fill="none"/>')
    rooms = rooms_in(poly, len(repos), clear)
    # A pin stands 14px above its room's centre, so a room that is clear of
    # the caption can still put a pin head across the words. Pinned
    # repositories take rooms whose whole pin is clear of the caption and its
    # count line, and whose head stays inside the walls. Rooms come out of
    # the sampler in random order, so the pins stay spread out.
    words_top, words_bottom = ly - 34, ly + len(lines) * 37 + 6
    def takes_a_pin(room):
        rx, ry = room[0] + room[2] / 2, room[1] + room[3] / 2
        on_words = abs(rx - lx) < 86 and ry + 3 > words_top and ry - 14 < words_bottom
        return not on_words and inside(rx, ry - 15, poly)
    kinds = [kind_of(r) for r in repos if kind_of(r)]
    assigned = dict(zip((j for j, room in enumerate(rooms) if takes_a_pin(room)), kinds))
    pins = []
    for j, (px, py, w, h) in enumerate(rooms):
        k = assigned.get(j)
        svg.append(f'  <rect x="{px:.1f}" y="{py:.1f}" width="{w:.1f}" '
                   f'height="{h:.1f}" fill="none" stroke="{colour}" '
                   f'stroke-width="1" opacity="{.55 if k else .28}"/>')
        if k:
            pins.append((px + w / 2, py + h / 2, k))
    svg.append('</g>')
    for px, py, k in pins:
        svg.append(pin(px, py, k))

    # The wall: a wide bloom under a crisp line, both roughened. This used to
    # pulse continuously, invalidating almost the entire map on every display
    # frame. A stable midpoint keeps the same illuminated appearance without
    # making the largest geometry in the profile repaint forever.
    svg.append('<g opacity=".82">')
    # The outline is stored once in defs and referenced six times; six copies
    # of a fifty-point polygon would have cost more bytes than the filter did.
    for bw, bo in BLOOM:
        # stroke-opacity, not opacity: `.lit` animates opacity on the wrapper
        # and a CSS animation overrides the presentation attribute outright.
        svg.append(f'    <use href="#w{i}" fill="none" stroke="{colour}" '
                   f'stroke-width="{bw}" stroke-opacity="{bo}" '
                   f'stroke-linejoin="round" stroke-linecap="round"/>')
    svg.append(f'  <path d="{path_of(poly, rough=1.4)}" fill="none" '
               f'stroke="{colour}" stroke-width="2"/>')
    svg.append('</g>')

    for j, line in enumerate(lines):
        svg.append(caps(lx, ly + j * 37, line, size=size + 7, track=1.8,
                        anchor="middle", glow=True))
    svg.append(prose(lx, ly + len(lines) * 37 - 8, f"{len(repos)} repos",
                     size=21 if "size" not in area else 15,
                     anchor="middle", opacity=.9))

# ── The Abyss ─────────────────────────────────────────────────────────────
d = path_of(ABYSS["poly"])
ax0, ay0, ax1, ay1 = bounds(ABYSS["poly"])
svg.append(f'<path d="{d}" fill="#03060B"/>')

# One grain pass for the whole map, laid after the Abyss so it covers that as
# well. This was seven turbulence passes, then one turbulence pass plus a
# second clipped one for the Abyss. The Abyss sits well inside the map's own
# bounds, so a single tiled pass does both.
svg.append('<rect x="40" y="140" width="1130" height="640" '
           'fill="url(#grainTile)" opacity=".13"/>')
# Pale light pooling on the floor. This was a solid ellipse under a 14px
# blur; the blur spread it by about three sigma either way, so an ellipse of
# that final size carrying a radial falloff is the same picture without the
# filter buffer.
svg.append(f'<ellipse cx="{(ax0+ax1)/2}" cy="{ay1-24}" rx="214" ry="100" '
           f'fill="url(#sporeCool)" opacity=".13"/>')
ABYSS_EDGE = "#3E6A7C"
svg.append(f'<path d="{d}" fill="none" stroke="{ABYSS_EDGE}" stroke-width="2.4" '
           f'opacity=".9" stroke-dasharray="5 9"/>')
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
    cls = ' class="breathe"' if i == 3 else ''
    svg.append(f'<g opacity=".65"{cls} '
               f'transform="rotate({tilt:.0f} {ex:.0f} {ey:.0f})">'
               f'<ellipse cx="{ex-gap:.1f}" cy="{ey:.1f}" rx="{er*1.6:.1f}" '
               f'ry="{er*2.1:.1f}" fill="url(#sporeCool)"/>'
               f'<ellipse cx="{ex+gap:.1f}" cy="{ey:.1f}" rx="{er*1.6:.1f}" '
               f'ry="{er*2.1:.1f}" fill="url(#sporeCool)"/></g>')

svg.append(motes(ax0 + 30, ay0 + 20, ax1 - ax0 - 60, ay1 - ay0 - 40, n=12, seed=31))
lx, ly = ABYSS["label"]
svg.append(caps(lx, ly, "AI Security", size=29, track=1.8, fill=SOUL,
                anchor="middle", glow=True))
# The Wayward Compass: the Knight's own mark on the map, and where it
# stands is the one area the map does not light.
kx, ky = 822, 652
svg.append(f'<circle class="ping" cx="{kx}" cy="{ky+2}" r="26" fill="none" '
           f'stroke="{SOUL}" stroke-width="1.4"/>')
svg.append(f'<ellipse cx="{kx}" cy="{ky+4}" rx="16" ry="16" fill="url(#sporeCool)" opacity=".55"/>')
svg.append(f'<g transform="translate({kx-9},{ky-10}) scale(.18)">'
           f'<path d="{SV.MASK}" fill="{LUMEN}"/>'
           + ''.join(f'<circle cx="{SV.EYE_CX + sx*SV.EYE_DX}" cy="{SV.EYE_CY}" r="{SV.EYE_R}" fill="{VOID}"/>'
                     for sx in (-1, 1)) + '</g>')
svg.append(prose(kx, ky + 40, "you are here", size=12, anchor="middle", opacity=.7))
# Legend for the pins, under the map.
lx = MARGIN + 4
for kind, label in PIN_LEGEND:
    svg.append(pin(lx, 806, kind))
    svg.append(prose(lx + 12, 804, label, size=13, opacity=.75))
    lx += 26 + len(label) * 6.4

