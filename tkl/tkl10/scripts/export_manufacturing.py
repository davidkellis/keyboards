#!/usr/bin/python3
"""Export the checked prototype; factory order remains subject to stated holds."""
from pathlib import Path
import csv,gc,hashlib,json,re,subprocess,sys,tempfile,zipfile
gc.disable()
import pcbnew as k
ROOT=Path(__file__).resolve().parents[1];K=ROOT/'kicad';O=ROOT/'manufacturing';P=K/'keyboard.kicad_pcb'
def run(*args):subprocess.run([str(a) for a in args],check=True)
def write_csv(path,header,rows):
 with path.open('w',newline='') as f:
  w=csv.writer(f,lineterminator='\n');w.writerow(header);w.writerows(rows)
def natural(r):
 m=re.fullmatch(r'([A-Za-z_]+)(\d+)',r);return (m[1],int(m[2])) if m else (r,0)
run(sys.executable,ROOT/'scripts/validate.py')
run(sys.executable,ROOT/'scripts/audit_revision.py')
G=O/'gerbers';G.mkdir(exist_ok=True)
run('kicad-cli','pcb','export','gerbers','-o',G,'-l','F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,F.Paste,B.Paste,Edge.Cuts','--use-drill-file-origin','--check-zones',P)
run('kicad-cli','pcb','export','drill','-o',G,'--excellon-separate-th','--excellon-oval-format','route','--drill-origin','plot','--generate-map','--map-format','pdf',P)
run('kicad-cli','pcb','export','pos','--format','csv','--units','mm','--side','both','--use-drill-file-origin','--exclude-dnp','-o',O/'positions-kicad.csv',P)
with (O/'positions-kicad.csv').open() as f:raw={r['Ref']:r for r in csv.DictReader(f)}
cat=json.loads((O/'parts.json').read_text());parts={r:g for g in cat['groups'] for r in g['refs']}
fitted={r for r,g in parts.items() if g['assembly'] in ('SMT','THT-bottom')}
assert len(fitted)==102 and fitted<=raw.keys() and 'U1' not in fitted
b=k.LoadBoard(str(P));fp={f.GetReference():f for f in b.GetFootprints()};origin=b.GetDesignSettings().GetAuxOrigin()
rows=[]
for ref in sorted(fitted,key=natural):
 r=raw[ref];f=fp[ref]
 assert r['Side']=='bottom' and f.GetLayer()==k.B_Cu
 assert abs(float(r['PosX'])-k.ToMM(f.GetPosition().x-origin.x))<.0001
 assert abs(float(r['PosY'])-k.ToMM(origin.y-f.GetPosition().y))<.0001
 rows.append([ref,r['PosX'],r['PosY'],'Bottom',r['Rot']])
write_csv(O/'jlcpcb-cpl.csv',['Designator','Mid X','Mid Y','Layer','Rotation'],rows)
groups=[g for g in cat['groups'] if g['assembly'] in ('SMT','THT-bottom')]
write_csv(O/'jlcpcb-bom.csv',['Comment','Designator','Footprint','LCSC Part #','Quantity','Manufacturer','Manufacturer Part Number'],
 [[g['mpn'],','.join(g['refs']),g['package'],g['lcsc'],len(g['refs']),g['manufacturer'],g['mpn']] for g in groups])
write_csv(O/'assembly-notes.csv',['Designator','Assembly','Specification','Notes','Source'],
 [[','.join(g['refs']),g['assembly'],g['spec'],g['notes'],g['source']] for g in cat['groups']])
write_csv(O/'pad-coordinates.csv',['Designator','Pad','Net','X mm','Y mm'],
 [[r,p.GetNumber(),p.GetNetname(),f'{k.ToMM(p.GetPosition().x-origin.x):.6f}',f'{k.ToMM(origin.y-p.GetPosition().y):.6f}'] for r in sorted(fp,key=natural) for p in fp[r].Pads() if p.GetNumber()])
row_names=['ROW'+str(i) for i in [*range(8),9,10,11]];matrix=[]
for i in range(1,87):
 sw=fp['SW'+str(i)];d=fp['D'+str(i)]
 rn=next(p.GetNetname() for p in d.Pads() if p.GetNumber()=='1')
 cn=next(p.GetNetname() for p in sw.Pads() if p.GetNumber()=='1')
 matrix.append([sw.GetReference(),d.GetReference(),rn,cn,row_names.index(rn),int(cn[3:]),k.ToMM(sw.GetPosition().x-origin.x),k.ToMM(origin.y-sw.GetPosition().y)])
write_csv(O/'matrix-map.csv',['Switch','Diode','Row net','Column net','Compact row','Column','X mm','Y mm'],matrix)
run('kicad-cli','sch','export','pdf','-o',O/'schematic.pdf',K/'keyboard.kicad_sch')
for side,layers in [('front','F.Cu,F.SilkS,Edge.Cuts'),('back','B.Cu,B.SilkS,Edge.Cuts')]:
 args=['kicad-cli','pcb','export','svg','--mode-single','--fit-page-to-board','--exclude-drawing-sheet','--check-zones','-o',ROOT/(side+'.svg'),'-l',layers]
 if side=='back':args.append('--mirror')
 run(*args,P)
with tempfile.TemporaryDirectory(prefix='v10-assembly-') as td:
 for f in b.GetFootprints():
  ref=f.Reference();ref.SetLayer(k.B_Fab if f.GetLayer()==k.B_Cu else k.F_Fab);ref.SetVisible(True)
  ref.SetTextSize(k.VECTOR2I(k.FromMM(.65),k.FromMM(.65)));ref.SetTextThickness(k.FromMM(.1));f.Value().SetVisible(False)
 drawing=Path(td)/'assembly.kicad_pcb';k.SaveBoard(str(drawing),b)
 for side,layer in [('bottom','B.Fab'),('top','F.Fab')]:
  args=['kicad-cli','pcb','export','pdf','--mode-single','--black-and-white','--scale','0','--sketch-pads-on-fab-layers','-o',O/f'assembly-{side}.pdf','-l',layer+',Edge.Cuts']
  if side=='bottom':args.append('--mirror')
  run(*args,drawing)
with zipfile.ZipFile(O/'tkl-v10-gerbers.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(G.iterdir()):
  if p.suffix!='.pdf':z.write(p,p.name)
 for name in ('FABRICATION.md','ORDERING.md'):z.write(O/name,name)
sources=[*K.glob('*.kicad_pcb'),*K.glob('*.kicad_sch'),K/'keyboard.kicad_pro',K/'keyboard.kicad_dru',O/'parts.json']
manifest=dict(revision='v10',parent='v9.3 mechanics / v9.1 electrical',copper_layers=2,finish='lead-free HASL',solder='lead-free',
 status='Prototype; exact clone, cable, battery/charging, RF and mechanical verification pending',
 source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
 validation=json.loads((ROOT/'validation/summary.json').read_text()),jlc_bom_groups=len(groups),jlc_placements=len(fitted))
(O/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(O/'tkl-v10-prototype-handoff.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name in ('tkl-v10-gerbers.zip','jlcpcb-bom.csv','jlcpcb-cpl.csv','assembly-notes.csv','assembly-bottom.pdf','assembly-top.pdf','schematic.pdf','FABRICATION.md','ORDERING.md','manifest.json'):z.write(O/name,name)
 z.write(ROOT/'BRINGUP.md','BRINGUP.md')
print('Exported',len(groups),'BOM groups and',len(fitted),'bottom-side placements.')
