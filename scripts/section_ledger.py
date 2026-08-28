#!/usr/bin/env python3
"""The ledger section — the counters, the web, and the hours.

Three figures, none of which repeats another.

The vessel is Hollow Knight's Soul orb as it appears in the HUD: a bowl of
pale, almost-white liquid behind a rough carved rim, with a mask's eye holes
cut into it. The big one holds the current year against the best year; the
three small ones are Soul Vessels, one per year. That is deliberate against
the masthead — up there a vessel has cracked and is losing what it held, down
here one is filling.

The web is Deepnest. A radar chart is a spider chart, and a spider chart drawn
properly is a web, so it is drawn as one: rings sagging inward between the
anchor threads the way silk actually hangs. It plots commits per area rather
than repositories, because the map above already counts what was made and this
counts where the work went. The two disagree, which is the point — Foundations
holds 0.74 of the repositories but 0.98 of the commits.

Axis order is not arbitrary. It runs clockwise from the top in the same order
the areas sit on the map, so the two figures can be read against each other.

Deliberately no lines-of-code total. This account is largely Jupyter
notebooks, whose committed JSON carries base64 image output, so an additions
figure would measure the file format rather than the work.
"""
import json, math, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from theme import *

ROOT = Path(__file__).resolve().parent.parent
W, H = 1200, 650
DEFS = ""

stats = json.loads((ROOT / "data" / "stats.json").read_text(encoding="utf-8"))

hours = stats["hours"]
peak = hours.index(max(hours))
years = stats["commits_by_year"]
best = max(years.values()) if years else 1
now = max(years) if years else "—"

# Soul in the HUD is near-white with only a breath of cold in it.
LIQUID = "#E4F6FA"

# The same shell drawn in the masthead, in its own 220x250 box.
ORB_MASK = (
    "M 34 120 "
    "C 22 90, 14 56, 7 26 C 5 19, 15 16, 19 24 C 31 56, 50 86, 70 98 "
    "C 84 76, 136 76, 150 98 "
    "C 170 86, 189 56, 201 24 C 205 16, 215 19, 213 26 C 206 56, 198 90, 186 120 "
    "C 188 164, 168 212, 110 236 C 52 212, 32 164, 34 120 Z"
)

COUNTS = [
    (stats["repos"],          "Repositories"),
    (stats["commits"],        "Commits"),
    (stats["scratch_builds"], "From scratch"),
]

# Clockwise from the top, in the order these areas sit on the map above.
AXES = ["FOUNDATIONS", "AGENTIC AI", "PARALLEL COMPUTE",
        "GENERATIVE AI", "MACHINE LEARNING", "COMPUTER VISION"]

effort = Counter()
for repo in stats["repo_list"]:
    effort[repo["region"]] += repo["commits"]
peak_effort = max(effort.values()) or 1


def vessel(cx, cy, r, frac, idx, eyes=True):
    """The Soul orb. Liquid behind a rough carved rim, with the eye holes cut
    into the bowl rather than the liquid, so the face reads at any level."""
    frac = max(0.0, min(1.0, frac))
    level = cy + r - 2 * r * frac
    out = [f'<clipPath id="lvl{idx}"><rect x="{cx-r}" y="{level:.1f}" '
           f'width="{2*r}" height="{2*r}"/></clipPath>',
           f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{SOUL}" opacity=".14" '
           f'filter="url(#glowWide)"/>',
           f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#0A1018"/>',
           f'<g clip-path="url(#lvl{idx})">',
           f'  <circle cx="{cx}" cy="{cy}" r="{r*0.94:.1f}" fill="{LIQUID}"/>',
           '</g>']
    if frac > 0.05:                       # light catching the surface
        half = (r ** 2 - (level - cy) ** 2) ** 0.5 if abs(level - cy) < r else r * .4
        out.append(f'<rect class="shimmer" x="{cx-half*.78:.1f}" '
                   f'y="{level:.1f}" width="{half*1.56:.1f}" height="2.2" '
                   f'fill="#FFFFFF" opacity=".35"/>')
    if eyes:
        k = r * 0.0056                    # the shell sits in the bowl, not over it
        out.append(f'<g transform="translate({cx - 110*k:.1f},{cy - 122*k:.1f}) '
                   f'scale({k:.4f})">')
        out.append(f'  <path d="{ORB_MASK}" fill="#05070C"/>')
        out.append(f'  <path d="{ORB_MASK}" fill="none" stroke="{BONE}" '
                   f'stroke-width="{4/k:.1f}" stroke-opacity=".35"/>')
        out.append('</g>')

    # The rim is carved, not drawn — two rough passes rather than one clean one.
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" '
               f'stroke="#05070C" stroke-width="{max(2.6, r*0.10):.1f}" '
               f'filter="url(#ink)"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{BONE}" '
               f'stroke-width="{max(1.2, r*0.028):.1f}" opacity=".55" '
               f'filter="url(#ink)"/>')
    return "".join(out)


