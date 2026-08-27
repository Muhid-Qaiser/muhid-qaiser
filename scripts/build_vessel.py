#!/usr/bin/env python3
"""assets/vessel.svg — the masthead.

A vessel is a shell built to hold something that must not get out. The seal on
this one has failed and the light inside is escaping. That is the whole job
description, so it is the whole picture.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from theme import *

W, H = 1200, 420
OUT = Path(__file__).resolve().parent.parent / "assets" / "vessel.svg"

# Mask drawn in a local 220x240 box, then placed. Horns thick at the base,
# sweeping outward before they rise; a shallow dome between them; cheeks
# tapering to a blunt chin.
MASK = (
    "M 34 120 "
    "C 22 90, 14 56, 7 26 C 5 19, 15 16, 19 24 C 31 56, 50 86, 70 98 "
    "C 84 76, 136 76, 150 98 "
    "C 170 86, 189 56, 201 24 C 205 16, 215 19, 213 26 C 206 56, 198 90, 186 120 "
    "C 188 164, 168 212, 110 236 C 52 212, 32 164, 34 120 Z"
)

# The failed seal, running the centre line between the eyes. A shell that
# opens is no longer a shell.
CRACK = "M 111 90 L 106 116 L 114 142 L 107 170 L 115 196 L 110 218"
BRANCH_A = "M 108 104 L 122 99"
BRANCH_B = "M 107 170 L 92 182"

svg = [head(W, H, extra_defs=f"""
  <linearGradient id="shell" x1="0" y1="0" x2="0.35" y2="1">
    <stop offset="0%" stop-color="#FFFDF6"/>
    <stop offset="55%" stop-color="{BONE}"/>
    <stop offset="100%" stop-color="#B9BDC4"/>
  </linearGradient>""")]

# Lantern light behind the shell.
svg.append('<ellipse cx="978" cy="200" rx="360" ry="270" fill="url(#lantern)"/>')

svg.append('<g transform="translate(846,46) scale(1.24)">')
svg.append(f'  <path d="{MASK}" fill="{SOUL}" opacity=".2" filter="url(#glowWide)"/>')
svg.append('  <g filter="url(#inkSoft)">')
svg.append(f'    <path d="{MASK}" fill="url(#shell)"/>')
svg.append(f'    <path d="{MASK}" fill="none" stroke="#6E7686" stroke-width="1.5" '
           f'opacity=".55"/>')
# Eye voids. Nothing looks back out.
svg.append(f'    <ellipse cx="80" cy="143" rx="16" ry="28" fill="{VOID}" '
           f'transform="rotate(-9 80 143)"/>')
svg.append(f'    <ellipse cx="140" cy="143" rx="16" ry="28" fill="{VOID}" '
           f'transform="rotate(9 140 143)"/>')
# Shading down the left cheek so the shell has a side that is turned away.
svg.append(f'    <path d="M 46 104 C 38 118, 36 136, 39 156 C 42 190, 58 214, 82 224 '
           f'C 57 202, 47 168, 48 134 Z" fill="#39404E" opacity=".3"/>')
svg.append('  </g>')

# The breach: dark fracture cut first, then the light coming through it.
for path, w in ((CRACK, 3.4), (BRANCH_A, 2.2), (BRANCH_B, 2.2)):
    svg.append(f'  <path d="{path}" fill="none" stroke="#2A3040" stroke-width="{w}" '
               f'stroke-linecap="round" stroke-linejoin="round"/>')
svg.append('  <g style="mix-blend-mode:screen">')
for flt, width, op in (("glowWide", 16, .75), ("glowMed", 7, .95)):
    for path in (CRACK, BRANCH_A, BRANCH_B):
        svg.append(f'    <path d="{path}" fill="none" stroke="{SOUL}" '
                   f'stroke-width="{width}" stroke-linecap="round" '
                   f'stroke-linejoin="round" opacity="{op}" filter="url(#{flt})"/>')
svg.append('  </g>')
for path, w in ((CRACK, 2.8), (BRANCH_A, 1.6), (BRANCH_B, 1.6)):
    svg.append(f'  <path d="{path}" fill="none" stroke="#DEFBFF" stroke-width="{w}" '
               f'stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)" '
               f'class="breathe"/>')
svg.append('</g>')

# Spores lifting out of the fracture.
svg.append(motes(965, 120, 70, 240, n=18, seed=11))

# -- Masthead lettering --------------------------------------------------
svg.append(f'<g filter="url(#glowWide)" opacity=".38">'
           f'{caps(72, 158, "Muhid Qaiser", size=46, track=9, fill=SOUL)}</g>')
svg.append(caps(72, 158, "Muhid Qaiser", size=46, track=9, fill=BONE))
svg.append(f'<path d="M 72 182 L 536 182" stroke="{BONE}" stroke-width="1.4" '
           f'opacity=".28" filter="url(#ink)"/>')

svg.append(prose(72, 221,
                 "AI Security Engineer. I red-team large language models "
                 "and the agents built on them.",
                 size=17.5, fill=BONE, italic=False))
svg.append(prose(72, 253,
                 "Before this, computer vision — where adversarial examples "
                 "were first found."))
svg.append(prose(72, 279,
                 "The method did not change when the input became language."))

svg.append(f'<path d="M 73 315 L 73 351" stroke="{SOUL}" stroke-width="2" opacity=".75"/>')
svg.append(caps(92, 330, "A vessel is only as good as its seal", size=11.5,
                track=3.6, fill=SOUL))
svg.append(prose(92, 351, "Islamabad, Pakistan", size=13, fill=ASH))

svg.append(vignette(W, H))
svg.append(tail())

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(svg), encoding="utf-8")
print(f"wrote {OUT}")
