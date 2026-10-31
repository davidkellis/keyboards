#!/usr/bin/env python3
"""Move the driver inboard to clear the existing case's rear support lip."""
from routing_geometry import *
from shapely.ops import unary_union
import sexpdata as sx,copy,uuid
R=Path(__file__).resolve().parents[1];P=R/'kicad/keyboard.kicad_pcb'
def tag(n):return str(n[0]) if isinstance(n,list) and n else ''
def field(n,t):return next((a for a in n if tag(a)==t),None)
b=k.LoadBoard(str(P));refs={'U2','L1','D87','C1','C2','R10','R11'}
for f in b.GetFootprints():
 if f.GetReference() in refs:f.SetPosition(f.GetPosition()+vec((16,5)))
 if f.GetReference()=='R11':f.SetPosition(vec((122.9,29.5)))
 if f.GetReference()=='LED10':f.Reference().SetPosition(vec((345,128.585)))
b.BuildConnectivity();k.SaveBoard(str(P),b)
area=unary_union([box(85,20.5,107,31.5),box(101,25.5,125.5,36.5)])
tree=sx.loads(P.read_text());out=[]
for n in tree:
 if tag(n) not in ['segment','via']:out.append(n);continue
 name=field(n,'net')[-1]
 if name in ['LED_HV','LED_FB','BL_EN']:continue
 if name=='BOOST_SW':
  assert tag(n)=='segment'
  for key in ['start','end']:field(n,key)[1]+=16;field(n,key)[2]+=5
  out.append(n);continue
 if tag(n)=='via':
  if Point(*field(n,'at')[1:3]).distance(area)<field(n,'size')[1]/2+.2:continue
  out.append(n);continue
 if field(n,'layer')[1]!='B.Cu':out.append(n);continue
 line=LineString([field(n,'start')[1:3],field(n,'end')[1:3]])
 safe=area.buffer(field(n,'width')[1]/2+.2)
 if line.disjoint(safe):out.append(n);continue
 remain=line.difference(safe)
 for seg in list(remain.geoms) if hasattr(remain,'geoms') else [remain]:
  if seg.is_empty or seg.length<.08:continue
  part=copy.deepcopy(n);field(part,'start')[1:]=[round(v,6) for v in seg.coords[0]]
  field(part,'end')[1:]=[round(v,6) for v in seg.coords[-1]];field(part,'uuid')[1]=str(uuid.uuid4());out.append(part)
P.write_text(sx.dumps(out));b=k.LoadBoard(str(P))
def route(name,pts,width=.4):
 for a,c in zip(pts,pts[1:]):
  t=k.PCB_TRACK(b);t.SetStart(vec(a));t.SetEnd(vec(c));t.SetLayer(k.B_Cu);t.SetWidth(mm(width));t.SetNet(b.FindNet(name));b.Add(t)
route('LED_HV',[(114.4,27.5),(116.325,29.425),(116.325,31)])
route('LED_HV',[(116.325,31),(116.325,29.5),(122.075,29.5)],.25)
b.BuildConnectivity();k.SaveBoard(str(P),b)
print('Moved driver 16 mm right, 5 mm forward; restored short bottom-side switch routing')
