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

VOID   = "#080B12"   # deepest ground
CAVERN = "#111725"   # midground panels and room fill
STONE  = "#1D2637"   # carved edges
BONE   = "#E9E6DC"   # the mask; anything carved or written
ASH    = "#8B96AB"   # secondary lettering — stays unlit
SOUL   = "#A9E8F0"   # pale light, still contained
INFECT = "#F0A93C"   # what leaked out — breach only

# Hollow Knight's wordmark is a bespoke Trajan-style inscriptional capital.
# Palatino is Zapf's revival of the same Renaissance letterforms and ships on
# Windows and macOS, so it survives GitHub's img sandbox where a webfont would
# not load at all.
SERIF = "'Palatino Linotype','Book Antiqua',Palatino,'URW Palladio L','Times New Roman',serif"

MARGIN = 72          # every figure indents to the same line
RULE_Y = 118         # every header rule sits at the same height


def _defs(extra=""):
    return f"""<defs>
  <filter id="ink" x="-8%" y="-8%" width="116%" height="116%">
    <feTurbulence type="fractalNoise" baseFrequency="0.028" numOctaves="3"
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
  <filter id="grain" x="0%" y="0%" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="4" seed="9"/>
    <feColorMatrix type="saturate" values="0"/>
  </filter>
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
  text {{ font-family: {SERIF}; }}
  .mote {{ animation: drift 11s ease-in-out infinite; transform-box: fill-box;
           transform-origin: center; }}
  @keyframes drift {{
    0%   {{ transform: translate(0,6px);      opacity: 0; }}
    18%  {{ opacity: .85; }}
    72%  {{ opacity: .5; }}
    100% {{ transform: translate(5px,-30px); opacity: 0; }}
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
    100% {{ transform: translateY(74px) scale(.5); opacity: 0; }}
  }}
  /* A lantern carried past: areas take the light in turn, never all at once. */
  .lit {{ animation: lit 14s ease-in-out infinite; }}
  @keyframes lit {{ 0%,72%,100% {{ opacity: .62 }} 30% {{ opacity: 1 }} }}
  /* The surface of a filled vessel is never quite still. */
  .shimmer {{ animation: shimmer 5.5s ease-in-out infinite; }}
  @keyframes shimmer {{ 0%,100% {{ opacity: .18 }} 50% {{ opacity: .5 }} }}

  @media (prefers-reduced-motion: reduce) {{
    .mote, .breathe, .drip, .lit, .shimmer {{
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
            f'<rect x="0" y="0" width="{w}" height="{band*0.7:.0f}" '
            f'fill="url(#edgeY)"/>'
            f'<g transform="translate(0,{h}) scale(1,-1)">'
            f'<rect x="0" y="0" width="{w}" height="{band*0.7:.0f}" '
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
           f'<rect width="{w}" height="{total}" fill="{VOID}"/>']
    dy = 0
    for h, body in sections:
        out.append(f'<g transform="translate(0,{dy})">')
        out.extend(body)
        out.append('</g>')
        dy += h
    out.append(edges(w, total))
    out.append('</svg>')
    return chr(10).join(out)


def section(title, subtitle, w=1200):
    """The one header block. Same place, same sizes, in every figure."""
    return (caps(MARGIN, 66, title, size=23, track=6.5, glow=True)
            + prose(MARGIN, 96, subtitle)
            + f'<path d="M {MARGIN} {RULE_Y} L {w - MARGIN} {RULE_Y}" '
              f'stroke="{BONE}" stroke-width="1.2" opacity=".2" '
              f'filter="url(#ink)"/>')


def footnote(text, y, w=1200):
    return (f'<path d="M {MARGIN} {y - 30} L {w - MARGIN} {y - 30}" '
            f'stroke="{BONE}" stroke-width="1" opacity=".14" filter="url(#ink)"/>'
            + prose(MARGIN, y, text, size=13, opacity=.85))


def caps(x, y, s, size=13, fill=BONE, track=4.2, weight="normal",
         anchor="start", opacity=1, glow=False):
    """Inscriptional caps — the house voice for anything that names a thing."""
    f = (f' filter="url(#{"bloom" if size >= 16 else "bloomSoft"})"'
         if glow else "")
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
            f'letter-spacing="{track}" font-weight="{weight}" '
            f'text-anchor="{anchor}" opacity="{opacity}"{f}>{esc(s.upper())}</text>')


def prose(x, y, s, size=15, fill=ASH, italic=True, anchor="start", opacity=1):
    """Body text stays unlit — in-game the dim things stay dim."""
    style = ' font-style="italic"' if italic else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}"{style} '
            f'text-anchor="{anchor}" opacity="{opacity}">{esc(s)}</text>')


def numeral(x, y, s, size=40, fill=BONE, anchor="start", glow=True):
    f = ' filter="url(#bloom)"' if glow else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
            f'letter-spacing="1.5" text-anchor="{anchor}"{f}>{esc(s)}</text>')


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
        out.append(f'<circle class="mote" cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.2f}" '
                   f'fill="{fill}" opacity="0" filter="url(#bloomSoft)" '
                   f'style="animation-delay:-{rng.uniform(0, dur):.1f}s;'
                   f'animation-duration:{dur:.1f}s"/>')
    return "".join(out)


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def commas(n):
    return f"{n:,}"
