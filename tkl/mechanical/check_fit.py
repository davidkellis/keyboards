#!/usr/bin/env python3
"""Check printable mesh integrity, bed size and PCB provenance."""
from pathlib import Path
import argparse
import hashlib
import json
import trimesh

p=argparse.ArgumentParser();p.add_argument('revision',type=Path);a=p.parse_args()
root=a.revision/'case';rows=[]
report=json.loads((root/'fit-report.json').read_text())
pcb=a.revision/'kicad/keyboard.kicad_pcb'
assert report['source_sha256']==hashlib.sha256(pcb.read_bytes()).hexdigest()
config=Path(__file__).with_name('fit-config.json')
assert report['fit_config_sha256']==hashlib.sha256(config.read_bytes()).hexdigest(), 'Rebuild after fit configuration changes'
assert (root/'fit-config.json').read_bytes()==config.read_bytes()
assert not report['collisions'] and report['pcb_case_overlap_mm3']<1e-4
for path in sorted(root.rglob('*.stl')):
    mesh=trimesh.load_mesh(path,process=True)
    pieces=mesh.split(only_watertight=False)
    row=dict(file=str(path.relative_to(root)),watertight=bool(mesh.is_watertight),
             positive_volume=bool(mesh.volume>0),extents_mm=mesh.extents.tolist(),shells=len(pieces),
             solid_shells=int(sum(s.volume>0 for s in pieces)),internal_voids=int(sum(s.volume<0 for s in pieces)))
    if '-left.' in path.name or '-right.' in path.name:
        assert all(e<256 for e in mesh.extents[:2]),row
    assert row['watertight'] and row['positive_volume'],row
    # Negative oriented shells are sealed internal cavities, e.g. a connector's
    # drilled hole capped by its body and solder gauge. They are not loose parts.
    if not path.name.startswith('keycap-envelopes'):assert row['solid_shells']==1,row
    rows.append(row)
(root/'mesh-validation.json').write_text(json.dumps(rows,indent=2)+'\n')
print(a.revision.name,len(rows),'meshes pass')
