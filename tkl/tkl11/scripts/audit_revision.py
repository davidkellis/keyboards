#!/usr/bin/env python3
"""Independent v11 geometry, assembly, series bypass and preservation audit."""
from routing_geometry import *
import hashlib,itertools
R=Path(__file__).resolve().parents[1]
preserved=json.loads((R/'reference/preserved-v10.json').read_text())
assert all(hashlib.sha256((R.parent/f).read_bytes()).hexdigest()==sha for f,sha in preserved.items())
b=k.LoadBoard(str(R/'kicad/keyboard.kicad_pcb'));old=k.LoadBoard(str(R.parent/'tkl10/kicad/keyboard.kicad_pcb'))
fp={f.GetReference():f for f in b.GetFootprints()};prior={f.GetReference():f for f in old.GetFootprints()}
assert b.GetCopperLayerCount()==2 and b.GetDesignSettings().GetBoardThickness()==mm(1.6)
assert b.GetBoardEdgesBoundingBox()==old.GetBoardEdgesBoundingBox()
def geometry(f):return (xy(f.GetPosition()),f.GetOrientationDegrees(),sorted((p.GetNumber(),xy(p.GetPosition()),xy(p.GetDrillSize())) for p in f.Pads()))
for ref in [*[f'SW{i}' for i in range(1,88)],*[f'D{i}' for i in range(1,87)],'U1','J1',*[f'H{i}' for i in range(1,13)]]:
 assert geometry(fp[ref])==geometry(prior[ref]),ref
expected={'LED1':(285.75,71.45),'LED2':(327,117.06),'LED3':(54.65,74.45),
 'LED4':(204.79,71.45),'LED5':(69.7,119.06),'LED6':(204.79,119.06),
 'LED7':(128,71.45),'LED8':(128.6,110.04),'LED9':(343,71.45),'LED10':(273.2,107.04)}
for ref,pos in expected.items():
 f=fp[ref];assert xy(f.GetPosition())==pos,(ref,xy(f.GetPosition()),pos)
 assert f.GetLayer()==k.B_Cu and f.GetOrientationDegrees()==0
 pads=sorted((p.GetNumber(),tuple(round(a-c,6) for a,c in zip(xy(p.GetPosition()),pos)),xy(p.GetDrillSize())) for p in f.Pads())
 template=[('',(0.0,0.0),(2.1,2.8)),('1',(-1.9,0.0),(0.0,0.0)),('2',(1.9,0.0),(0.0,0.0))]
 # KiCad's integer-nanometer transforms can truncate one nanometer on movement.
 assert len(pads)==len(template) and all(a[0]==e[0] and math.dist(a[1],e[1])<.000002 and a[2]==e[2] for a,e in zip(pads,template)),(ref,pads)
# LED1 intentionally moved left, with the same lands, optical slot and orientation.
assert xy(fp['LED1'].GetPosition())==(285.75,71.45)
assert fp['LED1'].GetOrientationDegrees()==prior['LED1'].GetOrientationDegrees()
assert sorted((p.GetNumber(),xy(p.GetPosition()),xy(p.GetDrillSize())) for p in fp['LED1'].Pads())==sorted(
 (p.GetNumber(),(round(xy(p.GetPosition())[0]-28.25,6),xy(p.GetPosition())[1]),xy(p.GetDrillSize())) for p in prior['LED1'].Pads())
