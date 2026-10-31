#!/usr/bin/env python3
"""Complete local switch-pattern reroutes; batch-check with KiCad DRC.

Uses conservative copper/hole masks on both layers, ordinary 0.6/0.3 vias,
and 0.2 mm tracks. Every saved batch must improve connectivity without adding
errors. Unlike build_v12.py this resumes from the current board.
"""
from routing_geometry import *
import argparse

R=Path(__file__).resolve().parents[1];P=R/'kicad/keyboard.kicad_pcb'
T=Path('/tmp/keyboards-v12');T.mkdir(exist_ok=True)
D=R/'validation/routing-drc.json'
parser=argparse.ArgumentParser();parser.add_argument('--batch',type=int,default=25);args=parser.parse_args()
subprocess.run(['g++','-O3','-o',str(T/'grid3'),str(R/'scripts/grid3.cpp')],check=True)
cfg=json.loads((R/'scripts/fit-config.json').read_text())
ANTENNA=box(*cfg['module']['antenna_keepout_kicad_bounds_mm'])
MOUNTS=[Point(27.03+p['xy'][0],149.19-p['xy'][1]).buffer(cfg['mounting']['copper_keepout_radius_mm']+.02) for p in cfg['mounting']['points']]
def drc():
 subprocess.run(['kicad-cli','pcb','drc','--format','json','-o',str(D),str(P)],check=True,stdout=subprocess.DEVNULL)
 return json.loads(D.read_text())
