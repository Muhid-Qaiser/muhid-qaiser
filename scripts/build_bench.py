#!/usr/bin/env python3
"""assets/bench.svg — the closing note.

In Hallownest a bench is the one place that is safe: you sit, the map gets
written up, and you decide where to go next. It is the right shape for a
footer. The working links live in the README beneath it.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from theme import *

OUT = Path(__file__).resolve().parent.parent / "assets" / "bench.svg"
W, H = 1200, 210

svg = [head(W, H)]
svg.append('<ellipse cx="600" cy="150" rx="330" ry="150" fill="url(#lantern)"/>')

# Lamp above the bench, and the pool of light it throws.
svg.append(f'<path d="M 600 18 L 600 44" stroke="{BONE}" stroke-width="1.4" '
           f'opacity=".35"/>')
svg.append(f'<circle cx="600" cy="52" r="7" fill="{SOUL}" filter="url(#glowMed)" '
           f'class="breathe"/>')
svg.append(f'<ellipse cx="600" cy="150" rx="210" ry="46" fill="{SOUL}" '
           f'opacity=".07" filter="url(#glowWide)"/>')

# The bench: a slab, two legs, a low back.
svg.append('<g filter="url(#ink)">')
svg.append(f'  <rect x="512" y="126" width="176" height="10" rx="3" '
           f'fill="{CAVERN}" stroke="{BONE}" stroke-width="1.3" '
           f'stroke-opacity=".55"/>')
for x in (536, 652):
    svg.append(f'  <rect x="{x}" y="136" width="11" height="30" rx="2" '
               f'fill="{CAVERN}" stroke="{BONE}" stroke-width="1.2" '
               f'stroke-opacity=".45"/>')
svg.append(f'  <path d="M 528 126 L 528 96 Q 600 84, 672 96 L 672 126" '
           f'fill="none" stroke="{BONE}" stroke-width="1.4" stroke-opacity=".4"/>')
svg.append('</g>')

svg.append(motes(500, 60, 200, 110, n=14, seed=23))

svg.append(caps(600, 196, "Rest here", size=13, track=5, fill=SOUL,
                anchor="middle"))
svg.append(vignette(W, H))
svg.append(tail())

OUT.write_text("\n".join(svg), encoding="utf-8")
print(f"wrote {OUT} ({W}x{H})")
