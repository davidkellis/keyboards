#!/usr/bin/env python3
"""Diagnostic Choc V2 samples with the plate TOP 2.2 mm above the PCB."""
from pathlib import Path
import argparse,json
import cadquery as cq
from plate_geometry import stabilizer_apertures, switch_aperture

p=argparse.ArgumentParser();p.add_argument('revision',type=Path);a=p.parse_args()
out=a.revision/'case/stabilizer-test';out.mkdir(parents=True,exist_ok=True)
data=json.loads((a.revision/'case/board-geometry.json').read_text())
key=next(s for s in data['switches'] if s['units']==1)
def block(x,y,z,w,d,h):return cq.Workplane('XY').box(w,d,h,centered=False).translate((x,y,z)).val()
def export(s,name):
    assert s.isValid() and len(s.Solids())==1,(name,len(s.Solids()))
    cq.exporters.export(s,str(out/name),tolerance=.025)
def extrude_polys(geometry,z=-1,h=5):
    return cq.Compound.makeCompound([cq.Workplane('XY').polyline(list(g.exterior.coords)[:-1]).close().extrude(h).translate((0,0,z)).val() for g in (geometry.geoms if hasattr(geometry,'geoms') else [geometry])])
for name,width,span in [('2u',60.,23.8),('spacebar-6.25u',135.,100.)]:
    cx,cy=width/2,17.5
    board=block(0,0,0,width,35,1.6)
    for h in data['holes']:
        if h['ref']!=key['ref']:continue
        x,y=h['xy'];x+=cx-key['xy'][0];y+=cy-key['xy'][1]
        assert abs(h['size'][0]-h['size'][1])<1e-6
        board=board.cut(cq.Workplane('XY').circle(h['size'][0]/2).extrude(3).translate((x,y,-.5)).val())
    slots=extrude_polys(stabilizer_apertures(cx,cy,span))
    for thick in (1.2,1.5,1.6):
        supported=board
        gap=2.2-thick
        for x,y in [(0,0),(width-8,0),(0,31),(width-8,31)]:
            supported=supported.fuse(block(x,y,1.59,8,4,gap+.01))
        supported=supported.clean()
        plate=block(0,0,0,width,35,thick).cut(extrude_polys(switch_aperture(cx,cy)),slots).clean()
        export(plate,f'{name}-plate-{thick:.1f}mm.stl')
        export(supported,f'{name}-pcb-for-{thick:.1f}mm-plate.stl')
        if thick==1.5:
            relief=supported
            for x in (cx-span/2,cx+span/2):relief=relief.cut(block(x-4,cy-8,-1,8,16,4))
            export(relief.clean(),f'{name}-pcb-diagnostic-relief.stl')
            assembly=cq.Assembly(name=name+'-diagnostic')
            assembly.add(supported,name='PCB-with-0.7mm-supports',color=cq.Color(.1,.45,.25))
            assembly.add(plate.translate((0,0,2.3)),name='plate-top-2.2mm-above-PCB',color=cq.Color(.2,.5,.85))
            assembly.export(str(out/f'{name}-assembly.step'))
            if name=='2u':
                # Keep previous familiar filenames, but correct their reference plane.
                export(supported,'pcb-solid-under-stabilizers.stl')
                export(relief.clean(),'pcb-with-diagnostic-relief.stl')
        if name=='2u':export(plate,f'plate-{thick:.1f}mm.stl')
    if name=='2u':export(board.cut(slots).clean(),'pcb-as-mounting-plate-1.6mm.stl')
(out/'README.md').write_text('''# Print the small sample first

Both purchased stabilizer sets are **plate mount**. These diagnostic samples
use generic Cherry-style slots; Durock V3 and TX AP latch fit, body depth,
stem height and travel with Choc V2 still need a physical test. Low-profile
keycaps are the intended choice. A cross-shaped stem alone does not establish
compatibility.

**Height correction:** the old sample incorrectly put the plate UNDERSIDE
2.2 mm above the PCB. Kailh's drawing places the switch seating flange, hence
the plate TOP, 2.2 mm above the PCB. Discard earlier printed sample supports.
For a 1.5 mm plate the air gap is **0.7 mm**; for 1.2 / 1.6 mm plates it is
1.0 / 0.6 mm respectively. Each new PCB sample is paired with its thickness.

1. Print `2u-pcb-for-1.5mm-plate.stl` and `2u-plate-1.5mm.stl` at 100% in mm.
   Use 0.1 mm layers to obtain a measured 1.5 mm plate. Ream undersized drills;
   do not scale the entire model. The older generic filenames now contain
   this corrected 1.5 mm arrangement.
2. Clip in one purchased stabilizer pair. Try the matched 1.2 / 1.6 mm files
   if latch fit requires it. Test Durock and TX AP separately.
3. Assemble the plate on its four supports and insert a real Choc V2 switch.
   Its base must seat fully on the PCB while its flange rests on the plate.
4. Attach the actual low-profile 2u keycap. Press at centre and both ends;
   check full travel/return, skirt clearance and that the cap sits level.
5. If the housings or wire hit the solid PCB, try `2u-pcb-diagnostic-relief.stl`.
   Its 8 × 16 mm diagnostic openings are NOT production PCB cutouts. Tell us
   where contact occurs and how far the stabilizer protrudes beneath the PCB.
6. Repeat with the `spacebar-6.25u-*` sample and your actual 6.25u spacebar.
   Its stem span is provisionally 100 mm; 2u samples use 23.8 mm. The 7u wire
   does not match this keyboard's 6.25u spacebar layout.

A passing sample does not certify the full plate: check every wide key, cover,
wire path and all underside electronics before soldering all switches. The
full PCBs still have no stabilizer housing relief, and exact stabilizer solids
are not included in the CAD collision test. Mechanical release remains on hold.

`pcb-as-mounting-plate-1.6mm.stl` remains an optional lower-plane diagnostic:
it clips PLATE-MOUNT stabilizers into PCB-thickness material. It is not a
PCB-clip-in footprint and is not the full assembly's chosen mounting plane.

[Kailh PG1353 drawing](https://www.kailhswitch.com/Content/upload/pdf/202015927/PG135301D03.pdf)
shows the 2.2 mm flange offset and 6.4 mm flange-to-stem height (8.6 mm total).
[Cherry mounting drawing, page 4](https://www.smcelectronics.com/DOWNLOADS/CHERRYMX.PDF)
is the reference for the generic slots, with small diagnostic print allowances.
''')
print(a.revision.name,'corrected 2u and 6.25u coupons generated')
