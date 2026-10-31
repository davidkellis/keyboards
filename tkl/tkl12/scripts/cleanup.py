#!/usr/bin/env python3
"""Strip KiCad-reported dead ends in batches, rolling back any connectivity loss."""
from pathlib import Path
import subprocess,json,sexpdata as sx
R=Path(__file__).resolve().parents[1];P=R/'kicad/keyboard.kicad_pcb';D=R/'validation/cleanup-drc.json'
def report():
 subprocess.run(['kicad-cli','pcb','drc','--format','json','-o',str(D),str(P)],check=True,stdout=subprocess.DEVNULL)
 return json.loads(D.read_text())
def okay(r):return not r['unconnected_items'] and not any(v['severity']=='error' for v in r['violations'])
def tag(n):return str(n[0]) if isinstance(n,list) and n else ''
def field(n,t):return next((c for c in n if tag(c)==t),None)
def remove(ids):
 backup=P.read_bytes();tree=sx.loads(backup.decode())
 tree=[n for n in tree if not(tag(n) in ('segment','via') and field(n,'uuid')[1] in ids)]
 try:
  P.write_text(sx.dumps(tree));after=report()
 except BaseException:
  P.write_bytes(backup);raise
 if okay(after):return len(ids)
 P.write_bytes(backup)
 if len(ids)<2:return 0
 half=len(ids)//2;return remove(ids[:half])+remove(ids[half:])
for iteration in range(200):
 r=report();assert okay(r)
 ids={v['items'][0]['uuid'] for v in r['violations'] if v['type'] in ('track_dangling','via_dangling')}
 ids.update(v['items'][-1]['uuid'] for v in r['violations'] if v['type']=='holes_co_located')
 if not ids:break
 count=remove(sorted(ids));print('Removed',count,'warned copper items in pass',iteration,flush=True)
 if not count:break
r=report();assert okay(r);print('Remaining',len(r['violations']),'warnings',flush=True)
