#!/usr/bin/env python3
"""The ledger section: the HUD, the web, and the hours as Crystal Peak.

The web is Deepnest: a radar chart drawn as silk, rings sagging between
anchor threads, on a logarithmic reach so every spoke prints its figure.

Every figure is read from data/stats.json, which the repo's nightly workflow
rewrites at 03:23 UTC. Nothing here is typed in by hand, and the layout is
sized from the data as well, so growth cannot break it:

- masks: one per day of the longest streak, capped at nine, the most the
  Knight can ever carry; the exact figures are printed beside them
- labels sit after their figures at the figures' measured width, so a
  four-digit count pushes its label along instead of running into it
- year vessels: the most recent four years, whatever they are
- the hour chart: each hour gets one of six crystal sprites, chosen by bands
  of commits per hour that are defined by their lower bounds only (BANDS).
  The top band, the Crown, has no ceiling, so any count lands in a band. The
  legend prints the bands.

"""
import json, math, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from theme import *
import section_vessel as SV

ROOT = Path(__file__).resolve().parent.parent
W, H = 1200, 860
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

# Five account-wide figures, largest first, clockwise from the top.
# Issues, gists and reviews are all zero on this account, so they are left
# off: three flat spokes would read as inactivity rather than as absence.
METRICS = [
    ("COMMITS",       stats["commits"]),
    ("REPOS",         stats["repos"]),
    ("REPOS STARRED", stats["starred"]),
    ("12-M COMMITS", stats["year"]["commits"]),
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


def vessel(cx, cy, r, frac, idx, eyes=True):
    """The Soul meter, after the game's own sprite.

    No rim and no outline — it is a soft mass of near-white with a bloom
    around it. The eye holes are large, set low and wide, and tilted outward;
    they are dark slate rather than black, so they read as holes against both
    the empty bowl and the liquid rising past them.
    """
    frac = max(0.0, min(1.0, frac))
    level = cy + r - 2 * r * frac
    shape = blob(cx, cy, r)
    wide = "glowWideT" if r >= 45 else "glowWide"
    med = "glowMedT" if r >= 45 else "glowMed"
    out = [f'<path d="{shape}" fill="{LIQUID}" opacity=".3" '
           f'filter="url(#{wide})"/>',
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
    out.append('  <g>')
    # The large meter moves; the tiny yearly vessels are too small for their
    # individual wave motion to read, but each still reflects its real level.
    tide = ' class="tide"' if r >= 45 else ""
    out.append(f'    <g{tide}><path d="{wave}" fill="{LIQUID}"/></g>')
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
               f'filter="url(#{med})"/>')
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
    # Silk is never spun to a true circle. That unevenness used to come from
    # an ink displacement at paint time — seven turbulence passes for a
    # hairline. It is baked into the radii instead, from a fixed seed, and the
    # wobble is carried per spoke rather than per vertex so consecutive
    # segments still meet and the stroke does not develop kinks.
    jr = random.Random(808)
    for ring in (0.17, 0.31, 0.45, 0.6, 0.76, 0.92, 1.0):
        r = R * ring
        sway = [1 + jr.uniform(-0.016, 0.016) for _ in spokes]
        d = []
        for i, a in enumerate(spokes):
            j = (i + 1) % len(spokes)
            x1, y1 = pt(a, r * sway[i])
            mx, my = pt(a + math.radians(360 / len(spokes) / 2),
                        r * 0.94 * (sway[i] + sway[j]) / 2)
            x2, y2 = pt(spokes[j], r * sway[j])
            d.append(f"{'M' if not i else 'L'} {x1:.1f} {y1:.1f} "
                     f"Q {mx:.1f} {my:.1f} {x2:.1f} {y2:.1f}")
        out.append(f'<path d="{" ".join(d)} Z" fill="none" stroke="{BONE}" '
                   f'stroke-width="{0.9 if ring == 1 else 0.6}" '
                   f'opacity="{.3 if ring == 1 else .13}"/>')

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
               f'opacity=".28" filter="url(#glowMedT)"/>')
    out.append(f'<path d="{shape}" fill="none" stroke="{SOUL}" stroke-width="1.9" '
               f'opacity=".95" filter="url(#bloomT)"/>')
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


