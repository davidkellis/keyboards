#!/usr/bin/python3
"""Prepare/import local Freerouting files; always run KiCad DRC afterward."""
import argparse,gc,sys,tempfile,shutil
import sexpdata as sx
from pathlib import Path
gc.disable()
import pcbnew as k
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'kicad/keyboard.kicad_pcb'
a=argparse.ArgumentParser();a.add_argument('operation',choices=('prepare','import'));a.add_argument('path',type=Path);args=a.parse_args()
temp=tempfile.TemporaryDirectory(prefix='v75-routing-')
seed=Path(temp.name)/'seed.kicad_pcb'
tree=sx.loads(P.read_text())
tree=[x for x in tree if not (isinstance(x,list) and str(x[0]) in ('segment','arc','via'))]
seed.write_text(sx.dumps(tree))
shutil.copyfile(P.with_suffix('.kicad_pro'),seed.with_suffix('.kicad_pro'))
b=k.LoadBoard(str(seed))
if args.operation=='prepare':
    assert k.ExportSpecctraDSN(b,str(args.path))
    s=args.path.read_text().replace('(clearance 45 (type smd_smd))','(clearance 180 (type smd_smd))')
    s=s.replace('  (structure\n','  (structure\n    (keepout antenna_top (rect F.Cu 360200 -102000 373000 -92000))\n    (keepout antenna_bottom (rect B.Cu 360200 -102000 373000 -92000))\n')
    # KiCad's DSN exporter omits oval optical drill keepouts. Reserve their
    # conservative bounding boxes on both layers, with the required hole gap.
    holes=[]
    for fp in b.GetFootprints():
        for pad in fp.Pads():
            drill=pad.GetDrillSize()
            if pad.GetAttribute()!=k.PAD_ATTRIB_NPTH or not drill.x or drill.x==drill.y:continue
            x,y=k.ToMM(pad.GetPosition().x),k.ToMM(pad.GetPosition().y)
            w,h=k.ToMM(drill.x),k.ToMM(drill.y)
            if round(pad.GetOrientationDegrees())%180:w,h=h,w
            for layer in ('F.Cu','B.Cu'):
                holes.append(f'(keepout optical_{fp.GetReference()}_{layer} (rect {layer} {(x-w/2-.2)*1000} {(-y-h/2-.2)*1000} {(x+w/2+.2)*1000} {(-y+h/2+.2)*1000}))')
    s=s.replace('  (structure\n','  (structure\n    '+'\n    '.join(holes)+'\n')
    args.path.write_text(s)
else:
    assert k.ImportSpecctraSES(b,str(args.path))
    k.SaveBoard(str(P),b)
print(args.operation,args.path)
