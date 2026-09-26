#!/usr/bin/env python3
"""Shared ink, colour and lettering. Every figure is built from this file, so
the profile reads as one place rather than a stack of unrelated panels.

Three rules hold it together:

1. Bloom. Hollow Knight runs a heavy bloom pass, so anything pale bleeds light
   into the dark around it. Bone text, room outlines and Soul all carry it;
   dim Ash text does not, because in-game the dim things stay dim.
2. Amber means a boundary was crossed. It is never decoration.
3. Every figure uses the same ground, the same 72px margin and the same header
   block, so scrolling the README feels like walking, not like changing tabs.
"""
import random
from pathlib import Path

VOID   = "#080B12"   # deepest ground
CAVERN = "#111725"   # midground panels and room fill
STONE  = "#1D2637"   # carved edges
BONE   = "#E9E6DC"   # the mask; anything carved or written
LUMEN  = "#F2F9FF"   # display lettering — cold, and lit
ASH    = "#A9B7CC"   # secondary lettering — cold, and unlit
SOUL   = "#A9E8F0"   # pale light, still contained
INFECT = "#F0A93C"   # what leaked out — breach only

# Hollow Knight's wordmark is a bespoke Trajan-style inscriptional capital.
# Palatino is Zapf's revival of the same Renaissance letterforms and ships on
# Windows and macOS, so it survives GitHub's img sandbox where a webfont would
# not load at all.
SERIF = "'Palatino Linotype','Book Antiqua',Palatino,'URW Palladio L','Times New Roman',serif"

# Hollow Knight sets its titles in Trajan, an inscriptional Roman capital.
# Cinzel is the standard free cut of the same letterforms (SIL OFL — see
# scripts/CINZEL-OFL.txt), subset here to just the caps, digits and marks the
# display faces actually set: 7.5 KB, about 10 KB once base64'd in.
#
# It is embedded as a data URI rather than linked, because GitHub renders
# README images through <img>, where any external request is blocked. Verified
# it applies in that mode before committing to it. Palatino stays behind it in
# the stack as the fallback, and keeps the body text, where it has real
# italics and reads better small.
# Film grain used to be an feTurbulence pass over the whole map: Perlin noise
# evaluated per device pixel, which at a 3x raster is six million samples for
# an effect that is 14% opaque. The same speckle tiles from a 64px image, and
# a tiled blit is close to free.
def _grain_tile(size=64, seed=9):
    import base64, random, struct, zlib
    rnd = random.Random(seed)
    raw = bytearray()
    for _ in range(size):
        raw.append(0)                              # per-scanline filter: none
        for _ in range(size):
            # Grey and alpha both wander, matching fractalNoise's habit of
            # varying coverage as well as brightness. Quantised to 32 levels
            # so the IDAT still compresses.
            g = min(255, max(0, int(rnd.gauss(128, 38)))) & 0xF8
            a = min(255, max(0, int(rnd.gauss(128, 38)))) & 0xF8
            raw += bytes((g, a))

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    png = (bytes((137, 80, 78, 71, 13, 10, 26, 10))   # PNG signature
           + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 4, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + chunk(b"IEND", b""))
    return base64.b64encode(png).decode()



def wobble(x0, y0, x1, y1, amp=1.1, step=44, seed=5):
    """A rule that was drawn by hand rather than laid against a straightedge.

    This was an feTurbulence displacement at paint time: Perlin noise
    evaluated per pixel in order to move a hairline by about one pixel. The
    same waver baked into the geometry from a fixed seed costs nothing, and
    since the seed never changes the file only moves when the data does.
    """
    r = random.Random(seed)
    n = max(2, int(abs(x1 - x0) / step))
    pts = []
    for i in range(n + 1):
        t = i / n
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        if 0 < i < n:
            x += r.uniform(-amp, amp)
            y += r.uniform(-amp, amp)
        pts.append((x, y))
    return "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts)


