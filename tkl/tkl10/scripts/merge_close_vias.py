"""Remove redundant same-net vias only when DRC/connectivity improves."""
from pathlib import Path
import sexpdata as sx,json,subprocess
R=Path(__file__).resolve().parents[1];P=R/'kicad/keyboard.kicad_pcb';D=R/'validation/via-cleanup-drc.json'
def child(n,t):return next((x for x in n if isinstance(x,list) and str(x[0])==t),None)
def report():
 subprocess.run(['kicad-cli','pcb','drc','--format','json','-o',str(D),str(P)],stdout=subprocess.DEVNULL,check=True)
 return json.loads(D.read_text())
changes=[]
for iteration in range(20):
 r=report();issues=[v for v in r['violations'] if v['type']=='hole_to_hole']
 if not issues:break
 success=False
 for issue in issues:
  backup=P.read_bytes();tree=sx.loads(backup.decode())
  ids=[i['uuid'] for i in issue['items']]
  vias=[n for n in tree if isinstance(n,list) and str(n[0])=='via' and child(n,'uuid')[1] in ids]
  if len(vias)!=2 or child(vias[0],'net')!=child(vias[1],'net'):continue
  for via in vias:
   uid=child(via,'uuid')[1];candidate=[n for n in tree if n is not via]
   P.write_text(sx.dumps(candidate));after=report()
   if not after['unconnected_items'] and not any(v['severity']=='error' for v in after['violations']) and sum(v['type']=='hole_to_hole' for v in after['violations'])<len(issues):
    changes.append(uid);success=True;print('Removed redundant via',uid,flush=True);break
   P.write_bytes(backup)
  if success:break
 assert success,'A drilled-hole violation requires rerouting; no verified redundant via'
r=report();assert not r['unconnected_items'] and not any(v['type']=='hole_to_hole' or v['severity']=='error' for v in r['violations'])
(R/'validation/merged-vias.json').write_text(json.dumps(dict(removed_redundant_vias=changes,connectivity_preserved=True),indent=2)+'\n')
