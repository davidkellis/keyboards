#!/usr/bin/env python3
"""Draw a board-coordinate plan of the v9.3 module trial, without vendor imagery."""
import json
from pathlib import Path
from html import escape
R=Path(__file__).resolve().parents[1];g=json.loads((R/'case/board-geometry.json').read_text());old=json.loads((R.parent/'tkl7.5/case/board-geometry.json').read_text())
X=lambda x:40+(x-287)*9
Y=lambda y:60+(150-y)*9
s=['<svg xmlns="http://www.w3.org/2000/svg" width="760" height="960" viewBox="0 0 760 960">','<rect width="760" height="960" fill="#f8fafc"/>','<g font-family="sans-serif" fill="#18212f">']
def text(t,x,y,size=15,anchor='start',fill='#18212f'):
 s.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{fill}">{escape(t)}</text>')
def rect(bounds,fill,stroke='#64748b',dash=False):
 x,y,xx,yy=bounds
 s.append(f'<rect x="{X(x)}" y="{Y(yy)}" width="{(xx-x)*9}" height="{(yy-y)*9}" rx="3" fill="{fill}" stroke="{stroke}" stroke-width="1.8"'+(' stroke-dasharray="6 4"' if dash else '')+'/>')
text('v9.3 · direct rear USB-C',32,30,25)
text('Module underneath PCB · rear is at the top',32,54,15)
rect([287,59,350.76,129.19],'#e3efe6','#386950')
for k in old['switches']:
 if k['ref'] in ('SW9','SW15','SW16'):
  x,y=k['xy'];rect([x-9.1,y-8.5,x+9.1,y+8.5],'none','#b28cc6',True)
labels={'SW32':'Insert','SW24':'Home','SW33':'PgUp','SW49':'Delete','SW42':'End','SW50':'PgDn'}
for k in g['switches']:
 if k['ref'] in labels:
  x,y=k['xy'];rect([x-7,y-7,x+7,y+7],'#ffffff');text(labels[k['ref']],X(x),Y(y)+5,15,'middle')
for name,color in [('U1','#e7a14b'),('USB_SOCKET','#86bfff'),('USB_PLUG_EXTERNAL','#f6d878'),('J1','#bed0df'),('SW87','#adb7c9')]:
 c=next(c for c in g['components'] if c['ref']==name);rect(c['bounds'],color)
 x,y,xx,yy=c['bounds'];label={'U1':'nRF52840','USB_SOCKET':'','USB_PLUG_EXTERNAL':'USB plug','J1':'BAT','SW87':'Power'}[name]
 if label:text(label,X((x+xx)/2),Y((y+yy)/2)+5,14,'middle')
m=next(c for c in g['components'] if c['ref']=='U1');x,y,xx,yy=m['bounds'];cx=X((x+xx)/2)
s.append(f'<path d="M {cx} {Y(117)} v -60 m -6 9 l 6 -9 l 6 9" fill="none" stroke="#583d1f" stroke-width="3"/>')
text('3 key positions removed',X(290),Y(110),13,fill='#794c91')
text('Dashed outlines: removed keys. Orange: module envelope.',32,910,16)
text('Fit trial only: actual thickness, socket position and RF remain unverified.',32,939,14)
s.extend(['</g>','</svg>']);(R/'case/layout-preview.svg').write_text('\n'.join(s)+'\n')