def _display_face():
    import base64
    woff = Path(__file__).resolve().parent / "cinzel-caps.woff2"
    if not woff.exists():
        return ""
    b64 = base64.b64encode(woff.read_bytes()).decode()
    return ("@font-face{font-family:'Hallow';font-style:normal;font-weight:400;"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}")


DISPLAY = "'Hallow'," + SERIF

MARGIN = 72          # every figure indents to the same line
RULE_Y = 118         # every header rule sits at the same height


def _defs(extra=""):
    return f"""<defs>
  <filter id="bloomSoft" x="-45%" y="-45%" width="190%" height="190%">
    <feGaussianBlur stdDeviation="1.7" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <!-- Halos for type. The general-purpose glows carry a 380% filter region,
       which allocates a buffer fourteen times the element's area — fine for a
       handful of shapes, ruinous across sixty-odd lines of text. These are
       sized to what a line of type actually needs. -->
  <filter id="haloL" x="-12%" y="-45%" width="124%" height="190%">
    <feGaussianBlur stdDeviation="5"/>
  </filter>
  <filter id="haloM" x="-10%" y="-40%" width="120%" height="180%">
    <feGaussianBlur stdDeviation="2.8"/>
  </filter>
  <filter id="haloS" x="-8%" y="-35%" width="116%" height="170%">
    <feGaussianBlur stdDeviation="1.5"/>
  </filter>
  <filter id="glow" x="-70%" y="-70%" width="240%" height="240%">
    <feGaussianBlur stdDeviation="4" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="b"/>
             <feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="glowMed" x="-120%" y="-120%" width="340%" height="340%">
    <feGaussianBlur stdDeviation="6"/>
  </filter>
  <filter id="glowWide" x="-140%" y="-140%" width="380%" height="380%">
    <feGaussianBlur stdDeviation="14"/>
  </filter>
  <!-- Same blurs, sized for shapes that are already big. A filter region is a
       buffer the renderer has to allocate and clear: at 380% that is fourteen
       times the element's own area, which a small dot needs and a map region
       does not. A Gaussian reaches about 3 sigma, so these are cut to what the
       blur can actually touch. -->
  <!-- Same soft bloom, for shapes that are already wide. bloomSoft reserves
       45% of the element's width on each side; on the hour chart, which is a
       thousand pixels across, that is a buffer twice the size of the thing
       being drawn for a blur that reaches five pixels. -->
  <filter id="bloomT" x="-5%" y="-30%" width="110%" height="160%">
    <feGaussianBlur stdDeviation="1.7" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="glowMedT" x="-25%" y="-25%" width="150%" height="150%">
    <feGaussianBlur stdDeviation="6"/>
  </filter>
  <filter id="glowWideT" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="14"/>
  </filter>
  <pattern id="grainTile" width="64" height="64" patternUnits="userSpaceOnUse">
    <image width="64" height="64" href="data:image/png;base64,{_grain_tile()}"/>
  </pattern>
  <!-- Soft dots as gradients rather than blurred circles: same look, no
       per-frame filter pass. Used by every drifting particle. -->
  <radialGradient id="sporeCool">
    <stop offset="0%"   stop-color="{SOUL}" stop-opacity="1"/>
    <stop offset="38%"  stop-color="{SOUL}" stop-opacity=".62"/>
    <stop offset="100%" stop-color="{SOUL}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="sporeWarm">
    <stop offset="0%"   stop-color="{INFECT}" stop-opacity="1"/>
    <stop offset="38%"  stop-color="{INFECT}" stop-opacity=".62"/>
    <stop offset="100%" stop-color="{INFECT}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="lantern" cx="50%" cy="46%" r="62%">
    <stop offset="0%" stop-color="#16203A" stop-opacity=".9"/>
    <stop offset="58%" stop-color="#0B1120" stop-opacity=".5"/>
    <stop offset="100%" stop-color="{VOID}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="edgeX" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#000" stop-opacity=".7"/>
    <stop offset="100%" stop-color="#000" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="edgeY" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#000" stop-opacity=".7"/>
    <stop offset="100%" stop-color="#000" stop-opacity="0"/>
  </linearGradient>
{extra}
</defs>"""


