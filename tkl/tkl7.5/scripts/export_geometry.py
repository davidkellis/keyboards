#!/usr/bin/python3
"""Extract fit geometry from the routed PCB. Run with KiCad's system Python."""
import argparse
import gc
import hashlib
import json
import re
import sys
from pathlib import Path

sys.excepthook = sys.__excepthook__
gc.disable()
import pcbnew as k

p = argparse.ArgumentParser()
p.add_argument('revision', type=Path)
a = p.parse_args()
root = a.revision.resolve()
pcb = root / 'kicad/keyboard.kicad_pcb'
b = k.LoadBoard(str(pcb))
catalog = json.loads((root / 'manufacturing/parts.json').read_text())
config_path=Path(__file__).with_name('fit-config.json')
config=json.loads(config_path.read_text())
parts = {r: g for g in catalog['groups'] for r in g['refs']}
mm = k.ToMM
edge = [d for d in b.GetDrawings() if d.GetLayer() == k.Edge_Cuts]
points = [q for d in edge for q in (d.GetStart(), d.GetEnd())]
x0, x1 = min(mm(q.x) for q in points), max(mm(q.x) for q in points)
y0, y1 = min(mm(q.y) for q in points), max(mm(q.y) for q in points)
def xy(q): return [round(mm(q.x)-x0, 6), round(y1-mm(q.y), 6)]

switches, holes, components, pins = [], [], [], []
for f in sorted(b.GetFootprints(), key=lambda f: f.GetReference()):
    ref = f.GetReference()
    pos = xy(f.GetPosition())
    name = str(f.GetFPID().GetLibItemName())
    is_key = ref.startswith('SW') and ref != 'SW87'
    if is_key:
        match = re.search(r'_([\d.]+)u', name)
        assert match, name
        switches.append(dict(ref=ref, xy=pos, units=float(match[1]), rotation=f.GetOrientationDegrees()))
    for pad in f.Pads():
        size = pad.GetDrillSize()
        if not size.x: continue
        holes.append(dict(ref=ref, pad=pad.GetNumber(), xy=xy(pad.GetPosition()),
                          size=[mm(size.x), mm(size.y)], angle=pad.GetOrientationDegrees(),
                          plated=pad.GetAttribute() != k.PAD_ATTRIB_NPTH))
        if is_key and pad.GetNumber():
            pins.append(dict(ref=ref, xy=xy(pad.GetPosition()), diameter=.9, depth=1.7,
                             collar_diameter=mm(size.x)+.6))
        if ref in ('J1', 'J5'):
            pins.append(dict(ref=ref, xy=xy(pad.GetPosition()), diameter=.65, depth=1.8, top=True,
                             collar_diameter=mm(size.x)+.6))
    if is_key or f.IsDNP() or parts[ref]['assembly'] not in ('SMT', 'THT-bottom'): continue
    # Courtyard bounds include pads and installation allowance. These are deliberately
    # conservative envelopes, not an assertion of exact manufacturer body geometry.
    layer = k.B_CrtYd if f.GetLayer() == k.B_Cu else k.F_CrtYd
    graphics = [d for d in f.GraphicalItems() if d.GetLayer() == layer]
    if not graphics:
        layer = k.B_Fab if f.GetLayer() == k.B_Cu else k.F_Fab
        graphics = [d for d in f.GraphicalItems() if d.GetLayer() == layer]
    boxes = [d.GetBoundingBox() for d in graphics]
    if boxes:
        xmin=min(mm(bb.GetLeft()) for bb in boxes)-x0
        xmax=max(mm(bb.GetRight()) for bb in boxes)-x0
        ymin=y1-max(mm(bb.GetBottom()) for bb in boxes)
        ymax=y1-min(mm(bb.GetTop()) for bb in boxes)
    else:
        xmin,ymin=pos[0]-1.5,pos[1]-1.5
        xmax,ymax=pos[0]+1.5,pos[1]+1.5
    package=parts[ref]['package']
    height=1.5
    for token, h in [('0402',.7),('0603',1.0),('SOD-123',1.35),('SOT-23',1.2),('0805',1.45)]:
        if token in package: height=h
    if ref.startswith('LED'): height=1.2 if 'reverse' in package.lower() else .65
    height={'U1':1.0,'U2':1.1,'J1':8.0,'J5':8.0,'J3':3.4,'SW87':2.0,
            'J4':3.5,'X1':.9,'X2':1.0}.get(ref,height)
    if ref in ('J1','J5'): # mated PH housing; leads need additional bend space
        xmin,xmax=pos[0]-2.5,pos[0]+4.5
        ymin,ymax=pos[1]-3.0,pos[1]+2.2
    components.append(dict(ref=ref,mpn=parts[ref]['mpn'],side='bottom' if f.GetLayer()==k.B_Cu else 'top',
                           bounds=[round(v,6) for v in (xmin,ymin,xmax,ymax)],height=height,
                           envelope='conservative courtyard/body allowance; see mechanical README'))
