#!/usr/bin/env python3
"""Remove warned dead copper with connectivity-checked rollback; tidy LED labels."""
from pathlib import Path
import subprocess,json,sexpdata as sx
R=Path(__file__).resolve().parents[1];P=R/'kicad/keyboard.kicad_pcb';D=R/'validation/cleanup-drc.json'
def report():
 subprocess.run(['kicad-cli','pcb','drc','--format','json','-o',str(D),str(P)],check=True,stdout=subprocess.DEVNULL)
 return json.loads(D.read_text())
def tag(n):return str(n[0]) if isinstance(n,list) and n else ''
def field(n,t):return next((c for c in n if tag(c)==t),None)
skipped=set()
for iteration in range(30):
 r=report();remove=set()
 for v in r['violations']:
  if v['type']=='holes_co_located':remove.add(v['items'][-1]['uuid'])
  if v['type'] in ['track_dangling','via_dangling']:remove.add(v['items'][0]['uuid'])
 candidates=remove-skipped
 if not candidates:break
 for uid in sorted(candidates):
  old=P.read_bytes();tree=sx.loads(old.decode())
  tree=[n for n in tree if not(tag(n) in ['segment','via'] and field(n,'uuid')[1]==uid)]
  P.write_text(sx.dumps(tree));after=report()
  if len(after['unconnected_items'])>len(r['unconnected_items']) or any(v['severity']=='error' for v in after['violations']):
   P.write_bytes(old);skipped.add(uid)
  else:
   print('Removed warned dead/duplicate item',uid);break
print('Remaining',[(v['type'],v['severity']) for v in report()['violations']])