# ── Motion ─────────────────────────────────────────────────────────────────
# GitHub shows the profile as an <img>, and a browser repaints an animated SVG
# image whole every time anything in it changes: about 38 ms of work per
# repaint at retina density, whatever changed, filters or not. Eight
# animations on unrelated clocks came to about 14 repaints a second, half a CPU
# core, just to show the page. So every animation changes only on one shared
# half-second beat, through step-end keyframes (a steps() timing restarts at
# every keyframe, which is how the old drip and typed line fired far more often
# than their step counts said). Their changes land in the same frame, so the
# whole profile repaints at most twice a second.
BEAT = 0.5


def beats(name, seconds, frame):
    """Keyframes holding frame(i, n) for beat i of an n-beat cycle."""
    n = round(seconds / BEAT)
    assert abs(n * BEAT - seconds) < 1e-9, f"{name}: a cycle is a whole number of beats"
    out, last = [], None
    for i in range(n):
        decl = frame(i, n)
        if decl != last:
            out.append(f"{100 * i / n:.4f}% {{ {decl} }}")
            last = decl
    return f"@keyframes {name} {{ {' '.join(out)} }}"


def _lerp(stops, p):
    for (p0, *a), (p1, *b) in zip(stops, stops[1:]):
        if p0 <= p <= p1:
            f = (p - p0) / (p1 - p0)
            return [x + (y - x) * f for x, y in zip(a, b)], f
    return stops[-1][1:], 1.0


def _drip(i, n):
    # Infection gathering at the breach, swelling, and falling away.
    p = i / n
    if p <= .38:
        (y, k, o), _ = _lerp([(0, 0, .35, 0), (.22, 2, 1, .95), (.38, 6, 1, .95)], p)
        return f"transform: translateY({y:.1f}px) scale({k:.2f}); opacity: {o:.2f};"
    (k, o), f = _lerp([(.38, 1, .95), (1, .5, 0)], p)
    return (f"transform: translateY(calc(6px + (var(--fall, 74px) - 6px) * {f:.3f})) "
            f"scale({k:.2f}); opacity: {o:.2f};")


def _ping(i, n):
    ring = [(.25, .9), (.5, .65), (.75, .4), (1, .15)]
    k, o = ring[i] if i < len(ring) else (1, 0)
    return f"transform: scale({k}); opacity: {o};"


MOTION = " ".join([
    beats("drip", 7, _drip),
    # Soul is a liquid: one crest crosses the large meter and repeats.
    beats("tide", 8, lambda i, n: f"transform: translateX({-40 * i / n:.1f}px);"),
    beats("caret", 1, lambda i, n: f"opacity: {1 - i};"),
    beats("glint", 3, lambda i, n: "opacity: .95; transform: scale(1);" if i == n - 1
          else "opacity: 0; transform: scale(.4);"),
    # The rain path repeats every 40px, so one period of travel loops seamlessly.
    beats("rain", 2, lambda i, n: f"transform: translateY({40 * i / n:.0f}px);"),
    beats("ping", 3, _ping),
    beats("breathe", 4, lambda i, n: f"opacity: {(.35, .6, .9, .6)[i // 2]};"),
])


def _anim(name, seconds):
    return f"animation: {name} {seconds}s step-end infinite;"


