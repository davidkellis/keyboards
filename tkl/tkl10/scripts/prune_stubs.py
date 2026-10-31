"""Remove dangling routing tails in checked batches, bisecting rejected batches."""
from pathlib import Path
import sexpdata as s,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'kicad/keyboard.kicad_pcb';D=ROOT/'validation/prune-drc.json'
def child(n,t):return next((x for x in n if isinstance(x,list) and str(x[0])==t),None)
def report():
 subprocess.run(['kicad-cli','pcb','drc','--refill-zones','--format','json','-o',str(D),str(P)],stdout=subprocess.DEVNULL,check=True)
 return json.loads(D.read_text())
def okay(d):return not d['unconnected_items'] and not any(e['severity']=='error' for e in d['violations'])
current=report();assert okay(current)
def remove_batch(ids):
 global current
 if not ids:return 0
 backup=P.read_bytes();tree=s.loads(backup.decode())
 candidate=[n for n in tree if not (isinstance(n,list) and str(n[0]) in ('segment','via') and child(n,'uuid') and child(n,'uuid')[1] in ids)]
 P.write_text(s.dumps(candidate));after=report()
 if okay(after):
  current=after;print('Pruned',len(ids),'dangling items;',len(after['violations']),'warnings',flush=True);return len(ids)
 P.write_bytes(backup)
 if len(ids)==1:return 0
 split=len(ids)//2
 return remove_batch(ids[:split])+remove_batch(ids[split:])
for iteration in range(4):
 ids=sorted({i['uuid'] for e in current['violations'] if e['type'] in ('track_dangling','via_dangling') for i in e['items']})
 if not ids or not remove_batch(ids):break
current=report();assert okay(current)
print('Remaining warnings:',len(current['violations']),flush=True)
