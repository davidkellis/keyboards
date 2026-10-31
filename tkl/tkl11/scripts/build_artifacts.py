#!/usr/bin/env python3
"""Build source-derived optical layout and a clearly labeled acrylic trial DXF."""
from pathlib import Path
import csv,json,math
from shapely.geometry import box,Point,LineString
from shapely.ops import unary_union
from plate_geometry import switch_aperture,stabilizer_apertures
R=Path(__file__).resolve().parents[1];O=R/'case';g=json.loads((O/'board-geometry.json').read_text())
cfg=json.loads((R/'scripts/fit-config.json').read_text());design=json.loads((R/'reference/lighting-design.json').read_text())
W,D=g['board']['width'],g['board']['depth']
cutouts=[switch_aperture(*s['xy']) for s in g['switches']]
for s in g['switches']:
 if s['units']>=2:cutouts.append(stabilizer_apertures(*s['xy'],100 if s['units']==6.25 else 23.8))
profile=box(0,.3,W,D).difference(unary_union(cutouts))
assert profile.geom_type=='Polygon'
module={h['pad']:h['xy'] for h in g['holes'] if h['ref']=='U1'}
pockets=[LineString([module[n] for n in nums]).buffer(1.3) for nums in [('28','12'),('29','13'),('25','26','27')]]
j1=[h['xy'] for h in g['holes'] if h['ref']=='J1'];pockets.append(LineString(j1).buffer(1.1))
layers=[('CUT',list(profile.exterior.coords)[:-1])]+[('CUT',list(r.coords)[:-1]) for r in profile.interiors]
for p in pockets:layers.append(('POCKET_0.6MM_UNDERSIDE',list(p.exterior.coords)[:-1]))
entry_checks=[]
for led in design['leds']:
 x,y=led['board_xy'];window=box(x-1.05,y-1.4,x+1.05,y+1.4)
 assert window.difference(profile).area<1e-6,(led['ref'],'LED aperture is not covered by acrylic')
 entry_checks.append(dict(ref=led['ref'],board_xy_mm=[x,y],aperture_outside_acrylic_area_mm2=window.difference(profile).area,
                          acrylic_edge_clearance_mm=window.distance(profile.boundary)))
 patch=window.intersection(profile)
 if not patch.is_empty:
  for p in list(patch.geoms) if hasattr(patch,'geoms') else [patch]:layers.append(('ETCH_OPTIONAL_UNDERSIDE',list(p.exterior.coords)[:-1]))
dxf=['0','SECTION','2','HEADER','9','$INSUNITS','70','4','0','ENDSEC','0','SECTION','2','ENTITIES']
for layer,points in layers:
 dxf+=['0','LWPOLYLINE','8',layer,'90',str(len(points)),'70','1']
 for x,y in points:dxf+=['10',str(x),'20',str(y)]
for m in cfg['mounting']['points']:
 x,y=m['xy'];dxf+=['0','CIRCLE','8','M2_REFERENCE_NOT_CUT','10',str(x),'20',str(y),'40','1.25']
dxf+=['0','ENDSEC','0','EOF'];(O/'acrylic-plate-trial.dxf').write_text('\n'.join(dxf)+'\n')
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="560" viewBox="0 0 1200 560"><rect width="1200" height="560" fill="#f5f2e9"/><g font-family="system-ui,sans-serif" fill="#18373c">',
 '<text x="30" y="37" font-size="24" font-weight="650">V11 · two staggered interior rows of five reverse-mounted LEDs</text>',
 '<text x="30" y="64" font-size="14">Top view. Positions are real; glow and uniformity are not simulated. Rear / function row is at the top.</text>']
s=3.2;ox=34;oy=87
def xy(x,y):return ox+x*s,oy+(D-y)*s
svg.append(f'<rect x="{ox}" y="{oy}" width="{W*s}" height="{D*s}" rx="5" fill="#d6e9e5" stroke="#6b9591"/>')
for p in cutouts:
 for q in list(p.geoms) if hasattr(p,'geoms') else [p]:
  coords=' '.join(f'{px:.3f},{py:.3f}' for px,py in [xy(x,y) for x,y in q.exterior.coords]);svg.append(f'<polygon points="{coords}" fill="#f5f2e9" stroke="#b3c6bd" stroke-width=".8"/>')
