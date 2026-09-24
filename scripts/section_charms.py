#!/usr/bin/env python3
"""The charms section: how the work is done, never what it is about.

The Map owns where, the Nail owns when, the Charms own how. Five real charms
at their real notch costs, ten of eleven notches, one left open. Each line
carries one engineering word inside the game's own cadence.
"""
import math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from theme import *

W = 1200

CHARM_H = 510
NOTCHES, USED = 11, 10

def g_quick_slash():
    # three nail arcs, each a little ahead of the last: the swing that does not wait
    arcs = "".join(
        f'<path d="M {-22+i*9} -24 A 30 30 0 0 1 {-22+i*9} 24" fill="none" stroke="{BONE}" '
        f'stroke-width="{3.2-i*.6:.1f}" stroke-linecap="round" opacity="{.35+i*.3:.2f}"/>' for i in range(3))
    return arcs + f'<path d="M 12 -6 L 26 0 L 12 6" fill="{LUMEN}"/>'

def g_spell_twister():
    pts = []
    for i in range(0, 121):
        t = i / 120
        a, r = t * math.pi * 4.6, 2 + t * 26
        pts.append(f"{r*math.cos(a):.1f} {r*math.sin(a):.1f}")
    d = "M " + " L ".join(pts)
    return (f'<path d="{d}" fill="none" stroke="{SOUL}" stroke-width="2.4" stroke-linecap="round"/>'
            f'<circle r="2.6" fill="{LUMEN}"/>')

def g_dream_wielder():
    rays = "".join(
        f'<path d="M {22*math.cos(a):.1f} {-8+22*math.sin(a):.1f} L {30*math.cos(a):.1f} {-8+30*math.sin(a):.1f}" '
        f'stroke="{SOUL}" stroke-width="1.6" stroke-linecap="round" opacity=".8"/>'
        for a in [math.radians(d) for d in (-150, -120, -90, -60, -30)])
    lashes = "".join(f'<path d="M {x} {y} L {x*1.15:.1f} {y+8}" stroke="{BONE}" stroke-width="1.8" '
                     f'stroke-linecap="round"/>' for x, y in ((-16, 6), (0, 9), (16, 6)))
    return (rays + f'<path d="M -26 0 Q 0 18 26 0" fill="none" stroke="{BONE}" stroke-width="2.6" '
            f'stroke-linecap="round"/>' + lashes)

def g_dreamshield():
    # the ward on its orbit around the thing it guards; a deflected shard falling away
    return (f'<circle r="26" fill="none" stroke="{SOUL}" stroke-width="1.2" stroke-dasharray="3 5" opacity=".7"/>'
            f'<circle r="5" fill="{BONE}" opacity=".9"/>'
            f'<path d="M 18 -26 L 30 -22 L 29 -8 L 18 0 L 7 -8 L 6 -22 Z" fill="{CAVERN}" stroke="{SOUL}" stroke-width="2.2"/>'
            f'<path d="M 36 -30 L 30 -36" stroke="{ASH}" stroke-width="1.6" stroke-linecap="round" opacity=".7"/>'
            f'<path d="M 39 -25 L 34 -33" stroke="{ASH}" stroke-width="1.2" stroke-linecap="round" opacity=".4"/>')

def g_steady_body():
    # a shell planted on flat ground, and the nail that hit it, with no recoil
    return (f'<path d="M -22 14 C -22 -10, -6 -22, 4 -22 C 18 -22, 26 -10, 24 14 Z" fill="#2A3448" '
            f'stroke="{BONE}" stroke-width="2.2"/>'
            f'<path d="M -6 -21 L -2 -4 M 10 -20 L 12 -6" stroke="{BONE}" stroke-width="1.1" opacity=".5"/>'
            f'<path d="M -34 14 L 34 14" stroke="{BONE}" stroke-width="2.4" stroke-linecap="round"/>'
            f'<path d="M -36 -2 L -22 -2" stroke="{LUMEN}" stroke-width="2.6" stroke-linecap="round"/>')

CHARMS = [
    ("Quick Slash",   3, "Fast iteration",
     "The bearer swings through sprints as others plan the first. Ship, learn, swing again.", g_quick_slash),
    ("Spell Twister", 2, "Efficiency",
     "Casts the same spell in fewer lines. Code that does more by carrying less.", g_spell_twister),
    ("Dream Wielder", 1, "Interpretability",
     "Lets the bearer hear what a model is thinking before it acts.", g_dream_wielder),
    ("Dreamshield",   3, "Guardrails",
     "A ward that circles the model and turns aside what was thrown at it.", g_dreamshield),
    ("Steady Body",   1, "Reliability",
     "The bearer does not recoil when the deadline strikes. What was promised arrives on the day it was promised.", g_steady_body),
]

def wrap(text, width=32):
    rows, cur = [], ""
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > width:
            rows.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur: rows.append(cur)
    return rows

def notch(x, y, filled, rx=5.5, ry=7.5):
    if filled:
        return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{BONE}" opacity=".92"/>'
    return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="none" stroke="{BONE}" stroke-width="1.2" opacity=".45"/>'

def charm(cx, cy, name, cost, role, line, glyph):
    core = True
    out = [f'<g transform="translate({cx},{cy})"><title>{esc(name)} / {esc(role)}: {esc(line)}</title>']
    # one static glow under the medallion, then rim, dish, inner ring, glyph
    out.append(f'<circle r="46" fill="{SOUL}" opacity=".30" filter="url(#glowMed)"/>')
    out.append(f'<circle r="46" fill="{CAVERN}" stroke="{BONE}" stroke-width="2.4" opacity=".98"/>')
    out.append(f'<circle r="39" fill="none" stroke="{BONE}" stroke-width="1" opacity=".28"/>')
    out.append('<g transform="scale(1.22)">' + glyph() + "</g>")
    out.append('</g>')
    out.append(caps(cx, cy + 82, name, size=15, track=2.2, anchor="middle",
                    fill=LUMEN if core else ASH, glow=core))
    out.append(caps(cx, cy + 104, role, size=12, track=2.4, fill=ASH, anchor="middle", opacity=.8))
    for k in range(cost):
        out.append(notch(cx + (k - (cost - 1) / 2) * 16, cy + 126, True, rx=4.2, ry=5.8))
    for r, row in enumerate(wrap(line)):
        out.append(prose(cx, cy + 154 + r * 19, row, size=14, anchor="middle", opacity=.85))
    return "".join(out)

charm_svg = [lantern(W, CHARM_H), section("The Charms")]
# the notch row, right of the rule: nine spent, two left open
nx = W - MARGIN - NOTCHES * 19 + 8
charm_svg.append(caps(nx - 16, 158, "Notches", size=13, track=2.6, fill=ASH, anchor="end", opacity=.8))
for k in range(NOTCHES):
    charm_svg.append(notch(nx + k * 19, 153, k < USED))
charm_svg.append(prose(MARGIN, 158, "Equipped at the bench. One notch left open.", size=14, opacity=.8))
for i, (name, cost, role, line, glyph) in enumerate(CHARMS):
    charm_svg.append(charm(600 + (i - 2) * 216, 270, name, cost, role, line, glyph))

H, svg, DEFS = CHARM_H, charm_svg, ""
