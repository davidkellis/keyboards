#!/usr/bin/python3
"""Derive a separate four-layer OSP revision from the fixed routed v7.2 PCB."""
from pathlib import Path
import gc, hashlib, json, sys
sys.excepthook=sys.__excepthook__;gc.disable()
import pcbnew as k
import sexpdata as sx

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT.parent/'tkl7/kicad/keyboard.kicad_pcb'
TARGET=ROOT/'kicad/keyboard.kicad_pcb'
assert ROOT.name=='tkl7.4' and SOURCE != TARGET
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='b3e4306501c04c6109a43bf4401a2a20836ebfe2fd93e6d52d637700bcefa449'
project=TARGET.with_suffix('.kicad_pro');project_bytes=project.read_bytes()
b=k.LoadBoard(str(SOURCE));assert b.GetCopperLayerCount()==4
# Retain the complete four-layer stack, every track/via, zone and footprint.
for fp in b.GetFootprints():
    if fp.GetReference()=='U1':fp.SetValue('nRF52840-QIAA-R')
    if fp.GetReference()=='J2':fp.SetValue('SWD_Solder_Wires_1V8')
title=b.GetTitleBlock();title.SetTitle('TKL v7.4 - four-layer OSP, bottom-side assembly');title.SetRevision('v7.4')
settings=b.GetDesignSettings();settings.m_CapVias=True;settings.m_FillVias=True
b.BuildConnectivity();k.SaveBoard(str(TARGET),b);project.write_bytes(project_bytes)

parts={ref:g for g in json.loads((ROOT/'manufacturing/parts.json').read_text())['groups'] for ref in g['refs']}
child=lambda n,tag:next(x for x in n if isinstance(x,list) and str(x[0])==tag)
tree=sx.loads(TARGET.read_text())
for fp in [x for x in tree if isinstance(x,list) and str(x[0])=='footprint']:
    props={x[1]:x for x in fp if isinstance(x,list) and str(x[0])=='property'}
    ref=props['Reference'][2]
    for name,key in [('Manufacturer','manufacturer'),('MPN','mpn'),('LCSC','lcsc'),('Assembly','assembly')]:
        props[name][2]=parts[ref][key]
stack=child(child(tree,'setup'),'stackup')
child(stack,'copper_finish')[1]='OSP'
TARGET.write_text(sx.dumps(tree).replace(') (',')\n(')+'\n')
check=k.LoadBoard(str(TARGET));assert check.GetCopperLayerCount()==4
assert check.GetDesignSettings().GetBoardThickness()==k.FromMM(1.6)
k.SaveBoard(str(TARGET),check);project.write_bytes(project_bytes)
print('Derived v7.4: original four-layer routing/stack, OSP, lead-free assembly metadata')