def errors(report):return [v for v in report['violations'] if v['severity']=='error' or v['type']=='hole_to_hole']
failed=set()
for batch in range(100):
 report=drc();assert not errors(report),errors(report)[:3]
 opens=report['unconnected_items'];print('Batch',batch,'opens',len(opens),flush=True)
 if not opens:break
 backup=P.read_bytes();b=k.LoadBoard(str(P));obs,holes=objects(b);byid={o['uuid']:o for o in obs};connected=0
 smd=[o['g'] for o in obs if isinstance(o['item'],k.PAD) and o['item'].GetAttribute()==k.PAD_ATTRIB_SMD]
 for e in opens:
  ids=tuple(i['uuid'] for i in e['items'])
  if ids in failed or any(i not in byid for i in ids):continue
  net=byid[ids[0]]['net'];mine=[o for o in obs if o['net']==net];groups=components(mine)
  index={o['uuid']:i for i,o in enumerate(mine)}
  ga,gb=[groups[index[i]] for i in ids]
  if ga==gb:continue
  foreign=[o for o in obs if o['net']!=net]
  geoms={l:[o['g'] for o in foreign if l in o['layers']] for l in LAYERS}
  trees={l:STRtree(geoms[l]) for l in LAYERS}
  def collision(g,l,margin):return any(g.distance(geoms[l][j])<margin-1e-6 for j in trees[l].query(g.buffer(margin)))
  def viavalid(p):
   g=Point(*p)
   return (not any(collision(g,l,.3+.18+.025) for l in LAYERS)
      and not any(g.distance(h)<.15+.2+.025 for h,n,npth in holes)
      and not any(g.distance(s)<.3+.05 for s in smd))
  ports=[]
  for group in (ga,gb):
   found=[]
   for i,o in enumerate(mine):
    if groups[i]!=group:continue
    for point,_ in o['ports']:
     for layer in o['layers']:
      if not collision(Point(*point),layer,.1+.18+.025):found.append((point,layer))
   ports.append(list(dict.fromkeys(found)))
  pairs=sorted(((math.dist(a[0],c[0])+(0 if a[1]==c[1] else 1.5),a,c) for a in ports[0] for c in ports[1]),key=lambda x:x[0])[:20]
  success=False
  for attempt,(distance,a,c) in enumerate(pairs):
   start,end=a[0],c[0];layers=[a[1],next(l for l in LAYERS if l!=a[1])]
   # The C++ search finishes on layer zero; use a conventional via at the
   # destination when that port is accessible only on the opposite layer.
   endvia=c[1]!=layers[0]
   if endvia and (not viavalid(end) or collision(Point(*end),layers[0],.1+.18+.025)):continue
   for margin in (5,15,40):
    step=.1;x0=max(27.65,math.floor((min(start[0],end[0])-margin)*10)/10);y0=max(20.65,math.floor((min(start[1],end[1])-margin)*10)/10)
    x1=min(377.15,max(start[0],end[0])+margin);y1=min(148.55,max(start[1],end[1])+margin)
    w=int((x1-x0)/step)+1;h=int((y1-y0)/step)+1
    grid=np.zeros((4,h,w),np.uint8);grid[2,:,:]=1
    region=box(x0-1,y0-1,x1+1,y1+1)
    def raster(g,l):
     if not g.intersects(region):return
     xa,ya,xb,yb=g.bounds;c0=max(0,int(math.floor((xa-x0)/step)));c1=min(w-1,int(math.ceil((xb-x0)/step)))
     r0=max(0,int(math.floor((ya-y0)/step)));r1=min(h-1,int(math.ceil((yb-y0)/step)))
     if c0>c1 or r0>r1:return
     xs=x0+np.arange(c0,c1+1)*step;ys=y0+np.arange(r0,r1+1)*step
     grid[l,r0:r1+1,c0:c1+1]|=contains_xy(g,xs[None,:],ys[:,None]).astype(np.uint8)
    for li,l in enumerate(layers):
     for j in trees[l].query(region):raster(geoms[l][j].buffer(.1+.18+.03,quad_segs=8),li)
     for g,n,npth in holes:
      if npth:raster(g.buffer(.1+.25+.03),li)
     raster(ANTENNA.buffer(.1+.025),li)
     for g in MOUNTS:raster(g.buffer(.1+.03),li)
    for o in foreign:
     if o['g'].intersects(region):raster(o['g'].buffer(.3+.18+.03),3)
    for g,n,npth in holes:
     if g.intersects(region):raster(g.buffer(.15+.2+.03),3)
    for g in smd:
     if g.intersects(region):raster(g.buffer(.3+.05),3)
    raster(ANTENNA.buffer(.3+.025),3)
    for g in MOUNTS:raster(g.buffer(.3+.03),3)
    loc=lambda p:(round((p[0]-x0)/step),round((p[1]-y0)/step))
    sa,se=loc(start),loc(end)
    if not(0<=sa[0]<w and 0<=sa[1]<h and 0<=se[0]<w and 0<=se[1]<h):continue
    if grid[0,sa[1],sa[0]] or grid[0,se[1],se[0]]:continue
    mask=T/'local-grid.bin';grid.tofile(mask)
    result=subprocess.run([str(T/'grid3'),str(w),str(h),*map(str,sa),*map(str,se),str(mask)],capture_output=True,text=True)
    if result.returncode:continue
    raw=[tuple(map(int,line.split())) for line in result.stdout.splitlines()];nodes=[(*start,0)]
    for i,p in enumerate(raw):
     if i in (0,len(raw)-1) or raw[i-1][2]!=p[2] or raw[i+1][2]!=p[2] or (p[0]-raw[i-1][0],p[1]-raw[i-1][1])!=(raw[i+1][0]-p[0],raw[i+1][1]-p[1]):nodes.append((x0+p[0]*step,y0+p[1]*step,p[2]))
    nodes.append((*end,0))
    if any(collision(LineString([p[:2],q[:2]]),layers[p[2]],.1+.18+.005) for p,q in zip(nodes,nodes[1:]) if p[2]==q[2] and math.dist(p[:2],q[:2])>1e-6):continue
    vias=set(p[:2] for p,q in zip(nodes,nodes[1:]) if p[2]!=q[2])
    if endvia:vias.add(end)
    if not all(viavalid(p) for p in vias):continue
    for p,q in zip(nodes,nodes[1:]):
     if p[2]!=q[2] or math.dist(p[:2],q[:2])<1e-6:continue
     t=k.PCB_TRACK(b);t.SetStart(vec(p[:2]));t.SetEnd(vec(q[:2]));t.SetWidth(mm(.2));t.SetLayer(layers[p[2]]);t.SetNet(b.FindNet(net));b.Add(t)
     g=LineString([xy(t.GetStart()),xy(t.GetEnd())]).buffer(.1,quad_segs=10)
     obs.append(dict(uuid=t.m_Uuid.AsString(),net=net,layers=[t.GetLayer()],g=g,ports=[(xy(t.GetStart()),True),(xy(t.GetEnd()),True)],item=t))
    for p in vias:
     v=k.PCB_VIA(b);v.SetPosition(vec(p));v.SetWidth(mm(.6));v.SetDrill(mm(.3));v.SetViaType(k.VIATYPE_THROUGH);v.SetLayerPair(k.F_Cu,k.B_Cu);v.SetNet(b.FindNet(net));b.Add(v)
     obs.append(dict(uuid=v.m_Uuid.AsString(),net=net,layers=LAYERS,g=Point(*p).buffer(.3),ports=[(p,True)],item=v));holes.append((Point(*p).buffer(.15),net,False))
    success=True;connected+=1
    print('Routed',net,'length',round(distance,2),'batch connection',connected,flush=True)
    break
   if success:break
  if not success:failed.add(ids);print('No path',net,ids,flush=True)
  if connected>=args.batch:break
 if not connected:break
 b.BuildConnectivity();k.SaveBoard(str(P),b);after=drc()
 if errors(after) or len(after['unconnected_items'])>=len(opens):
  (T/'rejected-batch.kicad_pcb').write_bytes(P.read_bytes());(T/'rejected-drc.json').write_text(json.dumps(after,indent=2))
  P.write_bytes(backup);print('Batch rejected and rolled back:',len(errors(after)),'errors;',len(after['unconnected_items']),'opens',flush=True);sys.exit(2)
 print('Batch accepted, remaining',len(after['unconnected_items']),flush=True)
final=drc();print('Final',len(final['unconnected_items']),'opens',flush=True)
sys.exit(bool(final['unconnected_items']) or bool(errors(final)))
