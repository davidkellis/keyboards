#!/usr/bin/python3
"""Export checked fabrication/assembly data from the finished v7.3 PCB."""
from pathlib import Path
import csv, gc, hashlib, json, re, shutil, subprocess, sys, tempfile, zipfile
sys.excepthook=sys.__excepthook__;gc.disable()
import pcbnew as k

ROOT=Path(__file__).resolve().parents[1];K=ROOT/'kicad';O=ROOT/'manufacturing'
REV='v7.3'
P=K/'keyboard.kicad_pcb';G=O/'gerbers';G.mkdir(exist_ok=True)
def package_handoff():
    """Package existing validated exports, replacing the ZIP only on success."""
    manifest=json.loads((O/'manifest.json').read_text())
    assert manifest['revision']==REV
    for name,digest in manifest['source_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    target=O/f'tkl-{REV}-jlcpcb-handoff.zip'
    temporary=target.with_suffix('.zip.tmp')
    with zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED) as archive:
        for name in [f'tkl-{REV}-gerbers.zip','jlcpcb-bom.csv','jlcpcb-cpl.csv',
                     'FABRICATION.md','ORDERING.md','COST_REDUCTION.md','STACKUP.md','assembly-top.pdf',
                     'assembly-bottom.pdf','assembly-notes.csv','schematic.pdf','parts.json',
                     'pad-coordinates.csv','manifest.json',
                     'fabrication-estimate-six-layer-osp.txt','fabrication-estimate-settings.json']:
            archive.write(O/name,name)
        archive.write(ROOT/'BRINGUP.md','BRINGUP.md')
        for name in ['BATTERY.md','OWNED_PARTS.md']:
            archive.write(ROOT/'case'/name,name)
        audit=ROOT/'validation/revision-audit.json'
        if audit.exists():archive.write(audit,audit.name)
        for quote in sorted(O.glob('JLC_QUOTE_*.md')):
            archive.write(quote,quote.name)
    temporary.replace(target)
if sys.argv[1:]==['--package-only']:
    package_handoff()
    print('Packaged existing validated exports')
    sys.exit(0)
def run(*args):subprocess.run([str(a) for a in args],check=True)
def write_csv(path,headers,rows):
    with path.open('w',newline='') as stream:
        w=csv.writer(stream,lineterminator='\n');w.writerow(headers);w.writerows(rows)
def natural(ref):
    m=re.fullmatch(r'([A-Za-z]+)(\d+)',ref);return m[1],int(m[2])

run(sys.executable,ROOT/'scripts/validate.py')
run(sys.executable,ROOT/'scripts/audit_revision.py')
validation=json.loads((ROOT/'validation/summary.json').read_text())
assert not any(value for key,value in validation.items() if key not in ('numbered_pads','unique_keys')),validation
catalog=json.loads((O/'parts.json').read_text());groups=catalog['groups']
b=k.LoadBoard(str(P));assert b.GetCopperLayerCount()==6;footprints={f.GetReference():f for f in b.GetFootprints()}
parts={r:g for g in groups for r in g['refs']}
assert len(parts)==sum(len(g['refs']) for g in groups),'Duplicate assembly references'
assert parts.keys()==footprints.keys(),'Catalog does not cover exact board reference set'
fitted={r for r,g in parts.items() if g['assembly'] in ('SMT','THT-bottom')}
assert all(not footprints[r].IsDNP() for r in fitted)
assert all(footprints[r].GetLayer()==k.B_Cu for r in fitted)
assert fitted.isdisjoint({'C10','C13','R10','J2','FID1','FID2','FID3'})
assert len(fitted)==142
vias=[t for t in b.GetTracks() if isinstance(t,k.PCB_VIA)]
assert len(vias)==273
assert all(v.GetDrillValue()>=k.FromMM(.3) and v.GetWidth(k.F_Cu)>=k.FromMM(.45) for v in vias)
assert all(v.GetWidth(k.F_Cu)-v.GetDrillValue()>=k.FromMM(.15) for v in vias), 'POFV preferred 0.075 mm annular ring'

run('kicad-cli','pcb','export','gerbers','-o',G,'-l',
    'F.Cu,In1.Cu,In2.Cu,In3.Cu,In4.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,F.Paste,B.Paste,Edge.Cuts',
    '--use-drill-file-origin','--check-zones',P)
run('kicad-cli','pcb','export','drill','-o',G,'--excellon-separate-th',
    '--excellon-oval-format','route','--drill-origin','plot','--generate-map',
    '--map-format','pdf','--generate-report','--report-path',O/'drill-report.txt',P)
run('kicad-cli','pcb','export','pos','--format','csv','--units','mm','--side','both',
    '--use-drill-file-origin','--exclude-dnp','-o',O/'positions-kicad.csv',P)
with (O/'positions-kicad.csv').open() as stream:raw={r['Ref']:r for r in csv.DictReader(stream)}
assert fitted <= raw.keys(),fitted-raw.keys()
origin=b.GetDesignSettings().GetAuxOrigin()
positions=[]
for ref in sorted(fitted,key=natural):
    r=raw[ref];fp=footprints[ref]
    x=k.ToMM(fp.GetPosition().x-origin.x);y=k.ToMM(origin.y-fp.GetPosition().y)
    assert abs(float(r['PosX'])-x)<.0001 and abs(float(r['PosY'])-y)<.0001
    assert r['Side']==('bottom' if fp.GetLayer()==k.B_Cu else 'top')
    positions.append([ref,f'{x:.6f}',f'{y:.6f}',r['Side'].title(),r['Rot']])
