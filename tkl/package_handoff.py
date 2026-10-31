#!/usr/bin/env python3
"""Package already exported and checked prototype files; never submit an order."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path

p=argparse.ArgumentParser();p.add_argument('revision',type=Path);a=p.parse_args()
root=a.revision.resolve();m=root/'manufacturing';case=root/'case'
v=root.name.removeprefix('tkl');prefix=f'tkl-v{v}'
manifest=json.loads((m/'manifest.json').read_text())
for name,digest in manifest['source_sha256'].items():
    assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest, f'Stale manufacturing export: {name}'
assert all(not val for key,val in manifest['validation'].items() if key not in ('numbered_pads','unique_keys'))
with zipfile.ZipFile(m/f'{prefix}-gerbers.zip','w',zipfile.ZIP_DEFLATED) as z:
    for path in sorted((m/'gerbers').iterdir()):
        if path.suffix!='.pdf':z.write(path,path.name)
    z.write(m/'FABRICATION.md','FABRICATION.md')
manifest['status']='Prototype quote package; production hold for stabilizer/keycap fit, battery selection and charging-temperature compatibility'
manifest['mechanical_fit_report']='../case/fit-report.json'
(m/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(m/f'{prefix}-jlcpcb-handoff.zip','w',zipfile.ZIP_DEFLATED) as z:
    for name in [f'{prefix}-gerbers.zip','jlcpcb-bom.csv','jlcpcb-cpl.csv','FABRICATION.md','ORDERING.md',
                 'assembly-top.pdf','assembly-bottom.pdf','assembly-notes.csv','schematic.pdf',
                 'parts.json','pad-coordinates.csv','manifest.json']:
        z.write(m/name,name)
    z.write(root/'BRINGUP.md','BRINGUP.md')
    z.write(case/'BATTERY.md','BATTERY.md')
    z.write(case/'OWNED_PARTS.md','OWNED_PARTS.md')
fit=json.loads((case/'fit-report.json').read_text())
assert fit['source_sha256']==hashlib.sha256((root/'kicad/keyboard.kicad_pcb').read_bytes()).hexdigest()
assert not fit['collisions'] and fit['pcb_case_overlap_mm3']<1e-4
assert fit['fit_config_sha256']==hashlib.sha256((case/'fit-config.json').read_bytes()).hexdigest()
checks=json.loads((case/'mesh-validation.json').read_text())
assert all(row['watertight'] and row['positive_volume'] for row in checks)
with zipfile.ZipFile(case/f'{prefix}-fit-test.zip','w',zipfile.ZIP_DEFLATED) as z:
    for path in sorted(case.rglob('*')):
        if path.suffix in ('.stl','.step','.md','.json','.scad','.png','.dxf','.svg'):
            z.write(path,str(path.relative_to(case)))
print('Packaged',prefix,'JLCPCB handoff and fit-test archive')