assert abs(xy(fp['SW40'].GetPosition())[0]+19.05/2-285.75)<1e-6
assert abs(xy(fp['SW41'].GetPosition())[0]-1.5*19.05/2-285.75)<1e-6
snapshot=R/'reference/before-staggered-layout'
saved=json.loads((snapshot/'manifest.json').read_text())
assert all(hashlib.sha256((snapshot/name).read_bytes()).hexdigest()==sha for name,sha in saved.items())
before=k.LoadBoard(str(snapshot/'kicad/keyboard.kicad_pcb'))
baseline={f.GetReference():f for f in before.GetFootprints()}
assert set(fp)==set(baseline)
assert all(geometry(f)==geometry(baseline[r]) for r,f in fp.items() if not r.startswith('LED'))
cat=json.loads((R/'manufacturing/parts.json').read_text());parts={r:g for g in cat['groups'] for r in g['refs']}
assert set(parts)==set(fp)
fitted=[r for r,g in parts.items() if g['assembly'] in ['SMT','THT-bottom']]
assert len(fitted)==106 and all(fp[r].GetLayer()==k.B_Cu for r in fitted)
assert not any(fp[r].IsDNP() for r in fitted)
assert parts['U1']['assembly']=='User-installed'
# Build the directed string from actual pad nets, independently of stored order.
leds={r:{p.GetNumber():p.GetNetname() for p in fp[r].Pads() if p.GetNumber()} for r in [f'LED{i}' for i in range(1,11)]}
node='LED_HV';order=[]
while node!='LED_FB':
 matches=[r for r,p in leds.items() if p['2']==node and r not in order]
 assert len(matches)==1,(node,matches)
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
  remaining=[r for r in order if r not in bypass]
  assert root('LED_HV')!=root('LED_FB')
  node=root('LED_HV')
  for r in remaining:
   assert root(leds[r]['2'])==node;node=root(leds[r]['1'])
  assert node==root('LED_FB');tested+=1
assert tested==386
assert {r for r in order if r not in ['LED7','LED8','LED9','LED10']}=={f'LED{i}' for i in range(1,7)}
assert 10*3.6+.220<38 and 6*2.0>4.2
switch_tracks=[t for t in b.GetTracks() if t.GetNetname()=='BOOST_SW']
assert not any(isinstance(t,k.PCB_VIA) for t in switch_tracks)
assert all(t.GetLayer()==k.B_Cu and t.GetWidth()>=mm(.35) for t in switch_tracks)
assert sum(k.ToMM(t.GetLength()) for t in switch_tracks)<10
vias=[t for t in b.GetTracks() if isinstance(t,k.PCB_VIA)]
assert all(v.GetWidth(k.F_Cu)>=mm(.6) and v.GetDrillValue()>=mm(.3) for v in vias)
minimum=1000
lands=[shape(p) for f in fp.values() for p in f.Pads() if p.GetAttribute()==k.PAD_ATTRIB_SMD]
for v in vias:
 minimum=min(minimum,min(Point(*xy(v.GetPosition())).distance(p) for p in lands)-k.ToMM(v.GetDrillValue())/2)
assert minimum>=.1-1e-5,('Via hole encroaches solder land',minimum)
ds=b.GetDesignSettings()
assert not ds.m_CapVias and not ds.m_FillVias
project=json.loads((R/'kicad/keyboard.kicad_pro').read_text())['board']['design_settings']
assert not project['drc_exclusions']
result=dict(revision='v11',parent='v10',preserved_v10_files=len(preserved),
 unchanged_keys_and_matrix_diodes=86,unchanged_m2_holes=12,unchanged_module_and_usb=True,
 unchanged_original_led_positions=1,led1_relocated_left_mm=28.25,
 led1_kicad_xy_mm=[285.75,71.45],all_non_led_footprint_geometry_unchanged=True,copper_layers=2,thickness_mm=1.6,
 layout='Two staggered interior rows of five',led_positions_mm=expected,
 led_count=10,series_order_from_pcb=order,bypass_configurations_checked=tested,
 six_led_conversion=['Remove LED7..LED10','Wire across each removed LED footprint pads 1 and 2; LED1 remains in its relocated position'],
 nominal_max_current_ma=2.04,current_sense_never_bridge='R10',factory_placements=106,
 factory_bom_groups=10,assembly_side='Bottom',boost_switch_node_vias=0,
 boost_switch_node_length_mm=sum(k.ToMM(t.GetLength()) for t in switch_tracks),
 via_count=len(vias),minimum_via_drill_to_smt_land_mm=minimum,filled_or_capped_vias=False,
 physical_optics_verified=False,hardware_tested=False,live_quote_obtained=False)
(R/'validation/revision-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