write_csv(O/'jlcpcb-cpl.csv',['Designator','Mid X','Mid Y','Layer','Rotation'],positions)
bom=[]
for g in groups:
    if not set(g['refs'])<=fitted:continue
    assert g['mpn'] and re.fullmatch(r'C\d+',g['lcsc'])
    bom.append([g['mpn'],','.join(g['refs']),g['package'],g['lcsc'],len(g['refs']),g['manufacturer'],g['mpn']])
write_csv(O/'jlcpcb-bom.csv',['Comment','Designator','Footprint','LCSC Part #','Quantity','Manufacturer','Manufacturer Part Number'],bom)
write_csv(O/'assembly-notes.csv',['Designator','Assembly','Specification','Notes','Source'],
          [[','.join(g['refs']),g['assembly'],g['spec'],g['notes'],g['source']] for g in groups])
write_csv(O/'pad-coordinates.csv',['Designator','Pad','Net','X mm','Y mm'],
          [[r,p.GetNumber(),p.GetNetname(),f'{k.ToMM(p.GetPosition().x-origin.x):.6f}',
            f'{k.ToMM(origin.y-p.GetPosition().y):.6f}']
           for r in sorted(footprints,key=natural) for p in footprints[r].Pads() if p.GetNumber()])
matrix=[]
row_names=['ROW'+str(i) for i in list(range(8))+[9,10,11]]
for i in range(1,87):
    sw=footprints['SW'+str(i)];di=footprints['D'+str(i)]
    row=next(p.GetNetname() for p in di.Pads() if p.GetNumber()=='1')
    col=next(p.GetNetname() for p in sw.Pads() if p.GetNumber()=='1')
    matrix.append([sw.GetReference(),di.GetReference(),row,col,row_names.index(row),int(col[3:]),
                   f'{k.ToMM(sw.GetPosition().x-origin.x):.6f}',f'{k.ToMM(origin.y-sw.GetPosition().y):.6f}'])
write_csv(O/'matrix-map.csv',['Switch','Diode','Row net','Column net','Compact row','Column','X mm','Y mm'],matrix)

run('kicad-cli','sch','export','pdf','-o',O/'schematic.pdf',K/'keyboard.kicad_sch')
for side,layers in [('front','F.Cu,F.SilkS,Edge.Cuts'),('back','B.Cu,B.SilkS,Edge.Cuts')]:
    args=['kicad-cli','pcb','export','svg','--mode-single','--fit-page-to-board',
          '--exclude-drawing-sheet','--check-zones','-o',ROOT/(side+'.svg'),'-l',layers]
    if side=='back':args.append('--mirror')
    run(*args,P)
    preview=ROOT/(side+'.svg')
    preview.write_text('\n'.join(line.rstrip() for line in preview.read_text().splitlines())+'\n')
# Assembly-only copy reveals references on fabrication layers; source is untouched.
with tempfile.TemporaryDirectory(prefix='v7-assembly-') as td:
    drawing=Path(td)/'assembly.kicad_pcb'
    for f in b.GetFootprints():
        ref=f.Reference();ref.SetLayer(k.B_Fab if f.GetLayer()==k.B_Cu else k.F_Fab)
        ref.SetVisible(True);ref.SetTextSize(k.VECTOR2I(k.FromMM(.65),k.FromMM(.65)))
        ref.SetTextThickness(k.FromMM(.1));f.Value().SetVisible(False)
    k.SaveBoard(str(drawing),b)
    for side,layer in [('bottom','B.Fab'),('top','F.Fab')]:
        args=['kicad-cli','pcb','export','pdf','--mode-single','--black-and-white','--scale','0',
              '--sketch-pads-on-fab-layers','--crossout-DNP-footprints-on-fab-layers',
              '-o',O/f'assembly-{side}.pdf','-l',layer+',Edge.Cuts']
        if side=='bottom':args.append('--mirror')
        run(*args,drawing)

with zipfile.ZipFile(O/f'tkl-{REV}-gerbers.zip','w',zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(G.iterdir()):
        if path.suffix not in ('.pdf',):archive.write(path,path.name)
    archive.write(O/'FABRICATION.md','FABRICATION.md')
    archive.write(O/'STACKUP.md','STACKUP.md')
sources=[P,K/'keyboard.kicad_pro',K/'keyboard.kicad_dru',K/'keyboard.kicad_sch',
         K/'matrix.kicad_sch',K/'power.kicad_sch',O/'parts.json']
manifest={'kicad_version':subprocess.check_output(['kicad-cli','version'],text=True).strip(),
          'revision':REV,
          'copper_layers':6,'stackup':'JLC06161H-7628','surface_finish':'OSP','solder':'lead-free',
          'status':'Experimental prototype: hold production for stabilizer, keycap and battery fit validation',
          'fitted_components':len(fitted),'smt_components':sum(parts[r]['assembly']=='SMT' for r in fitted),
          'tht_components':sum(parts[r]['assembly']=='THT-bottom' for r in fitted),
          'validation':validation,
          'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}
(O/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
package_handoff()
print('Exported',len(bom),'BOM lines and',len(positions),'assembly placements')