for m in cfg['mounting']['points']:
 x,y=xy(*m['xy']);svg.append(f'<circle cx="{x}" cy="{y}" r="4" fill="none" stroke="#7f9290"/>')
for led in design['leds']:
 hole=next(h for h in g['holes'] if h['ref']==led['ref'] and not h['pad'])
 assert all(abs(a-b)<1e-6 for a,b in zip(hole['xy'],led['board_xy'])),led['ref']
 x,y=xy(*led['board_xy']);color='#b86c29' if led['added'] else '#216a77'
 svg.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{color}"/><text x="{x+9}" y="{y-5}" font-size="12" font-weight="650" fill="{color}">{led["ref"]}</text>')
svg+=['<text x="34" y="531" font-size="14" fill="#216a77">Blue: LED1–LED6 · kept in six-LED mode</text>',
 '<text x="480" y="531" font-size="14" fill="#b86c29">Orange: LED7–LED10 · remove and wire across pads 1/2 to test six</text></g></svg>']
(O/'lighting-layout.svg').write_text(''.join(svg))
with (O/'lighting-placement.csv').open('w',newline='') as f:
 writer=csv.writer(f,lineterminator='\n');writer.writerow(['LED','Row','X from left mm','Y from front mm','KiCad X mm','KiCad Y mm','Retained in six-source mode'])
 for led in sorted(design['leds'],key=lambda l:int(l['ref'][3:])):
  writer.writerow([led['ref'],led['row'],*led['board_xy'],*led['kicad_xy'],not led['added']])
(R/'validation/acrylic-entry-check.json').write_text(json.dumps(dict(passed=True,
 scope='All ten optical slot projections lie within solid acrylic in the 2D trial plate',
 outputs=entry_checks,physical_optics_verified=False),indent=2)+'\n')
# A plan-view detail makes the requested LED1 location easy to compare with keys.
detail=['<svg xmlns="http://www.w3.org/2000/svg" width="850" height="650" viewBox="0 0 850 650">',
 '<rect width="850" height="650" fill="#f5f2e9"/><g font-family="system-ui,sans-serif" fill="#18373c">',
 '<text x="30" y="35" font-size="23" font-weight="650">LED1 · moved 28.25 mm left, below Backspace</text>',
 '<text x="30" y="61" font-size="14">Top view: keycap outlines and plate cutouts; the LED remains underneath the PCB.</text>']
def dxy(x,y):return 35+(x-257)*12,90+(y-49)*12
labels={'SW31':'Backspace','SW40':'] }','SW41':r'\ |'}
for ref,label in labels.items():
 key=next(s for s in g['switches'] if s['ref']==ref);x,y=key['xy'];x+=27.03;y=149.19-y
 w=key['units']*19.05-1.05;left,top=dxy(x-w/2,y-8.5)
 detail.append(f'<rect x="{left}" y="{top}" width="{w*12}" height="204" rx="10" fill="#fffdf7" stroke="#9aada9" stroke-width="2"/>')
 left,top=dxy(x-7.075,y-7.075)
 detail.append(f'<rect x="{left}" y="{top}" width="169.8" height="169.8" rx="2" fill="#d6e9e5" stroke="#6b9591" stroke-dasharray="5 4"/>')
 tx,ty=dxy(x,y);detail.append(f'<text x="{tx}" y="{ty+6}" text-anchor="middle" font-size="20">{label}</text>')
x,y=dxy(*design['led1_relocation']['to_kicad_xy']);oldx,oldy=dxy(*design['led1_relocation']['from_kicad_xy'])
detail.extend([f'<line x1="{oldx}" y1="{oldy}" x2="{x}" y2="{y}" stroke="#216a77" stroke-width="2" stroke-dasharray="5 4"/>',
 f'<circle cx="{oldx}" cy="{oldy}" r="8" fill="#f5f2e9" stroke="#9aada9" stroke-width="2"/>',
 f'<rect x="{x-12.6}" y="{y-16.8}" width="25.2" height="33.6" rx="12.6" fill="#216a77"/>',
 f'<text x="{x-20}" y="{y+5}" text-anchor="end" font-size="17" font-weight="650">LED1</text>',
 f'<text x="{oldx}" y="{oldy-18}" text-anchor="middle" font-size="13">Previous location</text>',
 '<text x="30" y="630" font-size="14">Dashed squares: switch-plate openings. The optical slot lies under solid acrylic between openings.</text></g></svg>'])
