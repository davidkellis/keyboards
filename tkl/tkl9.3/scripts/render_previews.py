"""Render actual STL meshes without requiring an X server or GPU context."""
from pathlib import Path
import json,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/tkl-v9.3-mpl')
from PIL import Image, ImageDraw, ImageFont
from matplotlib.colors import to_rgb
from matplotlib.font_manager import findfont, FontProperties
import numpy as np
import trimesh
from numba import njit

@njit(cache=True)
def rasterize(triangles,colors,pixels,depth):
    height,width=depth.shape
    for index in range(len(triangles)):
        t=triangles[index]
        x0,y0,z0=t[0];x1,y1,z1=t[1];x2,y2,z2=t[2]
        den=(y1-y2)*(x0-x2)+(x2-x1)*(y0-y2)
        if abs(den)<1e-10:continue
        xmin=max(0,int(np.floor(min(x0,x1,x2))))
        xmax=min(width-1,int(np.ceil(max(x0,x1,x2))))
        ymin=max(0,int(np.floor(min(y0,y1,y2))))
        ymax=min(height-1,int(np.ceil(max(y0,y1,y2))))
        for y in range(ymin,ymax+1):
            for x in range(xmin,xmax+1):
                a=((y1-y2)*(x+.5-x2)+(x2-x1)*(y+.5-y2))/den
                b=((y2-y0)*(x+.5-x2)+(x0-x2)*(y+.5-y2))/den
                c=1-a-b
                if min(a,b,c)<-1e-8:continue
                z=a*z0+b*z1+c*z2
                if z>depth[y,x]:
                    depth[y,x]=z
                    pixels[y,x]=colors[index]

case=Path(__file__).resolve().parents[1]/'case'
report=json.loads((case/'fit-report.json').read_text())
geometry=json.loads((case/'board-geometry.json').read_text())
cfg=json.loads((case/'fit-config.json').read_text())
rot=trimesh.transformations.rotation_matrix(np.radians(report['tilt_degrees']),[1,0,0])
rot[:3,3]=[2.4,2.4,report['pcb_underside_front_origin_z']]
def load(name):return trimesh.load_mesh(case/name,process=False)
def place(mesh):return mesh.copy().apply_transform(rot)
def crop(mesh,bounds):
    result=mesh.copy()
    for i in range(3):
        n=np.zeros(3);n[i]=1
        p=np.zeros(3);p[i]=bounds[0][i]
        result=result.slice_plane(p,n)
        p[i]=bounds[1][i]
        result=result.slice_plane(p,-n)
    return result

base=load('case.stl')
plate=load('plate.stl')
# Restore the board-space origin of the bed-normalized STL.
plate.apply_translation([0,cfg['recessed_plate']['front_edge_inset_mm'],report['stack']['pcb_top_z']])
pcb=place(load('pcb-bare.stl'))
plate_world=place(plate)
base_color='#455e73';plate_color='#a8c2d8';pcb_color='#28684a'
installed=[]
for mount in cfg['mounting']['points']:
    x,y=mount['xy'];m=cfg['mounting']
    head=trimesh.creation.cylinder(radius=m['screw_head_diameter_mm']/2,height=m['screw_head_height_mm'],sections=48)
    head.apply_translation([x,y,m['screw_head_seat_z_mm']+m['screw_head_height_mm']/2])
    installed.append((place(head),'#89939c'))
insert=load('led-diffuser.stl')
center=(insert.bounds[0]+insert.bounds[1])/2
for led in report['surface_finish']['led_centers']:
    x,y=led['xy'];m=insert.copy()
    m.apply_translation([x-center[0],y-center[1],report['stack']['plate_bottom_z']-cfg['surface_finish']['diffuser_flange_thickness_mm']])
    installed.append((place(m),'#edf1f4'))

