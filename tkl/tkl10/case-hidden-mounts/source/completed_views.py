#!/usr/bin/env python3
"""Render the completed assembly from all sides; manufacturing CAD is read-only."""
from pathlib import Path
import json, base64, math
import numpy as np
import cadquery as cq
import trimesh
from PIL import Image, ImageDraw, ImageFont
from matplotlib.font_manager import findfont, FontProperties
import mesh_render as renderer

out=Path(__file__).resolve().parents[1]
dest=out/'completed-views';dest.mkdir(exist_ok=True)
renderer.case=dest
cfg=json.loads((out.parent/'case/fit-config.json').read_text())
geo=json.loads((out.parent/'case/board-geometry.json').read_text())
fit=json.loads((out.parent/'case/fit-report.json').read_text())
def load(n):return trimesh.load_mesh(out/'reference'/(n+'-assembly.stl'),process=False)
def mesh(s):
    vv,ff=s.tessellate(.035,.12)
    return trimesh.Trimesh(vertices=[v.toTuple() for v in vv],faces=ff,process=False)
rot=trimesh.transformations.rotation_matrix(np.radians(fit['tilt_degrees']),[1,0,0])
rot[:3,3]=[2.4,2.4,fit['pcb_underside_front_origin_z']]
def placed(s):return mesh(s).apply_transform(rot)
def box(x,y,z,w,d,h):return cq.Workplane('XY').box(w,d,h,centered=False).translate((x,y,z)).val()
parts=[(load('upper'),'#53697b'),(load('bottom'),'#344651'),(load('bezel'),'#53697b'),
       (load('board'),'#266448'),(load('battery'),'#c9a45b')]
parts += [(load(f'M{i}-carrier'),'#c68d50') for i in range(1,9)]
parts += [(load(f'M{i}-{part}'),'#9da6ad') for i in range(1,9) for part in ['screw','nut']]
for s in geo['switches']:
    x,y=s['xy'];w=s['units']*19.05-1.05;d=17;h=5
    cap=cq.Workplane('XY').box(w,d,h).faces('>Z').edges().chamfer(.8).val()
    cap=cap.translate((x,y,1.6+8.6-cfg['keycaps']['assumed_socket_insertion_mm']+h/2))
    parts.append((placed(cap),'#d8ddd9' if s['units']==1 else '#a9b6bd'))
    parts.append((placed(box(x-6.975,y-6.975,1.6,13.95,13.95,5.5)),'#52565a'))
for c in geo['components']:
    if c['ref'].startswith('LED'):
        x,y,xx,yy=c['bounds']
        s=cq.Workplane('XY').circle(1.05).extrude(1.5).translate(((x+xx)/2,(y+yy)/2,2.3)).val()
        parts.append((placed(s),'#e8efe2'))
    if c['ref']=='SW87':
        x,y,xx,yy=c['bounds']
        parts.append((placed(box(x,y,-c['height'],xx-x,yy-y,c['height'])),'#242b32'))
# Simplified USB-C mouth located within the existing socket fit envelope.
# The measured module/socket shape remains provisional; these visual details
# do not alter the port, fit model or manufacturing files.
c=next(c for c in geo['components'] if c['ref']=='USB_SOCKET')
x,y,xx,yy=c['bounds'];w=xx-x;h=c['height'];depth=yy-y
cx,cy,cz=(x+xx)/2,(y+yy)/2,c['z_top']-h/2
outer=cq.Workplane('XY').box(w,depth,h).edges('|Y').fillet(1.4).val()
inner=cq.Workplane('XY').box(w-.5,depth+2,h-.5).edges('|Y').fillet(1.15).val()
parts.append((placed(outer.cut(inner).translate((cx,cy,cz))),'#c1c6ca'))
parts.append((placed(box(x+.25,y-.15,c['z_top']-h+.25,w-.5,.1,h-.5)),'#182029'))
parts.append((placed(box(cx-3.2,y,cz-.25,6.4,depth-.1,.5)),'#303740'))

names=['Front','Front-right','Right-front','Right','Right-rear','Rear-right',
       'Rear','Rear-left','Left-rear','Left','Left-front','Front-left']
views=[]
for i,label in enumerate(names):
    name=f'orbit-{i:02d}'
    renderer.render(name,parts,'v10 · '+label,'Actual rounded enclosure · illustrative keycaps, colours and port hardware',28,-90+i*30)
    views.append({'id':name,'label':label,'kind':'orbit','index':i,
                  'caption':'Assembled view. The shell is actual CAD; keycaps, colours and port hardware are illustrative.'})
for name,label,elev,azim,caption in [
    ('front','Front straight on',0,-90,'Low front edge with a broad 2.5 mm round. No top screw heads.'),
    ('right','Right side',0,0,'The plate slopes upward toward the rear. The side wall continues into the top.'),
    ('rear','Rear straight on',0,90,'Direct USB-C opening and power switch. Small local insert joints remain at the rear.'),
    ('left','Left side',0,180,'Flush sloping plate with 3 mm vertical corner radii.'),
    ('top','Top',90,-90,'Full key layout with illustrative blank keycaps. No raised rim around the plate.'),
    ('bottom','Underneath',-90,-90,'Inset removable bottom and eight recessed screw heads. Optional rubber feet are not modeled.')]:
    renderer.render(name,parts,'v10 · '+label,caption,elev,azim)
    views.append({'id':name,'label':label,'kind':'fixed','caption':caption})

# A compact CAD view sheet for inspection without opening the interactive file.
sheet=Image.new('RGB',(1920,1840),'#f5f7fa');draw=ImageDraw.Draw(sheet)
fontpath=findfont(FontProperties(family='DejaVu Sans'))
bold=findfont(FontProperties(family='DejaVu Sans',weight='bold'))
draw.text((55,30),'v10 · the completed keyboard, all around',font=ImageFont.truetype(bold,36),fill='#20364b')
draw.text((55,85),'Actual case geometry · illustrative keycaps and colours',font=ImageFont.truetype(fontpath,23),fill='#526a7b')
tiles=[('orbit-01','Front / right'),('orbit-07','Rear / left'),('left','Left profile'),
       ('right','Right profile'),('top','Top'),('bottom','Underside')]
for i,(name,label) in enumerate(tiles):
    x=35+(i%2)*950;y=155+(i//2)*535
    draw.text((x+20,y),label,font=ImageFont.truetype(bold,25),fill='#20364b')
    pic=Image.open(dest/(name+'.png')).crop((45,155,1635,805))
    pic.thumbnail((910,460),Image.Resampling.LANCZOS)
    sheet.paste(pic,(x+(920-pic.width)//2,y+45+(450-pic.height)//2))
draw.text((55,1775),'The upper shell is continuous. Split prints need bonding/finishing; physical fit remains unverified.',
          font=ImageFont.truetype(fontpath,19),fill='#526a7b')
sheet.save(out/'completed-overview.png')

for v in views:
    v['src']='data:image/png;base64,'+base64.b64encode((dest/(v['id']+'.png')).read_bytes()).decode()
template=(out/'source/completed-template.html').read_text()
html=template.replace('__VIEW_DATA__',json.dumps(views)).replace('__INITIAL_IMAGE__',views[1]['src'])
(out/'completed-keyboard.html').write_text(html)
(dest/'view-index.json').write_text(json.dumps([{k:v for k,v in item.items() if k!='src'} for item in views],indent=2)+'\n')
print('Completed gallery, overview and 18 views exported; no fabrication geometry modified.',flush=True)
