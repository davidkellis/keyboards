#!/usr/bin/env python3
"""Export exact and oversize-hole PCB models without changing fabrication data."""
from pathlib import Path
import gc,json,hashlib,subprocess,tempfile,zipfile
gc.disable()
import pcbnew as k
import trimesh
import manifold3d as m
R=Path(__file__).resolve().parents[1];P=R/'kicad/keyboard.kicad_pcb';O=R/'case'
before=hashlib.sha256(P.read_bytes()).hexdigest()
def export(source,target):
 subprocess.run(['kicad-cli','pcb','export','stl','--board-only','--drill-origin','--force','-o',str(target),str(source)],check=True,stdout=subprocess.DEVNULL)
export(P,O/'pcb-bare.stl')
b=k.LoadBoard(str(P));changed=0
for f in b.GetFootprints():
 ref=f.GetReference()
 if not (ref=='U1' or ref=='J1' or ref.startswith('H') or (ref.startswith('SW') and ref!='SW87')):continue
 for p in f.Pads():
  size=p.GetDrillSize()
  if not size.x:continue
  extra=.3 if p.GetAttribute()==k.PAD_ATTRIB_NPTH or not p.GetNumber() else .4
  p.SetDrillSize(size+k.VECTOR2I(k.FromMM(extra),k.FromMM(extra)));changed+=1
b.GetTitleBlock().SetTitle('V12 FIT GAUGE ONLY - oversize printed holes - NEVER FABRICATE')
with tempfile.TemporaryDirectory(prefix='v12-fit-model-') as td:
 tmp=Path(td)/'fit-only.kicad_pcb';k.SaveBoard(str(tmp),b);export(tmp,O/'pcb-fit-check.stl')
assert hashlib.sha256(P.read_bytes()).hexdigest()==before
# A small three-position print gauge from the actual finished board's drills.
# Every position has the identical universal pattern; the user can try each
# family without printing the full-width board.
source=k.LoadBoard(str(P));sample=next(f for f in source.GetFootprints() if f.GetReference()=='SW1')
coupon=m.Manifold.cube((61.1,24,1.6))
for cx in (11,30.05,49.1):
 for p in sample.Pads():
  ds=p.GetDrillSize()
  if not ds.x:continue
  extra=.3 if p.GetAttribute()==k.PAD_ATTRIB_NPTH or not p.GetNumber() else .4
  w,h=k.ToMM(ds.x)+extra,k.ToMM(ds.y)+extra
  x=cx+k.ToMM(p.GetPosition().x-sample.GetPosition().x)
  y=12-k.ToMM(p.GetPosition().y-sample.GetPosition().y)
  radius=min(w,h)/2;length=abs(w-h)
  hole=m.Manifold.cylinder(3.6,radius,radius,64).translate((x,y,-1))
  if length:
   assert w>h and abs(p.GetOrientationDegrees())<1e-6
   hole=(m.Manifold.cylinder(3.6,radius,radius,64).translate((x-length/2,y,-1))+
         m.Manifold.cylinder(3.6,radius,radius,64).translate((x+length/2,y,-1))+
         m.Manifold.cube((length,h,3.6)).translate((x-length/2,y-h/2,-1)))
  coupon-=hole
# A blind corner mark identifies the top face, preventing a mirrored fit test
# by accidentally inserting switches from the reverse of this flat gauge.
coupon-=m.Manifold.cube((3,1,.4)).translate((1.2,1.2,1.3))
cm=coupon.to_mesh()
trimesh.Trimesh(vertices=cm.vert_properties[:,:3],faces=cm.tri_verts,process=True).export(O/'switch-fit-coupon.stl')
models={}
for name in ['pcb-bare.stl','pcb-fit-check.stl','switch-fit-coupon.stl']:
 mesh=trimesh.load(str(O/name),force='mesh',process=True)
 native_thickness=float(mesh.extents[2])
 if name=='pcb-fit-check.stl':
  # KiCad's board-only export omits outer copper (1.53 mm FR4 for this 1.6 mm
  # finished stack). A mechanical print gauge should use finished thickness.
  mesh.vertices[:,2]=(mesh.vertices[:,2]-mesh.bounds[0,2])*1.6/native_thickness
  mesh.export(str(O/name))
 assert mesh.is_watertight and mesh.volume>0,(name,'mesh invalid')
 dims=list(map(float,mesh.extents));expected=(61.1,24) if name=='switch-fit-coupon.stl' else (350.76,129.19)
 assert abs(dims[0]-expected[0])<.01 and abs(dims[1]-expected[1])<.01 and 1.5<=dims[2]<=1.61,dims
 models[name]=dict(watertight=True,bounds_mm=dims,nominal_finished_thickness_mm=1.6,native_substrate_export_thickness_mm=native_thickness,volume_mm3=float(mesh.volume),sha256=hashlib.sha256((O/name).read_bytes()).hexdigest())
report=dict(source_sha256=before,production_source_unchanged=True,print_gauge_holes_enlarged=changed,
 extra_diameter_mm=dict(plated_pins=.4,plastic_and_mounts=.3),models=models,
 note='Exact model uses fabrication holes. FIT CHECK model compensates nominal printed-hole shrinkage; never use it for PCB fabrication.')
(O/'pcb-models.json').write_text(json.dumps(report,indent=2)+'\n')
with zipfile.ZipFile(O/'tkl-v12-fit-models.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name in ['pcb-bare.stl','pcb-fit-check.stl','switch-fit-coupon.stl','pcb-models.json','README.md']:z.write(O/name,name)
print('Exact and oversize-hole PCB models validated; fabrication PCB unchanged')
