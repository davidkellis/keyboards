#!/usr/bin/python3
"""Finish autorouter gaps using checked two-layer A* paths, without via-in-pad."""
from routing_geometry import *
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('--start-side',choices=('front','bottom'),default='front')
args=parser.parse_args()
if args.start_side=='bottom':LAYERS.reverse()
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'kicad/keyboard.kicad_pcb'
ANTENNA=json.loads((ROOT/'scripts/fit-config.json').read_text())['module']['antenna_keepout_kicad_bounds_mm']
MOUNTS=json.loads((ROOT/'scripts/fit-config.json').read_text())['mounting']
MOUNT_ZONES=[Point(27.03+p['xy'][0],149.19-p['xy'][1]).buffer(MOUNTS['copper_keepout_radius_mm']+.02) for p in MOUNTS['points']]
T=Path('/tmp/keyboards-v11');T.mkdir(exist_ok=True)
subprocess.run(['g++','-O3','-o',str(T/'grid3'),str(ROOT/'scripts/grid3.cpp')],check=True)
D=ROOT/'validation/route-progress.json';failed=set()
def drc():
 subprocess.run(['kicad-cli','pcb','drc','--format','json','-o',str(D),str(P)],check=True,stdout=subprocess.DEVNULL)
 return json.loads(D.read_text())
