from pathlib import Path
import json,math
import numpy as np
import pcbnew as k
from shapely.geometry import Point,LineString,box
from shapely.strtree import STRtree
b=k.LoadBoard(str((Path(__file__).resolve().parent / '../../kicad/keyboard.kicad_pcb').resolve()))
def xy(p):return np.array([k.ToMM(p.x),k.ToMM(p.y)])
items=[]
for t in b.GetTracks():
 if isinstance(t,k.PCB_VIA):g=Point(xy(t.GetPosition())).buffer(k.ToMM(max(t.GetWidth(k.F_Cu),t.GetWidth(k.B_Cu)))/2);kind='via'
 else:g=LineString([xy(t.GetStart()),xy(t.GetEnd())]).buffer(k.ToMM(t.GetWidth())/2);kind='track'
 items.append({'g':g,'kind':kind,'net':t.GetNetname(),'ref':None})
for f in b.GetFootprints():
 for p in f.Pads():
  if p.GetAttribute()==k.PAD_ATTRIB_NPTH:continue
  bb=p.GetBoundingBox();g=box(k.ToMM(bb.GetLeft()),k.ToMM(bb.GetTop()),k.ToMM(bb.GetRight()),k.ToMM(bb.GetBottom()))
  items.append({'g':g,'kind':'pad_bbox','net':p.GetNetname(),'ref':f.GetReference()})
tree=STRtree([i['g'] for i in items])
# All coordinates use the existing unrotated Choc V2 footprint axes. The
# Gateron bottom-view drawing has been mirrored into the top-view footprint.
cases={
 'choc_v1_add_two_alignment_holes':[{'xy':[-5.5,0],'drill':1.9,'pad':None},{'xy':[5.5,0],'drill':1.9,'pad':None}],
 'mx_pattern_add_two_contacts':[{'xy':[-2.54,-5.08],'drill':1.5,'pad':'1'},{'xy':[3.81,-2.54],'drill':1.5,'pad':'2'}],
 'mx_pattern_add_two_alignment_holes':[{'xy':[-5.08,0],'drill':1.7,'pad':None},{'xy':[5.08,0],'drill':1.7,'pad':None}],
}
report={}
for name,holes in cases.items():
 affected=[];allhits=set();padrefs=set()
 for f in b.GetFootprints():
  if not(f.GetReference().startswith('SW') and f.GetReference()!='SW87'):continue
  pads={p.GetNumber():p for p in f.Pads()};origin=xy(f.GetPosition())
  a=np.column_stack([xy(pads['1'].GetPosition())-origin,xy(pads['2'].GetPosition())-origin])@np.linalg.inv(np.array([[0,5],[-5.9,-3.8]]))
  local=[]
  for h in holes:
   center=origin+a@np.array(h['xy']);expected=pads[h['pad']].GetNetname() if h['pad'] else None
   # PTH: provisional 2.4 mm copper pad with 0.2 mm isolation. NPTH: drill
   # plus 0.25 mm copper clearance. Screening only; existing pad bboxes
   # overestimate some pad shapes and zones are deliberately excluded.
   radius=1.2+0.2 if h['pad'] else h['drill']/2+0.25
   region=Point(center).buffer(radius)
   hits=[]
   for idx in tree.query(region,predicate='intersects'):
    i=items[int(idx)]
    if expected and i['net']==expected:continue
    hits.append({'kind':i['kind'],'net':i['net'],'ref':i['ref']})
    allhits.add(int(idx))
    if i['kind']=='pad_bbox':padrefs.add(i['ref'])
   if hits:local.append({'local_xy':h['xy'],'hits':hits})
  if local:affected.append({'switch':f.GetReference(),'holes':local})
 report[name]={'new_holes_per_board':len(holes)*86,'switch_sites_with_existing_copper_conflicts':len(affected),'unique_items':len(allhits),'foreign_pad_refs':sorted(padrefs),'sites':affected}
print(json.dumps({name:{k:v for k,v in d.items() if k!='sites'} for name,d in report.items()},indent=2))
Path('/tmp/v11-other-switch-study/route-screen.json').write_text(json.dumps({'method':'Conservative 2D clearance screen, not DRC or a routed proposal. Existing pad bounding boxes are conservative; zones excluded. No CAD changed.','cases':report},indent=2))