hours = stats["hours"]
top = max(hours)
peak = hours.index(top)
years = dict(sorted(stats["commits_by_year"].items())[-4:])
best = max(years.values()) if years else 1


def numeral_width(s, size):
    """Measured advance of the display face: about 0.62em a figure, 0.28em a comma."""
    return (len(s) - s.count(",")) * size * 0.62 + s.count(",") * size * 0.28


def mask(x, y, k, fill=BONE, stroke=None, sw=1.2, eyes=True, opacity=1):
    """The Knight's mask from the masthead, at scale k (box 100 x 109.5)."""
    st = f' stroke="{stroke}" stroke-width="{sw/k:.2f}"' if stroke else ""
    out = [f'<g transform="translate({x:.1f},{y:.1f}) scale({k:.3f})" opacity="{opacity}">',
           f'<path d="{SV.MASK}" fill="{fill}"{st} stroke-linejoin="round"/>']
    if eyes:
        for sx in (-1, 1):
            out.append(f'<circle cx="{SV.EYE_CX + sx*SV.EYE_DX}" cy="{SV.EYE_CY}" '
                       f'r="{SV.EYE_R}" fill="{VOID}"/>')
    out.append('</g>')
    return "".join(out)


def star4(cx, cy, r, fill=LUMEN, cls="", delay=None):
    d = (f"M {cx:.1f} {cy-r:.1f} Q {cx:.1f} {cy:.1f} {cx+r:.1f} {cy:.1f} Q {cx:.1f} {cy:.1f} {cx:.1f} {cy+r:.1f} "
         f"Q {cx:.1f} {cy:.1f} {cx-r:.1f} {cy:.1f} Q {cx:.1f} {cy:.1f} {cx:.1f} {cy-r:.1f} Z")
    c = f' class="{cls}"' if cls else ""
    st = f' style="animation-delay:{delay:.1f}s"' if delay is not None else ""
    return f'<path d="{d}" fill="{fill}"{c}{st}/>'


# ── Crystal sprites ───────────────────────────────────────────────────────
# Six drawings, stored once in defs and placed with <use>: twenty-four hours
# cost twenty-four references, not twenty-four copies of the geometry. Each
# sprite stands on y=0 and is centred on x=0.
DIM = ("#B98DB3", "#7A5277")
MID = ("#E2B4DA", "#A8739F")
LIT = ("#FBEAF8", "#E2B4DA")


def facet(cx, h, w, lean, light, dark, edge=None):
    """One crystal: a lit face and a shadowed face meeting on a ridge."""
    bl, br = cx - w / 2, cx + w / 2
    tx, ty = cx + lean, -h
    rx = cx + lean * 0.35
    left = f"M {bl:.1f} 0 L {bl:.1f} {-h*.68:.1f} L {tx:.1f} {ty:.1f} L {rx:.1f} 0 Z"
    right = f"M {rx:.1f} 0 L {tx:.1f} {ty:.1f} L {br:.1f} {-h*.74:.1f} L {br:.1f} 0 Z"
    out = f'<path d="{left}" fill="{light}"/><path d="{right}" fill="{dark}"/>'
    if edge:
        out += (f'<path d="M {bl:.1f} {-h*.68:.1f} L {tx:.1f} {ty:.1f}" stroke="{edge}" '
                f'stroke-width="1" opacity=".85"/>')
    return out


