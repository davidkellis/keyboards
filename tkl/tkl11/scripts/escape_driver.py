#!/usr/bin/env python3
"""Fan out the driver pins before routing surrounding matrix/control nets."""
from routing_geometry import *
import sexpdata as sx,copy,uuid
R=Path(__file__).resolve().parents[1];P=R/'kicad/keyboard.kicad_pcb'
def tag(n):return str(n[0]) if isinstance(n,list) and n else ''
def field(n,t):return next((a for a in n if tag(a)==t),None)
tree=sx.loads(P.read_text());out=[];area=box(108,29.3,113.8,34)
for n in tree:
 if tag(n) not in ['segment','via']:out.append(n);continue
 name=field(n,'net')[-1]
 if name in ['BL_EN','LED_FB']:continue
 if name in ['BOOST_SW','LED_HV']:out.append(n);continue
 if tag(n)=='via':
  if Point(*field(n,'at')[1:3]).distance(area)<field(n,'size')[1]/2+.2:continue
  out.append(n);continue
 line=LineString([field(n,'start')[1:3],field(n,'end')[1:3]])
 safe=area.buffer(field(n,'width')[1]/2+.2)
 if line.disjoint(safe):out.append(n);continue
 remain=line.difference(safe)
 for seg in list(remain.geoms) if hasattr(remain,'geoms') else [remain]:
  if seg.is_empty or seg.length<.08:continue
  a=copy.deepcopy(n);field(a,'start')[1:]=[round(v,6) for v in seg.coords[0]]
  field(a,'end')[1:]=[round(v,6) for v in seg.coords[-1]];field(a,'uuid')[1]=str(uuid.uuid4());out.append(a)
P.write_text(sx.dumps(out));b=k.LoadBoard(str(P))
for name,pts in [('GND',[(109.6625,31.5),(110.5,31.5),(110.5,33.2)]),
                 ('BAT_SW',[(111.3375,32.15),(112,32.15),(112,32.9)]),
                 ('LED_FB',[(109.6625,30.85),(110.5,30.85),(110.5,29.8)]),
                 ('BL_EN',[(111.3375,30.85),(113,30.85),(113,30)])]:
 for a,c in zip(pts,pts[1:]):
  t=k.PCB_TRACK(b);t.SetStart(vec(a));t.SetEnd(vec(c));t.SetWidth(mm(.2));t.SetLayer(k.B_Cu);t.SetNet(b.FindNet(name));b.Add(t)
 v=k.PCB_VIA(b);v.SetPosition(vec(pts[-1]));v.SetWidth(mm(.6));v.SetDrill(mm(.3));v.SetViaType(k.VIATYPE_THROUGH);v.SetLayerPair(k.F_Cu,k.B_Cu);v.SetNet(b.FindNet(name));b.Add(v)
b.BuildConnectivity();k.SaveBoard(str(P),b)
print('Four driver pins escaped through standard 0.6 / 0.3 mm vias outside solder lands')
