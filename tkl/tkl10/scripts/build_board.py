#!/usr/bin/python3
"""Reset v10 from routed v9.1, restoring keys and moving the clone to Esc/F1.

Routes outside the changed component/keepout regions are retained. Run
finish_routing.py and prune_stubs.py, then validate and export after this reset.
"""
from routing_geometry import *
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'kicad/keyboard.kicad_pcb'
config=json.loads((ROOT/'scripts/fit-config.json').read_text());m=config['mounting']
import sexpdata as sx
restored={'SW9','SW15','SW16','D9','D15','D16'}
def tag(node):return str(node[0]) if isinstance(node,list) and node else ''
def ref(node):return next(a[2] for a in node if tag(a)=='property' and a[1]=='Reference')
tree=sx.loads((ROOT.parent/'tkl9.1/kicad/keyboard.kicad_pcb').read_text())
tree=[a for a in tree if tag(a)!='zone']
old=sx.loads((ROOT.parent/'tkl7.5/kicad/keyboard.kicad_pcb').read_text())
tree.extend(a for a in old if tag(a)=='footprint' and ref(a) in restored)
P.write_text(sx.dumps(tree))
b=k.LoadBoard(str(P));fp={f.GetReference():f for f in b.GetFootprints()}
regions=[box(348.7,19.8,369.4,63.5),box(46.85,19.8,67.45,54.75)]
u=fp['U1'];u.SetOrientationDegrees(0);u.SetPosition(vec(config['module']['placement_kicad_mm']))
for r in restored:
 bb=fp[r].GetBoundingBox(False,False)
 regions.append(box(k.ToMM(bb.GetLeft())-.6,k.ToMM(bb.GetTop())-.6,k.ToMM(bb.GetRight())+.6,k.ToMM(bb.GetBottom())+.6))
# Replace keepouts and reposition two existing M2 holes.
for point in m['points']:
 f=fp[point['ref']];prior=xy(f.GetPosition());pos=(27.03+point['xy'][0],149.19-point['xy'][1])
 if math.dist(prior,pos)>.01:regions.append(Point(*prior).buffer(m['copper_keepout_radius_mm']))
 f.SetPosition(vec(pos));regions.append(Point(*pos).buffer(m['copper_keepout_radius_mm']))
 def zone_polygon(points,name,forbidpads):
  z=k.ZONE(b);z.SetIsRuleArea(True);layers=k.LSET();layers.AddLayer(k.F_Cu);layers.AddLayer(k.B_Cu);z.SetLayerSet(layers)
  z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowPads(forbidpads);z.SetDoNotAllowZoneFills(True);z.SetDoNotAllowFootprints(False);z.SetZoneName(name)
  p=z.Outline();p.NewOutline()
  for x,y in points:p.Append(mm(x),mm(y))
  b.Add(z)
 radius=m['copper_keepout_radius_mm']
 zone_polygon([(pos[0]+radius*math.cos(i*math.pi/32),pos[1]+radius*math.sin(i*math.pi/32)) for i in range(64)],point['ref']+' mounting hardware clearance',False)
x,y,xx,yy=config['module']['antenna_keepout_kicad_bounds_mm']
zone_polygon([(x,y),(xx,y),(xx,yy),(x,yy)],'Clone antenna: validate assembled RF range',True)
regions.append(box(x,y,xx,yy));region=unary_union(regions)
b.GetTitleBlock().SetTitle('TKL v10 - Esc/F1 clone; 86 keys; plain recessed plate');b.GetTitleBlock().SetRevision('v10')
b.BuildConnectivity();k.SaveBoard(str(P),b)
# KiCad 10 Python Remove invalidates wrappers on this installation; edit the
# saved S-expression instead, keeping exact net/layer data on clipped tracks.
import copy,uuid
removed=added=0;tree=sx.loads(P.read_text());result=[]
def field(n,name):return next(a for a in n if tag(a)==name)
for node in tree:
 kind=tag(node)
 if kind not in ('segment','via'):
  result.append(node);continue
 if kind=='via':
  if Point(*field(node,'at')[1:3]).distance(region)<field(node,'size')[1]/2+.08:removed+=1
  else:result.append(node)
  continue
 line=LineString([field(node,'start')[1:3],field(node,'end')[1:3]])
 safe=region.buffer(field(node,'width')[1]/2+.08)
 if line.disjoint(safe):result.append(node);continue
 remaining=line.difference(safe);removed+=1
 for segment in (list(remaining.geoms) if hasattr(remaining,'geoms') else [remaining]):
  if segment.is_empty or segment.length<.08:continue
  part=copy.deepcopy(node)
  field(part,'start')[1:]=[round(v,6) for v in segment.coords[0]]
  field(part,'end')[1:]=[round(v,6) for v in segment.coords[-1]]
  field(part,'uuid')[1]=str(uuid.uuid4());result.append(part);added+=1
P.write_text(sx.dumps(result))
cat=json.loads((ROOT.parent/'tkl9.1/manufacturing/parts.json').read_text())
for group in cat['groups']:
 if 'SW1' in group['refs']:group['refs']=sorted(group['refs']+['SW9','SW15','SW16'],key=lambda x:int(x[2:]))
 if 'D1' in group['refs']:group['refs']=sorted(group['refs']+['D9','D15','D16'],key=lambda x:int(x[1:]))
 if group['refs']==['U1']:group['notes']='User installs clone beneath Esc/F1 gap, USB toward rear, 1 mm gap. Trim pins/solder to <=1 mm above carrier. Confirm auxiliary-pad registration, module/socket dimensions and RF range.'
cat['notes']='v10: 86-key two-layer carrier; Esc/F1 clone location; three restored rear-right keys; twelve M2 mounts, H9/H12 relocated; bottom-only factory assembly.'
(ROOT/'manufacturing/parts.json').write_text(json.dumps(cat,indent=2)+'\n')
print('Restored six footprints; moved U1/H9/H12; clipped',removed,'items, retained',added,'outer segments')
