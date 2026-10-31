#!/usr/bin/env python3
"""Check removable nut carriers and USB insert along their installation paths."""
from pathlib import Path
import json,math
import cadquery as cq
p=Path(__file__).resolve().parents[1]
g=json.loads((p.parent/'case/board-geometry.json').read_text())
f=json.loads((p.parent/'case/fit-report.json').read_text())
r=json.loads((p/'validation.json').read_text());deg=f['tilt_degrees'];a=math.radians(deg)
def block(x,y,z,w,d,h):return cq.Workplane('XY').box(w,d,h,centered=False).translate((x,y,z)).val()
def cyl(x,y,z,rr,h):return cq.Workplane('XY').circle(rr).extrude(h).translate((x,y,z)).val()
def place(s):return s.rotate((0,0,0),(1,0,0),deg).translate((2.4,2.4,f['pcb_underside_front_origin_z']))
def load(n):return cq.Shape.importBrep(str(p/'reference'/(n+'.brep')))
def intersects(s,t):
    b=s.BoundingBox();bb=t.BoundingBox()
    if any(getattr(b,k+'max')<=getattr(bb,k+'min')+1e-7 or getattr(bb,k+'max')<=getattr(b,k+'min')+1e-7 for k in ['x','y','z']):return 0.
    return s.intersect(t).Volume()
parts=[('PCB',load('board'))]
for c in g['components']:
    if c['ref']=='USB_PLUG_EXTERNAL':continue
    x,y,xx,yy=c['bounds'];h=c['height'];z=c.get('z_top',0)-h if c['side']=='bottom' else g['board']['thickness']-.03
    parts.append((c['ref'],place(block(x,y,z,xx-x,yy-y,h+.03))))
for n in g['pins']:
    x,y=n['xy'];t=g['board']['thickness'];top=n.get('top',False)
    s=cyl(x,y,t-.05 if top else -n['depth'],n['diameter']/2,n['depth']+.05)
    s=s.fuse(cyl(x,y,t-.03 if top else -.25,n['collar_diameter']/2,.28))
    parts.append((n['ref']+' pin',place(s)))
checks=[];fail=[]
for m in r['mounts']:
    print('Carrier withdrawal',m['id'],flush=True)
    sh=load(m['id']+'-carrier')
    direction={'left':(1,0,0),'right':(-1,0,0),'rear':(0,-1,0)}[m['side']]
    for dist in [.4,.8,1.2,1.5]:
        moved=sh.translate(tuple(d*dist for d in direction))
        hits=[]
        for name,s in parts:
            v=intersects(moved,s)
            if v>1e-4:hits.append({'part':name,'volume_mm3':v})
        checks.append({'carrier':m['id'],'inward_mm':dist,'hits':hits})
        fail.extend(hits)
bezel=load('bezel');upper=load('upper')
for dist in [.2,.5,1,2,4,8,15]:
    print('USB insert withdrawal downward',dist,flush=True)
    moved=bezel.translate((0,dist*math.sin(a),-dist*math.cos(a)))
    hits=[]
    for name,s in [('upper',upper)]+parts:
        v=intersects(moved,s)
        if v>1e-4:hits.append({'part':name,'volume_mm3':v})
    checks.append({'USB_insert_withdrawal_mm':dist,'direction':'normal to PCB, down and slightly rearward','hits':hits});fail.extend(hits)
(p/'assembly-paths.json').write_text(json.dumps({'checks':checks,'passed':not fail,'physical_fit_verified':False},indent=2)+'\n')
print('Path collisions',fail,flush=True)
assert not fail,fail