# Module and purchased cable are user-installed; their envelopes are explicit
# design limits, not measurements or exact manufacturer solids.
def extra(ref,bounds,height,z_top=0):
    x,y,xx,yy=bounds
    components.append(dict(ref=ref,mpn='FIT ENVELOPE - VERIFY ACTUAL PART',side='bottom',
        bounds=[x-x0,y1-yy,xx-x0,y1-y],height=height,z_top=z_top,
        envelope='provisional maximum permitted envelope',user_installed=True))
m=config['module'];u=config['usb_extension']
module=next(f for f in b.GetFootprints() if f.GetReference()=='U1')
pad_by_number={p.GetNumber():p for p in module.Pads()}
cx=(mm(pad_by_number['28'].GetPosition().x)+mm(pad_by_number['12'].GetPosition().x))/2
cy=mm(module.GetPosition().y)
length=m['pcb_measured_length_width_mm'][0]
tip=cx-length/2-m['usb_socket_overhang_mm']
extra('U1',(tip,cy-m['model_width_with_allowance_mm']/2,cx+length/2,cy+m['model_width_with_allowance_mm']/2),
      m['model_total_thickness_limit_mm'],-m['mounting_gap_mm'])
pl,pw=u['male_housing_length_width_mm'];ph=u['male_model_thickness_limit_mm']
extra('USB_MALE',(tip-pl,cy-pw/2,tip,cy+pw/2),ph,-m['usb_axis_below_carrier_mm']+ph/2)
# Rear connector is mounted to the vertical case wall, not tilted with the PCB.
# Reserve the entire flange width for its full depth, conservatively covering
# the unspecified narrower body and flange depth. build_fit.py registers it.
rc=u['female_center_x_kicad_mm'];rw=u['female_flange_width_mm']
extra('USB_REAR',(rc-rw/2,20.0,rc+rw/2,20.0+u['female_body_depth_mm']),u['female_model_height_limit_mm'],-2.0)
components[-1]['case_mount']='rear_panel'
# Conservative rectangular route envelopes for a <=3 mm flexible cable.
for i,bounds in enumerate([(305.5,cy-1.5,tip-pl,cy+1.5),(305.5,46.0,308.5,cy),
                           (305.5,46.0,316.5,57.0),(313.5,46.0,rc,49.0)]):
    extra('CABLE'+str(i+1),bounds,3.0,-2.0)
extra('CABLE5',(rc-1.5,38.0,rc+1.5,46.0),3.0,-2.0)
components[-1]['case_mount']='rear_strain_relief_allowance'
out=root/'case';out.mkdir(exist_ok=True)
data=dict(source=str(pcb.relative_to(root)),source_sha256=hashlib.sha256(pcb.read_bytes()).hexdigest(),
          fit_config_sha256=hashlib.sha256(config_path.read_bytes()).hexdigest(),
          board=dict(width=x1-x0,depth=y1-y0,thickness=mm(b.GetDesignSettings().GetBoardThickness()),
                     kicad_bounds=[x0,y0,x1,y1]),switches=switches,holes=holes,components=components,pins=pins)
(out/'board-geometry.json').write_text(json.dumps(data,indent=2)+'\n')
print(root.name, len(switches),'switches,',len(holes),'drilled pads,',len(components),'component envelopes')
