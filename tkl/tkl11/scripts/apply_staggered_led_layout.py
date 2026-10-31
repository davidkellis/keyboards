#!/usr/bin/env python3
"""One-time conversion of the saved V11 LED1-move board to the staggered layout."""
from routing_geometry import *
from shapely.ops import unary_union
import copy,hashlib,sexpdata as sx,uuid
R=Path(__file__).resolve().parents[1];P=R/'kicad/keyboard.kicad_pcb'
plan=json.loads((R/'reference/staggered-led-placement.json').read_text())
assert hashlib.sha256(P.read_bytes()).hexdigest()==plan['original_pcb_sha256'],'Apply to the saved pre-staggered board only'
def tag(n):return str(n[0]) if isinstance(n,list) and n else ''
def field(n,t):return next((a for a in n if tag(a)==t),None)
b=k.LoadBoard(str(P));fp={f.GetReference():f for f in b.GetFootprints()}
order=plan['series_order'];lands=[];slots=[]
for row in plan['placements']:
 ref=row['ref'];f=fp[ref];assert list(xy(f.GetPosition()))==row['previous_kicad_xy']
 f.SetPosition(vec(row['kicad_xy']));x,y=row['kicad_xy'];f.Reference().SetPosition(vec((x,y-2.65)))
 if ref in ['LED4','LED7','LED9']:f.Reference().SetPosition(vec((x+5,y)))
 for p in f.Pads():
  if not p.GetNumber():slots.append(shape(p,p.GetDrillSize()));continue
  index=order.index(ref)
  net=('LED_HV' if index==0 else 'LED_LINK_'+str(index)) if p.GetNumber()=='2' else ('LED_FB' if index==9 else 'LED_LINK_'+str(index+1))
  p.SetNet(b.FindNet(net));lands.append(shape(p))
b.BuildConnectivity();k.SaveBoard(str(P),b)
land_area=unary_union(lands);slot_area=unary_union(slots)
# Retain the settled driver layout, its short switch node, and local HV/FB links.
driver=box(101.5,25.0,125,37.5)
tree=sx.loads(P.read_text());out=[];clipped=0
for n in tree:
 if tag(n) not in ['segment','via']:out.append(n);continue
 net=field(n,'net')[-1]
 if net.startswith('LED_LINK_'):continue
 if tag(n)=='via':
  at=Point(*field(n,'at')[1:3]);radius=field(n,'size')[1]/2
  if net in ['LED_HV','LED_FB'] and not driver.covers(at):continue
  if at.distance(land_area)<radius+.22 or at.distance(slot_area)<radius+.3:clipped+=1;continue
  out.append(n);continue
 line=LineString([field(n,'start')[1:3],field(n,'end')[1:3]])
 if net in ['LED_HV','LED_FB']:line=line.intersection(driver)
 radius=field(n,'width')[1]/2;blocked=slot_area.buffer(radius+.3)
 if field(n,'layer')[1]=='B.Cu':blocked=blocked.union(land_area.buffer(radius+.22))
 if net not in ['LED_HV','LED_FB'] and line.disjoint(blocked):out.append(n);continue
 clipped+=1;remain=line.difference(blocked)
 for seg in list(remain.geoms) if hasattr(remain,'geoms') else [remain]:
  if seg.is_empty or seg.length<.08:continue
  part=copy.deepcopy(n);field(part,'start')[1:]=[round(v,6) for v in seg.coords[0]]
  field(part,'end')[1:]=[round(v,6) for v in seg.coords[-1]];field(part,'uuid')[1]=str(uuid.uuid4());out.append(part)
P.write_text(sx.dumps(out));b=k.LoadBoard(str(P));b.BuildConnectivity();k.SaveBoard(str(P),b)
design=json.loads((R/'reference/lighting-design.json').read_text())
byref={p['ref']:p for p in plan['placements']}
for l in design['leds']:
 p=byref[l['ref']];l.update(kicad_xy=p['kicad_xy'],board_xy=p['board_xy'],row=p['row'],
 relocated=l.get('relocated',False) or p['kicad_xy']!=p['previous_kicad_xy'])
design.update(series_order=order,placement_plan='reference/staggered-led-placement.json',layout='Two staggered rows of five interior optical entries')
(R/'reference/lighting-design.json').write_text(json.dumps(design,indent=2)+'\n')
print('Applied ten interior positions and spatial series order; affected non-series copper pieces:',clipped)
