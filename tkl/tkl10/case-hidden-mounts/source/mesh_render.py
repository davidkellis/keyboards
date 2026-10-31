"""Render actual STL meshes without requiring an X server or GPU context."""
from pathlib import Path
import json,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/tkl-v10-mpl')
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

