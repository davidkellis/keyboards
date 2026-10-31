#!/usr/bin/env python3
"""Remove or trim redundant tails, accepting only fully connected DRC-clean changes.

Mutation trials use a fresh pcbnew process to avoid SWIG ownership across loads.
"""
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'kicad/keyboard.kicad_pcb';D=ROOT/'validation/cleanup-drc.json'

def report():
 subprocess.run(['kicad-cli','pcb','drc','--refill-zones','--format','json','-o',str(D),str(P)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 return json.loads(D.read_text())
def okay(r):return not r['unconnected_items'] and not any(e['severity']=='error' for e in r['violations'])

def worker(uid,mode):
 from routing_geometry import k,xy,objects,LineString,Point,vec
 b=k.LoadBoard(str(P));tracks=list(b.GetTracks());t=next((t for t in tracks if t.m_Uuid.AsString()==uid),None)
 if t is None:return
 if mode=='remove':b.Remove(t)
 else:
  if isinstance(t,k.PCB_VIA):return
  line=LineString([xy(t.GetStart()),xy(t.GetEnd())]);obs,_=objects(b);contacts=[]
  for o in obs:
   if o['uuid']==uid or o['net']!=t.GetNetname() or t.GetLayer() not in o['layers']:continue
   g=line.intersection(o['g'].buffer(k.ToMM(t.GetWidth())/2+.002))
   if g.is_empty:continue
   def coords(g):
    if hasattr(g,'geoms'):return [p for c in g.geoms for p in coords(c)]
    return list(g.coords)
   contacts.extend(line.project(Point(p)) for p in coords(g))
  if len(contacts)<2:return
  lo,hi=min(contacts),max(contacts)
  lo=0 if lo<.01 else lo+.01
  hi=line.length if hi>line.length-.01 else hi-.01
  if hi-lo<.02 or (lo<.01 and hi>line.length-.01):return
  t.SetStart(vec(line.interpolate(lo).coords[0]));t.SetEnd(vec(line.interpolate(hi).coords[0]))
 b.BuildConnectivity();k.SaveBoard(str(P),b)

if len(sys.argv)>1:
 worker(*sys.argv[1:]);sys.exit()
r=report();assert okay(r)
for iteration in range(200):
 count=len(r['violations']);improved=False
 ids={i['uuid'] for e in r['violations'] if e['type'] in ('track_dangling','via_dangling') for i in e['items']}
 if not ids:break
 for uid in sorted(ids):
  for mode in ('remove','trim'):
   backup=P.read_bytes()
   result=subprocess.run([sys.executable,__file__,uid,mode],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
   if result.returncode or P.read_bytes()==backup:
    P.write_bytes(backup);continue
   rr=report()
   if okay(rr) and (mode=='remove' or len(rr['violations'])<count):
    print(mode,uid,'warnings',len(rr['violations']),flush=True);r=rr;improved=True;break
   P.write_bytes(backup)
  if improved:break
 if not improved:break
r=report();print('Remaining',len(r['violations']),'violations;',len(r['unconnected_items']),'opens',flush=True)
assert okay(r) and not r['violations']
