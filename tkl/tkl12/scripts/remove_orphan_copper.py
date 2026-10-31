#!/usr/bin/env python3
"""Remove DRC-reported isolated copper islands containing no component pads."""
from routing_geometry import *
import sexpdata as sx
R=Path(__file__).resolve().parents[1];P=R/'kicad/keyboard.kicad_pcb';D=R/'validation/orphan-drc.json'
def drc():
 subprocess.run(['kicad-cli','pcb','drc','--format','json','-o',str(D),str(P)],check=True,stdout=subprocess.DEVNULL)
 return json.loads(D.read_text())
def tag(n):return str(n[0]) if isinstance(n,list) and n else ''
removed=[]
for iteration in range(10):
 report=drc()
 if not report['unconnected_items']:break
 b=k.LoadBoard(str(P));obs,_=objects(b);lookup={o['uuid']:o for o in obs};remove=set()
 for pair in report['unconnected_items']:
  for item in pair['items']:
   o=lookup[item['uuid']];net=o['net']
   # Keep ground stitching and zone connectivity out of a trace-only graph.
   if not net or net=='GND':continue
   mine=[q for q in obs if q['net']==net];groups=components(mine)
   group=groups[next(i for i,q in enumerate(mine) if q['uuid']==o['uuid'])]
   connected=[q for i,q in enumerate(mine) if groups[i]==group]
   if not any(isinstance(q['item'],k.PAD) for q in connected):remove.update(q['uuid'] for q in connected)
 if not remove:break
 backup=P.read_bytes();tree=sx.loads(backup.decode())
 tree=[n for n in tree if not (tag(n) in ('segment','via') and next(v[1] for v in n if tag(v)=='uuid') in remove)]
 P.write_text(sx.dumps(tree));after=drc()
 if len(after['unconnected_items'])>=len(report['unconnected_items']) or any(v['severity']=='error' for v in after['violations']):
  P.write_bytes(backup);raise AssertionError('Orphan cleanup failed DRC; rolled back')
 removed.extend(sorted(remove));print('Removed',len(remove),'orphan copper items;',len(after['unconnected_items']),'opens')
(R/'validation/orphan-cleanup.json').write_text(json.dumps(dict(removed_uuids=removed),indent=2)+'\n')
assert not drc()['unconnected_items']
