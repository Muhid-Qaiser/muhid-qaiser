#!/usr/bin/env python3
"""assets/ledger.svg — the counters, and the hours the work actually happened.

Deliberately no lines-of-code total. This account is largely Jupyter
notebooks, whose committed JSON carries base64 image output, so an additions
figure would measure the file format rather than the work. Everything counted
here is a thing that was made or a commit that was pushed.
"""
import json, sys
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from theme import *

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "ledger.svg"
W, H = 1200, 372

stats = json.loads((ROOT / "data" / "stats.json").read_text(encoding="utf-8"))
since = date.fromisoformat(stats["since"])
years = (date.today() - since).days // 365

COUNTS = [
    (stats["repos"],          "Repositories"),
    (stats["commits"],        "Commits"),
    (stats["scratch_builds"], "From scratch"),
    (len(stats["regions"]),   "Regions mapped"),
    (years,                   "Years on record"),
]

hours = stats["hours"]
peak = hours.index(max(hours))

svg = [head(W, H)]
svg.append(section("The Ledger", "What is actually here, counted honestly."))

# ── Counters ──────────────────────────────────────────────────────────────
for i, (value, label) in enumerate(COUNTS):
    x = 72 + i * 216
    svg.append(numeral(x, 178, commas(value), size=46))
    svg.append(caps(x, 202, label, size=10.5, track=2.8, fill=ASH))
    if i:
        svg.append(f'<path d="M {x - 34} 142 L {x - 34} 200" stroke="{BONE}" '
                   f'stroke-width="1" opacity=".13"/>')

# ── Commits by hour ───────────────────────────────────────────────────────
BASE, TALL, SLOT = 322, 58, 44
svg.append(caps(72, 250, "Every commit, by hour", size=10.5, track=2.8, fill=ASH))
svg.append(caps(1128, 250, f"busiest at {peak:02d}:00", size=10.5, track=2.8,
                fill=SOUL, anchor="end", glow=True))

top = max(hours) or 1
svg.append('<g filter="url(#ink)">')
for h, count in enumerate(hours):
    x = 72 + h * SLOT
    height = max(2.5, count / top * TALL)
    lit = h == peak
    if lit:
        svg.append(f'  <rect x="{x}" y="{BASE - height:.1f}" width="30" '
                   f'height="{height:.1f}" fill="{SOUL}" opacity=".55" '
                   f'filter="url(#glowMed)"/>')
    svg.append(f'  <rect x="{x}" y="{BASE - height:.1f}" width="30" '
               f'height="{height:.1f}" fill="{SOUL if lit else BONE}" '
               f'opacity="{0.95 if lit else 0.42}"/>')
svg.append('</g>')
svg.append(f'<path d="M 72 {BASE + 1} L 1128 {BASE + 1}" stroke="{BONE}" '
           f'stroke-width="1" opacity=".22"/>')
for h in (0, 6, 12, 18):
    svg.append(prose(72 + h * SLOT + 15, BASE + 20, f"{h:02d}", size=11,
                     anchor="middle", opacity=.7))
svg.append(prose(1128, BASE + 20,
                 f"{sum(hours)} commits · local time", size=11,
                 anchor="end", opacity=.7))

svg.append(motes(90, 130, 1020, 190, n=16, seed=17))
svg.append(vignette(W, H))
svg.append(tail())

OUT.write_text("\n".join(svg), encoding="utf-8")
print(f"wrote {OUT} ({W}x{H})")
print("  rebuilt from scratch:",
      ", ".join(r["name"] for r in stats["repo_list"] if r["scratch"]))
