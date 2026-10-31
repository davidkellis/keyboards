from pathlib import Path
import sys,gc,subprocess,json,math,shutil,collections
sys.excepthook=sys.__excepthook__;gc.disable()
import pcbnew as k,numpy as np
from shapely.geometry import Point,LineString,box
from shapely.affinity import rotate
from shapely import contains_xy
from shapely.strtree import STRtree
mm=k.FromMM
LAYERS=[k.F_Cu,k.B_Cu]
def xy(v):return (k.ToMM(v.x),k.ToMM(v.y))
def vec(p):return k.VECTOR2I(mm(p[0]),mm(p[1]))
def shape(p,size=None):
 x,y=xy(p.GetPosition());w,h=xy(size or p.GetSize());a=-p.GetOrientationDegrees()
 if p.GetShape()==k.PAD_SHAPE_CIRCLE:g=Point(x,y).buffer(w/2,quad_segs=12)
 elif p.GetShape()==k.PAD_SHAPE_OVAL:
  d=abs(w-h)/2
  g=LineString([(x-d,y),(x+d,y)] if w>h else [(x,y-d),(x,y+d)]).buffer(min(w,h)/2,quad_segs=12)
 else:g=box(x-w/2,y-h/2,x+w/2,y+h/2)
 return rotate(g,a,origin=(x,y)) if a else g

def objects(b):
 out=[];holes=[]
 for f in b.GetFootprints():
  for p in f.Pads():
   attr=p.GetAttribute();pos=xy(p.GetPosition());layers=[l for l in LAYERS if p.IsOnLayer(l)]
   g=shape(p);net=p.GetNetname();uid=p.m_Uuid.AsString()
   if attr==k.PAD_ATTRIB_NPTH:net='!hole';layers=LAYERS
   if p.GetDrillSize().x:
    ds=p.GetDrillSize();w,h=xy(ds)
    if abs(w-h)<1e-6:hole=Point(*pos).buffer(w/2,quad_segs=12)
    else:
     d=abs(w-h)/2;hole=LineString([(pos[0]-d,pos[1]),(pos[0]+d,pos[1])] if w>h else [(pos[0],pos[1]-d),(pos[0],pos[1]+d)]).buffer(min(w,h)/2)
     hole=rotate(hole,-p.GetOrientationDegrees(),origin=pos)
    holes.append((hole,net,attr==k.PAD_ATTRIB_NPTH))
   out.append(dict(uuid=uid,net=net,layers=layers,g=g,ports=[(pos,k.F_Cu in layers)],item=p))
 for t in b.GetTracks():
  if isinstance(t,k.PCB_VIA):
   pos=xy(t.GetPosition());g=Point(*pos).buffer(k.ToMM(t.GetWidth(k.F_Cu))/2,quad_segs=12)
   layers=LAYERS;ports=[(pos,True)]
   holes.append((Point(*pos).buffer(k.ToMM(t.GetDrill())/2),t.GetNetname(),False))
  else:
   a,c=xy(t.GetStart()),xy(t.GetEnd());g=LineString([a,c]).buffer(k.ToMM(t.GetWidth())/2,quad_segs=10)
   layers=[t.GetLayer()];ports=[(a,k.F_Cu in layers),(c,k.F_Cu in layers)]
   if math.dist(a,c)>3:ports += [(((a[0]+c[0])/2,(a[1]+c[1])/2),k.F_Cu in layers)]
  out.append(dict(uuid=t.m_Uuid.AsString(),net=t.GetNetname(),layers=layers,g=g,ports=ports,item=t))
 return out,holes

def components(items):
 par=list(range(len(items)))
 def root(i):
  while par[i]!=i:par[i]=par[par[i]];i=par[i]
  return i
 tree=STRtree([a['g'] for a in items])
 for i,a in enumerate(items):
  for j in tree.query(a['g'].buffer(.0002)):
   if j>=i:continue
   if set(a['layers'])&set(items[j]['layers']) and a['g'].distance(items[j]['g'])<.0002:par[root(i)]=root(j)
 return [root(i) for i in range(len(items))]
