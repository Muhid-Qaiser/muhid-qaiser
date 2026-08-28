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
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from theme import *

ROOT = Path(__file__).resolve().parent.parent
W, H = 1200, 960
DEFS = ""

stats = json.loads((ROOT / "data" / "stats.json").read_text(encoding="utf-8"))

hours = stats["hours"]
peak = hours.index(max(hours))
years = stats["commits_by_year"]
best = max(years.values()) if years else 1
now = max(years) if years else "—"

# Soul in the HUD is near-white with only a breath of cold in it.
LIQUID = "#F3ECEC"

# The same shell drawn in the masthead, in its own 220x250 box.
ORB_MASK = (
    "M 34 120 "
    "C 22 90, 14 56, 7 26 C 5 19, 15 16, 19 24 C 31 56, 50 86, 70 98 "
    "C 84 76, 136 76, 150 98 "
    "C 170 86, 189 56, 201 24 C 205 16, 215 19, 213 26 C 206 56, 198 90, 186 120 "
    "C 188 164, 168 212, 110 236 C 52 212, 32 164, 34 120 Z"
)

COUNTS = [(v, k) for v, k in (
    (stats["repos"],              "Repos"),
    (stats["pull_requests"],      "Pull requests"),
    (stats["streak_best"],        "Longest streak"),
    (stats["contributions_year"], "Last 12 months"),
) if v > 0]

# Six account-wide figures, largest first, clockwise from the top.
# Issues, gists and reviews are all zero on this account, so they are left
# off: three flat spokes would read as inactivity rather than as absence.
METRICS = [
    ("COMMITS",       stats["commits"]),
    ("REPOS",         stats["repos"]),
    ("REPOS STARRED", stats["starred"]),
    ("LAST 12 MONTHS", stats["contributions_year"]),
    ("PULL REQUESTS", stats["pull_requests"]),
]
# These span 241 down to 6. On one linear radius everything but commits
# collapses to a sliver, so the reach is logarithmic and every spoke prints
# its exact figure — the shape indexes, the numbers tell the truth.
# A spoke that could not be fetched drops out rather than plotting zero — a
# zero here is a statement about the account, not about the fetch.
METRICS = [(n, v) for n, v in METRICS if v > 0]
_TOP = math.log(1 + max(v for _, v in METRICS))
reach = lambda v: math.log(1 + v) / _TOP


def blob(cx, cy, r):
    """The meter is not a circle. Its silhouette wanders a little, which is
    most of why the sprite reads as carved rather than drawn."""
    wob = (1.0, 0.975, 1.025, 0.99, 1.015, 0.97, 1.02, 0.995)
    pts = []
    for i, k in enumerate(wob):
        a = math.radians(i * 45)
        pts.append((cx + math.cos(a) * r * k, cy + math.sin(a) * r * k))
    d = [f"M {pts[0][0]:.1f} {pts[0][1]:.1f}"]
    for i in range(len(pts)):
        nxt = pts[(i + 1) % len(pts)]
        a = math.radians(i * 45 + 22.5)
        cr = r * 1.09
        d.append(f"Q {cx + math.cos(a) * cr:.1f} {cy + math.sin(a) * cr:.1f} "
                 f"{nxt[0]:.1f} {nxt[1]:.1f}")
    return " ".join(d) + " Z"


