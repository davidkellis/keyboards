#!/usr/bin/python3
"""Prepare/import local Freerouting files; always run KiCad DRC afterward."""
import argparse,gc,sys,tempfile,shutil
import sexpdata as sx
from pathlib import Path
gc.disable()
import pcbnew as k
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'kicad/keyboard.kicad_pcb'
a=argparse.ArgumentParser();a.add_argument('operation',choices=('prepare','import'));a.add_argument('path',type=Path);args=a.parse_args()
temp=tempfile.TemporaryDirectory(prefix='v10-routing-')
seed=Path(temp.name)/'seed.kicad_pcb'
tree=sx.loads(P.read_text())
tree=[x for x in tree if not (isinstance(x,list) and str(x[0]) in ('segment','arc','via'))]
seed.write_text(sx.dumps(tree))
shutil.copyfile(P.with_suffix('.kicad_pro'),seed.with_suffix('.kicad_pro'))
b=k.LoadBoard(str(seed))
if args.operation=='prepare':
    assert k.ExportSpecctraDSN(b,str(args.path))
    s=args.path.read_text().replace('(clearance 45 (type smd_smd))','(clearance 180 (type smd_smd))')
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
    placements={f.GetReference():(f.GetPosition(),f.GetOrientationDegrees()) for f in b.GetFootprints()}
    assert k.ImportSpecctraSES(b,str(args.path))
    # DSN rounds to 0.1 um. Keep the source's exact switch/drill coordinates.
    for footprint in b.GetFootprints():
        pos,angle=placements[footprint.GetReference()]
        footprint.SetPosition(pos);footprint.SetOrientationDegrees(angle)
    # Freerouting may neck through-hole power routes down to 0.15 mm;
    # retain the carrier's 0.18 mm minimum and check clearance in KiCad.
    for track in b.GetTracks():
        if not isinstance(track,k.PCB_VIA) and track.GetWidth()<k.FromMM(.18):
            track.SetWidth(k.FromMM(.18))
    k.SaveBoard(str(P),b)
print(args.operation,args.path)
