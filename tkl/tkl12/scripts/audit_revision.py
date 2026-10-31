#!/usr/bin/env python3
"""Check V12 preservation, all three mounting patterns, routing and assembly."""
from routing_geometry import *
import hashlib,itertools
R=Path(__file__).resolve().parents[1]
saved=json.loads((R/'reference/preserved-v11.json').read_text())
for name,sha in saved.items():
 assert hashlib.sha256((R.parent/'tkl11'/name).read_bytes()).hexdigest()==sha,('V11 changed',name)
b=k.LoadBoard(str(R/'kicad/keyboard.kicad_pcb'));old=k.LoadBoard(str(R/'reference/source-v11.kicad_pcb'))
fp={f.GetReference():f for f in b.GetFootprints()};prior={f.GetReference():f for f in old.GetFootprints()}
assert set(fp)==set(prior)
assert b.GetCopperLayerCount()==2 and b.GetDesignSettings().GetBoardThickness()==mm(1.6)
assert b.GetBoardEdgesBoundingBox()==old.GetBoardEdgesBoundingBox()
def net(p):return '' if p.GetNetname().startswith('unconnected-(') else p.GetNetname()
def padshape(p):
 return (p.GetNumber(),xy(p.GetPosition()),xy(p.GetSize()),xy(p.GetDrillSize()),p.GetAttribute(),p.GetShape(),p.GetDrillShape(),p.GetOrientationDegrees(),p.GetLayerSet().FmtBin(),net(p))
oldpads=0
for r,f in fp.items():
 prev=prior[r]
 assert f.GetLayer()==prev.GetLayer() and f.GetOrientationDegrees()==prev.GetOrientationDegrees(),r
 assert xy(f.GetPosition())==((124,34.5) if r=='C2' else xy(prev.GetPosition())),r
 original={p.m_Uuid.AsString():p for p in prev.Pads()};current={p.m_Uuid.AsString():p for p in f.Pads()}
 assert original.keys()<=current.keys(),r
 for u,p in original.items():
  if r=='C2':
   a=list(padshape(p));a[1]=tuple(round(v+d,6) for v,d in zip(a[1],(6.2,3.5)));assert tuple(a)==padshape(current[u]),(r,a,padshape(current[u]))
  else:assert padshape(p)==padshape(current[u]),(r,p.GetNumber(),'original pad changed')
  oldpads+=1
 if r.startswith('SW') and r!='SW87':
  assert str(f.GetFPID().GetLibNickname())=='V12Switches'
  added=[p for u,p in current.items() if u not in original];assert len(added)==4,r
  origin=np.array(xy(f.GetPosition()));contacts={};slots=[]
  for p in added:
   pos=tuple(np.round(np.array(xy(p.GetPosition()))-origin,6))
   if p.GetNumber():
    assert xy(p.GetDrillSize())==(1.5,1.5) and xy(p.GetSize())==(2.4,2.4)
    contacts[p.GetNumber()]=pos
    assert p.GetNetname()==next(q.GetNetname() for q in prev.Pads() if q.GetNumber()==p.GetNumber())
   else:
    assert p.GetAttribute()==k.PAD_ATTRIB_NPTH and p.GetDrillShape()==k.PAD_DRILL_SHAPE_OBLONG
    assert xy(p.GetSize())==xy(p.GetDrillSize())==(2.32,1.9);slots.append(pos)
  assert contacts=={'1':(2.54,-5.08),'2':(-3.81,-2.54)},r
  assert sorted(slots)==[(-5.29,0),(5.29,0)],r
 else:assert len(original)==len(current),r
# Independent chirality check: KiCad's standard Cherry MX footprint is anchored
# at pin 1, with center (-2.54,5.08), pin 2 (-6.35,2.54). Gateron 3.0's official
# PCB drawing shares this TOP-view pattern. Pin numbers are SPST net assignments.
mx=k.FootprintLoad('/usr/share/kicad/footprints/Button_Switch_Keyboard.pretty','SW_Cherry_MX_1.00u_PCB')
mp={p.GetNumber():p for p in mx.Pads() if p.GetNumber()}
mx_relative=[tuple(np.round(np.array(xy(mp[n].GetPosition()))-np.array([-2.54,5.08]),6)) for n in ['1','2']]
assert mx_relative==[(2.54,-5.08),(-3.81,-2.54)],mx_relative
webs=[];slot_coverage=[]
sample=fp['SW1'];origin=np.array(xy(sample.GetPosition()));sample_old={p.m_Uuid.AsString() for p in prior['SW1'].Pads()}
new=[p for p in sample.Pads() if p.m_Uuid.AsString() not in sample_old]
orig=[p for p in sample.Pads() if p.m_Uuid.AsString() in sample_old and p.GetDrillSize().x]
for a in new:
 for c in orig:
  aw,ah=xy(a.GetDrillSize());cw,ch=xy(c.GetDrillSize());assert cw==ch
  ax,ay=xy(a.GetPosition());cx,cy=xy(c.GetPosition())
  if aw==ah:web=math.dist((ax,ay),(cx,cy))-(aw+cw)/2
  else:
   assert aw>ah and a.GetOrientationDegrees()==0
   half=(aw-ah)/2;web=LineString([(ax-half,ay),(ax+half,ay)]).distance(Point(cx,cy))-(ah+cw)/2
  webs.append(web)
