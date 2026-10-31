#!/usr/bin/env python3
"""Check the exported drill file and assembly lists against this revision."""
from pathlib import Path
import csv, hashlib, json, re, zipfile
import pcbnew as k
R=Path(__file__).resolve().parents[1];M=R/'manufacturing'
cfg=json.loads((R/'scripts/fit-config.json').read_text())
lines=(M/'gerbers/keyboard-NPTH.drl').read_text().splitlines()
assert any('TF.FileFunction,NonPlated' in s for s in lines)
header={}
for s in lines:
 m=re.fullmatch(r'(T\d+)C([0-9.]+)',s)
 if m:header[m[1]]=float(m[2])
selected=None;coords=[]
for s in lines:
 if re.fullmatch(r'T\d+',s):selected=s
 m=re.fullmatch(r'X(-?[0-9.]+)Y(-?[0-9.]+)',s)
 if m and header.get(selected)==cfg['mounting']['pcb_drill_mm']:coords.append(tuple(float(v) for v in m.groups()))
expected=[tuple(p['xy']) for p in cfg['mounting']['points']]
assert sorted(coords)==sorted(expected),(coords,expected)
tool=None;start=None;slots=[]
for line in lines:
 if re.fullmatch(r'T\d+',line):tool=line
 m=re.fullmatch(r'G00X(-?[0-9.]+)Y(-?[0-9.]+)',line)
 if m and header.get(tool)==2.1:start=tuple(float(v) for v in m.groups())
 m=re.fullmatch(r'G01X(-?[0-9.]+)Y(-?[0-9.]+)',line)
 if m and start:
  end=tuple(float(v) for v in m.groups())
  assert abs(start[0]-end[0])<1e-6 and abs(abs(start[1]-end[1])-.7)<1e-6
  slots.append(((start[0]+end[0])/2,(start[1]+end[1])/2));start=None
leds=json.loads((R/'reference/lighting-design.json').read_text())['leds']
assert len(slots)==10
assert all(any(abs(x-e['board_xy'][0])<.001 and abs(y-e['board_xy'][1])<.001 for x,y in slots) for e in leds)
# Check the actual shared locator CNC moves, not just the source pad shapes.
tool=None;start=None;locators=[]
for line in lines:
 if re.fullmatch(r'T\d+',line):tool=line
 m=re.fullmatch(r'G00X(-?[0-9.]+)Y(-?[0-9.]+)',line)
 if m and header.get(tool)==1.9:start=tuple(float(v) for v in m.groups())
 m=re.fullmatch(r'G01X(-?[0-9.]+)Y(-?[0-9.]+)',line)
 if m and start:
  end=tuple(float(v) for v in m.groups())
  # Excellon metric coordinates have 0.001 mm resolution. Independent
  # rounding of the two endpoints can change a 0.420 mm move by 0.001 mm.
  assert abs(start[1]-end[1])<1e-6 and abs(abs(start[0]-end[0])-.42)<.0011
  locators.append(((start[0]+end[0])/2,(start[1]+end[1])/2));start=None
assert len(locators)==172
b=k.LoadBoard(str(R/'kicad/keyboard.kicad_pcb'));origin=b.GetDesignSettings().GetAuxOrigin()
def xy(p):return (round(k.ToMM(p.x-origin.x),6),round(k.ToMM(origin.y-p.y),6))
expected_locators=[];expected_contacts=[]
for f in b.GetFootprints():
 if f.GetReference().startswith('SW') and f.GetReference()!='SW87':
  for p in f.Pads():
   if p.GetAttribute()==k.PAD_ATTRIB_NPTH and p.GetDrillShape()==k.PAD_DRILL_SHAPE_OBLONG:expected_locators.append(xy(p.GetPosition()))
   if p.GetNumber() and p.GetDrillSize().x==k.FromMM(1.5):expected_contacts.append(xy(p.GetPosition()))
assert all(sum(abs(x-ex)<.0006 and abs(y-ey)<.0006 for x,y in locators)==1 for ex,ey in expected_locators)
plated=(M/'gerbers/keyboard-PTH.drl').read_text().splitlines();sizes={};tool=None;contact_drills=[]
assert any('TF.FileFunction,Plated' in s for s in plated)
for line in plated:
 m=re.fullmatch(r'(T\d+)C([0-9.]+)',line)
 if m:sizes[m[1]]=float(m[2])
 if re.fullmatch(r'T\d+',line):tool=line
 m=re.fullmatch(r'X(-?[0-9.]+)Y(-?[0-9.]+)',line)
 if m and sizes.get(tool)==1.5:contact_drills.append(tuple(float(v) for v in m.groups()))
assert len(expected_contacts)==172
assert all(sum(abs(x-ex)<.0006 and abs(y-ey)<.0006 for x,y in contact_drills)==1 for ex,ey in expected_contacts)
with (M/'jlcpcb-cpl.csv').open() as f:cpl=list(csv.DictReader(f))
assert len(cpl)==106 and all(r['Layer']=='Bottom' and not r['Designator'].startswith('H') for r in cpl)
assert {'D9','D15','D16',*[f'LED{i}' for i in range(1,11)],'U2','L1','D87','R10','R11'} <= {r['Designator'] for r in cpl}
with zipfile.ZipFile(M/'tkl-v12-gerbers.zip') as z:
 for p in (M/'gerbers').iterdir():
  if p.suffix!='.pdf':assert z.read(p.name)==p.read_bytes(),p.name
with zipfile.ZipFile(M/'tkl-v12-prototype-handoff.zip') as z:
 for name in ('tkl-v12-gerbers.zip','jlcpcb-bom.csv','jlcpcb-cpl.csv'):assert z.read(name)==(M/name).read_bytes()
manifest=json.loads((M/'manifest.json').read_text())
for name,sha in manifest['source_sha256'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==sha,name
result=dict(revision='v12',npth_mount_drills=coords,npth_optical_slots=slots,restored_key_diodes=True,
 shared_locator_slots=len(locators),extra_gateron_contact_drills=len(expected_contacts),
 drill_export_coordinate_tolerance_mm=.0006,
 assembly_side="Bottom",jlc_placements=106,archives_match_exports=True,source_hashes_current=True,
 fabrication_has_new_mounting_drills=True,prototype_hardware_tested=False)
(R/'validation/handoff-check.json').write_text(json.dumps(result,indent=2)+'\n')
print('Exported drills: 12 mounts, 10 optical slots, 172 shared slots, 172 Gateron contacts; 106 bottom placements; archive hashes: pass')
