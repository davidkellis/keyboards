#!/usr/bin/python3
"""Derive the module carrier placement from v7.4. Replaces this revision only."""
import copy, gc, hashlib, json, sys
from pathlib import Path
import sexpdata as sx
gc.disable()
import pcbnew as k

ROOT=Path(__file__).resolve().parents[1]; PARENT=ROOT.parent/'tkl7.4'; K=ROOT/'kicad'
S=sx.Symbol
def child(n,t):return next((x for x in n if isinstance(x,list) and str(x[0])==t),None)
def children(n,t):return [x for x in n if isinstance(x,list) and str(x[0])==t]
def f(t,*a):return [S(t),*a]
def mm(x):return k.FromMM(x)
def vec(x,y):return k.VECTOR2I(mm(x),mm(y))
source=PARENT/'kicad/keyboard.kicad_pcb'
preserved={str(p.relative_to(ROOT.parent)):hashlib.sha256(p.read_bytes()).hexdigest()
           for root in ('tkl7','tkl8','tkl7.3','tkl7.4') for p in (ROOT.parent/root).rglob('*')
           if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts and not p.name.endswith('.pyc')}
(ROOT/'reference/preserved-revisions.json').write_text(json.dumps(preserved,indent=2)+'\n')
pcb=sx.loads(source.read_text())
keep={'J1','SW87','Q1','R9',*[f'R{i}' for i in range(1,7)],*[f'LED{i}' for i in range(1,7)],
      *[f'D{i}' for i in range(1,87)],*[f'SW{i}' for i in range(1,87)],'FID1','FID2','FID3'}
out=[]
for item in pcb:
    if not isinstance(item,list):out.append(item);continue
    tag=str(item[0])
    if tag in ('segment','arc','via','zone','group'):continue
    if tag.startswith('gr_') and (child(item,'layer') or [None,None])[1]!='Edge.Cuts':continue
    if tag=='footprint':
        props={x[1]:x[2] for x in children(item,'property')}
        ref=props['Reference']
        if ref not in keep:continue
        for field in ('path','sheetname','sheetfile'):
            item[:]=[x for x in item if not (isinstance(x,list) and str(x[0])==field)]
    out.append(item)
pcb=out
layers=child(pcb,'layers');layers[:]=[x for x in layers if not isinstance(x,list) or not str(x[1]).startswith('In')]
stack=child(child(pcb,'setup'),'stackup')
stack[:]=[stack[0],f('layer','F.Cu',f('type','copper'),f('thickness',.035)),
          f('layer','dielectric 1',f('type','core'),f('thickness',1.53),f('material','FR4')),
          f('layer','B.Cu',f('type','copper'),f('thickness',.035)),f('copper_finish','OSP')]
child(pcb,'title_block')[:]=[S('title_block'),f('title','TKL v7.5 - module carrier; bottom assembly'),f('rev','v7.5')]
old=sx.loads((ROOT.parent/'tkl6/kicad/keyboard.kicad_pcb').read_text())
module=copy.deepcopy(next(x for x in children(old,'footprint') if x[1].startswith('MCU_nice_nano:')))
module[:]=[x for x in module if not (isinstance(x,list) and str(x[0]) in ('path','sheetname','sheetfile','zone','model'))]
child(module,'at')[1:]=[347.55,97.0,90]
# This is the historical v6 orientation; photograph agrees on edge and auxiliary GPIO.
for p in children(module,'pad'):
    pin=str(p[1]); net=child(p,'net')
    if pin in ('3','4','23','28'): net[-1]='GND'
    if pin in ('24','29'):net[-1]='BAT_SW'
    if pin=='21':net[-1]='VCC'
pcb.append(module)
(K/'keyboard.kicad_pcb').write_text(sx.dumps(pcb))
b=k.LoadBoard(str(K/'keyboard.kicad_pcb'));b.SetCopperLayerCount(2)
b.GetDesignSettings().m_FillVias=False
b.GetDesignSettings().m_CapVias=False
def net(n):
    item=b.FindNet(n)
    if not item:item=k.NETINFO_ITEM(b,n);b.Add(item)
    return item