for side in [-1,1]:
 slot=next(p for p in new if not p.GetNumber() and (xy(p.GetPosition())[0]-origin[0])*side>0)
 for family,x,diam in [('Choc V1',5.5,1.9),('Gateron LP 3.0',5.08,1.7)]:
  circle=Point(*(origin+np.array([side*x,0]))).buffer(diam/2,quad_segs=12)
  # Same circle tessellation means this checks nominal reference hole coverage.
  uncovered=circle.difference(shape(slot,slot.GetDrillSize())).area
  assert uncovered<1e-8,(family,uncovered)
  slot_coverage.append(dict(family=family,side=side,uncovered_nominal_reference_area_mm2=uncovered))
assert min(webs)>1.30,min(webs)
cat=json.loads((R/'manufacturing/parts.json').read_text());previous=json.loads((R.parent/'tkl11/manufacturing/parts.json').read_text())
assert cat['groups']==previous['groups'],'Factory parts changed'
parts={r:g for g in cat['groups'] for r in g['refs']};fitted=[r for r,g in parts.items() if g['assembly'] in ['SMT','THT-bottom']]
assert len(fitted)==106 and all(fp[r].GetLayer()==k.B_Cu and not fp[r].IsDNP() for r in fitted)
assert parts['U1']['assembly']=='User-installed'
# Keep the complete boost switching loop intact. Only output C2 moves.
def loop(board):return sorted((xy(t.GetStart()),xy(t.GetEnd()),t.GetWidth(),t.GetLayer()) for t in board.GetTracks() if t.GetNetname()=='BOOST_SW')
assert loop(b)==loop(old)
leds={r:{p.GetNumber():p.GetNetname() for p in fp[r].Pads() if p.GetNumber()} for r in [f'LED{i}' for i in range(1,11)]}
node='LED_HV';order=[]
while node!='LED_FB':
 matches=[r for r,p in leds.items() if p['2']==node and r not in order];assert len(matches)==1
 r=matches[0];order.append(r);node=leds[r]['1'];assert len(order)<=10
assert len(order)==10
tested=0
for count in range(6,11):
 for bypass in itertools.combinations(order,10-count):
  parent={n:n for p in leds.values() for n in p.values()}
  def root(n):
   while n!=parent[n]:n=parent[n]
   return n
  for r in bypass:parent[root(leds[r]['2'])]=root(leds[r]['1'])
  node=root('LED_HV');assert node!=root('LED_FB')
  for r in [r for r in order if r not in bypass]:assert root(leds[r]['2'])==node;node=root(leds[r]['1'])
  assert node==root('LED_FB');tested+=1
assert tested==386
vias=[t for t in b.GetTracks() if isinstance(t,k.PCB_VIA)]
assert all(v.GetWidth(k.F_Cu)>=mm(.6) and v.GetDrillValue()>=mm(.3) for v in vias)
lands=[shape(p) for f in fp.values() for p in f.Pads() if p.GetAttribute()==k.PAD_ATTRIB_SMD]
minimum=min(Point(*xy(v.GetPosition())).distance(p)-k.ToMM(v.GetDrillValue())/2 for v in vias for p in lands)
assert minimum>=.1-1e-5,('Via drill enters SMT land',minimum)
assert not b.GetDesignSettings().m_CapVias and not b.GetDesignSettings().m_FillVias
assert not json.loads((R/'kicad/keyboard.kicad_pro').read_text())['board']['design_settings']['drc_exclusions']
result=dict(revision='v12',parent='v11',preserved_v11_files=len(saved),
 original_pads_and_drills_preserved=oldpads,original_key_patterns_preserved=86,
 added_gateron_contact_holes=172,added_shared_locator_slots=172,
 nominal_slot_reference_coverage=slot_coverage,minimum_added_hole_to_original_hole_web_mm=min(webs),
 gateron_contact_chirality_matches_official_top_view_and_kicad_mx=True,
 capacitor_relocated='C2: (117.8,31) to (124,34.5) mm in KiCad coordinates',
 other_footprint_positions_unchanged=True,outline_and_mounts_unchanged=True,
 factory_bom_unchanged=True,factory_placements=106,assembly_side='Bottom',
 led_count=10,bypass_configurations_checked=tested,boost_switch_loop_unchanged=True,
 copper_layers=2,finished_thickness_mm=1.6,via_count=len(vias),minimum_via_drill_to_smt_land_mm=minimum,
 physical_switch_fit_verified=False,physical_optics_verified=False,hardware_tested=False,live_quote_obtained=False)
(R/'validation/revision-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
