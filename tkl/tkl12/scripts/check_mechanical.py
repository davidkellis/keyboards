#!/usr/bin/env python3
"""Check new or relocated bottom parts against existing v10 assembled case meshes."""
from pathlib import Path
import json,hashlib
import numpy as np,trimesh,manifold3d as m
R=Path(__file__).resolve().parents[1];V10=R.parent/'tkl10';REF=V10/'case-hidden-mounts/reference'
g=json.loads((R/'case/board-geometry.json').read_text())
d=json.loads((V10/'case-hidden-mounts/validation.json').read_text())
def load(p):
 t=trimesh.load(str(p),force='mesh',process=True)
 result=m.Manifold(m.Mesh(np.array(t.vertices,np.float32),np.array(t.faces,np.uint32)))
 assert result.status()==m.Error.NoError,(p,result.status())
 return result
refs={name:REF/(name+'-assembly.stl') for name in ['bottom','upper','bezel','battery']}
refs.update({f'M{i}-carrier':REF/f'M{i}-carrier-assembly.stl' for i in range(1,9)})
obstacles={name:load(p) for name,p in refs.items()}
added={f'LED{i}' for i in range(1,11)}|{'U2','L1','D87','C1','C2','R10','R11'}
rows=[]
for c in g['components']:
 if c['ref'] not in added:continue
 x,y,xx,yy=c['bounds'];h=c['height']
 def solid(clearance):
  return m.Manifold.cube((xx-x+2*clearance,yy-y+2*clearance,h+clearance)).translate((x-clearance,y-clearance,-h-clearance)).rotate((d['tilt_degrees'],0,0)).translate((2.4,2.4,d['pcb_origin_z']))
 a=solid(0);expanded=solid(.4)
 hits={name:(a^ob).volume() for name,ob in obstacles.items()}
 margins={name:(expanded^ob).volume() for name,ob in obstacles.items()}
 assert all(v<.005 for v in hits.values()),(c['ref'],'collision',hits)
 assert all(v<.005 for v in margins.values()),(c['ref'],'clearance <0.4 mm',margins)
 rows.append(dict(ref=c['ref'],height_envelope_mm=h,physical_intersections_mm3=hits,expanded_0_4mm_intersections_mm3=margins))
assert len(rows)==len(added)
result=dict(passed=True,scope='New or relocated bottom components versus unchanged v10 hidden-mount case, battery and nut carriers',
 minimum_tested_clearance_mm=.4,added_parts=rows,
 source_mesh_sha256={str(p.relative_to(V10)):hashlib.sha256(p.read_bytes()).hexdigest() for p in refs.values()},
 acrylic_plate_fit_validated=False,real_hardware_fit_validated=False)
(R/'validation/added-component-clearance.json').write_text(json.dumps(result,indent=2)+'\n')
print('New or relocated bottom envelopes:',len(rows),'clear by >=0.4 mm against existing case and battery meshes')
