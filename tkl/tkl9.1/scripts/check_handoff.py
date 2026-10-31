#!/usr/bin/env python3
"""Check the exported drill file and assembly lists against this revision."""
from pathlib import Path
import csv, hashlib, json, re, zipfile
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
for name in ('jlcpcb-bom.csv','jlcpcb-cpl.csv'):
 assert (M/name).read_bytes()==(R.parent/'tkl9/manufacturing'/name).read_bytes(),name
with (M/'jlcpcb-cpl.csv').open() as f:cpl=list(csv.DictReader(f))
assert len(cpl)==99 and all(r['Layer']=='Bottom' and not r['Designator'].startswith('H') for r in cpl)
with zipfile.ZipFile(M/'tkl-v9.1-gerbers.zip') as z:
 for p in (M/'gerbers').iterdir():
  if p.suffix!='.pdf':assert z.read(p.name)==p.read_bytes(),p.name
with zipfile.ZipFile(M/'tkl-v9.1-prototype-handoff.zip') as z:
 for name in ('tkl-v9.1-gerbers.zip','jlcpcb-bom.csv','jlcpcb-cpl.csv'):assert z.read(name)==(M/name).read_bytes()
manifest=json.loads((M/'manifest.json').read_text())
for name,sha in manifest['source_sha256'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==sha,name
result=dict(revision='v9.1',npth_mount_drills=coords,assembly_bom_identical_to_v9=True,
 assembly_cpl_identical_to_v9=True,jlc_placements=99,archives_match_exports=True,source_hashes_current=True,
 fabrication_has_new_mounting_drills=True,prototype_hardware_tested=False)
(R/'validation/handoff-check.json').write_text(json.dumps(result,indent=2)+'\n')
print('Exported NPTH: 12 matching mounts; BOM/CPL: unchanged 99 bottom placements; ZIP/source hashes: pass')
