#!/usr/bin/env python3
"""assets/profile.svg — the whole profile as one continuous picture.

The three sections used to be three images, which meant GitHub put a band of
page background between them and the thing read as a stack of panels. They are
now one document: one ground, one set of filters, one vignette drawn only at
the outer edges, and each section translated into place so it keeps its own
local coordinates.

Import order is the reading order down the page.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from theme import document

# A merge can leave conflict markers in data/stats.json, which parses as a
# JSONDecodeError three imports later with a traceback that says nothing
# useful. Fail here instead, with the reason.
_stats = Path(__file__).resolve().parent.parent / "data" / "stats.json"
try:
    json.loads(_stats.read_text(encoding="utf-8"))
except json.JSONDecodeError as exc:
    raise SystemExit(
        f"{_stats} is not valid JSON ({exc}). "
        "If a merge left conflict markers in it, re-run scripts/fetch_stats.py "
        "to overwrite it with fresh data.")

import section_vessel, section_map, section_ledger

OUT = Path(__file__).resolve().parent.parent / "assets" / "profile.svg"
W = 1200

SECTIONS = [section_vessel, section_map, section_ledger]

svg = document(
    W,
    [(s.H, s.svg) for s in SECTIONS],
    extra_defs="".join(s.DEFS for s in SECTIONS),
)

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(svg, encoding="utf-8")

total = sum(s.H for s in SECTIONS)
print(f"wrote {OUT} ({W}x{total})")
for s in SECTIONS:
    print(f"  {s.__name__.replace('section_', ''):10} {s.H:>5}px")
