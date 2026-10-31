#!/usr/bin/env python3
"""One-time V11 edit: align LED1 below Backspace at the ] / backslash boundary."""
from routing_geometry import *
from shapely.ops import unary_union
import copy, hashlib, sexpdata as sx, uuid

R=Path(__file__).resolve().parents[1];P=R/'kicad/keyboard.kicad_pcb'
OLD=(314.0,71.45);NEW=(285.75,71.45)
def tag(n):return str(n[0]) if isinstance(n,list) and n else ''
def field(n,t):return next((a for a in n if tag(a)==t),None)
b=k.LoadBoard(str(P));fp={f.GetReference():f for f in b.GetFootprints()}
assert xy(fp['LED1'].GetPosition())==OLD,'This transform applies only to the pre-move V11 board'
snapshot=R/'reference/led1-before-move';snapshot.mkdir(exist_ok=True)
for p in [P,R/'reference/lighting-design.json']:
 target=snapshot/p.name
 assert not target.exists() or target.read_bytes()==p.read_bytes(),'Do not overwrite a different baseline'
 if not target.exists():target.write_bytes(p.read_bytes())
baseline_sha=hashlib.sha256(P.read_bytes()).hexdigest()
f=fp['LED1'];nets={p.GetNetname() for p in f.Pads() if p.GetNumber()}
assert nets=={'LED_LINK_3','LED_LINK_4'}
f.SetPosition(vec(NEW));b.BuildConnectivity();k.SaveBoard(str(P),b)
# Clear only the two affected LED links and copper in the new footprint's way.
lands=unary_union([shape(p) for p in f.Pads() if p.GetNumber()])
slot=next(shape(p,p.GetDrillSize()) for p in f.Pads() if not p.GetNumber())
tree=sx.loads(P.read_text());out=[];removed_links=0;clipped=0
for n in tree:
 if tag(n) not in ['segment','via']:out.append(n);continue
 if field(n,'net')[-1] in nets:removed_links+=1;continue
 if tag(n)=='via':
  at=Point(*field(n,'at')[1:3]);radius=field(n,'size')[1]/2
  if at.distance(lands)<radius+.22 or at.distance(slot)<radius+.3:clipped+=1;continue
  out.append(n);continue
 line=LineString([field(n,'start')[1:3],field(n,'end')[1:3]])
 radius=field(n,'width')[1]/2
 blocked=slot.buffer(radius+.3)
 if field(n,'layer')[1]=='B.Cu':blocked=blocked.union(lands.buffer(radius+.22))
 if line.disjoint(blocked):out.append(n);continue
 clipped+=1;remain=line.difference(blocked)
 for seg in list(remain.geoms) if hasattr(remain,'geoms') else [remain]:
  if seg.is_empty or seg.length<.08:continue
  part=copy.deepcopy(n);field(part,'start')[1:]=[round(v,6) for v in seg.coords[0]]
  field(part,'end')[1:]=[round(v,6) for v in seg.coords[-1]]
  field(part,'uuid')[1]=str(uuid.uuid4());out.append(part)
P.write_text(sx.dumps(out));b=k.LoadBoard(str(P));b.BuildConnectivity();k.SaveBoard(str(P),b)
design=json.loads((R/'reference/lighting-design.json').read_text())
led=next(l for l in design['leds'] if l['ref']=='LED1')
led.update(kicad_xy=list(NEW),board_xy=[round(NEW[0]-27.03,6),round(149.19-NEW[1],6)],relocated=True)
design['optional_for_six_led_mode']=design.pop('optional_to_retain_v10_six')
design['led1_relocation']=dict(from_kicad_xy=list(OLD),to_kicad_xy=list(NEW),left_mm=OLD[0]-NEW[0],
 target='Below Backspace (SW31), between the upper corners of right bracket (SW40) and backslash/pipe (SW41)',
 pre_move_pcb_sha256=baseline_sha)
(R/'reference/lighting-design.json').write_text(json.dumps(design,indent=2)+'\n')
print('Moved LED1',OLD,'->',NEW,'; removed affected LED-link tracks/vias:',removed_links,'; clipped other copper:',clipped)