ROCK = '<path d="M -20 0 Q -16 -6 -6 -7 Q 6 -8 14 -5 Q 20 -3 21 0 Z" fill="#2E2638"/>'
TIERS = [
    # (name, sprite)
    ("Rubble",  '<path d="M -9 0 L -7 -3 L -3 -4 L -1 0 Z M 1 0 L 3 -2.5 L 7 -3 L 8 0 Z" fill="#3B3447"/>'),
    ("Shard",   facet(0, 18, 10, 2, *DIM)),
    ("Twin",    facet(-6, 18, 8, -3, *DIM) + facet(3, 34, 12, 2, *MID)),
    ("Cluster", facet(-9, 30, 9, -4, *MID) + facet(9, 38, 10, 4, *MID)
                + facet(0, 56, 14, 1, *MID, edge=LIT[0])),
    ("Spire",   ROCK + facet(-11, 30, 9, -5, *MID) + facet(11, 44, 11, 5, *MID)
                + facet(0, 84, 16, 2, *LIT, edge="#FFFFFF")),
    ("Crown",   '<ellipse cx="0" cy="-56" rx="40" ry="74" fill="url(#cryGlow)"/>'
                + ROCK + facet(-13, 40, 10, -6, *MID) + facet(13, 62, 12, 6, *LIT)
                + facet(0, 116, 18, 2, *LIT, edge="#FFFFFF")),
]
HEIGHT = [4, 18, 34, 56, 84, 116]
# The bands, by their lower bound only, in commits per hour. Each hour wears
# the crystal of the highest band it reaches. Nothing has an upper bound: the
# Crown runs from its floor to infinity, so no hour, however busy, can fall
# outside a band. Tune the floors here; the legend follows them.
BANDS = [0, 1, 10, 20, 35, 50]          # rubble, shard, twin, cluster, spire, crown


def tier_of(c):
    return max(t for t, floor in enumerate(BANDS) if c >= floor)


def ranges():
    """Each band as the legend prints it: 1-9, 10-19, ... 50+ (hi is None)."""
    out = []
    for t in range(1, len(BANDS)):
        hi = BANDS[t + 1] - 1 if t + 1 < len(BANDS) else None
        out.append((t, BANDS[t], hi))
    return out


DEFS = ('<radialGradient id="cryGlow"><stop offset="0%" stop-color="#F3B6E6" stop-opacity=".42"/>'
        '<stop offset="100%" stop-color="#F3B6E6" stop-opacity="0"/></radialGradient>'
        + "".join(f'<g id="cry{i}">{sprite}</g>' for i, (_, sprite) in enumerate(TIERS)))


svg = [lantern(W, H, cx=420, cy=300, rx=560, ry=300)]
svg.append(section("The Ledger"))

# ── HUD, left ─────────────────────────────────────────────────────────────
# The Soul orb holds the last twelve months against the best calendar year on
# record, so it drains in a quiet year and brims in a busy one. The figure under
# it is every commit ever gathered.
recent = stats["year"]["commits"]
brim = max([recent] + list(stats["commits_by_year"].values())) or 1
svg.append(vessel(180, 262, 62, recent / brim, 900))
svg.append(numeral(180, 366, commas(stats["commits"]), size=32, anchor="middle"))
svg.append(caps(180, 390, "commits gathered", size=13, track=2.4, fill=ASH, anchor="middle"))
svg.append(prose(180, 410, f"soul: {commas(recent)} in 12 months, of a best {commas(brim)}",
                 size=12, anchor="middle", opacity=.7))

# Masks: one per day of the longest streak, up to nine; the current run filled.
longest, current = stats["streak_best"], stats["streak_current"]
shown = max(1, min(longest, 9))
filled = min(current, shown)
mx, my, k, gap = 292, 172, 0.32, 42
for i in range(shown):
    x = mx + i * gap
    if i < filled:
        svg.append(f'<ellipse cx="{x+16}" cy="{my+17}" rx="28" ry="28" '
                   f'fill="url(#sporeCool)" opacity=".55"/>')
        svg.append(mask(x, my, k, fill=BONE))
    else:
        svg.append(mask(x, my, k, fill="#0B1019", stroke=BONE, sw=1.3, eyes=False, opacity=.55))
svg.append(caps(mx, my + 66, "streak", size=12, track=2.6, fill=ASH))
n = str(current)
svg.append(numeral(mx + 66, my + 66, n, size=16, glow=False))
svg.append(prose(mx + 74 + numeral_width(n, 16), my + 66,
                 f"of {longest} {'day' if longest == 1 else 'days'} at best", size=13, opacity=.8))

