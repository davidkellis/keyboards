#!/usr/bin/env python3
"""Draw actual V12 switch lands/drills, with family-specific usage highlighted."""
from routing_geometry import *
from html import escape
R=Path(__file__).resolve().parents[1]
b=k.LoadBoard(str(R/'kicad/keyboard.kicad_pcb'));f=next(f for f in b.GetFootprints() if f.GetReference()=='SW1')
origin=np.array(xy(f.GetPosition()))
s=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="545" viewBox="0 0 1100 545">',
 '<rect width="1100" height="545" fill="#f5f7fa"/>',
 '<style>text{font-family:sans-serif;fill:#172334}.title{font-size:25px;font-weight:700}.sub{font-size:14px}.label{font-size:13px}</style>',
 '<text x="30" y="38" class="title">V12 · one soldered PCB, three switch families</text>',
 '<text x="30" y="64" class="sub">Top view · all original Choc V2 holes remain unchanged · choose one family per key</text>']
for index,(name,note) in enumerate([('Kailh Choc V2 / Whale','Original holes and contacts'),('Kailh Choc V1','Original contacts + shared side slots'),('Gateron Low Profile 3.0','Alternate contacts + shared side slots')]):
 cx=190+index*360;cy=257;scale=16
 s.extend([f'<rect x="{cx-162}" y="90" width="324" height="340" rx="16" fill="white" stroke="#d6dde5"/>',
           f'<text x="{cx}" y="119" text-anchor="middle" font-size="18" font-weight="700">{escape(name)}</text>',
           f'<rect x="{cx-7.5*scale}" y="{cy-7.5*scale}" width="{15*scale}" height="{15*scale}" rx="5" fill="#f6faf6" stroke="#87a88e" stroke-dasharray="4 4"/>'])
 for p in f.Pads():
  ds=p.GetDrillSize()
  if not ds.x:continue
  pos=np.array(xy(p.GetPosition()))-origin;dx,dy=pos
  x,y=cx+dx*scale,cy+dy*scale
  addedcontact=p.GetNumber() and k.ToMM(ds.x)==1.5
  slot=p.GetDrillShape()==k.PAD_DRILL_SHAPE_OBLONG
  used=(not addedcontact and not slot) if index==0 else ((p.GetNumber() and not addedcontact) or slot or abs(dx)<.01) if index==1 else (addedcontact or slot or abs(dx)<.01 and abs(dy)<.01)
  color=('#ca7a2a' if p.GetNumber() else '#307bba') if used else '#cfd5dc'
  if p.GetAttribute()!=k.PAD_ATTRIB_NPTH:
   w,h=xy(p.GetSize());s.append(f'<ellipse cx="{x}" cy="{y}" rx="{w*scale/2}" ry="{h*scale/2}" fill="{color}"/>')
  w,h=xy(ds)
  if slot:s.append(f'<rect x="{x-w*scale/2}" y="{y-h*scale/2}" width="{w*scale}" height="{h*scale}" rx="{h*scale/2}" fill="white" stroke="{color}" stroke-width="2"/>')
  else:s.append(f'<circle cx="{x}" cy="{y}" r="{w*scale/2}" fill="white" stroke="{color}" stroke-width="2"/>')
  if p.GetNumber() and used:s.append(f'<text x="{x}" y="{y-22}" text-anchor="middle" class="label">{p.GetNumber()}</text>')
 s.append(f'<text x="{cx}" y="411" text-anchor="middle" class="label">{escape(note)}</text>')
s.extend(['<text x="30" y="465" class="sub">Shared locating slots: 2.32 × 1.90 mm at X = ±5.29 mm · Center: 5.05 mm · Gateron contacts: Ø1.50 mm</text>',
 '<text x="30" y="491" class="sub">Kailh plate top: 2.2 mm above PCB · Gateron plate top: 2.5 mm · Choc V1 requires Choc keycaps</text>',
 '<text x="30" y="517" class="sub">Grey = unused holes for that family. CAD mounting support; physical plate, keycap, stabilizer and optical fit still need testing.</text>','</svg>'])
(R/'reference/switch-pattern.svg').write_text('\n'.join(s)+'\n')
