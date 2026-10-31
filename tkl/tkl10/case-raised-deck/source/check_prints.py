#!/usr/bin/env python3
"""Independently inspect the written binary STL files, not the source solids."""
from pathlib import Path
import hashlib,json,struct
import numpy as np
import manifold3d as mf

OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parent
dt=np.dtype([('normal','<f4',(3,)),('vertex','<f4',(3,3)),('attribute','<u2')])
checks=[]
for path in sorted((OUT/'prints').glob('*.stl')):
    data=path.read_bytes();n=struct.unpack_from('<I',data,80)[0]
    assert len(data)==84+50*n,path.name
    triangles=np.ndarray(n,dt,data,84)['vertex']
    vertices,idx=np.unique(triangles.reshape(-1,3),axis=0,return_inverse=True)
    faces=idx.reshape(-1,3)
    edges=np.sort(np.concatenate([faces[:,[0,1]],faces[:,[1,2]],faces[:,[2,0]]]),axis=1)
    _,counts=np.unique(edges,axis=0,return_counts=True)
    areas=np.linalg.norm(np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0]),axis=1)
    mesh=mf.Mesh(np.array(vertices,dtype=np.float32),np.array(faces,dtype=np.uint32));mesh.merge();solid=mf.Manifold(mesh)
    lo,hi=vertices.min(0),vertices.max(0)
    check=dict(file=path.name,sha256=hashlib.sha256(data).hexdigest(),triangles=n,
               watertight=bool(np.all(counts==2)),zero_area_facets=int((areas<1e-10).sum()),
               volume_mm3=solid.volume(),connected_components=len(solid.decompose()),
               manifold_status=str(solid.status()),minimum_z_mm=float(lo[2]),
               dimensions_mm=(hi-lo).tolist(),fits_256_bed=bool(max((hi-lo)[:2])<=256))
    assert check['watertight'] and check['zero_area_facets']==0,check
    assert check['connected_components']==1 and check['volume_mm3']>0 and solid.status()==mf.Error.NoError,check
    assert abs(check['minimum_z_mm'])<.0001,check
    if path.name not in ['plate-upper.stl','plate-upper-navigation.stl','case-bottom.stl']:assert check['fits_256_bed'],check
    checks.append(check)
preserved=json.loads((ROOT/'case-hidden-mounts/preserved-inputs.json').read_text())
for relative,sha in preserved.items():
    assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==sha,relative
for relative,sha in json.loads((OUT/'validation.json').read_text())['source_sha256'].items():
    assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==sha,relative
report=dict(passed=True,print_meshes=checks,original_source_files_preserved=len(preserved),
            physical_fit_verified=False,note='Mesh topology and nominal fit are checked; print strength and real keycap seating are not certified.')
(OUT/'print-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('Passed written-STL validation:',len(checks),'meshes;',len(preserved),'original source files preserved.')
