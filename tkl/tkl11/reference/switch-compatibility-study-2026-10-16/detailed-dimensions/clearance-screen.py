from pathlib import Path
import json,math,hashlib
import numpy as np
import pcbnew as k
from shapely.geometry import Point,LineString,box
from shapely.strtree import STRtree
boardpath=(Path(__file__).resolve().parent / '../../../kicad/keyboard.kicad_pcb').resolve()
b=k.LoadBoard(str(boardpath))
def xy(p):return np.array([k.ToMM(p.x),k.ToMM(p.y)])
assert not any(isinstance(t,k.PCB_ARC) for t in b.GetTracks()),'Arc geometry needs special treatment'
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
switches=[f for f in b.GetFootprints() if f.GetReference().startswith('SW') and f.GetReference()!='SW87']
assert len(switches)==86
# Coordinates are TOP-VIEW footprint coordinates, with candidate LED window
# facing the same edge as Choc V2 before rotation. Contact numbers here are
# candidate net assignments, not manufacturer terminal labels (SPST has no polarity).
baseholes=[{'xy':[0,0],'drill':5.05,'name':'center'},{'xy':[0,-5.9],'drill':1.2,'name':'1'},{'xy':[5,-3.8],'drill':1.2,'name':'2'},{'xy':[-5,5.15],'drill':1.6,'name':'support'}]
def hole(x,y,d,net=None):return {'xy':[x,y],'drill':d,'net':net}
contacts_mx=[hole(-2.54,-5.08,1.5,'1'),hole(3.81,-2.54,1.5,'2')]
pegs_mx=[hole(-5.08,0,1.7),hole(5.08,0,1.7)]
cases={
'choc_v1_alignment':{'holes':[hole(-5.5,0,1.9),hole(5.5,0,1.9)],'center':5.05,'source':'Kailh CPG135001D01-16 manufacturer drawing'},
'gateron3_mx_contacts_only':{'holes':contacts_mx,'center':5.05,'source':'Gateron Grey Heron drawing; contacts-only view excludes required pegs'},
'gateron3_mx_complete':{'holes':contacts_mx+pegs_mx,'center':5.05,'source':'Gateron Grey Heron, Silver 3.0 and Silent Red 3.0 drawings'},
'gateron2_three_pin_solder_feasibility':{'holes':[hole(-2.6,-5.75,1.5,'1'),hole(4.4,-4.7,1.5,'2')],'center':5.2,'source':'Gateron KS-33H10B050NN-Y24; 1.5 mm solder drills are provisional, manufacturer drawing shows 3 mm connector clearance holes'},
'gateron2_silent_five_pin_solder_feasibility':{'holes':[hole(-2.6,-5.75,1.5,'1'),hole(4.4,-4.7,1.5,'2')]+pegs_mx,'center':5.25,'source':'Gateron KS-33FJH10B045NW-X5; provisional 1.5 mm round solder drills instead of manufacturer connector slots'},
}
report={}
for name,case in cases.items():
 variants=[]
 for deg in (0,90,180,270):
  theta=math.radians(deg);rot=np.array([[math.cos(theta),-math.sin(theta)],[math.sin(theta),math.cos(theta)]])
  proposed=[dict(h,xy=(rot@np.array(h['xy'])).round(6).tolist()) for h in case['holes']]
  webs=[]
  for h in proposed:
   for old in baseholes:
    d=math.dist(h['xy'],old['xy'])-(h['drill']+old['drill'])/2
    webs.append({'new_hole_xy':h['xy'],'existing_hole':old['name'],'edge_separation_mm':round(d,4)})
  webs.sort(key=lambda v:v['edge_separation_mm'])
  best=None
  for swap in (False,True):
   affected=[];allhits=set();padrefs=set()
   for f in switches:
    pads={p.GetNumber():p for p in f.Pads()};origin=xy(f.GetPosition())
    a=np.column_stack([xy(pads['1'].GetPosition())-origin,xy(pads['2'].GetPosition())-origin])@np.linalg.inv(np.array([[0,5],[-5.9,-3.8]]))
    local=[]
    for h in proposed:
     center=origin+a@np.array(h['xy']);pn=h['net']
     if pn and swap:pn='2' if pn=='1' else '1'
     expected=pads[pn].GetNetname() if pn else None
     radius=1.4 if pn else h['drill']/2+0.25
     region=Point(center).buffer(radius);hits=[]
     for idx in tree.query(region,predicate='intersects'):
      i=items[int(idx)]
      if expected and i['net']==expected:continue
      hits.append({'kind':i['kind'],'net':i['net'],'ref':i['ref']});allhits.add(int(idx))
      if i['kind']=='pad_bbox':padrefs.add(i['ref'])
     if hits:local.append({'local_xy':h['xy'],'hits':hits})
    if local:affected.append({'switch':f.GetReference(),'holes':local})
   result={'rotation_deg':deg,'swap_contact_net_assignment':swap,'proposed_holes':proposed,'new_holes':len(proposed)*86,'minimum_web_to_existing_switch_holes_mm':webs[0]['edge_separation_mm'],'closest_holes':webs[:3],'switch_sites_with_copper_conflicts':len(affected),'unique_items':len(allhits),'foreign_component_refs':sorted(r for r in padrefs if not r.startswith('SW')),'sites':affected}
   score=(len(result['foreign_component_refs']),len(affected),len(allhits))
   if best is None or score<best[0]:best=(score,result)
  variants.append(best[1])
 report[name]={'center_hole_required_mm':case['center'],'center_hole_diameter_increase_mm':round(case['center']-5.05,3),'source':case['source'],'variants':variants}
print(json.dumps({name:{'center_increase_mm':c['center_hole_diameter_increase_mm'],'variants':[{key:value for key,value in v.items() if key not in ['sites','proposed_holes','closest_holes']} for v in c['variants']]} for name,c in report.items()},indent=2))
out={'board_sha256':hashlib.sha256(boardpath.read_bytes()).hexdigest(),'method':'Conservative 2D screen of existing tracks/vias/pad bounding boxes; excludes zones. Existing switch drills preserved. Every case considered at four rotations; choose contact net assignment minimizing component clashes, sites, then item count. No board mutation. Not DRC or manufacturing validation.','assumptions':['Alternate electrical copper pads provisionally 2.4 mm diameter plus 0.2 mm clearance','NPTH copper clearance screened at 0.25 mm','0.25 mm hole-to-hole web used as a study threshold only; confirm actual fabrication rules','Gateron 2.0 1.5 mm solder drills provisional; original drawing connector holes differ','A rotation changes switch LED-window orientation and can change latch fit; not an approved mechanical solution'],'cases':report}
Path('/tmp/v11-switch-dimensions/expanded-clearance-screen.json').write_text(json.dumps(out,indent=2))
