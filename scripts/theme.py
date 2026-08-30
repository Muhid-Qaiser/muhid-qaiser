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
  <filter id="ink" x="-8%" y="-8%" width="116%" height="116%">
    <feTurbulence type="fractalNoise" baseFrequency="0.028" numOctaves="2"
                  seed="7" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="2.6"
                       xChannelSelector="R" yChannelSelector="G"/>
  </filter>
  <filter id="inkSoft" x="-8%" y="-8%" width="116%" height="116%">
    <feTurbulence type="fractalNoise" baseFrequency="0.05" numOctaves="2"
                  seed="19" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="1.3"
                       xChannelSelector="R" yChannelSelector="G"/>
  </filter>
  <!-- The game's bloom pass: pale things bleed light into the dark. -->
  <filter id="bloom" x="-60%" y="-60%" width="220%" height="220%">
    <feGaussianBlur stdDeviation="3.4" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="b"/>
             <feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
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


_STYLE = f"""<style>
  {_display_face()}
  text {{ font-family: {SERIF}; }}
  .d {{ font-family: {DISPLAY}; }}
  .mote {{ animation: drift 11s ease-in-out infinite; transform-box: fill-box;
           transform-origin: center; }}
  @keyframes drift {{
    0%   {{ transform: translate(0,6px);      opacity: 0; }}
    18%  {{ opacity: .85; }}
    72%  {{ opacity: .5; }}
    100% {{ transform: translate(5px,-30px); opacity: 0; }}
  }}
  /* One field across the whole document rather than a field per section, so
     a spore can leave the masthead and arrive in the map. Distance, duration
     and brightness ride on each particle as variables. */
  .dust {{ animation: dust var(--t, 40s) linear infinite;
           transform-box: fill-box; transform-origin: center; }}
  @keyframes dust {{
    0%        {{ transform: translate(0,0);                    opacity: 0; }}
    12%, 84%  {{ opacity: var(--o, .3); }}
    100%      {{ transform: translate(var(--dx,0), var(--dy,-300px));
                 opacity: 0; }}
  }}
  .breathe {{ animation: breathe 6.5s ease-in-out infinite; }}
  @keyframes breathe {{ 0%,100% {{ opacity: .5 }} 50% {{ opacity: 1 }} }}

  /* Infection gathering at the breach, swelling, and falling away. */
  .drip {{ animation: drip 7s cubic-bezier(.5,0,.85,.4) infinite;
           transform-box: fill-box; transform-origin: center; }}
  @keyframes drip {{
    0%   {{ transform: translateY(0) scale(.35); opacity: 0; }}
    22%  {{ transform: translateY(2px) scale(1);  opacity: .95; }}
    38%  {{ transform: translateY(6px) scale(1);  opacity: .95; }}
    100% {{ transform: translateY(var(--fall, 74px)) scale(.5); opacity: 0; }}
  }}
  /* A lantern carried past: areas take the light in turn, never all at once. */
  .lit {{ animation: lit 14s ease-in-out infinite; }}
  @keyframes lit {{ 0%,72%,100% {{ opacity: .62 }} 30% {{ opacity: 1 }} }}
  /* The surface of a filled vessel is never quite still. */
  .shimmer {{ animation: shimmer 5.5s ease-in-out infinite; }}
  @keyframes shimmer {{ 0%,100% {{ opacity: .18 }} 50% {{ opacity: .5 }} }}

  /* Soul is a liquid. The crest travels one wavelength and repeats, so the
     loop is seamless; the level rises and falls the way the meter does when
     Soul is spent and gathered again. */
  .tide {{ animation: tide 6.5s linear infinite; }}
  @keyframes tide {{ to {{ transform: translateX(-40px); }} }}
  .rise {{ animation: rise 15s ease-in-out infinite; }}
  @keyframes rise {{
    0%, 100% {{ transform: translateY(var(--low, 0px)); }}
    45%, 62% {{ transform: translateY(0px); }}
  }}

  /* A line typed one character at a time: a clip slid right in steps, one
     step per character, with the caret riding the same timing. */
  @keyframes typeline {{
    0%        {{ transform: translateX(0); }}
    62%, 100% {{ transform: translateX(var(--w, 0)); }}
  }}
  @keyframes caret {{ 0%,49% {{ opacity: 1 }} 50%,100% {{ opacity: 0 }} }}

  @media (prefers-reduced-motion: reduce) {{
    /* Stopping the reveal mid-way would leave the line half-invisible, so it
       jumps to fully typed and the caret goes away. */
    .typeline {{ animation: none !important;
                 transform: translateX(var(--w, 0)) !important; }}
    .caret {{ display: none; }}
  }}
  @media (prefers-reduced-motion: reduce) {{
    .mote, .dust, .breathe, .drip, .lit, .shimmer, .tide, .rise {{
      animation: none; opacity: .7;
    }}
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
    dy = 0
    for h, body in sections:
        out.append(f'<g transform="translate(0,{dy})">')
        out.extend(body)
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
            + f'<path d="M {MARGIN} {RULE_Y} L {w - MARGIN} {RULE_Y}" '
              f'stroke="{BONE}" stroke-width="1.2" opacity=".2" '
              f'filter="url(#ink)"/>')


def footnote(text, y, w=1200):
    return (f'<path d="M {MARGIN} {y - 30} L {w - MARGIN} {y - 30}" '
            f'stroke="{BONE}" stroke-width="1" opacity=".14" filter="url(#ink)"/>'
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
    return (_halo(body, txt, size, opacity)
            + f'<text class="d" {body} fill="{fill}" opacity="{opacity}">{txt}</text>')


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
    return (_halo(body, txt, size)
            + f'<text class="d" {body} fill="{fill}">{txt}</text>')


def typeline(x, y, text, size=17, fill=None, cycle=14, italic=True,
             em=0.397):
    """One line, typed out a character at a time, then held and repeated.

    The reveal is a clip rectangle slid right in steps() — one step per
    character — and the caret runs the same animation so it always sits at the
    reveal edge. textLength pins the line to the width the steps were computed
    from, so the caret lands exactly on the final glyph instead of drifting
    past it. `em` is the measured average advance for the face: 0.397 for
    Palatino italic, 0.464 upright.
    """
    import zlib
    fill = SOUL if fill is None else fill
    n = len(text)
    w = size * em * n
    uid = zlib.crc32(text.encode()) % 100000     # stable across runs
    anim = f"animation:typeline {cycle}s steps({n},end) infinite"
    style = ' font-style="italic"' if italic else ""
    return (
        f'<clipPath id="tw{uid}"><rect class="typeline" x="{x - w:.1f}" '
        f'y="{y - size * 1.15:.1f}" width="{w:.1f}" height="{size * 1.6:.1f}" '
        f'style="--w:{w:.1f}px;{anim}"/></clipPath>'
        # Halo and core are both inside the clip, so they reveal together.
        f'<g clip-path="url(#tw{uid})">'
        f'<text x="{x}" y="{y}" font-size="{size}" fill="{SOUL}" opacity=".7"{style} '
        f'filter="url(#haloM)" textLength="{w:.1f}" lengthAdjust="spacing">'
        f'{esc(text)}</text>'
        f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}"{style} '
        f'textLength="{w:.1f}" lengthAdjust="spacing">{esc(text)}</text></g>'
        f'<rect class="typeline caret" x="{x - 1.4:.1f}" '
        f'y="{y - size * 0.95:.1f}" width="1.9" height="{size * 1.18:.1f}" '
        f'fill="{fill}" '
        f'style="--w:{w:.1f}px;{anim},caret .85s step-end infinite"/>'
    )


def dust(w, h, n=64, seed=101):
    """Ambient spores for the whole page, drawn once behind every section.

    These travel far enough to cross a section boundary — up to two thirds of
    a section's height — so the page reads as one column of air rather than
    three stacked panels that each happen to have their own weather. Slower
    and dimmer than the per-section motes, which stay where they are.
    """
    import random
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        cx, cy = rng.uniform(-20, w + 20), rng.uniform(0, h)
        r = rng.uniform(0.9, 3.2)
        far = rng.uniform(220, 520)          # comfortably past a section edge
        dur = rng.uniform(34, 78)
        out.append(
            f'<circle class="dust" cx="{cx:.0f}" cy="{cy:.0f}" r="{r*1.9:.2f}" '
            f'fill="url(#sporeCool)" opacity="0" '
            f'style="--t:{dur:.0f}s;--dx:{rng.uniform(-34, 34):.0f}px;'
            f'--dy:-{far:.0f}px;--o:{rng.uniform(.10, .34):.2f};'
            f'animation-delay:-{rng.uniform(0, dur):.0f}s"/>')
    return "".join(out)


def motes(x, y, w, h, n=14, seed=3, fill=SOUL):
    """Ambient spores. Deterministic, so a file changes only when data does."""
    import random
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        cx, cy = x + rng.random() * w, y + rng.random() * h
        r = rng.uniform(0.8, 2.1)
        dur = rng.uniform(9, 16)
        # Negative delay: every spore is already partway through its drift when
        # the image loads, so the field is never empty on first paint.
        grad = "sporeWarm" if fill == INFECT else "sporeCool"
        out.append(f'<circle class="mote" cx="{cx:.1f}" cy="{cy:.1f}" '
                   f'r="{r*1.9:.2f}" fill="url(#{grad})" opacity="0" '
                   f'style="animation-delay:-{rng.uniform(0, dur):.1f}s;'
                   f'animation-duration:{dur:.1f}s"/>')
    return "".join(out)


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def commas(n):
    return f"{n:,}"