_STYLE = f"""<style>
  {_display_face()}
  text {{ font-family: {SERIF}; }}
  .d {{ font-family: {DISPLAY}; }}
  {MOTION}
  .drip {{ {_anim("drip", 7)} transform-box: fill-box; transform-origin: center; }}
  .tide {{ {_anim("tide", 8)} }}
  .glint {{ {_anim("glint", 3)} transform-box: fill-box; transform-origin: center; }}
  .rain {{ {_anim("rain", 2)} }}
  .ping {{ {_anim("ping", 3)} transform-box: fill-box; transform-origin: center; }}
  .breathe {{ {_anim("breathe", 4)} }}
  @media (prefers-reduced-motion: reduce) {{
    /* Stopping the reveal mid-way would leave the line half-invisible, so it
       jumps to fully typed and the caret goes away. */
    .typeline {{ animation: none !important;
                 transform: translateX(var(--w, 0)) !important; }}
    .caret {{ display: none; }}
    .glint, .rain, .ping, .breathe {{ animation: none; opacity: .6; }}
    .drip, .tide {{ animation: none; opacity: .7; }}
  }}
</style>"""


def lantern(w, h, cx=None, cy=None, rx=None, ry=None):
    """A pool of light. Sections carry their own, so the ground down the page
    reads as a cave lit at intervals rather than one flat wash."""
    cx = w / 2 if cx is None else cx
    cy = h * 0.46 if cy is None else cy
    rx = w * 0.62 if rx is None else rx
    ry = h * 0.7 if ry is None else ry
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#lantern)"/>'


def edges(w, h, band=170):
    """One vignette for the whole document — drawn only at the outer edges, so
    stacked sections never show a dark seam where they meet."""
    return (f'<rect x="0" y="0" width="{band}" height="{h}" fill="url(#edgeX)"/>'
            f'<rect x="{w}" y="0" width="{band}" height="{h}" fill="url(#edgeX)" '
            f'transform="translate({w},0) rotate(180) translate({-w},{-h})"/>'
            f'<rect x="0" y="0" width="{w}" height="{band*0.62:.0f}" '
            f'fill="url(#edgeY)"/>'
            f'<g transform="translate(0,{h}) scale(1,-1)">'
            f'<rect x="0" y="0" width="{w}" height="{band*0.36:.0f}" '
            f'fill="url(#edgeY)"/></g>')


def document(w, sections, extra_defs=""):
    """Compose sections into one continuous picture.

    Each section is (height, [elements]) and is translated into place, so a
    section keeps its own local coordinates and nothing has to be re-measured.
    """
    total = sum(h for h, _ in sections)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{total}" '
           f'     viewBox="0 0 {w} {total}" role="img">',
           _defs(extra_defs), _STYLE,
           f'<rect width="{w}" height="{total}" fill="{VOID}"/>',
           dust(w, total)]
    # Every section's pool of light goes down first, under all of them, and
    # the bodies after. Stacked one section at a time, the next section's pool
    # painted over the one above and cut the masthead's halo flat at the line.
    is_pool = lambda el: el.startswith("<ellipse") and 'fill="url(#lantern)"' in el
    for pools in (True, False):
        dy = 0
        for h, body in sections:
            out.append(f'<g transform="translate(0,{dy})">')
            out.extend(el for el in body if is_pool(el) == pools)
            out.append('</g>')
            dy += h
    out.append(edges(w, total))
    out.append('</svg>')
    return chr(10).join(out)


def section(title, subtitle="", w=1200):
    """The one header block. Same place, same sizes, in every figure.

    Subtitles are gone: at this width they rendered around 11px in the browser
    and nobody reads an 11px caption on a profile. A section is its title and
    its rule. The rule stays at the same height regardless, so the three
    sections still line up.
    """
    return (caps(MARGIN, 76, title, size=36, track=5.5, glow=True)
            + f'<path d="{wobble(MARGIN, RULE_Y, w - MARGIN, RULE_Y, seed=3)}" '
              f'fill="none" stroke="{BONE}" stroke-width="1.2" opacity=".2"/>')


def footnote(text, y, w=1200):
    return (f'<path d="{wobble(MARGIN, y - 30, w - MARGIN, y - 30, seed=11)}" '
            f'fill="none" stroke="{BONE}" stroke-width="1" opacity=".14"/>'
            + prose(MARGIN, y, text, size=13, opacity=.85))