def spider(cx, cy, s=1.0):
    """The weaver, small, where a web's owner sits."""
    out = [f'<g stroke="{BONE}" stroke-width="{1.1*s:.1f}" fill="none" '
           f'stroke-linecap="round" opacity=".7">']
    for sx in (-1, 1):
        for dx, dy, bx, by in ((7, -6, 13, -12), (8, -1, 15, -3),
                               (8, 4, 14, 8), (6, 8, 10, 15)):
            out.append(f'<path d="M {cx+sx*2*s:.1f} {cy:.1f} '
                       f'Q {cx+sx*dx*s:.1f} {cy+dy*s:.1f} '
                       f'{cx+sx*bx*s:.1f} {cy+by*s:.1f}"/>')
    out.append('</g>')
    out.append(f'<ellipse cx="{cx:.1f}" cy="{cy+4*s:.1f}" rx="{5.2*s:.1f}" '
               f'ry="{6.4*s:.1f}" fill="#05070C" stroke="{BONE}" '
               f'stroke-width="{1*s:.1f}" stroke-opacity=".55"/>')
    out.append(f'<ellipse cx="{cx:.1f}" cy="{cy-4.5*s:.1f}" rx="{3.4*s:.1f}" '
               f'ry="{3.2*s:.1f}" fill="#05070C" stroke="{BONE}" '
               f'stroke-width="{1*s:.1f}" stroke-opacity=".55"/>')
    return "".join(out)


def web(cx, cy, R):
    """A radar chart is a spider chart, so it is drawn as a web: the rings sag
    inward between anchor threads, the way silk hangs between them."""
    n = len(AXES)
    ang = [math.radians(-90 + i * 360 / n) for i in range(n)]
    pt = lambda a, r: (cx + math.cos(a) * r, cy + math.sin(a) * r)
    out = []

    # A web is not a hexagon. The rings sag between *every* spoke, and there
    # are far more spokes than data axes, so the silk scallops finely instead
    # of reading as a wireframe box.
    spokes = [math.radians(-90 + i * 360 / (n * 4)) for i in range(n * 4)]
    for ring in (0.17, 0.31, 0.45, 0.6, 0.76, 0.92, 1.0):
        r = R * ring
        d = []
        for i, a in enumerate(spokes):
            b = spokes[(i + 1) % len(spokes)]
            x1, y1 = pt(a, r)
            mx, my = pt(a + math.radians(360 / len(spokes) / 2), r * 0.94)
            x2, y2 = pt(b, r)
            d.append(f"{'M' if not i else 'L'} {x1:.1f} {y1:.1f} "
                     f"Q {mx:.1f} {my:.1f} {x2:.1f} {y2:.1f}")
        out.append(f'<path d="{" ".join(d)} Z" fill="none" stroke="{BONE}" '
                   f'stroke-width="{0.9 if ring == 1 else 0.6}" '
                   f'opacity="{.3 if ring == 1 else .13}" filter="url(#ink)"/>')

    # Fine radials first, then the six anchor threads the data hangs from.
    for a in spokes:
        x, y = pt(a, R)
        out.append(f'<path d="M {cx} {cy} L {x:.1f} {y:.1f}" stroke="{BONE}" '
                   f'stroke-width="0.55" opacity=".1"/>')

    # What was woven: commits per area.
    pts = [pt(a, R * effort[name] / peak_effort) for a, name in zip(ang, AXES)]
    shape = " ".join(f"{'M' if not i else 'L'} {x:.1f} {y:.1f}"
                     for i, (x, y) in enumerate(pts)) + " Z"
    out.append(f'<path d="{shape}" fill="{SOUL}" opacity=".13"/>')
    out.append(f'<path d="{shape}" fill="none" stroke="{SOUL}" stroke-width="6" '
               f'opacity=".28" filter="url(#glowMed)"/>')
    out.append(f'<path d="{shape}" fill="none" stroke="{SOUL}" stroke-width="1.9" '
               f'opacity=".95" filter="url(#bloomSoft)"/>')
    for x, y in pts:
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{SOUL}" '
                   f'filter="url(#bloomSoft)"/>')

    out.append(spider(cx, cy))

    for a, name in zip(ang, AXES):
        lx, ly = pt(a, R + 34)
        cosa = math.cos(a)
        anchor = "middle" if abs(cosa) < 0.3 else ("start" if cosa > 0 else "end")
        out.append(caps(lx, ly, name, size=9.5, track=1.8, anchor=anchor,
                        opacity=.85))
        out.append(prose(lx, ly + 15, f"{effort[name]} commits", size=11,
                         anchor=anchor, opacity=.68))
    return "".join(out)


