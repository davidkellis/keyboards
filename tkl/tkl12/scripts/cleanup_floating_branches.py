"""Delete entire leaf track/via chains, with DRC-gated rollback.

A dangling branch may contain many short segments; walk to its first pad or
junction so cleanup does not need one KiCad invocation per segment.
"""
from routing_geometry import *
import sexpdata as sx
R=Path(__file__).resolve().parents[1];P=R/'kicad/keyboard.kicad_pcb';D=R/'validation/branch-cleanup-drc.json'
def child(n,t):return next((a for a in n if isinstance(a,list) and str(a[0])==t),None)
def report():
 subprocess.run(['kicad-cli','pcb','drc','--format','json','-o',str(D),str(P)],stdout=subprocess.DEVNULL,check=True)
 return json.loads(D.read_text())
def okay(r):return not r['unconnected_items'] and not any(v['severity']=='error' for v in r['violations'])
for iteration in range(30):
 r=report();assert okay(r)
 duplicates={v['items'][-1]['uuid'] for v in r['violations'] if v['type']=='holes_co_located'}
 seeds={i['uuid'] for v in r['violations'] if v['type'] in ('track_dangling','via_dangling') for i in v['items']}
 seeds.update(duplicates)
 if not seeds:break
 b=k.LoadBoard(str(P));obs,_=objects(b);index={o['uuid']:i for i,o in enumerate(obs)}
 tree=STRtree([o['g'] for o in obs]);adj={i:set() for i in range(len(obs))}
 for i,o in enumerate(obs):
  for j in tree.query(o['g'].buffer(.0002)):
   j=int(j)
   if j==i or o['net']!=obs[j]['net'] or not set(o['layers'])&set(obs[j]['layers']):continue
   if o['g'].distance(obs[j]['g'])<.0002:adj[i].add(j)
 # Repeatedly strip electrical graph leaves, never pads. Every removed chain
 # is independently checked by KiCad; a geometric graph can be conservative.
 remove=set();queue=[index[u] for u in seeds if u in index]
 while queue:
  i=queue.pop()
  if i in remove or isinstance(obs[i]['item'],k.PAD):continue
  neighbors=adj[i]-remove
  # Overlapping short segments can form triangles in the copper graph.
  # A track/via whose remaining neighbors all already touch one another
  # cannot be the only electrical bridge between those neighbors.
  if any(v not in adj[u] for u in neighbors for v in neighbors if u!=v):continue
  remove.add(i);queue.extend(neighbors)
 ids={obs[i]['uuid'] for i in remove}|duplicates
 if not ids:break
 def safely_remove(candidates):
  backup=P.read_bytes();nodes=sx.loads(backup.decode())
  nodes=[n for n in nodes if not (isinstance(n,list) and str(n[0]) in ('segment','via') and child(n,'uuid')[1] in candidates)]
  try:
   P.write_text(sx.dumps(nodes));after=report()
  except BaseException:
   P.write_bytes(backup);raise
  if okay(after):return len(candidates)
  P.write_bytes(backup)
  if len(candidates)<2:return 0
  half=len(candidates)//2
  return safely_remove(candidates[:half])+safely_remove(candidates[half:])
 count=safely_remove(sorted(ids))
 if not count:break
 after=report();print('Removed',count,'leaf-chain copper items;',len(after['violations']),'remaining warnings',flush=True)
r=report();assert okay(r)
