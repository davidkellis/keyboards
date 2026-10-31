#!/usr/bin/env python3
"""One-time off-land escape for D3; open adjacent tracks for final rerouting."""
from routing_geometry import *
from shapely.ops import unary_union
import sexpdata as sx,copy,uuid
R=Path(__file__).resolve().parents[1];P=R/'kicad/keyboard.kicad_pcb'
b=k.LoadBoard(str(P));pad=next(p for f in b.GetFootprints() if f.GetReference()=='D3' for p in f.Pads() if p.GetNumber()=='2')
net=pad.GetNetname();start=xy(pad.GetPosition());end=(101.35,40.45)
backup=P.read_bytes();tree=sx.loads(backup.decode())
def tag(n):return str(n[0]) if isinstance(n,list) and n else ''
def field(n,t):return next(v for v in n if tag(v)==t)
result=[];clipped=0
via=Point(*end).buffer(.3);fanout=LineString([start,end]).buffer(.1)
for n in tree:
 if tag(n) not in ('segment','via') or field(n,'net')[-1]==net:result.append(n);continue
 if tag(n)=='via':
  pos=Point(field(n,'at')[1:3]);radius=field(n,'size')[1]/2
  if pos.distance(via)<radius+.23 or pos.distance(fanout)<radius+.23:clipped+=1
  else:result.append(n)
  continue
 line=LineString([field(n,'start')[1:3],field(n,'end')[1:3]]);radius=field(n,'width')[1]/2
 obstacles=[via.buffer(radius+.23)]
 if field(n,'layer')[1]=='B.Cu':obstacles.append(fanout.buffer(radius+.23))
 safe=unary_union(obstacles)
 if line.disjoint(safe):result.append(n);continue
 clipped+=1;remain=line.difference(safe)
 for seg in list(remain.geoms) if hasattr(remain,'geoms') else [remain]:
  if seg.is_empty or seg.length<.08:continue
  part=copy.deepcopy(n);field(part,'start')[1:]=[round(v,6) for v in seg.coords[0]];field(part,'end')[1:]=[round(v,6) for v in seg.coords[-1]];field(part,'uuid')[1]=str(uuid.uuid4());result.append(part)
P.write_text(sx.dumps(result));b=k.LoadBoard(str(P))
t=k.PCB_TRACK(b);t.SetStart(vec(start));t.SetEnd(vec(end));t.SetWidth(mm(.2));t.SetLayer(k.B_Cu);t.SetNet(b.FindNet(net));b.Add(t)
v=k.PCB_VIA(b);v.SetPosition(vec(end));v.SetWidth(mm(.6));v.SetDrill(mm(.3));v.SetViaType(k.VIATYPE_THROUGH);v.SetLayerPair(k.F_Cu,k.B_Cu);v.SetNet(b.FindNet(net));b.Add(v)
b.BuildConnectivity();k.SaveBoard(str(P),b)
d=R/'validation/escape-drc.json';subprocess.run(['kicad-cli','pcb','drc','--format','json','-o',str(d),str(P)],check=True,stdout=subprocess.DEVNULL)
r=json.loads(d.read_text());errors=[v for v in r['violations'] if v['severity']=='error']
if errors:P.write_bytes(backup);raise AssertionError(errors)
(R/'reference/escape-vias.json').write_text(json.dumps(dict(ref='D3',pad='2',start=start,via=end,clipped_tracks=clipped),indent=2)+'\n')
print('Off-land escape at',end,'clipped',clipped,'adjacent copper items;',len(r['unconnected_items']),'connections to finish')
