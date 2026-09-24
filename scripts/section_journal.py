#!/usr/bin/env python3
"""The Hunter's Journal: AI Security as a bestiary, and the page's finale.

Every attack family the work has met is an entry: a framed portrait, the name,
the region of the map it was met in, and one line in the Hunter's voice. No
counts anywhere: the Journal records what was seen, not how often.

Drawn the way Hollow Knight draws its bugs: a thick dark ink line around every
shape, pale masks shaded toward the lower right with tall black eyes, dark
bodies, and colour kept to the rim light and the few things that glow. The rim
light is the colour of the map region the creature haunts. The frames carry
the corner flourishes of the game's own menus.
"""
import math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from theme import *
import section_vessel as SV
import section_map as SM

W, H = 1200, 580
SHELL = "#0B1019"        # the frame's plate
INK = "#04060A"          # the outline every shape is drawn with
DARK = "#161B28"         # a bug's body
LEG = "#2A3142"
REGION = {k: v["colour"] for k, v in SM.AREAS.items()}

DEFS = ('<linearGradient id="hkMask" x1="0" y1="0" x2=".7" y2="1">'
        '<stop offset="0" stop-color="#FFFFFF"/><stop offset=".55" stop-color="#E4E2DA"/>'
        '<stop offset="1" stop-color="#A3A8B4"/></linearGradient>')


# ── The ink kit ───────────────────────────────────────────────────────────
def E(cx, cy, rx, ry):
    """An ellipse as path data, so it can take the same ink as everything else."""
    return (f"M {cx-rx:.1f} {cy:.1f} A {rx:.1f} {ry:.1f} 0 1 0 {cx+rx:.1f} {cy:.1f} "
            f"A {rx:.1f} {ry:.1f} 0 1 0 {cx-rx:.1f} {cy:.1f} Z")


def inked(d, fill, rim=None, w=3.2, fop=1):
    """A filled shape with the ink line painted under it, so half the stroke
    shows as an outline: one element, no filter. An optional rim of the
    region's colour sits on the edge, the way the game lights its bugs."""
    fo = f' fill-opacity="{fop}"' if fop != 1 else ""
    s = (f'<path d="{d}" fill="{fill}"{fo} stroke="{INK}" stroke-width="{w}" '
         f'stroke-linejoin="round" stroke-linecap="round" paint-order="stroke"/>')
    if rim:
        s += (f'<path d="{d}" fill="none" stroke="{rim}" stroke-width="1" '
              f'stroke-linejoin="round" opacity=".75"/>')
    return s


