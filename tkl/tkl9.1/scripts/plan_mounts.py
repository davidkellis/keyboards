#!/usr/bin/env python3
"""Find mounting candidates against real v9 placements before changing copper."""
from pathlib import Path
import json, sys, math
import numpy as np
from shapely.geometry import Point, box
from shapely.ops import unary_union
from shapely.strtree import STRtree
from plate_geometry import switch_aperture, stabilizer_apertures
from routing_geometry import k, objects

ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT.parent/'tkl9/case/board-geometry.json').read_text())
plate=[switch_aperture(*s['xy']) for s in d['switches']]
for s in d['switches']:
 if s['units']>=2:plate.append(stabilizer_apertures(*s['xy'],100 if s['units']==6.25 else 23.8))
top=unary_union(plate)
bottom=unary_union([box(*c['bounds']).buffer(.4) for c in d['components'] if c['side']=='bottom']+
 [Point(*h['xy']).buffer(max(h['size'])/2+.45) for h in d['holes']])
board=k.LoadBoard(str(ROOT/'kicad/keyboard.kicad_pcb'))
obs,_=objects(board)
tracks=[o for o in obs if not isinstance(o['item'],k.PAD)]
tree=STRtree([o['g'] for o in tracks])
pads=unary_union([o['g'] for o in obs if isinstance(o['item'],k.PAD)])
# Conservative XY projection of the preserved world-space battery reserve.
battery=box(2.8,75.5,275.0,130.0)
ant=box(326.97,86.25,336.97,99.05).buffer(5)
candidates=[]
for y in np.arange(20.6,126,.5):
 for x in np.arange(5,346,.5):
  p=Point(x,y)
  if p.distance(top)<2.4 or p.distance(bottom)<3.65:continue
  # Rear anchors are cantilevered from the rear wall above the battery, rather
  # than growing from the floor through its reserved volume.
  if (y<123.5 and p.distance(battery)<4) or p.distance(ant)<4:continue
  q=Point(x+27.03,149.19-y)
  if q.distance(pads)<3.25:continue
  hits=[int(i) for i in tree.query(q.buffer(3.4)) if q.distance(tracks[i]['g'])<3.4]
  candidates.append(dict(x=float(x),y=float(y),tracks=len(hits)))
print('Candidates',len(candidates))
targets=[(35,21),(115,21),(195,21),(285,21),(35,59),(145,59),(255,59),
         (330,50),(30,125),(140,125),(250,125),(297,120)]
selected=[]
for tx,ty in targets:
 options=[p for p in candidates if all(math.hypot(p['x']-q['x'],p['y']-q['y'])>20 for q in selected)]
 p=min(options,key=lambda p:math.hypot((p['x']-tx),(p['y']-ty)*1.5)+p['tracks']*4)
 selected.append(p)
print(json.dumps(selected,indent=2))
(ROOT/'validation/mount-candidates.json').write_text(json.dumps(dict(selected=selected,candidates=candidates),indent=2)+'\n')
