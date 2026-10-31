#!/usr/bin/env python3
"""Draw the actual v10 placements and highlights in a full-board plan."""
import json
from pathlib import Path
from html import escape
R=Path(__file__).resolve().parents[1];g=json.loads((R/'case/board-geometry.json').read_text())
W=g['board']['width'];D=g['board']['depth'];scale=4
X=lambda x:35+x*scale
Y=lambda y:90+(D-y)*scale
s=['<svg xmlns="http://www.w3.org/2000/svg" width="1475" height="710" viewBox="0 0 1475 710">','<rect width="1475" height="710" fill="#f8fafc"/>','<g font-family="sans-serif" fill="#18212f">']
def text(t,x,y,size=15,anchor='start',fill='#18212f'):
 s.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{fill}">{escape(t)}</text>')
def rect(bounds,fill,stroke='#64748b',dash=False):
 x,y,xx,yy=bounds
 s.append(f'<rect x="{X(x)}" y="{Y(yy)}" width="{(xx-x)*scale}" height="{(yy-y)*scale}" rx="3" fill="{fill}" stroke="{stroke}" stroke-width="1.4"'+(' stroke-dasharray="6 4"' if dash else '')+'/>')
text('v10 · Esc/F1 controller · all 86 keys',35,35,27)
text('Top view of PCB coordinates · USB faces rear · orange module sits underneath',35,64,17)
rect([0,0,W,D],'#e3efe6','#386950')
labels={'SW1':'Esc','SW2':'F1','SW15':'SW15','SW9':'SW9','SW16':'SW16','SW32':'Insert','SW24':'Home','SW33':'PgUp'}
for key in g['switches']:
 x,y=key['xy'];w=key['units']*19.05-1.05
 rect([x-w/2,y-8.5,x+w/2,y+8.5],'#ded2f0' if key['ref'] in ('SW9','SW15','SW16') else '#ffffff')
 text(labels.get(key['ref'],key['ref']),X(x),Y(y)+5,13,'middle')
for name,color in [('U1','#e7a14b'),('USB_SOCKET','#86bfff'),('J1','#bed0df'),('SW87','#adb7c9')]:
 c=next(c for c in g['components'] if c['ref']==name);rect(c['bounds'],color,dash=name=='U1')
 if name=='U1':
  x,y,xx,yy=c['bounds'];text('MCU',X((x+xx)/2),Y((y+yy)/2),14,'middle')
text('Purple: restored three keys · original switch centers retained · module USB connects directly through the rear bezel',35,650,18)
text('Module height, auxiliary-pad registration and assembled wireless range require a physical trial.',35,682,17)
s.extend(['</g>','</svg>']);(R/'case/layout-preview.svg').write_text('\n'.join(s)+'\n')
