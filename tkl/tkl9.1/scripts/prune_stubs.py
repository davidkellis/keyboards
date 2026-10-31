from pathlib import Path
import sexpdata as s,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'kicad/keyboard.kicad_pcb';D=ROOT/'validation/prune-drc.json'
def c(n,t):return next((x for x in n if isinstance(x,list) and str(x[0])==t),None)
for iteration in range(10):
 subprocess.run(['kicad-cli','pcb','drc','--refill-zones','--format','json','-o',str(D),str(P)],stdout=subprocess.DEVNULL,check=True)
 d=json.loads(D.read_text());ids={i['uuid'] for e in d['violations'] if e['type'] in ('track_dangling','via_dangling') for i in e['items']}
 if not ids:break
 tree=s.loads(P.read_text());backup=P.read_bytes();candidate=[n for n in tree if not (isinstance(n,list) and c(n,'uuid') and c(n,'uuid')[1] in ids)]
 P.write_text(s.dumps(candidate));subprocess.run(['kicad-cli','pcb','drc','--refill-zones','--format','json','-o',str(D),str(P)],stdout=subprocess.DEVNULL,check=True)
 after=json.loads(D.read_text());errors=[e for e in after['violations'] if e['severity']=='error']
 if after['unconnected_items'] or errors:P.write_bytes(backup);print('Batch requires trimming:',len(ids),'opens',len(after['unconnected_items']),flush=True);break
 print('Pruned',len(ids),'dangling items',flush=True)
