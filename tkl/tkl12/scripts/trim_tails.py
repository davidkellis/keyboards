#!/usr/bin/env python3
"""Trim warned track ends to their copper contacts, with KiCad rollback checks."""
from routing_geometry import *
import sexpdata as sx
R=Path(__file__).resolve().parents[1];P=R/'kicad/keyboard.kicad_pcb';D=R/'validation/tail-trim-drc.json'
def report():
 subprocess.run(['kicad-cli','pcb','drc','--format','json','-o',str(D),str(P)],check=True,stdout=subprocess.DEVNULL)
 return json.loads(D.read_text())
def okay(r):return not r['unconnected_items'] and not any(v['severity']=='error' for v in r['violations'])
def tag(n):return str(n[0]) if isinstance(n,list) and n else ''
def field(n,t):return next(v for v in n if tag(v)==t)
def coords(g):
 if hasattr(g,'geoms'):return [p for c in g.geoms for p in coords(c)]
 return list(g.coords)
for iteration in range(10):
 r=report();assert okay(r)
 ids={i['uuid'] for v in r['violations'] if v['type']=='track_dangling' for i in v['items']}
 if not ids:break
 b=k.LoadBoard(str(P));obs,_=objects(b);lookup={o['uuid']:o for o in obs};tree=STRtree([o['g'] for o in obs]);plans={}
 for uid in ids:
  t=lookup[uid]['item']
  if isinstance(t,k.PCB_VIA):continue
  line=LineString([xy(t.GetStart()),xy(t.GetEnd())]);contacts=[]
  for j in tree.query(line.buffer(k.ToMM(t.GetWidth())/2+.003)):
   o=obs[j]
   if o['uuid']==uid or o['net']!=t.GetNetname() or t.GetLayer() not in o['layers']:continue
   # Track junctions end exactly on the other centerline. Merely overlapping
   # copper can pass connectivity while still leaving a warned free tail.
   other=o['item']
   if isinstance(other,k.PCB_TRACK) and not isinstance(other,k.PCB_VIA):
    g=line.intersection(LineString([xy(other.GetStart()),xy(other.GetEnd())]))
   else:g=line.intersection(o['g'].buffer(-.005))
   if not g.is_empty:contacts.extend(line.project(Point(p)) for p in coords(g))
  if len(contacts)<2:continue
  lo,hi=min(contacts),max(contacts)
  lo=0 if lo<.00001 else lo;hi=line.length if hi>line.length-.00001 else hi
  if hi-lo<.02 or (lo<.01 and hi>line.length-.01):continue
  plans[uid]=[list(line.interpolate(lo).coords[0]),list(line.interpolate(hi).coords[0])]
 if not plans:break
 def apply(ids):
  backup=P.read_bytes();nodes=sx.loads(backup.decode())
  for n in nodes:
   if tag(n)=='segment' and field(n,'uuid')[1] in ids:
    a,c=plans[field(n,'uuid')[1]];field(n,'start')[1:]=[round(v,6) for v in a];field(n,'end')[1:]=[round(v,6) for v in c]
  try:
   P.write_text(sx.dumps(nodes));after=report()
  except BaseException:
   P.write_bytes(backup);raise
  if okay(after):return len(ids)
  P.write_bytes(backup)
  if len(ids)<2:return 0
  half=len(ids)//2;return apply(ids[:half])+apply(ids[half:])
 count=apply(sorted(plans));after=report();print('Trimmed',count,'tracks;',len(after['violations']),'warnings',flush=True)
 if not count or len(after['violations'])>=len(r['violations']):break
r=report();assert okay(r);print('Final warnings',len(r['violations']),flush=True)