def line(d, colour, w=1.6):
    """An inked line: a dark underlay one pixel wider each side, colour on top."""
    return (f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{w + 2}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{w}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def face(cx, cy, rx, ry, edx, erx, ery, edy=0, tilt=10, chin=0):
    """A bug's mask: pale, shaded, inked, with two tall black eyes set wide
    and leaning in at the top. `chin` draws the jaw down to a point."""
    if chin:
        d = (f"M {cx-rx:.1f} {cy:.1f} Q {cx-rx:.1f} {cy-ry:.1f} {cx:.1f} {cy-ry:.1f} "
             f"Q {cx+rx:.1f} {cy-ry:.1f} {cx+rx:.1f} {cy:.1f} "
             f"Q {cx+rx*.62:.1f} {cy+ry+chin:.1f} {cx:.1f} {cy+ry+chin:.1f} "
             f"Q {cx-rx*.62:.1f} {cy+ry+chin:.1f} {cx-rx:.1f} {cy:.1f} Z")
    else:
        d = E(cx, cy, rx, ry)
    s = inked(d, "url(#hkMask)")
    for sg in (-1, 1):
        ex, ey = cx + sg * edx, cy + edy
        s += (f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{erx}" ry="{ery}" fill="#000" '
              f'transform="rotate({-sg*tilt} {ex:.1f} {ey:.1f})"/>')
    return s


def leaf(cx, cy, L, ang, W_=0.42):
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    x0, y0, x1, y1 = cx - ux*L/2, cy - uy*L/2, cx + ux*L/2, cy + uy*L/2
    return (f"M {x0:.1f} {y0:.1f} Q {cx + px*L*W_:.1f} {cy + py*L*W_:.1f} {x1:.1f} {y1:.1f} "
            f"Q {cx - px*L*W_:.1f} {cy - py*L*W_:.1f} {x0:.1f} {y0:.1f} Z"), (x0, y0, x1, y1)


# ── The creatures ─────────────────────────────────────────────────────────
def mosscreep(t):
    # a bug under a mound of leaves, only its mask showing: an order hidden
    # inside what looks like plain ground
    s = "".join(line(d, LEG, 1.4) for d in ("M -12 14 L -16 21", "M -4 16 L -5 22",
                                            "M 4 16 L 5 22", "M 12 14 L 16 21"))
    s += inked(E(0, 6, 21, 12), DARK)
    for cx, cy, L, ang in ((-17, 1, 17, 200), (17, 1, 17, 340), (-11, -8, 19, 235),
                           (11, -8, 19, 305), (0, -12, 19, 270), (-5, -3, 16, 250), (5, -3, 16, 290)):
        d, (x0, y0, x1, y1) = leaf(cx, cy, L, ang)
        s += inked(d, t, w=2.4)
        s += (f'<path d="M {x0:.1f} {y0:.1f} L {x1:.1f} {y1:.1f}" stroke="{INK}" '
              f'stroke-width=".9" opacity=".45"/>')
    s += face(0, 11, 12, 7.5, 5, 2.4, 3.6, edy=.5, tilt=12)
    return s


def baldur(t):
    # the rolled shell, plated and pale; it has opened a crack at one side,
    # and a face looks out of it: every blow but the right one
    s = inked(E(-2, 0, 23, 22), "url(#hkMask)", rim=t)
    for x in (-17, -9, -1):
        h = math.sqrt(22**2 - (x + 2)**2) * .92
        s += (f'<path d="M {x} {-h:.1f} Q {x+7} 0 {x} {h:.1f}" fill="none" stroke="#5C6272" '
              f'stroke-width="1.5" opacity=".8"/>')
    s += inked("M 8 -20.7 A 23 22 0 0 1 8 20.7 Q 15 0 8 -20.7 Z", DARK)
    s += face(15, 0, 6.5, 8, 2.8, 1.6, 2.7, tilt=8)
    s += line("M 12 9 L 10 18", LEG, 1.3) + line("M 18 8 L 20 17", LEG, 1.3)
    return s


def gruzzer(t):
    # the bloated flier, carrying infection in boils along its sides
    s = ""
    for sg in (-1, 1):
        d, _ = leaf(sg * 10, -17, 20, -90 + sg * 32, .5)
        s += (f'<path d="{d}" fill="{SOUL}" fill-opacity=".28" stroke="{INK}" '
              f'stroke-width="1.4" stroke-linejoin="round"/>')
    s += inked(E(0, 4, 21, 19), DARK, rim=t)
    for x, y, r in ((-16, -4, 2.6), (15, -6, 2.2), (14, 13, 1.8), (-13, 15, 1.6)):
        s += (f'<circle cx="{x}" cy="{y}" r="{r*2.4:.1f}" fill="url(#sporeWarm)" opacity=".8"/>'
              f'<circle cx="{x}" cy="{y}" r="{r}" fill="{INFECT}" stroke="{INK}" stroke-width=".8"/>'
              f'<circle cx="{x-r*.35:.1f}" cy="{y-r*.35:.1f}" r="{r*.35:.1f}" fill="#FFE2A8"/>')
    s += face(0, 4, 12.5, 10.5, 5.2, 3.1, 4.4, edy=-1, tilt=14, chin=3)
    return s


def weaver(t):
    # a small dark weaver with more hands than the job needs, a tool in each
    s = ""
    for sg in (-1, 1):
        for (x0, y0, x1, y1, x2, y2) in ((4, 0, 16, -12, 25, -14), (5, 4, 19, 2, 27, 2),
                                         (4, 8, 15, 16, 22, 22)):
            s += line(f"M {sg*x0} {y0} L {sg*x1} {y1} L {sg*x2} {y2}", t, 1.3)
    s += line("M -25 -14 L -28 -21", SOUL, 1.8)
    s += (f'<circle cx="27" cy="2" r="3" fill="none" stroke="{INK}" stroke-width="3"/>'
          f'<circle cx="27" cy="2" r="3" fill="none" stroke="{SOUL}" stroke-width="1.3"/>')
    s += f'<circle cx="-22" cy="22" r="2.6" fill="{SOUL}" stroke="{INK}" stroke-width="1"/>'
    s += line("M 22 22 L 26 17 M 24 19.5 L 27 21", SOUL, 1.2)
    s += inked(E(0, 6, 8, 10), DARK, rim=t)
    s += line("M -4 -14 L -6 -21", "#D9D6CC", 1.4) + line("M 4 -14 L 6 -21", "#D9D6CC", 1.4)
    s += face(0, -8, 8, 7.5, 3.3, 2, 3.1, tilt=14, chin=2)
    return s


def vengefly(t):
    # a snapping flier with a skull for a face, leaving with something pale
    s = ""
    for sg in (-1, 1):
        d = (f"M {sg*6} -6 L {sg*26} -20 L {sg*22} -12 L {sg*29} -8 L {sg*21} -4 "
             f"L {sg*25} 2 L {sg*8} 2 Z")
        s += (f'<path d="{d}" fill="{t}" fill-opacity=".38" stroke="{INK}" stroke-width="1.5" '
              f'stroke-linejoin="round"/>')
    s += line("M -4 10 L -3 15", LEG, 1.3) + line("M 4 10 L 3 15", LEG, 1.3)
    s += inked(E(0, 5, 7, 7), DARK, rim=t)
    s += (f'<circle cx="0" cy="20" r="9.5" fill="url(#sporeCool)" opacity=".95"/>'
          f'<circle cx="0" cy="20" r="4.2" fill="{SOUL}" stroke="{INK}" stroke-width="1.2"/>')
    s += face(0, -7, 12, 10, 5, 3.4, 4.8, tilt=16, chin=4)
    s += inked("M -4 5 L -2.5 10 L -1 5 Z M 1 5 L 2.5 10 L 4 5 Z", "#E4E2DA", w=1.4)
    return s


def grub_mimic(t):
    # a grub in its jar, waiting to be rescued, which is what it wants you to see
    jar = "M -16 -14 L 16 -14 L 17 20 Q 17 25 12 25 L -12 25 Q -17 25 -17 20 Z"
    s = inked(jar, SOUL, rim=SOUL, fop=.07)
    s += inked("M -13 -21 L 13 -21 L 13 -14 L -13 -14 Z", STONE, rim=BONE, w=2.6)
    body = "M -11 23 Q -13 2 0 -2 Q 13 2 11 23 Z"
    s += inked(body, "url(#hkMask)", rim=t, w=2.6)
    s += (f'<path d="M -11.5 11 Q 0 15 11.5 11 M -11 17 Q 0 21 11 17" fill="none" '
          f'stroke="#7E8494" stroke-width="1"/>')
    for x in (-4.5, 4.5):
        s += (f'<circle cx="{x}" cy="3.5" r="3" fill="#000"/>'
              f'<circle cx="{x-1}" cy="2.4" r=".9" fill="#FFFFFF"/>')
    s += '<path d="M -6 8 Q 0 13 6 8 Z" fill="#000"/>'
    s += '<path d="M -5 8.3 L -3.5 10.6 L -2 8.6 L -0.5 10.9 L 1 8.6 L 2.5 10.6 L 4 8.4 Z" fill="#E4E2DA"/>'
    s += '<path d="M -12 -8 L -12.5 15" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" opacity=".28"/>'
    return s


def ooma(t):
    # the see-through drifter from Fog Canyon: its inside is on show, which is
    # what an MRI is. The mark inside it is bright, ringed, and was never there.
    s = "".join(line(f"M {x} 7 q {dx} 8 0 14 q {-dx} 5 {dx*.6:.1f} 9", t, 1.1)
                for x, dx in ((-14, -3), (-6, 3), (3, -3), (12, 3)))
    bell = "M -21 6 Q -21 -24 0 -24 Q 21 -24 21 6 Q 16 10 10.5 6 Q 5 10 0 6 Q -5 10 -10.5 6 Q -16 10 -21 6 Z"
    s += inked(bell, t, fop=.3, w=2.8)
    s += f'<path d="{bell}" fill="none" stroke="{t}" stroke-width="1.1" opacity=".9"/>'
    s += '<path d="M -15 -13 Q -11 -20 -3 -21" fill="none" stroke="#FFFFFF" stroke-width="1.4" stroke-linecap="round" opacity=".55"/>'
    s += (f'<circle cx="-5" cy="-5" r="7.5" fill="url(#sporeCool)" opacity=".9"/>'
          f'<circle cx="-5" cy="-5" r="3" fill="{SOUL}" stroke="{INK}" stroke-width="1"/>')
    s += (f'<circle cx="10" cy="-9" r="4.4" fill="#FFFFFF"/>'
          f'<circle cx="10" cy="-9" r="7.5" fill="none" stroke="#FFFFFF" stroke-width="1" '
          f'stroke-dasharray="2.5 2"/>'
          f'<path d="M 10 -19.5 L 10 -17 M 10 -1 L 10 1.5 M -0.5 -9 L 2 -9 M 18 -9 L 20.5 -9" '
          f'stroke="#FFFFFF" stroke-width="1.1"/>')
    return s



def false_knight(t):
    # the False Knight: a great helm and pauldrons, and nothing knightly inside
    # but a maggot peering through the visor. Around it, a detector's box,
    # corner brackets and a label tab, drawn with total confidence.
    s = inked("M -16 12 Q -23 14 -23 22 L 23 22 Q 23 14 16 12 Z", DARK, rim=t)
    helm = "M -17 12 L -19 -6 Q -18 -20 0 -22 Q 18 -20 19 -6 L 17 12 Q 0 17 -17 12 Z"
    s += inked(helm, "url(#hkMask)")
    s += f'<path d="{helm}" fill="{t}" opacity=".22"/>'
    s += (f'<path d="M -18.5 -9 Q 0 -13 18.5 -9 M 0 -22 L 0 -12" fill="none" stroke="#4E5566" '
          f'stroke-width="1.3"/>')
    s += line("M -6 -21 L -7 -25", "#E4E2DA", 1.8) + line("M 6 -21 L 7 -25", "#E4E2DA", 1.8)
    s += inked("M -12 -4 L 12 -4 L 10 3 L -10 3 Z", "#000", w=1.6)
    s += face(2, 0, 4.2, 2.8, 1.6, .85, 1.2, tilt=0)
    for d in ("M -24 -18 L -24 -24 L -18 -24", "M 18 -24 L 24 -24 L 24 -18",
              "M 24 18 L 24 24 L 18 24", "M -18 24 L -24 24 L -24 18"):
        s += line(d, LUMEN, 1.5)
    s += inked("M -24 -29.5 L -11 -29.5 L -11 -24 L -24 -24 Z", LUMEN, w=1.6)
    s += f'<path d="M -22.5 -26.8 L -12.5 -26.8" stroke="{SHELL}" stroke-width="1.2"/>'
    return s


def shade(t):
    # the Knight's own shade: black where the Knight is white, white where it
    # is black, describing a room that was never there
    room = (f'<path d="M -28 -4 L -28 -26 L -6 -26 L -6 -18 L 26 -18 L 26 8 L 28 8 L 28 24 L -28 24 Z" '
            f'fill="none" stroke="{t}" stroke-width="1" stroke-dasharray="3 3" opacity=".6"/>')
    smoke = "M -10 8 Q -17 17 -10 25 Q -5 19 0 26 Q 5 19 10 25 Q 17 17 10 8 Z"
    s = room + inked(smoke, "#05070B", rim=t, w=2)
    s += "".join(line(f"M {x} -26 q {dx} -3 {dx*.4:.1f} -6", t, .9)
                 for x, dx in ((-12, -3), (12, 3)))
    s += (f'<g transform="translate(-18,-27) scale(.36)">'
          f'<path d="{SV.MASK}" fill="#05070B" stroke="{t}" stroke-width="3.2" stroke-linejoin="round"/>'
          + "".join(f'<ellipse cx="{SV.EYE_CX + sg*SV.EYE_DX}" cy="{SV.EYE_CY}" rx="{SV.EYE_R*2}" '
                    f'ry="{SV.EYE_R*2}" fill="url(#sporeCool)" opacity=".7"/>'
                    f'<circle cx="{SV.EYE_CX + sg*SV.EYE_DX}" cy="{SV.EYE_CY}" r="{SV.EYE_R}" fill="#F4FBFF"/>'
                    for sg in (-1, 1)) + '</g>')
    return s


ENTRIES = [
    (mosscreep,    "Prompt Injection",  "AGENTIC AI",       "An order hidden inside what looks like plain ground."),
    (baldur,       "Jailbreak",         "GENERATIVE AI",    "The shell holds every blow but the one it was waiting for."),
    (gruzzer,      "Data Poisoning",    "MACHINE LEARNING", "Fed early, seen late. It carries what it was given."),
    (weaver,       "Excessive Agency",  "AGENTIC AI",       "Given one tool, it reaches for all the rest."),
    (vengefly,     "Exfiltration",      "AGENTIC AI",       "Leaves in a hurry, carrying something pale."),
    (grub_mimic,   "Model Extraction",  "MACHINE LEARNING", "A thousand questions, then it wears the shape."),
    (ooma,         "MRI Phantom",       "COMPUTER VISION",  "A speck laid on the MRI, and a tumour appears that the body never had."),
    (false_knight, "False Knight",      "COMPUTER VISION",  "A maggot in borrowed armour. Every watching eye boxes it as a knight."),
    (shade,        "Hallucination",     "GENERATIVE AI",    "Describes, with perfect confidence, a room that was never there."),
]


def wrap(text, width=38):
    rows, cur = [], ""
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > width:
            rows.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        rows.append(cur)
    return rows


def frame(fx, fy, t):
    """The entry frame, after the game's menus: a dark plate, a thin inner line
    in the region's colour, bright corner brackets that curl inward, and a
    small diamond at the top and bottom."""
    o = [f'<ellipse cx="{fx}" cy="{fy}" rx="50" ry="44" fill="url(#sporeCool)" opacity=".14"/>',
         f'<rect x="{fx-34}" y="{fy-34}" width="68" height="68" rx="4" fill="{SHELL}" '
         f'stroke="{BONE}" stroke-width=".8" opacity=".95"/>',
         f'<ellipse cx="{fx}" cy="{fy+2}" rx="26" ry="24" fill="{t}" opacity=".08"/>',
         f'<rect x="{fx-30}" y="{fy-30}" width="60" height="60" rx="2" fill="none" '
         f'stroke="{t}" stroke-width=".7" opacity=".4"/>']
    d = ""
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        cx, cy = fx + sx * 34, fy + sy * 34
        d += (f"M {cx} {cy - sy*13} L {cx} {cy} L {cx - sx*13} {cy} "
              f"M {cx - sx*4} {cy - sy*11} Q {cx - sx*4} {cy - sy*4} {cx - sx*11} {cy - sy*4} ")
        o.append(f'<circle cx="{cx - sx*8.5}" cy="{cy - sy*8.5}" r="1.2" fill="{BONE}" opacity=".85"/>')
    o.append(f'<path d="{d}" fill="none" stroke="{BONE}" stroke-width="1.5" stroke-linecap="round" opacity=".9"/>')
    for y in (fy - 34, fy + 34):
        o.append(f'<path d="M {fx} {y-3.2} L {fx+3.2} {y} L {fx} {y+3.2} L {fx-3.2} {y} Z" fill="{BONE}"/>')
    return "".join(o)


svg = [lantern(W, H, cy=H * .55, rx=W * .55)]
svg.append(section("Hunter's Journal"))

COL, ROW = 352, 136
for i, (draw, name, region, note) in enumerate(ENTRIES):
    col, row = i % 3, i // 3
    t = REGION[region]
    fx, fy = MARGIN + col * COL + 34, 200 + row * ROW      # frame centre
    tx = fx + 54                                           # text column
    svg.append(frame(fx, fy, t))
    svg.append(f'<g transform="translate({fx},{fy}) scale(1.02)"><title>{esc(name)}, met in '
               f'{esc(region.title())}: {esc(note)}</title>{draw(t)}</g>')
    svg.append(caps(tx, fy - 14, name, size=15, track=2.2, glow=True))
    svg.append(caps(tx, fy + 3, f"met in {region}", size=10.5, track=2.4, fill=t, opacity=.85))
    for r, row_text in enumerate(wrap(note)):
        svg.append(prose(tx, fy + 22 + r * 17, row_text, size=13, opacity=.85))

svg.append(footnote("What was met in the dark. The Journal is never finished.", 560))
svg.append(motes(90, 150, 1030, 360, n=14, seed=23))
