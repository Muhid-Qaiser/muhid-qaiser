#!/usr/bin/env python3
"""A restrained in-game ledger: four figures, one Soul meter, one rhythm."""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from theme import *

ROOT = Path(__file__).resolve().parent.parent
W, H = 1200, 850
DEFS = ""

stats = json.loads((ROOT / "data" / "stats.json").read_text(encoding="utf-8"))
hours = stats["hours"]
peak = hours.index(max(hours)) if hours else 0

COUNTS = [
    (stats["streak_current"], "Current streak"),
    (stats["streak_best"], "Longest streak"),
    (stats["pull_requests"], "Pull requests"),
    (stats["year"]["commits"], "12-M commits"),
]


def soul_meter(cx, cy, r, fraction):
    """One simplified HUD vessel. Only its liquid surface moves."""
    points = []
    wobble = (1.0, .97, 1.02, .985, 1.015, .975, 1.02, .99)
    for i, k in enumerate(wobble):
        angle = math.radians(i * 45)
        points.append((cx + math.cos(angle) * r * k,
                       cy + math.sin(angle) * r * k))
    d = [f"M {points[0][0]:.1f} {points[0][1]:.1f}"]
    for i in range(len(points)):
        next_x, next_y = points[(i + 1) % len(points)]
        angle = math.radians(i * 45 + 22.5)
        control_r = r * 1.09
        control_x = cx + math.cos(angle) * control_r
        control_y = cy + math.sin(angle) * control_r
        d.append(f"Q {control_x:.1f} {control_y:.1f} {next_x:.1f} {next_y:.1f}")
    shape = " ".join(d) + " Z"

    fraction = max(.12, min(1.0, fraction))
    level = cy + r - 2 * r * fraction
    x0 = cx - r - 40
    wave = (f"M {x0} {level:.1f} "
            + "q 10 -4 20 0 q 10 4 20 0 " * 7
            + f"L {cx+r+40} {cy+r+30} L {x0} {cy+r+30} Z")

    out = [
        f'<clipPath id="soulLevel"><path d="{shape}"/></clipPath>',
        f'<path d="{shape}" fill="#0D131D" stroke="#677386" '
        'stroke-width="1.3"/>',
        '<g clip-path="url(#soulLevel)">',
        f'<g class="tide"><path d="{wave}" fill="#E9E6DC"/></g>',
        '</g>',
    ]
    for sx in (-1, 1):
        ex, ey = cx + sx * r * .43, cy + r * .36
        out.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{r*.22:.1f}" '
                   f'ry="{r*.24:.1f}" fill="#202938" '
                   f'transform="rotate({sx*14} {ex:.1f} {ey:.1f})"/>')
    out.append(f'<path d="{shape}" fill="none" stroke="{BONE}" '
               'stroke-width="3" opacity=".72"/>')
    return "".join(out)


svg = []

# Four measures, aligned like a quiet game menu rather than boxed dashboard
# cards. The merged count is supporting evidence, not a fifth headline stat.
row_x = (175, 458, 742, 1025)
for x, (value, label) in zip(row_x, COUNTS):
    svg.append(caps(x, 84, label, size=17, track=1.7, fill=BONE,
                    anchor="middle", opacity=.82))
    svg.append(numeral(x, 157, commas(value), size=58, fill=BONE,
                       anchor="middle", glow=False))
for x in (316, 600, 884):
    svg.append(f'<path d="M {x} 66 L {x} 176" stroke="{BONE}" '
               'stroke-width="1" opacity=".18"/>')
svg.append(caps(742, 191, f'{stats["pull_requests_merged"]} merged',
                size=14, track=1.6, fill=ASH, anchor="middle", opacity=.82))

# The liquid level compares the rolling year with the strongest recorded year;
# the printed lifetime count remains literal and unscaled.
year_values = list(stats.get("commits_by_year", {}).values())
denominator = max(year_values + [stats["year"]["commits"], 1])
level = stats["year"]["commits"] / denominator
svg.append(soul_meter(600, 372, 76, level))
svg.append(f'<path d="M 492 339 Q 466 372 492 405 M 708 339 Q 734 372 708 405" '
           f'fill="none" stroke="{BONE}" stroke-width="1.4" opacity=".58"/>')
for x, y, rotate in ((477, 350, -28), (475, 394, 28),
                     (723, 350, 28), (725, 394, -28)):
    svg.append(f'<ellipse cx="{x}" cy="{y}" rx="3" ry="7" fill="{BONE}" '
               f'opacity=".62" transform="rotate({rotate} {x} {y})"/>')
svg.append(numeral(600, 530, commas(stats["commits"]), size=64,
                   fill=BONE, anchor="middle", glow=False))
svg.append(caps(600, 568, "commits gathered", size=17, track=2.2,
                fill=BONE, anchor="middle", opacity=.86))
svg.append('<path d="M 500 595 L 700 595 M 489 595 l 7 -7 7 7 -7 7 Z '
           'M 711 595 l -7 -7 -7 7 7 7 Z" fill="none" '
           f'stroke="{BONE}" stroke-width="1" opacity=".34"/>')

# A single useful chart remains: the account's working rhythm in PKT.
BASE, TALL, X0, SPAN = 790, 72, 72, 1056
SLOT = SPAN / 24
svg.append(caps(X0, 690, "Every commit, by hour of day (PKT)", size=16,
                track=1.9, fill=ASH, opacity=.9))
top = max(hours) if hours else 1
for hour, count in enumerate(hours):
    x = X0 + hour * SLOT + SLOT * .16
    height = max(3, count / top * TALL)
    colour = SOUL if hour == peak else BONE
    opacity = 1 if hour == peak else .82
    svg.append(f'<rect x="{x:.1f}" y="{BASE-height:.1f}" '
               f'width="{SLOT*.68:.1f}" height="{height:.1f}" '
               f'fill="{colour}" opacity="{opacity}"/>')
svg.append(f'<path d="M {X0} {BASE+1} L {X0+SPAN} {BASE+1}" '
           f'stroke="{BONE}" stroke-width="1" opacity=".28"/>')
for hour in (0, 6, 12, 18, 24):
    x = X0 + hour * SLOT
    anchor = "middle"
    if hour == 0:
        anchor = "start"
    elif hour == 24:
        anchor = "end"
    svg.append(prose(x, BASE + 29, f"{hour:02d}", size=16, fill=ASH,
                     italic=True, anchor=anchor, opacity=.78))