for fp in b.GetFootprints():
    ref=fp.GetReference()
    for pad in fp.Pads():
        if ref=='SW87':pad.SetNet(net({'1':'VBAT','2':'BAT_SW'}.get(pad.GetNumber(),pad.GetNetname())))
        if ref.startswith('R') and ref not in ('R9',) and pad.GetNetname()=='VDDH':pad.SetNet(net('VCC'))
    fp.Reference().SetVisible(False);fp.Value().SetVisible(False)
    if ref=='U1':fp.SetAttributes(k.FP_THROUGH_HOLE|k.FP_EXCLUDE_FROM_POS_FILES|k.FP_EXCLUDE_FROM_BOM)
    if ref in ('U1','SW42','SW49','SW50'):
        for graphic in list(fp.GraphicalItems()):
            if graphic.GetLayer() in (k.F_SilkS,k.B_SilkS):
                graphic.SetLayer(k.B_Fab if graphic.GetLayer()==k.B_SilkS else k.F_Fab)
        library=K/'footprints/V75.pretty';library.mkdir(exist_ok=True)
        name=ref+'_'+str(fp.GetFPID().GetLibItemName())
        fp.SetFPID(k.LIB_ID('V75',name));k.PCB_IO_MGR.FindPlugin(k.PCB_IO_MGR.KICAD_SEXP).FootprintSave(str(library),fp)
    # All plated pin connections receive annular lands on both copper layers.
    # No via-in-pad is needed anywhere on this carrier.
# Clear copper below/beyond the antenna end of the module. No RF trace on carrier.
for layer in (k.F_Cu,k.B_Cu):
    z=k.ZONE(b);z.SetLayer(layer);z.SetIsRuleArea(True)
    z.SetDoNotAllowZoneFills(True);z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True)
    z.SetDoNotAllowPads(True);z.SetDoNotAllowFootprints(False)
    p=z.Outline();p.NewOutline()
    for x,y in [(360.2,92),(373.0,92),(373.0,102),(360.2,102)]:p.Append(mm(x),mm(y))
    b.Add(z)
k.SaveBoard(str(K/'keyboard.kicad_pcb'),b)
pro=json.loads((PARENT/'kicad/keyboard.kicad_pro').read_text())
nc=pro['net_settings']['classes'][0];nc.update(clearance=.18,track_width=.2,via_diameter=.6,via_drill=.3)
rules=pro['board']['design_settings']['rules'];rules.update(min_clearance=.18,min_track_width=.18,min_via_diameter=.6,min_via_annular_width=.15)
pro['board']['design_settings']['drc_exclusions']=[]
(K/'keyboard.kicad_pro').write_text(json.dumps(pro,indent=2)+'\n')
(K/'keyboard.kicad_dru').write_text('(version 1)\n(rule "Perimeter clearance" (condition "A.FootprintReference != \'LED*\'") (constraint edge_clearance (min 0.5mm)))\n')
table=(PARENT/'kicad/fp-lib-table').read_text()
table=table[:table.rfind(')')]+' (lib (name "V75")(type "KiCad")(uri "${KIPRJMOD}/footprints/V75.pretty")(options "")(descr "v7.5 module and silk-clearance variants"))\n)\n'
(K/'fp-lib-table').write_text(table)
cat=json.loads((PARENT/'manufacturing/parts.json').read_text()); groups=[]
for group in cat['groups']:
    group=copy.deepcopy(group);group['refs']=[r for r in group['refs'] if r in keep]
    if group['refs']==['SW87']:group['notes']='Battery isolation: both charging and discharge pass through the 300 mA contacts. Never enable 500 mA charge boost.'
    if group['refs']==['J1']:group['notes']='Body on bottom; pin 1 battery positive, pin 2 ground. No carrier cell-NTC connector.'
    if group['refs']==[f'R{i}' for i in range(1,7)]:group['notes']='Conservative initial LED current from module switched 3.3 V. Measure before changing resistance.'
    if group['refs'] and group['refs'][0]=='D1':group['notes']='Retained BAT46W footprint and polarity. Validate matrix scan/leakage with the 3.3 V module.'
    if group['refs']:groups.append(group)
groups.append(dict(refs=['U1'],package='ProMicro-nRF52840-29-pad',manufacturer='TENSTAR ROBOT / exact clone to verify',
    mpn='ProMicro NRF52840 clone',lcsc='',spec='21 exposed GPIO; integrated USB, BLE and charger',assembly='User-installed',
    notes='v6 footprint, underside; exact clone dimensions and charging must be verified. No tall sockets.',
    source='User photograph 2026-09-25; https://nicekeyboards.com/docs/nice-nano/pinout-schematic/'))
cat.update(groups=groups,notes='v7.5 carrier: retained v7.4 switches, matrix diodes and backlight. Module is installed by user. Charger is on module; no carrier BQ24072/NTC circuit.')
(ROOT/'manufacturing/parts.json').write_text(json.dumps(cat,indent=2)+'\n')
print('Built',len(list(b.GetFootprints())),'footprints, two copper layers; module at 347.55,97.0 / 90 degrees.')
