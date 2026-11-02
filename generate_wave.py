#!/usr/bin/env python3
"""Makes assets/wave-banner.svg: black banner with rolling waves of 0s and 1s.
Run:  python generate_wave.py            (edit the settings below first)
No dependencies, no API, works offline."""
import random, html

TEXT   = "ANWAR"
SUB    = "dev student | apps dev"
W, H   = 1000, 170
ROWS   = 7                 # rows of digits
STEP   = 12                # horizontal spacing between digits
AMP    = 16                # wave height in px
PERIOD = 4.0               # seconds for one wave cycle
SPREAD = 0.075             # phase shift per column (smaller = longer waves)
C1, C2 = "#ffffff", "#8c8c8c"   # white fading to grey, left to right

random.seed(3)
cols = W // STEP
y0 = (H - (ROWS - 1) * 18) / 2
els = []
for r in range(ROWS):
    for c in range(cols):
        x = c * STEP + 6
        y = y0 + r * 18
        delay = -(PERIOD - ((c * SPREAD + r * 0.22) % PERIOD))
        ch = random.choice("01")
        els.append(f'<text x="{x}" y="{y:.0f}" class="d" style="animation-delay:{delay:.2f}s">{ch}</text>')

title = ""
if TEXT:
    title = (f'<text x="{W/2}" y="{H/2 + 6}" text-anchor="middle" class="t" fill="#fff" filter="url(#glow)">{html.escape(TEXT)}</text>')
    if SUB:
        title += f'<text x="{W/2}" y="{H/2 + 34}" text-anchor="middle" class="s" fill="{C1}">{html.escape(SUB)}</text>'

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="'DejaVu Sans Mono',Menlo,Consolas,'Courier New',monospace">
<defs>
  <linearGradient id="g" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="0"><stop offset="0" stop-color="{C1}"/><stop offset="1" stop-color="{C2}"/></linearGradient>
  <linearGradient id="fade" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="0"><stop offset="0" stop-color="#000"/><stop offset=".12" stop-color="#fff"/><stop offset=".88" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>
  <mask id="m"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
  <filter id="glow" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <radialGradient id="hole" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#000" stop-opacity=".85"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
</defs>
<style>
  .d {{ font-size:14px; fill:url(#g); animation:wave {PERIOD}s ease-in-out infinite; }}
  @keyframes wave {{
    0%   {{ transform:translateY(0);          opacity:.55 }}
    25%  {{ transform:translateY(-{AMP}px);   opacity:1   }}
    50%  {{ transform:translateY(0);          opacity:.55 }}
    75%  {{ transform:translateY({AMP}px);    opacity:.2  }}
    100% {{ transform:translateY(0);          opacity:.55 }}
  }}
  .t {{ font-size:44px; font-weight:bold; letter-spacing:6px; }}
  .s {{ font-size:15px; letter-spacing:2px; }}
</style>
<rect width="{W}" height="{H}" fill="#000"/>
<g mask="url(#m)">{"".join(els)}</g>
{'<ellipse cx="%s" cy="%s" rx="330" ry="70" fill="url(#hole)"/>' % (W/2, H/2) if TEXT else ''}
{title}
</svg>'''
open("assets/wave-banner.svg", "w").write(svg)
print("wrote assets/wave-banner.svg", len(svg) // 1024, "KB")
