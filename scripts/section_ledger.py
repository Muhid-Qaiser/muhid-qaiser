#!/usr/bin/env python3
"""The ledger section — the counters, and the hours the work happened.

Built on Hollow Knight's Soul meter: a bowl that fills with pale liquid, with
two eye holes cut into it so a filled vessel reads as a face. The big one
holds the current year measured against the best year; the three small ones
are the Soul Vessels, one per year, each filled to its own share.

That is deliberate against the masthead. Up there a vessel has cracked and is
losing what it held. Down here one is filling.

Deliberately no lines-of-code total. This account is largely Jupyter
notebooks, whose committed JSON carries base64 image output, so an additions
figure would measure the file format rather than the work. Everything counted
here is a thing that was made or a commit that was pushed.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from theme import *

ROOT = Path(__file__).resolve().parent.parent
W, H = 1200, 470
DEFS = ""

stats = json.loads((ROOT / "data" / "stats.json").read_text(encoding="utf-8"))

hours = stats["hours"]
peak = hours.index(max(hours))
years = stats["commits_by_year"]
best = max(years.values()) if years else 1
now = max(years) if years else "—"

COUNTS = [
    (stats["repos"],          "Repositories"),
    (stats["commits"],        "Commits"),
    (stats["scratch_builds"], "From scratch"),
]


def vessel(cx, cy, r, frac, idx, eyes=True):
    """A Soul vessel. The eye holes are cut into the bowl rather than into the
    liquid, so the face reads at any level and the liquid rises behind it."""
    frac = max(0.0, min(1.0, frac))
    level = cy + r - 2 * r * frac
    out = [f'<clipPath id="lvl{idx}"><rect x="{cx-r}" y="{level:.1f}" '
           f'width="{2*r}" height="{2*r}"/></clipPath>',
           f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#101827"/>',
           f'<g clip-path="url(#lvl{idx})">',
           f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="{SOUL}" opacity=".92"/>',
           '</g>']
    if frac > 0.04:                       # light catching the surface
        half = (r ** 2 - (level - cy) ** 2) ** 0.5 if abs(level - cy) < r else r * .4
        out.append(f'<rect class="shimmer" x="{cx-half*.8:.1f}" '
                   f'y="{level:.1f}" width="{half*1.6:.1f}" height="2.4" '
                   f'fill="#FFFFFF" opacity=".3"/>')
    if eyes:
        for sx in (-1, 1):
            ex = cx + sx * r * .33
            ey = cy - r * .10
            out.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{r*.17:.1f}" '
                       f'ry="{r*.28:.1f}" fill="#06090F" '
                       f'transform="rotate({sx*8} {ex:.1f} {ey:.1f})"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{SOUL}" '
               f'stroke-width="{max(1.4, r*0.035):.1f}" opacity=".8" '
               f'filter="url(#bloomSoft)"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{SOUL}" opacity=".1" '
               f'filter="url(#glowWide)"/>')
    return "".join(out)


svg = [lantern(W, H)]
svg.append(section("The Ledger", "What there is, and when it happened."))

# ── The vessel, and one smaller vessel per year ───────────────────────────
svg.append(vessel(196, 292, 78, years.get(now, 0) / best, 0))
svg.append(caps(196, 400, f"{now} so far · {years.get(now, 0)} commits",
                size=11, track=2.6, fill=SOUL, anchor="middle", glow=True))
svg.append(prose(196, 420, f"against {best}, the best year", size=12,
                 anchor="middle", opacity=.7))

for i, (year, n) in enumerate(sorted(years.items())):
    cy = 236 + i * 62
    svg.append(vessel(320, cy, 23, n / best, 10 + i, eyes=False))
    svg.append(caps(352, cy - 2, year, size=11, track=2.4, opacity=.9))
    svg.append(prose(352, cy + 14, f"{n} commits", size=11.5, opacity=.72))

# ── Counters ──────────────────────────────────────────────────────────────
for i, (value, label) in enumerate(COUNTS):
    x = 474 + i * 214
    svg.append(numeral(x, 220, commas(value), size=52))
    svg.append(caps(x, 246, label, size=10.5, track=2.6, fill=ASH))
    if i:
        svg.append(f'<path d="M {x - 36} 180 L {x - 36} 242" stroke="{BONE}" '
                   f'stroke-width="1" opacity=".13"/>')

# ── Commits by hour ───────────────────────────────────────────────────────
BASE, TALL, X0, SPAN = 404, 66, 474, 654
SLOT = SPAN / 24
svg.append(caps(X0, 320, "Every commit, by hour", size=10.5, track=2.8, fill=ASH))
svg.append(caps(1128, 320, f"busiest at {peak:02d}:00", size=10.5, track=2.8,
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

svg.append(motes(90, 150, 1030, 210, n=16, seed=17))
