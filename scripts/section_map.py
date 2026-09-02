#!/usr/bin/env python3
"""A sparse Hallownest journey whose labels and counts come from live data."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from theme import *

ROOT = Path(__file__).resolve().parent.parent
W, H = 1200, 1050
DEFS = ""

stats = json.loads((ROOT / "data" / "stats.json").read_text(encoding="utf-8"))
counts = {r["name"]: r["count"] for r in stats["regions"]}

# The silhouettes stay fixed so daily redraws do not shuffle the page. Their
# labels and counts are live; the route is the constant journey through them.
AREAS = [
    ("FOUNDATIONS", 500, 135,
     "M 350 70 Q 382 38 432 42 L 474 36 L 516 43 L 560 37 L 625 45 "
     "Q 681 55 694 98 L 681 190 Q 651 229 593 233 L 525 226 "
     "L 472 234 L 404 225 Q 353 213 340 174 L 345 117 Z"),
    ("COMPUTER VISION", 214, 352,
     "M 72 276 Q 101 237 151 231 L 206 237 L 258 232 L 300 246 "
     "Q 337 262 345 300 L 337 429 Q 310 469 259 479 L 209 474 "
     "L 164 481 L 124 463 Q 80 445 66 405 L 71 348 L 64 317 Z"),
    ("AGENTIC AI", 850, 292,
     "M 700 213 Q 731 178 781 177 L 831 185 L 877 180 L 930 190 "
     "Q 978 202 995 246 L 987 351 Q 968 391 916 405 L 872 399 "
     "L 825 407 L 768 395 Q 718 382 701 341 L 707 287 L 697 254 Z"),
    ("MACHINE LEARNING", 510, 440,
     "M 353 339 Q 380 303 432 300 L 482 308 L 526 302 L 605 312 "
     "Q 652 325 670 368 L 661 505 Q 642 548 584 560 L 531 552 "
     "L 478 562 L 418 549 Q 376 532 357 492 L 364 428 L 352 386 Z"),
    ("GENERATIVE AI", 824, 604,
     "M 670 503 Q 701 466 752 465 L 804 473 L 853 468 L 916 478 "
     "Q 964 492 985 536 L 976 671 Q 957 713 899 724 L 850 717 "
     "L 796 727 L 730 711 Q 687 695 669 657 L 676 594 L 666 550 Z"),
    ("PARALLEL COMPUTE", 1069, 659,
     "M 970 587 Q 990 552 1029 553 L 1063 560 L 1095 554 L 1121 563 "
     "Q 1152 576 1162 610 L 1155 722 Q 1140 757 1103 768 L 1070 762 "
     "L 1036 770 L 1014 757 Q 984 743 973 715 L 978 664 L 968 624 Z"),
]


def area_label(name, x, y):
    lines = name.split() if " " in name else [name]
    start = y - 15 * (len(lines) - 1)
    out = []
    for i, line in enumerate(lines):
        out.append(caps(x, start + i * 34, line, size=24, track=1.5,
                        fill=BONE, anchor="middle", opacity=.94))
    out.append(prose(x, start + len(lines) * 34 + 1,
                     f'{counts.get(name, 0)} repos', size=18,
                     fill=BONE, anchor="middle", opacity=.78))
    return "".join(out)


svg = []

# Cavern bodies. A single edge and one inner echo provide depth without blur.
for name, lx, ly, path in AREAS:
    svg.append(f'<path d="{path}" fill="#0C1119" stroke="#202A39" '
               'stroke-width="3.5" stroke-linejoin="round"/>')
    svg.append(f'<path d="{path}" fill="none" stroke="#586476" '
               'stroke-width="1.2" opacity=".42"/>')

# The Abyss: darker, broader and deliberately less mapped than the six regions.
ABYSS = ("M 350 760 Q 384 731 438 733 L 714 739 Q 776 749 797 797 "
         "L 789 948 Q 763 994 700 1002 L 442 996 Q 382 983 356 936 Z")
svg.append(f'<path d="{ABYSS}" fill="#070A10" stroke="#202A3A" '
           'stroke-width="5"/>')
svg.append(f'<path d="{ABYSS}" fill="none" stroke="#536174" '
           'stroke-width="1.1" opacity=".34"/>')

# Minimal stalactites and flora. These are shared scene cues, not a decoration
# pass applied to every room.
svg.append('<path d="M 356 64 l 18 35 17 -38 18 47 20 -55 18 46 21 -58 '
           '18 52 22 -51 19 45 20 -42 18 43 17 -38 21 46" '
           'fill="#080B12" opacity=".96"/>')
for teeth in (
    "M 78 281 l 18 31 15 -29 17 38 16 -42 18 35 18 -36 17 34 19 -31",
    "M 711 215 l 17 28 15 -26 18 35 16 -37 18 31 18 -30 18 27",
    "M 366 340 l 17 29 16 -27 18 38 17 -41 18 34 18 -31 19 28",
    "M 681 503 l 17 30 16 -28 18 39 17 -42 18 35 18 -32 20 28",
    "M 982 588 l 14 27 13 -24 15 34 14 -36 16 30 15 -27",
):
    svg.append(f'<path d="{teeth}" fill="none" stroke="{VOID}" '
               'stroke-width="8" stroke-linejoin="miter" opacity=".98"/>')
svg.append(f'<path d="M 365 765 l 20 34 17 -31 21 42 18 -45 21 38 '
           f'20 -35 20 32 22 -31 19 34 20 -29 22 35 20 -33 '
           f'22 38 19 -34 20 29" fill="none" stroke="{VOID}" '
           'stroke-width="9" stroke-linejoin="miter" opacity=".98"/>')
svg.append('<path d="M 84 415 q 22 -30 10 -72 q 31 20 30 63 '
           'M 98 375 q -21 -9 -29 -27 M 110 361 q 19 -12 27 -31" '
           'fill="none" stroke="#344052" stroke-width="4" opacity=".7"/>')
svg.append('<path d="M 938 684 q -20 -28 -8 -69 q -29 19 -29 60 '
           'M 923 646 q 20 -8 28 -25" fill="none" stroke="#344052" '
           'stroke-width="4" opacity=".7"/>')

# One continuous pilgrimage route. Layered plain strokes replace a blur and
# keep repainting cheap while retaining the pale in-game route treatment.
ROUTE = ("M 606 -26 C 604 30 700 28 686 112 S 604 194 641 247 "
         "S 745 292 702 358 S 604 415 637 486 S 764 536 733 610 "
         "S 659 677 706 735 S 760 812 720 866")
for width, opacity in ((10, .07), (5, .12)):
    svg.append(f'<path d="{ROUTE}" fill="none" stroke="{BONE}" '
               f'stroke-width="{width}" opacity="{opacity}" '
               'stroke-linecap="round"/>')
svg.append(f'<path d="{ROUTE}" fill="none" stroke="{BONE}" '
           'stroke-width="1.8" opacity=".92" stroke-linecap="round"/>')
svg.append(f'<circle cx="606" cy="-26" r="4" fill="{BONE}"/>')
svg.append(f'<path d="M 714 855 l 8 12 -8 12 -8 -12 Z" fill="{BONE}"/>')

# One Stagway sign and one empty bench mark the journey without turning the
# scene into a catalogue of game references.
svg.append('<g transform="translate(624,274)" opacity=".78">'
           f'<circle r="18" fill="{VOID}" stroke="{BONE}" stroke-width="1.5"/>'
           f'<path d="M -8 5 Q -12 -5 -7 -11 M 8 5 Q 12 -5 7 -11 '
           f'M -8 5 Q 0 12 8 5" fill="none" stroke="{BONE}" '
           'stroke-width="1.7" stroke-linecap="round"/></g>')
svg.append('<g transform="translate(226,714)" opacity=".72">'
           '<path d="M 0 30 Q 75 21 150 30 M 18 30 L 10 51 M 132 30 L 140 51 '
           'M 12 12 Q 75 2 138 12 L 147 27 Q 75 19 3 27 Z" '
           'fill="#111824" stroke="#526073" stroke-width="3" '
           'stroke-linejoin="round"/>'
           '<path d="M 5 11 q -18 2 -16 16 M 145 11 q 18 2 16 16 '
           'M -18 53 Q 58 40 176 54" fill="none" stroke="#273244" '
           'stroke-width="6" stroke-linecap="round"/></g>')

# Three distant platforms make the Abyss identifiable without filling it.
for x, y, w in ((438, 914, 46), (564, 946, 54), (704, 910, 42)):
    svg.append(f'<path d="M {x} {y} q {w/2:.0f} -10 {w} 0 l -8 13 '
               f'q {-w/2+8:.0f} 8 {-w+16:.0f} 0 Z" fill="#161E2A" '
               'stroke="#39475A" stroke-width="1" opacity=".82"/>')

for name, lx, ly, _path in AREAS:
    svg.append(area_label(name, lx, ly))
svg.append(caps(575, 862, "AI Security", size=27, track=2.1,
                fill=BONE, anchor="middle", opacity=.9))

svg.append(f'<path d="{wobble(72, 1032, 1128, 1032, amp=.6, seed=31)}" '
           f'fill="none" stroke="{BONE}" stroke-width="1" opacity=".28"/>')
svg.append('<path d="M 600 1025 l 7 7 -7 7 -7 -7 Z" fill="none" '
           f'stroke="{BONE}" stroke-width="1" opacity=".46"/>')
