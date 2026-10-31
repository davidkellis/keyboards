#!/usr/bin/env python3
"""Start v9.1 from preserved routed v9; add mechanical holes and clear routes.

This replaces v9.1 routing edits. Run finish_routing.py afterwards.
"""
from routing_geometry import *
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'kicad/keyboard.kicad_pcb'
b=k.LoadBoard(str(ROOT.parent/'tkl9/kicad/keyboard.kicad_pcb'))
config=json.loads((ROOT/'scripts/fit-config.json').read_text());m=config['mounting']
keepouts=[]
for point in m['points']:
 x,y=point['xy'];pos=(27.03+x,149.19-y)
 f=k.FOOTPRINT(b);f.SetReference(point['ref']);f.SetValue('Mount_M2_2.5mm')
 f.SetFPID(k.LIB_ID('Local','Mount_M2_2.5mm'))
 f.SetAttributes(k.FP_BOARD_ONLY|k.FP_EXCLUDE_FROM_BOM|k.FP_EXCLUDE_FROM_POS_FILES)
 f.SetPosition(vec(pos));f.Reference().SetVisible(False);f.Value().SetVisible(False)
 pad=k.PAD(f);pad.SetNumber('');pad.SetAttribute(k.PAD_ATTRIB_NPTH)
 pad.SetShape(k.PAD_SHAPE_CIRCLE);pad.SetSize(vec((m['pcb_drill_mm'],)*2))
 pad.SetDrillSize(vec((m['pcb_drill_mm'],)*2));pad.SetLayerSet(k.LSET.AllCuMask())
 pad.SetPosition(vec(pos));f.Add(pad);b.Add(f)
 z=k.ZONE(b);z.SetIsRuleArea(True);layers=k.LSET();layers.AddLayer(k.F_Cu);layers.AddLayer(k.B_Cu);z.SetLayerSet(layers)
 # The NPTH itself is a pad. Electrical pad clearance is independently audited.
 z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowPads(False)
 z.SetDoNotAllowZoneFills(True);z.SetDoNotAllowFootprints(False)
 z.SetZoneName(point['ref']+' mounting hardware clearance')
 radius=m['copper_keepout_radius_mm']
 poly=z.Outline();poly.NewOutline()
 for i in range(64):
  a=2*math.pi*i/64;poly.Append(mm(pos[0]+radius*math.cos(a)),mm(pos[1]+radius*math.sin(a)))
 b.Add(z);keepouts.append(Point(*pos).buffer(radius,quad_segs=32))
# Clip routes locally, preserving the rest of v9's checked routing.
from shapely.ops import unary_union
region=unary_union(keepouts);removed=0;added=0
for t in list(b.GetTracks()):
 if isinstance(t,k.PCB_VIA):
  if Point(*xy(t.GetPosition())).distance(region)<k.ToMM(t.GetWidth(k.F_Cu))/2+.05:
   b.Remove(t);removed+=1
  continue
 line=LineString([xy(t.GetStart()),xy(t.GetEnd())])
 safe=region.buffer(k.ToMM(t.GetWidth())/2+.06)
 if line.disjoint(safe):continue
 remaining=line.difference(safe);b.Remove(t);removed+=1
 for segment in (list(remaining.geoms) if hasattr(remaining,'geoms') else [remaining]):
  if segment.is_empty or segment.length<.05:continue
  p=k.PCB_TRACK(b);p.SetStart(vec(segment.coords[0]));p.SetEnd(vec(segment.coords[-1]))
  p.SetWidth(t.GetWidth());p.SetLayer(t.GetLayer());p.SetNetCode(t.GetNetCode());b.Add(p);added+=1
# Persist the board-only footprint library as well as the placed instances.
library=ROOT/'kicad/footprints/Local.pretty';library.mkdir(parents=True,exist_ok=True)
k.PCB_IO_KICAD_SEXPR().FootprintSave(str(library),next(f for f in b.GetFootprints() if f.GetReference()=='H1'))
table=ROOT/'kicad/fp-lib-table';text=table.read_text()
if '(name "Local")' not in text:
 text=text.rstrip()[:-1]+'  (lib (name "Local")(type "KiCad")(uri "${KIPRJMOD}/footprints/Local.pretty")(options "")(descr "Board-only mechanical mounting holes"))\n)\n'
 table.write_text(text)
b.GetTitleBlock().SetTitle('TKL v9.1 - integrated upper / 12 mechanical mounts')
b.GetTitleBlock().SetRevision('v9.1')
b.BuildConnectivity();k.ZONE_FILLER(b).Fill(b.Zones());k.SaveBoard(str(P),b)
# Parts remain electrically identical; mechanical holes are excluded from PCBA.
cat=json.loads((ROOT.parent/'tkl9/manufacturing/parts.json').read_text())
cat['notes']='v9.1: v9 electronics and placements retained; 12 non-plated M2 mounting holes with copper exclusions; integrated upper case.'
cat['groups'].append(dict(refs=[p['ref'] for p in m['points']],package='NPTH 2.5 mm',manufacturer='',mpn='',lcsc='',spec='M2 mechanical mounting hole',assembly='Mechanical',notes='No factory component placement; user installs screws/nuts',source='scripts/fit-config.json'))
(ROOT/'manufacturing/parts.json').write_text(json.dumps(cat,indent=2)+'\n')
print('Added',len(keepouts),'mounts; clipped',removed,'copper items; retained',added,'outer segments')