svg = [lantern(W, H)]
svg.append(section("The Ledger",
                   "What there is, where the work went, and when it happened."))

# ── Counters ──────────────────────────────────────────────────────────────
for i, (value, label) in enumerate(COUNTS):
    x = 72 + i * 178
    svg.append(numeral(x, 194, commas(value), size=46))
    svg.append(caps(x, 218, label, size=10.5, track=2.6, fill=ASH))
    if i:
        svg.append(f'<path d="M {x - 30} 158 L {x - 30} 214" stroke="{BONE}" '
                   f'stroke-width="1" opacity=".13"/>')

# ── The vessel, and one smaller vessel per year ───────────────────────────
svg.append(vessel(168, 360, 68, years.get(now, 0) / best, 0))
svg.append(caps(168, 460, f"{now} so far · {years.get(now, 0)} commits",
                size=10.5, track=2.4, fill=SOUL, anchor="middle", glow=True))
svg.append(prose(168, 479, f"against {best}, the best year", size=11.5,
                 anchor="middle", opacity=.7))

for i, (year, n) in enumerate(sorted(years.items())):
    cy = 310 + i * 50
    svg.append(vessel(290, cy, 18, n / best, 10 + i, eyes=False))
    svg.append(caps(318, cy - 2, year, size=10.5, track=2.2, opacity=.9))
    svg.append(prose(318, cy + 13, f"{n} commits", size=11, opacity=.72))

# ── The web ───────────────────────────────────────────────────────────────
svg.append(caps(856, 172, "Where the work went", size=10.5, track=2.8,
                fill=ASH, anchor="middle"))
svg.append(web(856, 360, 126))

# ── Commits by hour ───────────────────────────────────────────────────────
BASE, TALL, X0, SPAN = 596, 52, 72, 1056
SLOT = SPAN / 24
svg.append(caps(X0, 536, "Every commit, by hour", size=10.5, track=2.8, fill=ASH))
svg.append(caps(1128, 536, f"busiest at {peak:02d}:00", size=10.5, track=2.8,
                fill=SOUL, anchor="end", glow=True))

top = max(hours) or 1
svg.append('<g filter="url(#ink)">')
for h, count in enumerate(hours):
    x = X0 + h * SLOT
    height = max(2.5, count / top * TALL)
    lit = h == peak
    if lit:
        svg.append(f'  <rect class="breathe" x="{x:.1f}" y="{BASE-height:.1f}" '
                   f'width="{SLOT*0.68:.1f}" height="{height:.1f}" fill="{SOUL}" '
                   f'opacity=".5" filter="url(#glowMed)"/>')
    svg.append(f'  <rect x="{x:.1f}" y="{BASE - height:.1f}" '
               f'width="{SLOT*0.68:.1f}" height="{height:.1f}" '
               f'fill="{SOUL if lit else BONE}" '
               f'opacity="{0.95 if lit else 0.42}"/>')
svg.append('</g>')
svg.append(f'<path d="M {X0} {BASE+1} L {X0+SPAN} {BASE+1}" stroke="{BONE}" '
           f'stroke-width="1" opacity=".22"/>')
for h in (0, 6, 12, 18):
    svg.append(prose(X0 + h * SLOT + SLOT * .34, BASE + 19, f"{h:02d}", size=11,
                     anchor="middle", opacity=.65))
svg.append(prose(1128, BASE + 19, f"{sum(hours)} commits · local time", size=11,
                 anchor="end", opacity=.65))

svg.append(motes(90, 150, 1030, 330, n=16, seed=17))
