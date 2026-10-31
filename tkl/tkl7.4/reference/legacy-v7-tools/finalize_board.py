#!/usr/bin/python3
"""Apply fabrication metadata and assembly markings without changing routing."""
from pathlib import Path
import sys,gc,json
sys.excepthook=sys.__excepthook__;gc.disable()
import pcbnew as k
import sexpdata as sx
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'kicad/keyboard.kicad_pcb'
pro=P.with_suffix('.kicad_pro');settings=pro.read_bytes();b=k.LoadBoard(str(P));mm=k.FromMM
catalog=json.loads((ROOT/'manufacturing/parts.json').read_text())
parts={r:g for g in catalog['groups'] for r in g['refs']}
v=lambda x,y:k.VECTOR2I(mm(x),mm(y))
b.GetDesignSettings().SetAuxOrigin(v(27.03,149.19))
for f in b.GetFootprints():
 r=f.GetReference()
 if r.startswith('D') and r[1:].isdigit():f.SetValue('BAT46W')
 if r.startswith('FID'):f.SetAttributes(f.GetAttributes()|k.FP_EXCLUDE_FROM_BOM|k.FP_BOARD_ONLY)
 if r.startswith('LED'):
  f.SetValue('LTW-C230DS')
  f.SetFPID(k.LIB_ID('V7',r+'_LTW-C230DS_ReverseMount_Hole2.1x2.8'))
 if r in ('C10','C11','SW87'):
  # Original coupon silks overlap optional parts; switch actuator overhangs.
  for g in list(f.GraphicalItems()):
   if g.GetLayer()==k.B_SilkS:g.SetLayer(k.B_Fab)
 if r in ('J1','J5'):f.SetValue('B2B-PH-K-S(LF)(SN)')
 if r=='U1':f.SetValue('nRF52840-QIAA-R7')
 if r=='U2':f.SetValue('BQ24072RGTR')
 if str(f.GetFPID().GetLibNickname())=='V7':
  name=str(f.GetFPID().GetLibItemName());local=k.FOOTPRINT(f)
  if local.GetLayer()==k.B_Cu:local.Flip(local.GetPosition(),k.FLIP_DIRECTION_TOP_BOTTOM)
  local.SetOrientationDegrees(0);local.SetPosition(v(0,0));k.PCB_IO_KICAD_SEXPR().FootprintSave(str(ROOT/'kicad/footprints/V7.pretty'),local)
# Three global optical targets, kept clear of switch and connector footprints.
refs={f.GetReference() for f in b.GetFootprints()}
for r,x,y in [('FID1',30,22.5),('FID2',374.5,146),('FID3',30,146)]:
 if r in refs:continue
 f=k.FootprintLoad('/usr/share/kicad/footprints/Fiducial.pretty','Fiducial_1mm_Mask2mm')
 f.SetReference(r);f.SetValue('Fiducial');f.SetFPID(k.LIB_ID('Fiducial','Fiducial_1mm_Mask2mm'))
 b.Add(f);f.Flip(v(0,0),k.FLIP_DIRECTION_TOP_BOTTOM);f.SetPosition(v(x,y));f.Reference().SetVisible(False);f.Value().SetVisible(False)
 f.SetAttributes(f.GetAttributes()|k.FP_EXCLUDE_FROM_BOM|k.FP_BOARD_ONLY)
b.BuildConnectivity();k.SaveBoard(str(P),b);pro.write_bytes(settings)
# KiCad stackup follows JLCPCB's nominal 1.6 mm four-layer 7628 construction.
S=sx.Symbol
f=lambda tag,*args:[S(tag),*args]
def child(n,tag):return next((x for x in n if isinstance(x,list) and str(x[0])==tag),None)
t=sx.loads(P.read_text());setup=child(t,'setup');setup[:]=[x for x in setup if not (isinstance(x,list) and str(x[0])=='stackup')]
stack=f('stackup')
for name,typ,th in [('F.SilkS','Top Silk Screen',None),('F.Paste','Top Solder Paste',None),('F.Mask','Top Solder Mask',.01),('F.Cu','copper',.035),('dielectric 1','prepreg',.2104),('In1.Cu','copper',.0152),('dielectric 2','core',1.065),('In2.Cu','copper',.0152),('dielectric 3','prepreg',.2104),('B.Cu','copper',.035),('B.Mask','Bottom Solder Mask',.01),('B.Paste','Bottom Solder Paste',None),('B.SilkS','Bottom Silk Screen',None)]:
 layer=f('layer',name,f('type',typ))
 if th is not None:layer.append(f('thickness',th))
 if typ in ('prepreg','core'):layer.extend([f('material','FR4'),f('epsilon_r',4.4 if typ=='prepreg' else 4.6),f('loss_tangent',.02)])
 stack.append(layer)
stack.extend([f('copper_finish','ENIG'),f('dielectric_constraints',S('no'))]);setup.append(stack)
for fp in [x for x in t if isinstance(x,list) and str(x[0])=='footprint']:
 props={x[1]:x[2] for x in fp if isinstance(x,list) and str(x[0])=='property'}
 ref=props['Reference'];part=parts[ref]
 for name,key in [('Manufacturer','manufacturer'),('MPN','mpn'),('LCSC','lcsc'),('Assembly','assembly')]:
  fp[:]=[x for x in fp if not (isinstance(x,list) and x[:2]==[S('property'),name])]
  fp.append(f('property',name,part[key],f('at',0,0,0),f('layer','B.Fab'),f('hide',S('yes')),
              f('effects',f('font',f('size',1,1),f('thickness',.15)))))
P.write_text(sx.dumps(t).replace(') (',')\n(')+'\n')
print('Applied stackup, assembly fiducials and final part values')