def render(name,parts,title,subtitle,elev=33,azim=-62):
    e,a=np.radians([elev,azim])
    eye=np.array([np.cos(e)*np.cos(a),np.cos(e)*np.sin(a),np.sin(e)])
    right=np.array([-np.sin(a),np.cos(a),0.])
    up=np.cross(eye,right)
    camera=np.stack([right,up,eye],axis=1)
    projected=[];colors=[]
    light=np.array([-.25,-.45,.86]);light/=np.linalg.norm(light)
    for mesh,color in parts:
        visible=(mesh.face_normals@eye)>1e-9
        projected.append(mesh.triangles[visible]@camera)
        shade=.60+.40*np.maximum(0,mesh.face_normals[visible]@light)
        colors.append(np.array(to_rgb(color))[None,:]*shade[:,None]*255)
    triangles=np.concatenate(projected)
    lo=triangles.min(axis=(0,1));hi=triangles.max(axis=(0,1))
    scale=min(1500/(hi[0]-lo[0]),610/(hi[1]-lo[1]))
    triangles[:,:,0]=(triangles[:,:,0]-(lo[0]+hi[0])/2)*scale+840
    triangles[:,:,1]=-(triangles[:,:,1]-(lo[1]+hi[1])/2)*scale+480
    pixels=np.full((840,1680,3),[245,247,250],dtype=np.uint8)
    depth=np.full((840,1680),-np.inf)
    rasterize(triangles,np.clip(np.concatenate(colors),0,255).astype(np.uint8),pixels,depth)
    img=Image.fromarray(pixels)
    draw=ImageDraw.Draw(img)
    draw.text((70,35),title,font=ImageFont.truetype(findfont(FontProperties(family='DejaVu Sans',weight='bold')),34),fill='#20364b')
    draw.text((70,92),subtitle,font=ImageFont.truetype(findfont('DejaVu Sans'),21),fill='#4d6173')
    img.save(case/(name+'.png'))
    print('Rendered',name,flush=True)

render('plate-preview',[(plate,plate_color)],'v9.3 · plain switch plate',
       'Solid surface over controller and connector · clearance pockets underneath',40,-65)
render('base-preview',[(base,base_color)],'v9.3 · continuous case rim',
       'Raised outer walls · captive nuts · reinforced floor · same footprint and height',40,-65)
complete=[(base,base_color),(pcb,pcb_color),(plate_world,plate_color)]+installed
render('assembled-preview',complete,
       'v9.3 · clean plate surface',
       'Concealed pin clearances · flush light windows · screw heads shown · keys omitted',37,-70)
render('assembled-exploded',[(base,base_color),(pcb,pcb_color),(plate_world.copy().apply_translation([0,0,18]),plate_color)],
       'v9.3 · separate plate and case',
       'Exploded view · the same twelve M2 screws clamp the plate and PCB to the base',35,-65)
corner=crop(base,[[290,77,-1],[357,136,30]])
parts=[(corner,base_color)]
for c in geometry['components']:
    if c['ref'] not in ('U1','USB_SOCKET','USB_PLUG_EXTERNAL'):continue
    x,y,xx,yy=c['bounds'];z=c['z_top'];h=c['height']
    m=trimesh.creation.box(extents=[xx-x,yy-y,h]);m.apply_translation([(x+xx)/2,(y+yy)/2,z-h/2])
    parts.append((place(m),'#d89036' if c['ref']=='U1' else '#dabc5f'))
render('module-fit',parts,'Rear module fit envelope',
       'Orange: assumed clone envelope · yellow: USB socket/plug · plate omitted',45,-65)
rear=crop(base,[[317,113,-1],[357,136,30]])
render('usb-surround',[(rear,base_color)],'Direct USB-C surround',
       'Socket-sized through aperture inside a larger blind plug recess',10,85)
detail=[]
for mesh,color in complete:
    clipped=crop(mesh,[[289,94,-1],[357,136,30]])
    if len(clipped.faces):detail.append((clipped,color))
render('rear-detail',detail,'v9.3 · controller area',
       'One continuous top surface · pin reliefs are underneath · removable M2 screws',48,-65)
