#!/usr/bin/env python3
"""Move the sense resistor beside the input capacitor for accessible routing."""
from routing_geometry import *
import sexpdata as sx,copy,uuid
R=Path(__file__).resolve().parents[1];P=R/'kicad/keyboard.kicad_pcb';b=k.LoadBoard(str(P))
f=next(f for f in b.GetFootprints() if f.GetReference()=='R10');f.SetPosition(vec((107.5,36)))
b.BuildConnectivity();k.SaveBoard(str(P),b)
tree=sx.loads(P.read_text());out=[];area=box(105.8,35.1,109.2,36.9)
def tag(n):return str(n[0]) if isinstance(n,list) and n else ''
def field(n,t):return next((a for a in n if tag(a)==t),None)
for n in tree:
 if tag(n)=='via' and Point(*field(n,'at')[1:3]).distance(area)<field(n,'size')[1]/2+.2:continue
 if tag(n)!='segment' or field(n,'layer')[1]!='B.Cu':out.append(n);continue
 line=LineString([field(n,'start')[1:3],field(n,'end')[1:3]]);safe=area.buffer(field(n,'width')[1]/2+.2)
 if line.disjoint(safe):out.append(n);continue
 rem=line.difference(safe)
 for seg in list(rem.geoms) if hasattr(rem,'geoms') else [rem]:
  if seg.is_empty or seg.length<.08:continue
  a=copy.deepcopy(n);field(a,'start')[1:]=[round(v,6) for v in seg.coords[0]];field(a,'end')[1:]=[round(v,6) for v in seg.coords[-1]];field(a,'uuid')[1]=str(uuid.uuid4());out.append(a)
P.write_text(sx.dumps(out));print('R10 moved to 107.5, 36 mm; clear of switch and mounting holes')