def vessel(cx, cy, r, frac, idx, eyes=True, drain=False):
    """The Soul meter, after the game's own sprite.

    No rim and no outline — it is a soft mass of near-white with a bloom
    around it. The eye holes are large, set low and wide, and tilted outward;
    they are dark slate rather than black, so they read as holes against both
    the empty bowl and the liquid rising past them.
    """
    frac = max(0.0, min(1.0, frac))
    level = cy + r - 2 * r * frac
    shape = blob(cx, cy, r)
    out = [f'<path d="{shape}" fill="{LIQUID}" opacity=".3" '
           f'filter="url(#glowWide)"/>',
           f'<clipPath id="lvl{idx}"><path d="{shape}"/></clipPath>',
           f'<path d="{shape}" fill="#0B111C"/>']

    # Soul is a liquid, so the surface is a wave, not a straight edge. The
    # crest travels exactly one wavelength and repeats, which makes the loop
    # seamless; the body is drawn wider than the bowl so no edge is ever
    # exposed as it slides.
    wl, amp = 40, max(1.6, r * 0.045)
    x0, span = cx - r - wl, 2 * r + 2 * wl
    body = [f"M {x0:.1f} {level:.1f}"]
    x = x0
    while x < x0 + span:
        body.append(f"q {wl/4:.1f} {-amp:.1f} {wl/2:.1f} 0 "
                    f"q {wl/4:.1f} {amp:.1f} {wl/2:.1f} 0")
        x += wl
    body.append(f"L {x:.1f} {cy + r * 2.2:.1f} L {x0:.1f} {cy + r * 2.2:.1f} Z")
    wave = " ".join(body)

    out.append(f'<g clip-path="url(#lvl{idx})">')
    if drain:
        # The meter is spent and gathered again, never emptied — the level
        # stays above the eye holes so the face reads throughout.
        out.append(f'  <g class="rise" style="--low:{r*0.5:.0f}px">')
    else:
        out.append('  <g>')
    out.append(f'    <g class="tide"><path d="{wave}" fill="{LIQUID}"/></g>')
    out.append('  </g>')
    out.append('</g>')

    if eyes:
        # Geometry measured off the game's own Soul_Meter sprite: the holes sit
        # low and wide — at ±0.47r across and +0.43r down, radius ~0.27r — which
        # is why a part-filled meter still reads as a face rather than as a
        # pair of eyes floating above a waterline.
        for sx in (-1, 1):
            ex, ey = cx + sx * r * .47, cy + r * .43
            out.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{r*.27:.1f}" '
                       f'ry="{r*.26:.1f}" fill="#232A3C" '
                       f'transform="rotate({sx*16} {ex:.1f} {ey:.1f})"/>')
    out.append(f'<path d="{shape}" fill="{LIQUID}" opacity=".16" '
               f'filter="url(#glowMed)"/>')
    return "".join(out)


def spider(cx, cy, s=1.0):
    """Hornet's mask, traced from the same line-art reference as the shell.

    Measured off it: 231 x 374, so h/w 1.62 — much taller and narrower than my
    earlier passes — symmetric rather than leaning, with the notch between the
    horns closing halfway down at y=81.8. The eyes are angled almonds set low,
    their long axes at about 52 and 128 degrees.

    Box is 100 x 162, scaled to the caller.
    """
    k = s * 0.26
    tx, ty = cx - 50 * k, cy - 81 * k
    mask = "M 31.6 0.4 L 26 5.2 L 19.9 14.7 L 7.8 40.7 L 0.9 68.8 L 0 95.2 L 1.7 106.9 L 5.2 119.5 L 14.3 137.2 L 22.9 147.2 L 30.7 153.7 L 39.8 158.9 L 47.6 161.5 L 56.3 160.2 L 70.1 152.4 L 80.5 142.9 L 86.6 134.6 L 92.2 123.8 L 97 109.1 L 99.1 94.4 L 99.1 76.2 L 95.2 53.2 L 87.4 30.7 L 80.1 16 L 72.3 3.9 L 69.3 1.3 L 65.4 0 L 61 2.6 L 59.7 7.4 L 64.1 25.5 L 65.8 40.3 L 65.4 56.3 L 63.6 65.4 L 59.7 74.9 L 53.2 81.4 L 47.2 81.8 L 41.6 77.9 L 36.8 69.3 L 33.8 55.8 L 34.2 31.2 L 39.4 8.7 L 39 4.3 L 35.5 0.4 Z"
    out = [f'<g transform="translate({tx:.1f},{ty:.1f}) scale({k:.3f})">',
           f'  <path d="{mask}" fill="{SOUL}" opacity=".3" filter="url(#glowMed)"/>',
           f'  <path d="{mask}" fill="{LUMEN}"/>']
    for ex, rot in ((31.4, -38), (68.2, 38)):
        out.append(f'  <ellipse cx="{ex}" cy="134.4" rx="7.6" ry="12.4" '
                   f'fill="#0A0D14" transform="rotate({rot} {ex} 134.4)"/>')
    out.append('</g>')
    return "".join(out)