# Geo: pull requests are what the work was traded for.
gx, gy = mx + 8, my + 118
geo = (f"M {gx} {gy-14} L {gx+12} {gy-6} L {gx+12} {gy+6} L {gx} {gy+14} "
       f"L {gx-12} {gy+6} L {gx-12} {gy-6} Z")
svg.append(f'<path d="{geo}" fill="#0B1019" stroke="{BONE}" stroke-width="1.6"/>')
svg.append(f'<path d="M {gx-12} {gy-6} L {gx} {gy-1} L {gx+12} {gy-6} M {gx} {gy-1} L {gx} {gy+14}" '
           f'fill="none" stroke="{BONE}" stroke-width="1.1" opacity=".8"/>')
n = commas(stats["pull_requests"])
svg.append(numeral(gx + 26, gy + 9, n, size=30, glow=False))
svg.append(caps(gx + 40 + numeral_width(n, 30), gy + 9, "pull requests", size=12, track=2.4, fill=ASH))

# Year vessels: each year's Soul against the best of them.
for i, (year, c) in enumerate(years.items()):
    cx = mx + 26 + i * 104
    svg.append(vessel(cx, 372, 22, c / best, 910 + i, eyes=False))
    svg.append(caps(cx, 420, year, size=13, track=2, anchor="middle", opacity=.95))
    svg.append(prose(cx, 438, f"{commas(c)} commits", size=13, anchor="middle", opacity=.8))


# ── The web, right ────────────────────────────────────────────────────────
svg.append(web(930, 330, 116))

# ── Crystal Peak: commits by hour ─────────────────────────────────────────
BASE, X0, SPAN = 752, 72, 1056
SLOT = SPAN / 24
svg.append(caps(X0, 600, "Every commit, by hour of day (PKT)", size=15, track=2.3, fill=ASH))
svg.append(caps(W - MARGIN, 600, f"most commits at {peak:02d}:00", size=15, track=2.3,
                fill=SOUL, anchor="end", glow=True))
glints = []
for h, c in enumerate(hours):
    t = tier_of(c)
    cx = X0 + h * SLOT + SLOT / 2
    svg.append(f'<use href="#cry{t}" x="{cx:.1f}" y="{BASE}">'
               f'<title>{h:02d}:00, {commas(c)} {"commit" if c == 1 else "commits"}</title></use>')
    if t >= 4:
        glints.append((cx + 4, BASE - HEIGHT[t] * .55, t))
for i, (gx_, gy_, t) in enumerate(glints):
    svg.append(star4(gx_, gy_, 5 if t == 5 else 4, LUMEN, cls="glint", delay=-i * 1.0))
svg.append(f'<path d="{wobble(X0 - 10, BASE + 1, X0 + SPAN + 10, BASE + 1, amp=2.2, step=30, seed=19)}" '
           f'fill="none" stroke="{BONE}" stroke-width="1.2" opacity=".3"/>')
for h in (0, 6, 12, 18):
    svg.append(prose(X0 + h * SLOT + SLOT / 2, BASE + 24, f"{h:02d}", size=15, anchor="middle", opacity=.75))

# The legend: each sprite, small, with the commit range its threshold covers.
lx = X0
for t, lo, hi in ranges():
    svg.append(f'<use href="#cry{t}" transform="translate({lx + 10},{BASE + 80}) scale(.42)"/>')
    svg.append(caps(lx + 26, BASE + 64, TIERS[t][0], size=11, track=2.2,
                    fill=LUMEN if t == 5 else ASH, opacity=.9))
    rng = f"{lo}+" if hi is None else (f"{lo}" if lo == hi else f"{lo}\u2013{hi}")
    svg.append(prose(lx + 26, BASE + 80, f"{rng} {'commit' if hi == 1 else 'commits'}", size=12, opacity=.75))
    lx += 176
svg.append(prose(W - MARGIN, BASE + 80, "commits in that hour, all time", size=12,
                 anchor="end", opacity=.6))

svg.append(motes(90, 150, 1030, 560, n=22, seed=17))
