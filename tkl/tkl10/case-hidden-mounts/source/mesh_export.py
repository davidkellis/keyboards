"""Remove zero-area STL facets at fillet poles without changing geometry."""
from pathlib import Path
import numpy as np
import trimesh

def clean_degenerate_facets(path):
    path=Path(path)
    mesh=trimesh.load_mesh(path,process=True)
    before=float(mesh.volume)
    bounds=mesh.bounds.copy()
    faces=np.sort(mesh.faces,axis=1)
    # Coincident vertices can collapse to one STL vertex at a spherical pole.
    # Only remove triangles containing the very same welded vertex twice.
    bad=np.any(np.diff(faces,axis=1)==0,axis=1)
    count=int(bad.sum())
    if count:
        mesh.update_faces(~bad)
        mesh.remove_unreferenced_vertices()
        assert mesh.is_watertight,('Remaining open/nonmanifold STL',path)
        assert abs(mesh.volume-before)<1e-6,(path,'Changed volume')
        assert np.allclose(mesh.bounds,bounds,rtol=0,atol=1e-7),(path,'Changed bounds')
        mesh.export(path)
        checked=trimesh.load_mesh(path,process=True)
        assert checked.is_watertight and checked.volume>0,path
    return {'file':str(path),'removed_zero_area_facets':count,
            'volume_change_mm3':float(mesh.volume-before),'watertight':bool(mesh.is_watertight)}
