#!/usr/bin/env python3
"""Shared ink, colour and lettering for the profile figures.

The palette is Hallownest's: a blue-black ground, bone for anything carved or
written, pale Soul for what is contained, and Infection amber for what has got
out. Amber is reserved for breach — it never decorates.
"""

VOID   = "#080B12"   # deepest ground
CAVERN = "#111725"   # midground panels
STONE  = "#1D2637"   # carved edges, rules
BONE   = "#E9E6DC"   # the mask; primary lettering
ASH    = "#8B96AB"   # secondary lettering
SOUL   = "#A9E8F0"   # pale light, still contained
INFECT = "#F0A93C"   # what leaked out — breach only

# Hollow Knight titles are Roman inscriptional caps. Palatino is Zapf's
# revival of the same Renaissance letterforms and ships on Windows and macOS,
# so it survives GitHub's img sandbox where a webfont would not.
SERIF = "'Palatino Linotype','Book Antiqua',Palatino,'URW Palladio L','Times New Roman',serif"


def head(w, h, extra_defs="", extra_css=""):
    """Open an SVG with the shared ink filters, glow and motion guard."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}"
     viewBox="0 0 {w} {h}" role="img">
<defs>
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
  <radialGradient id="lantern" cx="50%" cy="46%" r="62%">
    <stop offset="0%" stop-color="#16203A" stop-opacity=".95"/>
    <stop offset="58%" stop-color="#0B1120" stop-opacity=".55"/>
    <stop offset="100%" stop-color="{VOID}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="vignette" cx="50%" cy="50%" r="78%">
    <stop offset="55%" stop-color="{VOID}" stop-opacity="0"/>
    <stop offset="100%" stop-color="#000" stop-opacity=".72"/>
  </radialGradient>
{extra_defs}
</defs>
<style>
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
  @keyframes breathe {{ 0%,100% {{ opacity: .48 }} 50% {{ opacity: .95 }} }}
  @media (prefers-reduced-motion: reduce) {{
    .mote, .breathe {{ animation: none; opacity: .6; }}
  }}
</style>
<rect width="{w}" height="{h}" fill="{VOID}"/>'''


def tail():
    return "</svg>"


def vignette(w, h):
    return f'<rect width="{w}" height="{h}" fill="url(#vignette)"/>'


def caps(x, y, s, size=13, fill=BONE, track=4.2, weight="normal",
         anchor="start", opacity=1):
    """Inscriptional caps — the house voice for anything that names a thing."""
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
            f'letter-spacing="{track}" font-weight="{weight}" '
            f'text-anchor="{anchor}" opacity="{opacity}">{esc(s.upper())}</text>')


def prose(x, y, s, size=15, fill=ASH, italic=True, anchor="start", opacity=1):
    style = ' font-style="italic"' if italic else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}"{style} '
            f'text-anchor="{anchor}" opacity="{opacity}">{esc(s)}</text>')


def numeral(x, y, s, size=40, fill=BONE, anchor="start"):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
            f'letter-spacing="1.5" text-anchor="{anchor}">{esc(s)}</text>')


def motes(x, y, w, h, n=14, seed=3, fill=SOUL):
    """Ambient spores. Deterministic so the file only changes when data does."""
    import random
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        cx = x + rng.random() * w
        cy = y + rng.random() * h
        r = rng.uniform(0.8, 2.1)
        dur = rng.uniform(9, 16)
        # Negative delay: every spore is already partway through its drift when
        # the image loads, so the field is never empty on first paint.
        out.append(f'<circle class="mote" cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.2f}" '
                   f'fill="{fill}" opacity="0" '
                   f'style="animation-delay:-{rng.uniform(0, dur):.1f}s;'
                   f'animation-duration:{dur:.1f}s"/>')
    return "".join(out)


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def commas(n):
    return f"{n:,}"