def _halo(body, txt, size, opacity=1.0):
    """The layers under a lit line of type, largest first."""
    if size >= 30:
        stack = (("haloL", .55), ("haloM", .8))
    elif size >= 20:
        stack = (("haloM", .8),)
    else:
        stack = (("haloS", .75),)
    return "".join(
        f'<text class="d" {body} fill="{SOUL}" opacity="{op * opacity:.2f}" '
        f'filter="url(#{flt})">{txt}</text>' for flt, op in stack)


def _lit(body, txt, fill, size, opacity=1.0):
    """One line of type, glowing: a Soul-coloured blur under a cold core.

    A stroke laid behind the fill was tried here instead, to save the second
    glyph run and the filter buffer. Measured over sixty draws it came out
    slightly slower than the blur — stroking glyph outlines costs about what
    blurring them does — and it thickened type at 24px. The blur stays.
    """
    op = "" if opacity == 1 else f' opacity="{opacity}"'
    return (_halo(body, txt, size, opacity)
            + f'<text class="d" {body} fill="{fill}"{op}>{txt}</text>')


def caps(x, y, s, size=13, fill=None, track=4.2, weight="normal",
         anchor="start", opacity=1, glow=False):
    """Inscriptional caps — the house voice for anything that names a thing.

    glow=True sets the line twice: a Soul-coloured blur underneath and the
    cold white on top of it. A single blurred copy of the text itself only
    ever makes the text fuzzy; the halo has to be a different colour from the
    core for it to read as light coming off the letters. Halo radius follows
    the type size, because a big blur under a 12px cap is just a smudge.
    """
    fill = LUMEN if fill is None else fill
    body = (f'x="{x}" y="{y}" font-size="{size}" letter-spacing="{track}" '
            f'font-weight="{weight}" text-anchor="{anchor}"')
    txt = esc(s.upper())
    if not glow:
        return f'<text class="d" {body} fill="{fill}" opacity="{opacity}">{txt}</text>'
    return _lit(body, txt, fill, size, opacity)


def prose(x, y, s, size=15, fill=ASH, italic=True, anchor="start", opacity=1):
    """Body text stays unlit — in-game the dim things stay dim."""
    style = ' font-style="italic"' if italic else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}"{style} '
            f'text-anchor="{anchor}" opacity="{opacity}">{esc(s)}</text>')


def numeral(x, y, s, size=40, fill=None, anchor="start", glow=True):
    """Figures carry the same halo as the caps, for the same reason."""
    fill = LUMEN if fill is None else fill
    body = (f'x="{x}" y="{y}" font-size="{size}" letter-spacing="1.5" '
            f'text-anchor="{anchor}"')
    txt = esc(s)
    if not glow:
        return f'<text class="d" {body} fill="{fill}">{txt}</text>'
    return _lit(body, txt, fill, size)


# Advance widths in em, measured off Palatino Linotype Italic (palai.ttf, 2048
# units per em), for the characters the typed line uses. Other characters fall
# back to the face's average.
PALATINO_ITALIC = {
    " ": .25, ".": .25, "N": .778, "a": .444, "b": .463, "c": .407, "d": .5,
    "e": .389, "f": .278, "g": .5, "h": .5, "i": .278, "k": .444, "l": .278,
    "m": .778, "n": .556, "o": .444, "r": .389, "s": .389, "t": .333, "u": .556,
    "v": .5, "w": .722, "y": .5,
}


