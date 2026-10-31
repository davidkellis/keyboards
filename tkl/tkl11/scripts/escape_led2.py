#!/usr/bin/env python3
"""Give LED2 cathode an ordinary via outside its solder land, through COL7's loop."""
from routing_geometry import *
import copy,sexpdata as sx,uuid
R=Path(__file__).resolve().parents[1];P=R/'kicad/keyboard.kicad_pcb'
start=(325.1,117.06);end=(323.2,117.06)
gap=LineString([start,end]).buffer(.42)
def tag(n):return str(n[0]) if isinstance(n,list) and n else ''
def field(n,t):return next((a for a in n if tag(a)==t),None)
tree=sx.loads(P.read_text());out=[]
for n in tree:
 if tag(n)!='segment' or field(n,'net')[-1]!='COL7' or field(n,'layer')[1]!='B.Cu':out.append(n);continue
 line=LineString([field(n,'start')[1:3],field(n,'end')[1:3]])
 if line.disjoint(gap):out.append(n);continue
 remain=line.difference(gap)
 for seg in list(remain.geoms) if hasattr(remain,'geoms') else [remain]:
  if seg.is_empty or seg.length<.08:continue
  part=copy.deepcopy(n);field(part,'start')[1:]=[round(v,6) for v in seg.coords[0]]
  field(part,'end')[1:]=[round(v,6) for v in seg.coords[-1]];field(part,'uuid')[1]=str(uuid.uuid4());out.append(part)
P.write_text(sx.dumps(out));b=k.LoadBoard(str(P));net=b.FindNet('LED_LINK_5')
if not any(isinstance(t,k.PCB_VIA) and xy(t.GetPosition())==end for t in b.GetTracks()):
 t=k.PCB_TRACK(b);t.SetStart(vec(start));t.SetEnd(vec(end));t.SetWidth(mm(.2));t.SetLayer(k.B_Cu);t.SetNet(net);b.Add(t)
 v=k.PCB_VIA(b);v.SetPosition(vec(end));v.SetWidth(mm(.6));v.SetDrill(mm(.3));v.SetViaType(k.VIATYPE_THROUGH);v.SetLayerPair(k.F_Cu,k.B_Cu);v.SetNet(net);b.Add(v)
b.BuildConnectivity();k.SaveBoard(str(P),b)
print('Added LED2 cathode fanout; reroute COL7 and the remaining LED link next')
