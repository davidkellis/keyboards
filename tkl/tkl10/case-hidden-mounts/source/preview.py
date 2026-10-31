#!/usr/bin/env python3
"""Render the exported prototype geometry, including a removable-floor view."""
from pathlib import Path
import json,math
import numpy as np
import trimesh
import cadquery as cq
import mesh_render as renderer

out=Path(__file__).resolve().parents[1]
renderer.case=out
cfg=json.loads((out.parent/'case/fit-config.json').read_text())
geo=json.loads((out.parent/'case/board-geometry.json').read_text())
fit=json.loads((out.parent/'case/fit-report.json').read_text())
def load(name):return trimesh.load_mesh(out/'reference'/(name+'-assembly.stl'),process=False)
upper=load('upper');base=load('bottom');bezel=load('bezel');board=load('board');battery=load('battery')
uc='#53697b';bc='#344651';pc='#266448'
carriers=[(load(f'M{i}-carrier'),'#c68d50') for i in range(1,9)]
hardware=[(load(f'M{i}-{part}'),'#9da6ad') for i in range(1,9) for part in ['screw','nut']]
rot=trimesh.transformations.rotation_matrix(np.radians(fit['tilt_degrees']),[1,0,0])
rot[:3,3]=[2.4,2.4,fit['pcb_underside_front_origin_z']]
def mesh(s):
    vv,ff=s.tessellate(.08)
    return trimesh.Trimesh(vertices=[v.toTuple() for v in vv],faces=ff,process=False)
caps=[]
switch_bodies=[]
for s in geo['switches']:
    x,y=s['xy'];w=s['units']*19.05-1.05;d=17;h=5
    solid=cq.Workplane('XY').box(w,d,h).faces('>Z').edges().chamfer(.8).val()
    cap=mesh(solid)
    cap.apply_translation([x,y,1.6+8.6-cfg['keycaps']['assumed_socket_insertion_mm']+h/2])
    cap.apply_transform(rot)
    caps.append((cap,'#d8ddd9' if s['units']==1 else '#a9b6bd'))
    body=trimesh.creation.box(extents=[13.95,13.95,5.5])
    body.apply_translation([x,y,1.6+2.75]);body.apply_transform(rot)
    switch_bodies.append((body,'#52565a'))
diffusers=[]
for c in geo['components']:
    if not c['ref'].startswith('LED'):continue
    x,y,xx,yy=c['bounds']
    m=trimesh.creation.cylinder(radius=1.05,height=1.5,sections=32)
    m.apply_translation([(x+xx)/2,(y+yy)/2,3.05]);m.apply_transform(rot)
    diffusers.append((m,'#e8efe2'))
complete=[(upper,uc),(base,bc),(bezel,uc),(board,pc)]+carriers+hardware+diffusers
renderer.render('assembled-preview',complete,'v10 · flush top and rounded edges',
    '2.5 mm top-edge radius · 3 mm vertical corners · concealed underside fasteners',42,-70)
renderer.render('with-keycaps-preview',complete+switch_bodies+caps,'v10 · alternate enclosure',
    'Actual case geometry with illustrative keycaps · flush perimeter, no raised lip',34,-70)
renderer.render('top-preview',complete,'v10 · uninterrupted plate surface',
    'Switch and stabilizer openings, plus six light windows · all fasteners underneath',90,-90)
renderer.render('underside-preview',[(base,bc),(upper,uc),(bezel,uc)]+hardware,
    'v10 · removable bottom panel','Eight recessed M2 x 4 screws · PCB mounting holes remain unchanged',-60,-70)
exploded=[(upper.copy().apply_translation([0,0,28]),uc),(base.copy().apply_translation([0,0,-12]),bc),
    (board,pc),(battery,'#c9a45b'),(bezel.copy().apply_translation([0,13,0]),uc)]
exploded += [(s.copy().apply_translation([0,0,9]),c) for s,c in carriers]
renderer.render('exploded-preview',exploded,'v10 · hidden mounting arrangement',
    'Upper shell · unchanged PCB · eight removable nut carriers · supported bottom · USB insert',32,-68)

def crop(m,lo,hi):
    q=m.copy()
    for i in range(3):
        nn=np.zeros(3);nn[i]=1;pp=np.zeros(3);pp[i]=lo[i]
        q=q.slice_plane(pp,nn);pp[i]=hi[i];q=q.slice_plane(pp,-nn)
    return q
items=[]
for m,c in complete:
    q=crop(m,[-.1,43,-.1],[17,61,17])
    if len(q.faces):items.append((q,c))
renderer.render('mount-detail',items,'Hidden M2 mount · cutaway',
    'Orange carrier engages wall pocket · bottom pins locate carrier · screw head recessed below',-15,-55)
items=[]
for m,c in [(upper,uc),(base,bc)]:
    q=crop(m,[-.1,-.1,-.1],[45,35,14])
    if len(q.faces):items.append((q,c))
renderer.render('rounded-edge-detail',items,'Flush plate · rounded outer edge',
    'Actual front-left corner · 2.5 mm top roll-over · 3 mm corner radius',38,-65)
print('Preview images finished',flush=True)