for iteration in range(100):
 report=drc();opens=report['unconnected_items'];print('Iteration',iteration,'opens',len(opens),flush=True)
 if not opens:break
 b=k.LoadBoard(str(P));obs,holes=objects(b);byid={o['uuid']:o for o in obs};success=False
 for e in opens:
  ids=tuple(i['uuid'] for i in e['items'])
  if ids in failed:continue
  net=byid[ids[0]]['net'];mine=[o for o in obs if o['net']==net];groups=components(mine)
  index={o['uuid']:i for i,o in enumerate(mine)};ga,gb=[groups[index[i]] for i in ids]
  if ga==gb:failed.add(ids);continue
  foreign=[o for o in obs if o['net']!=net]
  geoms={l:[o['g'] for o in foreign if l in o['layers']] for l in LAYERS}
  trees={l:STRtree(geoms[l]) for l in LAYERS}
  def collision(g,l,margin):return any(g.distance(geoms[l][j])<margin-1e-6 for j in trees[l].query(g.buffer(margin)))
  smd=[o['g'] for o in obs if isinstance(o['item'],k.PAD) and o['item'].GetAttribute()==k.PAD_ATTRIB_SMD]
  def viavalid(p):
   g=Point(*p)
   return (not any(collision(g,l,.3+.18+.02) for l in LAYERS)
      and not any(g.distance(h)<.15+.2+.02 for h,n,npth in holes)
      and not any(g.distance(s)<.3+.05 for s in smd))
  ports=[]
  for group in (ga,gb):
   found=[]
   for i,o in enumerate(mine):
    if groups[i]!=group:continue
    for point,_ in o['ports']:
     front=LAYERS[0] in o['layers']
     if not front and not viavalid(point):continue
     if not collision(Point(*point),LAYERS[0],.1+.18+.02):found.append((point,front))
   ports.append(list(dict.fromkeys(found)))
  pairs=sorted(((math.dist(a[0],c[0])+2*int(not a[1])+2*int(not c[1]),a,c) for a in ports[0] for c in ports[1]),key=lambda x:x[0])[:30]
  print('Trying',net,'ports',*[len(x) for x in ports],flush=True)
  step=.1;x0,y0=27.7,20.7;w=int((377.1-x0)/step)+1;h=int((148.5-y0)/step)+1
  grid=np.zeros((4,h,w),np.uint8);grid[2,:,:]=1
  def raster(g,l):
   xa,ya,xb,yb=g.bounds;c0=max(0,int(math.floor((xa-x0)/step)));c1=min(w-1,int(math.ceil((xb-x0)/step)))
   r0=max(0,int(math.floor((ya-y0)/step)));r1=min(h-1,int(math.ceil((yb-y0)/step)))
   if c0>c1 or r0>r1:return
   xs=x0+np.arange(c0,c1+1)*step;ys=y0+np.arange(r0,r1+1)*step
   grid[l,r0:r1+1,c0:c1+1]|=contains_xy(g,xs[None,:],ys[:,None]).astype(np.uint8)
  for i,l in enumerate(LAYERS):
   for o in foreign:
    if l in o['layers']:raster(o['g'].buffer(.1+.18+.025,quad_segs=8),i)
   for g,n,npth in holes:
    if npth:raster(g.buffer(.1+.25+.025),i)
   raster(box(*ANTENNA).buffer(.1+.02),i)
   for g in MOUNT_ZONES:raster(g.buffer(.1+.03),i)
  for o in foreign:raster(o['g'].buffer(.3+.18+.025),3)
  for g,n,npth in holes:raster(g.buffer(.15+.2+.025),3)
  for g in smd:raster(g.buffer(.3+.05),3)
  raster(box(*ANTENNA).buffer(.3+.02),3)
  for g in MOUNT_ZONES:raster(g.buffer(.3+.03),3)
  mask=T/'finish-grid.bin';grid.tofile(mask)
  for _,a,c in pairs:
   start,end=a[0],c[0];loc=lambda p:(round((p[0]-x0)/step),round((p[1]-y0)/step))
   sa,se=loc(start),loc(end)
   if grid[0,sa[1],sa[0]] or grid[0,se[1],se[0]]:continue
   result=subprocess.run([str(T/'grid3'),str(w),str(h),*map(str,sa),*map(str,se),str(mask)],capture_output=True,text=True)
   if result.returncode:continue
   raw=[tuple(map(int,line.split())) for line in result.stdout.splitlines()];nodes=[(*start,0)]
   for i,p in enumerate(raw):
    if i in (0,len(raw)-1) or raw[i-1][2]!=p[2] or raw[i+1][2]!=p[2] or (p[0]-raw[i-1][0],p[1]-raw[i-1][1])!=(raw[i+1][0]-p[0],raw[i+1][1]-p[1]):nodes.append((x0+p[0]*step,y0+p[1]*step,p[2]))
   nodes.append((*end,0));backup=P.read_bytes();added=[];vias=[];invalid=False
   for p,q in zip(nodes,nodes[1:]):
    if p[2]!=q[2]:vias.append(p[:2]);continue
    if math.dist(p[:2],q[:2])<1e-6:continue
    if collision(LineString([p[:2],q[:2]]),LAYERS[p[2]],.1+.18):invalid=True;break
   if invalid:continue
   for p,q in zip(nodes,nodes[1:]):
    if p[2]!=q[2] or math.dist(p[:2],q[:2])<1e-6:continue
    t=k.PCB_TRACK(b);t.SetStart(vec(p[:2]));t.SetEnd(vec(q[:2]));t.SetWidth(mm(.2));t.SetLayer(LAYERS[p[2]]);t.SetNet(b.FindNet(net));b.Add(t);added.append(t)
   vias += [point for point,front in (a,c) if not front]
   for point in set(vias):
    v=k.PCB_VIA(b);v.SetPosition(vec(point));v.SetWidth(mm(.6));v.SetDrill(mm(.3));v.SetViaType(k.VIATYPE_THROUGH);v.SetLayerPair(k.F_Cu,k.B_Cu);v.SetNet(b.FindNet(net));b.Add(v);added.append(v)
   b.BuildConnectivity();k.SaveBoard(str(P),b);after=drc()
   if any(v['severity']=='error' or v['type']=='hole_to_hole' for v in after['violations']) or len(after['unconnected_items'])>=len(opens):
    P.write_bytes(backup);b=k.LoadBoard(str(P));continue
   print('Connected',net,'remaining',len(after['unconnected_items']),flush=True);success=True;break
  if success:break
  failed.add(ids);print('No accepted path',net,flush=True)
 if not success:break
final=drc();print('Final',len(final['unconnected_items']),'opens',flush=True)
sys.exit(bool(final['unconnected_items']) or any(v['severity']=='error' for v in final['violations']))
