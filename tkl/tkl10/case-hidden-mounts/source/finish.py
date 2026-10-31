#!/usr/bin/env python3
"""Export 256 mm bed halves, a mount trial, and independently inspect meshes."""
from pathlib import Path
import json,hashlib,math,zipfile
import cadquery as cq
import trimesh
from shapely.geometry import box,Polygon
from split_geometry import lap_split
from mesh_export import clean_degenerate_facets

out=Path(__file__).resolve().parents[1];root=out.parent
g=json.loads((root/'case/board-geometry.json').read_text())
c=json.loads((root/'case/fit-config.json').read_text())
f=json.loads((root/'case/fit-report.json').read_text())
r=json.loads((out/'validation.json').read_text())
W,D=[g['board'][k] for k in ['width','depth']];CW,CD=c['fixed_footprint_mm'];T=g['board']['thickness']
PT=T+c['plate_top_above_pcb_mm'];PB=PT-c['plate_thickness_mm'];deg=f['tilt_degrees'];z0=f['pcb_underside_front_origin_z']
def block(x,y,z,w,d,h):return cq.Workplane('XY').box(w,d,h,centered=False).translate((x,y,z)).val()
def local(s):return s.translate((-2.4,-2.4,-z0)).rotate((0,0,0),(1,0,0),-deg)
def world(s):return s.rotate((0,0,0),(1,0,0),deg).translate((2.4,2.4,z0))
def load(n):return cq.Shape.importBrep(str(out/'reference'/(n+'.brep')))
def solid(p,z,h):
    ss=[]
    for q in list(p.geoms) if hasattr(p,'geoms') else [p]:
        if q.is_empty:continue
        s=cq.Workplane('XY').polyline(list(q.exterior.coords)[:-1]).close().extrude(h).translate((0,0,z)).val()
        for ring in q.interiors:s=s.cut(cq.Workplane('XY').polyline(list(ring.coords)[:-1]).close().extrude(h+.2).translate((0,0,z-.1)).val())
        ss.append(s)
    return cq.Compound.makeCompound(ss)
def export(s,n):
    assert s.isValid() and len(s.Solids())==1,(n,len(s.Solids()))
    b=s.BoundingBox();s=s.translate((-b.xmin,-b.ymin,-b.zmin))
    cq.exporters.export(s,str(out/(n+'.stl')),tolerance=.025,angularTolerance=.12)
    clean_degenerate_facets(out/(n+'.stl'))
    return s
upper=load('upper');base=load('bottom');board=load('board')
rows=sorted(set(round(s['xy'][1],4) for s in g['switches']))
seam=[]
for i,y in enumerate(rows):
    xs=sorted(s['xy'][0] for s in g['switches'] if abs(s['xy'][1]-y)<.01)
    xs=[(a+b)/2 for a,b in zip(xs,xs[1:]) if b-a>18]
    xx=min(xs,key=lambda x:abs(x-W/2))
    lo=-10 if i==0 else (rows[i-1]+y)/2;hi=D+10 if i==len(rows)-1 else (rows[i+1]+y)/2
    seam.extend([(xx,lo),(xx,hi)])
left=Polygon([(-10,-10)]+seam+[(-10,D+10)])
print('Split upper and bottom with bonded half-laps',flush=True)
us,ur=lap_split(local(upper),left,box(-10,-10,W+10,D+10),PB,PT,4,.2,solid)
bs,br=lap_split(base,box(-10,-10,CW/2,CD+10),box(-10,-10,CW+10,CD+10),0,1.2,6,.2,solid)
for side,s in zip(['left','right'],us):export(s.rotate((0,0,0),(1,0,0),180),'plate-upper-'+side)
for side,s in zip(['left','right'],bs):export(s,'case-bottom-'+side)
corner=upper.intersect(block(0,0,0,40,28,30)).clean()
export(local(corner).rotate((0,0,0),(1,0,0),180),'edge-coupon-upper')
print('Mount coupon using the actual first side mount',flush=True)
pos=r['mounts'][0]['position_mm'];crop=block(0,pos-8,0,18,16,30)
cu=upper.intersect(crop).clean();cb=base.intersect(crop).clean();cp=board.intersect(crop).clean()
export(local(cu).rotate((0,0,0),(1,0,0),180),'mount-coupon-upper')
export(cb,'mount-coupon-bottom');export(local(cp),'mount-coupon-pcb')
ca=cq.Assembly(name='hidden-mount-fit-trial')
for name,s,col in [('upper',cu,(.25,.35,.45)),('bottom',cb,(.15,.2,.25)),('PCB',cp,(.1,.4,.25)),('carrier',load('M1-carrier'),(.8,.5,.2)),('screw',load('M1-screw'),(.65,.65,.65)),('nut',load('M1-nut'),(.65,.65,.65))]:ca.add(s,name=name,color=cq.Color(*col))
ca.export(str(out/'mount-coupon-assembly.step'))
print('USB corner trial with the new sliding insert',flush=True)
usb_crop=block(13,90,0,41,CD-90,30)
uu=upper.intersect(usb_crop).clean();ub=base.intersect(usb_crop).clean();up=local(board.intersect(usb_crop).clean())
bb=up.BoundingBox();tools=[]
for h in g['holes']:
    if not (h['ref'].startswith('SW') or h['ref']=='U1'):continue
    x,y=h['xy'];w,d=h['size']
    if not (bb.xmin-1<x<bb.xmax+1 and bb.ymin-1<y<bb.ymax+1):continue
    w+=.4;d+=.4
    if abs(w-d)<1e-7:tool=cq.Workplane('XY').circle(w/2).extrude(T+2)
    else:tool=cq.Workplane('XY').slot2D(max(w,d),min(w,d),h['angle']+(90 if d>w else 0)).extrude(T+2)
    tools.append(tool.translate((x,y,-1)).val())