def web(cx, cy, R):
    """A radar chart is a spider chart, so it is drawn as a web: the rings sag
    inward between anchor threads, the way silk hangs between them."""
    n = len(METRICS)
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

    # What was woven: the account's own figures.
    pts = [pt(a, R * reach(v)) for a, (_, v) in zip(ang, METRICS)]
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

    out.append(spider(cx, cy, 1.5))

    for a, (name, value) in zip(ang, METRICS):
        # One order everywhere: name above, figure below. Straight up that
        # needs extra clearance, because the figure hangs 30px down and the
        # polygon reaches full radius on that spoke.
        lx, ly = pt(a, R + (58 if math.sin(a) < -0.5 else 34))
        cosa = math.cos(a)
        anchor = "middle" if abs(cosa) < 0.3 else ("start" if cosa > 0 else "end")
        out.append(caps(lx, ly, name, size=16, track=1.3, anchor=anchor,
                        opacity=.85))
        out.append(numeral(lx, ly + 30, commas(value), size=30, anchor=anchor,
                           glow=False))
    return "".join(out)


svg = [lantern(W, H)]
svg.append(section("The Ledger"))

# ── The figures across the top, centred ───────────────────────────────────
# Positions and dividers both come from how many figures survived the
# zero-guard, so a dropped stat cannot leave a divider standing alone or
# pull the row off centre.
STEP = 260
row_x = [600 + (i - (len(COUNTS) - 1) / 2) * STEP for i in range(len(COUNTS))]
for x, (value, label) in zip(row_x, COUNTS):
    svg.append(numeral(x, 190, commas(value), size=58, anchor="middle"))
    svg.append(caps(x, 220, label, size=17, track=2.1, fill=ASH, anchor="middle"))
for a, b in zip(row_x, row_x[1:]):
    svg.append(f'<path d="M {(a+b)/2:.0f} 150 L {(a+b)/2:.0f} 204" '
               f'stroke="{BONE}" stroke-width="1" opacity=".13"/>')

# ── The vessel, left ──────────────────────────────────────────────────────
svg.append(vessel(200, 500, 68, 1.0, 0, drain=True))
svg.append(numeral(200, 630, commas(stats["commits"]), size=44, anchor="middle"))
svg.append(caps(200, 658, "commits gathered", size=16, track=2.1, fill=ASH,
                anchor="middle"))

for i, (year, n) in enumerate(sorted(years.items())):
    cy = 450 + i * 54
    svg.append(vessel(332, cy, 19, n / best, 10 + i, eyes=False))
    svg.append(caps(364, cy - 4, year, size=16, track=1.7, opacity=.95))
    svg.append(prose(364, cy + 17, f"{n} commits", size=17, opacity=.9))

# ── The web, right ────────────────────────────────────────────────────────
svg.append(web(884, 500, 130))

# ── Commits by hour, across the foot ──────────────────────────────────────
BASE, TALL, X0, SPAN = 862, 62, 72, 1056
SLOT = SPAN / 24
svg.append(caps(X0, 790, "Every commit, by hour of day (PKT)", size=17, track=2.3, fill=ASH))
svg.append(caps(1128, 790, f"most commits at {peak:02d}:00", size=17, track=2.3,
                fill=SOUL, anchor="end", glow=True))

top = max(hours) or 1
svg.append('<g filter="url(#bloomSoft)">')
for h, count in enumerate(hours):
    x = X0 + h * SLOT
    height = max(2.5, count / top * TALL)
    lit = h == peak
    if lit:
        svg.append(f'  <rect class="breathe" x="{x:.1f}" y="{BASE-height:.1f}" '
                   f'width="{SLOT*0.68:.1f}" height="{height:.1f}" fill="{SOUL}" '
                   f'opacity=".75" filter="url(#glowMed)"/>')
    svg.append(f'  <rect x="{x:.1f}" y="{BASE - height:.1f}" '
               f'width="{SLOT*0.68:.1f}" height="{height:.1f}" '
               f'fill="#FFFFFF" opacity="1"/>')
svg.append('</g>')
svg.append(f'<path d="M {X0} {BASE+1} L {X0+SPAN} {BASE+1}" stroke="{BONE}" '
           f'stroke-width="1" opacity=".22"/>')
for h in (0, 6, 12, 18):
    svg.append(prose(X0 + h * SLOT + SLOT * .34, BASE + 22, f"{h:02d}", size=17,
                     anchor="middle", opacity=.75))

svg.append(motes(90, 150, 1030, 620, n=22, seed=17))