(O/'led1-placement.svg').write_text(''.join(detail))
notes=dict(status='2D optical/fit trial, not production plate or complete hidden-mount case upper',
 dimensions_mm=[W,D],nominal_stock_thickness_mm=1.5,switch_opening_mm=14.15,
 layers=dict(CUT='Perimeter and diagnostic switch/stabilizer loops only; no LED holes',
 POCKET_0_6MM_UNDERSIDE='0.6 mm blind pockets under module/connector tails, preserving 0.9 mm roof in 1.5 mm stock',
 ETCH_OPTIONAL_UNDERSIDE='Experimental optical entry areas; no through cuts, not a finished extraction or coupler pattern',
 M2_REFERENCE_NOT_CUT='Existing PCB mounting coordinates; acrylic retention still needs a chosen case interface'),
 tool_compensation_applied=False,corner_dogbones_applied=False,physical_switch_clip_fit_verified=False)
(O/'acrylic-trial-notes.json').write_text(json.dumps(notes,indent=2)+'\n')
html='''<!doctype html><html><head><meta charset="utf-8"><title>TKL v11 — ten reverse LEDs</title><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{background:#f5f2e9;color:#18373c;font:17px/1.6 system-ui;margin:0}main{max-width:1200px;margin:30px auto;padding:20px}h1{font-size:38px;line-height:1.15}img{width:100%;height:auto}a{color:#216a77}.card{background:#fffdf7;padding:24px;border:1px solid #bdcbc3;border-radius:10px;margin:20px 0}.links a{display:inline-block;margin:8px 24px 8px 0}strong{font-weight:700}</style></head><body><main><h1>V11: two staggered rows of five LEDs</h1><p>Reverse-mounted LEDs shine through the PCB into the acrylic switch plate. All factory components remain on the bottom; v10 is preserved. LED type, count and maximum current are unchanged.</p><p>The locations follow the shared placement guidance: five interior lighting zones in each row, using solid acrylic between the switch cutouts.</p><img src="case/lighting-layout.svg" alt="Actual V11 LED layout showing LED1–LED6 in blue and four additions in orange"><div class="card"><strong>To test six-source lighting:</strong> disconnect power, remove LED7–LED10, and bridge pads 1 and 2 at each removed LED with a short insulated wire. The series driver adjusts the voltage and retains the same per-LED current. <strong>Never bridge R10.</strong> See the full rework procedure before soldering.</div><p>LED1 stays below Backspace between the right bracket and backslash/pipe keys. Eight other LEDs move; LED6 retains its position. LED10 is offset around the existing bottom-case support.</p><img src="case/led1-placement.svg" alt="Close-up of LED1 below Backspace at the boundary between right bracket and backslash"><div class="links"><a href="render-assembly/index.html">Interactive 3D assembly studio</a><a href="README.md">Design and rework notes</a><a href="manufacturing/tkl-v11-prototype-handoff.zip">Manufacturing handoff</a><a href="manufacturing/schematic.pdf">Schematic PDF</a><a href="case/acrylic-plate-trial.dxf">Acrylic trial DXF</a><a href="case/lighting-placement.csv">LED coordinate table</a><a href="case/pcb-bare.stl">Native substrate STL</a><a href="case/pcb-fit-check.stl">Print-fit PCB STL</a><a href="validation/summary.json">Electrical checks</a></div><p>The acrylic pattern is an optical/fit trial with optional entry marks. Optical couplers and an extraction pattern still need physical trials; relocation alone does not establish brightness or uniformity. The latest hidden-mount case upper integrates its original plate, so a flat acrylic sheet still needs a compatible retention design. This is a prototype PCB, not hardware-tested production.</p></main></body></html>'''
(R/'index.html').write_text(html)
print('Wrote optical map, acrylic trial DXF and v11 review page')
