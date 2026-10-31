#!/usr/bin/python3
"""Derive v7.3 from the immutable, fully routed v7.2 board; never edit the parent.

This is a deliberate rebuild of this revision's PCB, not an incremental edit.
Run build_schematic.py, sync_nc_nets.py, validation and export afterward.
"""
from pathlib import Path
import gc, hashlib, json, sys
sys.excepthook = sys.__excepthook__
gc.disable()
import pcbnew as k
import sexpdata as sx

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT.parent / 'tkl7'
SOURCE = BASE / 'kicad/keyboard.kicad_pcb'
TARGET = ROOT / 'kicad/keyboard.kicad_pcb'
assert ROOT.name == 'tkl7.3' and TARGET != SOURCE
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == 'b3e4306501c04c6109a43bf4401a2a20836ebfe2fd93e6d52d637700bcefa449'
project_bytes = TARGET.with_suffix('.kicad_pro').read_bytes()
b = k.LoadBoard(str(SOURCE))
assert b.GetCopperLayerCount() == 4

# Keep both outer-to-adjacent-layer distances unchanged. The original In2
# signal/ground layer becomes In4; two new ground planes occupy the core.
b.SetCopperLayerCount(6)
layers = b.GetEnabledLayers()
for layer in (k.In1_Cu, k.In2_Cu, k.In3_Cu, k.In4_Cu):
    layers.AddLayer(layer)
b.SetEnabledLayers(layers)
for track in b.GetTracks():
    if not isinstance(track, k.PCB_VIA) and track.GetLayer() == k.In2_Cu:
        track.SetLayer(k.In4_Cu)
for zone in list(b.Zones()):
    if zone.GetLayer() == k.In2_Cu:
        zone.SetLayer(k.In4_Cu)

# Replicate the existing In1 ground zones AND RF copper exclusion on each
# new plane. Never put a new plane beneath the Nordic antenna match/feed.
templates = [z for z in b.Zones() if z.GetLayer() == k.In1_Cu]
assert len(templates) == 3 and sum(z.GetIsRuleArea() for z in templates) == 1
for layer in (k.In2_Cu, k.In3_Cu):
    for template in templates:
        zone = k.ZONE(template)
        zone.SetUuid(k.KIID())
        zone.SetLayer(layer)
        zone.UnFill()
        b.Add(zone)
for zone in b.Zones():
    if not zone.GetIsRuleArea():
        zone.UnFill()

catalog = json.loads((ROOT/'manufacturing/parts.json').read_text())
parts = {ref: group for group in catalog['groups'] for ref in group['refs']}
for fp in b.GetFootprints():
    ref = fp.GetReference()
    if ref == 'U1':
        fp.SetValue('nRF52840-QIAA-R')
    if ref == 'J2':
        fp.SetValue('SWD_Solder_Wires_1V8')
title = b.GetTitleBlock()
title.SetTitle('TKL v7.3 - six-layer OSP, bottom-side assembly')
title.SetRevision('v7.3')
settings = b.GetDesignSettings()
settings.SetBoardThickness(k.FromMM(1.6))
settings.m_CapVias = True
settings.m_FillVias = True
b.BuildConnectivity()
k.SaveBoard(str(TARGET), b)
TARGET.with_suffix('.kicad_pro').write_bytes(project_bytes)

# JLC06161H-7628: manufacturer-published nominal construction. The finished
# board remains nominal 1.6 mm; constituent figures are not a custom stack.
S = sx.Symbol
node = lambda tag, *args: [S(tag), *args]
child = lambda parent, tag: next(x for x in parent if isinstance(x,list) and str(x[0]) == tag)
tree = sx.loads(TARGET.read_text())
for fp in [x for x in tree if isinstance(x,list) and str(x[0]) == 'footprint']:
    props = {x[1]:x for x in fp if isinstance(x,list) and str(x[0]) == 'property'}
    ref = props['Reference'][2]
    for name, key in [('Manufacturer','manufacturer'),('MPN','mpn'),('LCSC','lcsc'),('Assembly','assembly')]:
        props[name][2] = parts[ref][key]
setup = child(tree, 'setup')
setup[:] = [x for x in setup if not (isinstance(x,list) and str(x[0]) == 'stackup')]
stack = node('stackup')
construction = [
    ('F.SilkS','Top Silk Screen',None), ('F.Paste','Top Solder Paste',None),
    ('F.Mask','Top Solder Mask',.01), ('F.Cu','copper',.035),
    ('dielectric 1','prepreg',.2104), ('In1.Cu','copper',.0152),
    ('dielectric 2','core',.4), ('In2.Cu','copper',.0152),
    ('dielectric 3','prepreg',.2028), ('In3.Cu','copper',.0152),
    ('dielectric 4','core',.4), ('In4.Cu','copper',.0152),
    ('dielectric 5','prepreg',.2104), ('B.Cu','copper',.035),
    ('B.Mask','Bottom Solder Mask',.01), ('B.Paste','Bottom Solder Paste',None),
    ('B.SilkS','Bottom Silk Screen',None),
]
for name, kind, thickness in construction:
    layer = node('layer', name, node('type',kind))
    if thickness is not None:
        layer.append(node('thickness',thickness))
    if kind in ('prepreg','core'):
        layer.extend([node('material','FR4'), node('epsilon_r',4.4 if kind == 'prepreg' else 4.6), node('loss_tangent',.02)])
    stack.append(layer)
stack.extend([node('copper_finish','OSP'),node('dielectric_constraints',S('no'))])
setup.append(stack)
TARGET.write_text(sx.dumps(tree).replace(') (',')\n(')+'\n')
# Normalize the output without asking the placer/router to recreate copper.
check = k.LoadBoard(str(TARGET))
assert check.GetCopperLayerCount() == 6
assert check.GetDesignSettings().GetBoardThickness() == k.FromMM(1.6)
k.SaveBoard(str(TARGET),check)
TARGET.with_suffix('.kicad_pro').write_bytes(project_bytes)
print('Derived six-layer OSP v7.3; old signal copper moved from In2 to In4.')