up=up.cut(*tools).clean()
export(local(uu).rotate((0,0,0),(1,0,0),180),'usb-coupon-upper')
export(ub,'usb-coupon-bottom');export(up,'usb-coupon-pcb')
ua=cq.Assembly(name='sliding-USB-bezel-fit-trial')
for name,s,col in [('upper',uu,(.25,.35,.45)),('bottom',ub,(.15,.2,.25)),('PCB-gauge',world(up),(.1,.4,.25)),('USB-insert',load('bezel'),(.45,.6,.7))]:ua.add(s,name=name,color=cq.Color(*col))
ua.export(str(out/'usb-coupon-assembly.step'))
print('Inspect closed mounting surfaces and print meshes',flush=True)
closures=[]
for mount in c['mounting']['points']:
    x,y=mount['xy'];w=cq.Workplane('XY').circle(2.0).extrude(.5).translate((x,y,PT-.6)).val()
    missing=world(w).cut(upper).Volume()
    closures.append({'old_mount':mount['ref'],'missing_top_material_mm3':missing})
    assert missing<1e-5,('Visible mount hole',mount,missing)
meshes=[]
names=['plate-upper','plate-upper-left','plate-upper-right','case-bottom','case-bottom-left','case-bottom-right','nut-carrier','usb-bezel','led-diffuser','mount-coupon-upper','mount-coupon-bottom','mount-coupon-pcb','usb-coupon-upper','usb-coupon-bottom','usb-coupon-pcb','edge-coupon-upper']
for name in names:
    m=trimesh.load_mesh(out/(name+'.stl'),process=True)
    check={'file':name+'.stl','watertight':bool(m.is_watertight),'positive_volume':bool(m.volume>0),'connected_shells':len(m.split()),'bounds_mm':m.extents.tolist(),'min_z':float(m.bounds[0,2]),'fits_256_bed':bool(max(m.extents[:2])<=256)}
    assert check['watertight'] and check['positive_volume'] and check['connected_shells']==1,check
    if name not in ['plate-upper','case-bottom']:assert check['fits_256_bed'],check
    meshes.append(check)
hashes=json.loads((out/'preserved-inputs.json').read_text());changed=[]
for name,digest in hashes.items():
    p=root/name
    if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:changed.append(name)
assert not changed,changed
assert not r['collisions'],r['collisions']
assert not r['insertion_collisions'],r['insertion_collisions']
paths=json.loads((out/'assembly-paths.json').read_text())
assert paths['passed'],paths
vertices=[v.Center() for v in upper.Vertices()]
front=max(v.z for v in vertices if abs(v.y)<1e-5)
rear=max(v.z for v in vertices if abs(v.y-CD)<1e-5)
bb=upper.BoundingBox()
assert all(abs(actual-expected)<1e-4 for actual,expected in zip([front,rear],r['surface']['outer_wall_top_front_rear_mm'])),(front,rear)
assert local(upper).BoundingBox().zmax<=PT+1e-5,'Perimeter protrudes above plate'
assert r['surface']['raised_rim_mm']==0 and r['surface']['rounded_edge_count']==12
assert abs(bb.xlen-CW)<1e-4 and abs(bb.ylen-CD)<1e-4
corner_checks=[]
for label,x,y,dx,dy in [('front-left',0,0,1,1),('front-right',CW,0,-1,1),('rear-left',0,CD,1,-1),('rear-right',CW,CD,-1,-1)]:
    low=cq.Edge.makeLine((x,y,.6),(x+dx*5,y+dy*5,.6))
    roof=cq.Edge.makeLine((x+dx*2.2,y+dy*2.2,2),(x+dx*2.2,y+dy*2.2,30))
    low_segments=[e.Length() for e in upper.intersect(low).Edges()]
    roof_segments=[e.Length() for e in upper.intersect(roof).Edges()]
    assert len(low_segments)==1 and low_segments[0]>=.8,(label,low_segments)
    assert len(roof_segments)==1 and roof_segments[0]>=1.2,(label,roof_segments)
    corner_checks.append({'corner':label,'skirt_diagonal_at_z_0p6_mm':low_segments[0],
                          'roof_vertical_at_xy_inset_2p2_mm':roof_segments[0]})
v={'solid_collision_checks_pass':True,'insertion_checks_pass':True,'removable_part_paths_pass':True,'measured_front_rear_heights_mm':[front,rear],'surface':r['surface'],'corner_section_checks':corner_checks,'measured_footprint_mm':[bb.xlen,bb.ylen],'original_files_checked':len(hashes),'changed_original_files':changed,'old_top_mount_closure_checks':closures,'print_meshes':meshes,'split_joints':{'upper':ur,'bottom':br},'physical_fit_verified':False}
(out/'print-validation.json').write_text(json.dumps(v,indent=2)+'\n')
with zipfile.ZipFile(out/'v10-hidden-mount-print-files.zip','w',zipfile.ZIP_DEFLATED) as z:
    for n in names:z.write(out/(n+'.stl'),n+'.stl')
    if (out/'README.md').exists():z.write(out/'README.md','README.md')
print('Print package and validation complete',flush=True)