def typeline(x, y, text, size=17, fill=None, cycle=15, italic=True,
             em=0.397):
    """One line, typed out a word per beat, then held and repeated.

    The reveal is a clip rectangle slid right to the end of each word in turn,
    on the shared beat, and the caret rides the same keyframes so it always
    sits at the reveal edge. A letter per step was nine repaints a second of
    the whole image. Each word is its own run at its measured Palatino width,
    pinned there by textLength, so a word ends where the reveal stops in any
    font: one run placed off an average width let the glyphs drift and the
    reveal cut words in half, and average-width slots crushed wide words.
    `em` is the fallback advance for a character the table does not hold.
    """
    import re, zlib
    fill = SOUL if fill is None else fill
    at = [0.0]                                     # x offset before each char
    for c in text:
        at.append(at[-1] + size * PALATINO_ITALIC.get(c, em))
    w = at[-1]
    lean = size * 0.12      # an italic's last glyph leans past its slot
    uid = zlib.crc32(text.encode()) % 100000     # stable across runs
    words = [(m.start(), m.end(), m.group()) for m in re.finditer(r"\S+", text)]
    edges = [0] + [at[end] + lean for _, end, _ in words]
    reveal = beats(f"tw{uid}", cycle, lambda i, _: f"transform: translateX("
                   f"{min(edges[min(i, len(edges) - 1)], w):.1f}px);")
    anim = f"animation:tw{uid} {cycle}s step-end infinite"
    style = ' font-style="italic"' if italic else ""
    runs = "".join(
        f'<text x="{x + at[a]:.1f}" y="{y}" textLength="{at[b] - at[a]:.1f}" '
        f'lengthAdjust="spacing">{esc(word)}</text>' for a, b, word in words)
    return (
        f'<style>{reveal}</style>'
        f'<clipPath id="tw{uid}"><rect class="typeline" x="{x - w:.1f}" '
        f'y="{y - size * 1.15:.1f}" width="{w:.1f}" height="{size * 1.6:.1f}" '
        f'style="--w:{w:.1f}px;{anim}"/></clipPath>'
        # Halo and core are both inside the clip, so they reveal together. The
        # halo is one filter over the group, not one per word.
        f'<g clip-path="url(#tw{uid})" font-size="{size}"{style}>'
        f'<g fill="{SOUL}" opacity=".7" filter="url(#haloM)">{runs}</g>'
        f'<g fill="{fill}">{runs}</g></g>'
        f'<rect class="typeline caret" x="{x - 1.4:.1f}" '
        f'y="{y - size * 0.95:.1f}" width="1.9" height="{size * 1.18:.1f}" '
        f'fill="{fill}" '
        f'style="--w:{w:.1f}px;{anim},caret 1s step-end infinite"/>'
    )


def dust(w, h, n=64, seed=101):
    """Sparse ambient spores behind every section, with no runtime repaint."""
    import random
    rng = random.Random(seed)
    out = []
    for i in range(n):
        cx, cy = rng.uniform(-20, w + 20), rng.uniform(0, h)
        r = rng.uniform(0.9, 3.2)
        rng.uniform(220, 520)
        dur = rng.uniform(34, 78)
        rng.uniform(-34, 34)
        opacity = rng.uniform(.10, .34)
        rng.uniform(0, dur)
        body = (f'cx="{cx:.0f}" cy="{cy:.0f}" r="{r*1.9:.2f}" '
                f'fill="url(#sporeCool)"')
        if i % 4 == 1:
            out.append(f'<circle {body} opacity="{opacity * .55:.2f}"/>')
    return "".join(out)


def motes(x, y, w, h, n=14, seed=3, fill=SOUL):
    """Sparse local spores. Deterministic, so builds stay reproducible."""
    import random
    rng = random.Random(seed)
    out = []
    for i in range(n):
        cx, cy = x + rng.random() * w, y + rng.random() * h
        r = rng.uniform(0.8, 2.1)
        dur = rng.uniform(9, 16)
        grad = "sporeWarm" if fill == INFECT else "sporeCool"
        rng.uniform(0, dur)
        body = (f'cx="{cx:.1f}" cy="{cy:.1f}" r="{r*1.9:.2f}" '
                f'fill="url(#{grad})"')
        if i % 3 == 1:
            out.append(f'<circle {body} opacity=".16"/>')
    return "".join(out)


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def commas(n):
    return f"{n:,}"
