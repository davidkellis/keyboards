#!/usr/bin/env python3
"""Build board-derived, millimetre fit models with CadQuery (see README)."""
import argparse
import hashlib
import json
import math
from pathlib import Path

import cadquery as cq
from shapely.geometry import Point, LineString, box, Polygon
from shapely.ops import unary_union
from shapely.affinity import rotate
from plate_geometry import stabilizer_apertures, switch_aperture
from fit_preview import export_previews
from usb_surround import make_surround

p=argparse.ArgumentParser()
p.add_argument('revision',type=Path)
a=p.parse_args()
root=a.revision.resolve();out=root/'case'
d=json.loads((out/'board-geometry.json').read_text())
assert d['source_sha256']==hashlib.sha256((root/d['source']).read_bytes()).hexdigest(), 'Re-export PCB geometry first'
B=d['board'];W=B['width'];D=B['depth'];T=B['thickness']
config_path=Path(__file__).with_name('fit-config.json')
config=json.loads(config_path.read_text())
assert d['fit_config_sha256']==hashlib.sha256(config_path.read_bytes()).hexdigest(), 'Re-export geometry after fit configuration changes'
(out/'fit-config.json').write_text(config_path.read_text())
M=2.4;WALL=2.;FLOOR=1.2
PLATE_T=config['plate_thickness_mm'];PLATE_TOP=T+config['plate_top_above_pcb_mm']
PLATE_BOTTOM=PLATE_TOP-PLATE_T
GAP=config['plate_top_above_pcb_mm']+config['cover_gap_above_plate_mm']
COVER_T=config['cover_thickness_mm'];FRONT=config['front_lip_mm'];REAR=config['rear_lip_mm']
assert [FRONT,REAR]==config['fixed_lips_mm'], 'Preserve the user-specified assembled case/cover heights'
# Solve the tilt so both specified lip heights are true world-coordinate heights.
lo,hi=0.,.3
for _ in range(60):
    ang=(lo+hi)/2
    if D*math.sin(ang)+2*M*math.tan(ang)<REAR-FRONT:lo=ang
    else:hi=ang
C=math.cos(ang);S=math.sin(ang);slope=math.tan(ang)
CW=W+2*M;CD=D*C+2*M;Z0=FRONT+M*slope-(T+GAP+COVER_T)/C
assert all(abs(actual-fixed)<1e-5 for actual,fixed in zip((CW,CD),config['fixed_footprint_mm'])), 'Preserve the user-specified footprint'
degrees=math.degrees(ang)
def block(x,y,z,w,dep,h):
    return cq.Workplane('XY').box(w,dep,h,centered=False).translate((x,y,z)).val()
def prism(points,z,h):
    return cq.Workplane('XY').polyline(points).close().extrude(h).translate((0,0,z)).val()
def compound(shapes):return cq.Compound.makeCompound(shapes)
def overlap_volume(left,right):
    a=left.BoundingBox();b=right.BoundingBox()
    if any(getattr(a,axis+'max')<=getattr(b,axis+'min') or getattr(b,axis+'max')<=getattr(a,axis+'min') for axis in ('x','y','z')):
        return 0.0
    return left.intersect(right).Volume()
def polygon_solid(poly,z,h):
    pieces=[]
    for poly in (list(poly.geoms) if hasattr(poly,'geoms') else [poly]):
        s=prism(list(poly.exterior.coords)[:-1],z,h)
        for ring in poly.interiors:s=s.cut(prism(list(ring.coords)[:-1],z-.1,h+.2))
        pieces.append(s)
    return compound(pieces)
def place(shape):return shape.rotate((0,0,0),(1,0,0),degrees).translate((M,M,Z0))
def unplace(shape):return shape.translate((-M,-M,-Z0)).rotate((0,0,0),(1,0,0),-degrees)
def plane_z(y,z=0):return Z0+(y-M)*slope+z/C
def under_plane(z):
    return cq.Workplane('YZ').polyline([(-5,-10),(CD+5,-10),(CD+5,plane_z(CD+5,z)),(-5,plane_z(-5,z))]).close().extrude(CW+10).translate((-5,0,0)).val()
def flat_export(shape,name):
    # These files are individually placed on the print bed; assembly STEP retains coordinates.
    bb=shape.BoundingBox();s=shape.translate((-bb.xmin,-bb.ymin,-bb.zmin))
    cq.exporters.export(s,str(out/name),tolerance=.035,angularTolerance=.15)
    return s

print('Board drills and split seam',flush=True)
holes=[];hole_geoms=[]
for h in d['holes']:
    x,y=h['xy'];w,dep=h['size'];angle=h['angle']
    if abs(w-dep)<1e-6:
        q=cq.Workplane('XY').circle(w/2).extrude(T+2).translate((x,y,-1)).val()
        g=Point(x,y).buffer(w/2)
    else:
        q=cq.Workplane('XY').slot2D(max(w,dep),min(w,dep),angle+(90 if dep>w else 0)).extrude(T+2).translate((x,y,-1)).val()
        delta=abs(w-dep)/2
        g=LineString([(x-delta,y),(x+delta,y)] if w>dep else [(x,y-delta),(x,y+delta)]).buffer(min(w,dep)/2)
        g=rotate(g,angle,origin=(x,y))
    holes.append(q);hole_geoms.append((g,h['ref']))
board=block(0,0,0,W,D,T).cut(*holes).clean()
assert len(board.Solids())==1 and board.isValid()
# Each row's seam is between entire switch bodies, including every switch pin.
rows=sorted(set(round(s['xy'][1],4) for s in d['switches']))
seam=[]
for i,y in enumerate(rows):
    xs=sorted(s['xy'][0] for s in d['switches'] if abs(s['xy'][1]-y)<.01)
    candidates=[(l+r)/2 for l,r in zip(xs,xs[1:]) if r-l>18]
    x=min(candidates,key=lambda x:abs(x-W/2))
    low=0 if i==0 else (rows[i-1]+y)/2
    high=D if i==len(rows)-1 else (rows[i+1]+y)/2
    seam.extend([(x,low),(x,high)])
seamline=LineString(seam)
assert all(seamline.distance(g)>.6 for g,r in hole_geoms if r.startswith('SW')), 'Seam crosses a switch drill'
# Extend split masks beyond the outline and below the tallest connector so the
# populated halves retain the complete USB/switch overhang and JST housings.
leftpoly=Polygon([(-10,-10),(seam[0][0],-10)]+seam+[(seam[-1][0],D+10),(-10,D+10)])
rightpoly=box(-10,-10,W+10,D+10).difference(leftpoly)
halves=[polygon_solid(poly,-20,50) for poly in (leftpoly,rightpoly)]
flat_export(board,'pcb-bare.stl')
for label,half in zip(('left','right'),halves):flat_export(board.intersect(half),f'pcb-{label}.stl')
cq.exporters.export(board,str(out/'pcb-bare.step'))

print('Component and pin envelopes',flush=True)
component_shapes=[];obstacles=[];bottom_parts=[];case_mounted_components=[]
for c in d['components']:
    x,y,xx,yy=c['bounds'];h=c['height']
    z=c.get('z_top',0)-h if c['side']=='bottom' else T-.03
    shape=block(x,y,z,xx-x,yy-y,h+.03)
    component_shapes.append((c['ref'],shape,c['side']))
    if c['side']=='bottom':
        obstacles.append(box(x,y,xx,yy).buffer(.6))
        bottom_parts.append((c['ref'],place(shape)))
pin_shapes=[]
for pin in d['pins']:
    x,y=pin['xy'];h=pin['depth'];top=pin.get('top',False)
    shape=cq.Workplane('XY').circle(pin['diameter']/2).extrude(h+.05).translate((x,y,T-.05 if top else -h)).val()
    # A solder allowance also joins printed pin gauges to the board around the drill.
    collar=cq.Workplane('XY').circle(pin['collar_diameter']/2).extrude(.28).translate((x,y,T-.03 if top else -.25)).val()
    shape=shape.fuse(collar)
    pin_shapes.append(shape)
    if not top:bottom_parts.append((pin['ref']+' pin',place(shape)))
# Fast fused STL for a physical envelope mock-up; bare PCB lets real switches be inserted.
# Print only board-mounted electronics as a connected PCB gauge.
mounted=[s for ref,s,side in component_shapes if ref not in ('U1','USB_SOCKET','USB_PLUG_EXTERNAL')]
populated=board.fuse(*mounted,*pin_shapes).clean()
assert populated.isValid()
flat_export(populated,'pcb-populated.stl')
pop_halves=[populated.intersect(half) for half in halves]
assert abs(sum(s.Volume() for s in pop_halves)-populated.Volume())<.001, 'Split masks truncated populated PCB'
for label,shape in zip(('left','right'),pop_halves):flat_export(shape,f'pcb-populated-{label}.stl')
pcb_asm=cq.Assembly(name=root.name+'-pcb')
pcb_asm.add(board,name='FR4',color=cq.Color(.13,.38,.19))
for ref,s,side in component_shapes:pcb_asm.add(s,name=ref,color=cq.Color(.75,.7,.35) if ref.startswith('LED') else cq.Color(.2,.2,.22))
for i,s in enumerate(pin_shapes):pcb_asm.add(s,name=f'pin-{i}',color=cq.Color(.6,.6,.6))
pcb_asm.export(str(out/'pcb-populated.step'))

print('Case, safe ledge and supports',flush=True)
# A vertical-walled wedge with a truly flat floor. Cover and base have flush outer edges.
case=block(0,0,0,CW,CD,30).intersect(under_plane(T+GAP-.12))
cavity=block(WALL,WALL,FLOOR,CW-2*WALL,CD-2*WALL,40)
case=case.cut(cavity)
ledge_region=box(WALL,WALL,CW-WALL,CD-WALL).difference(box(M+1.3,M+1.3,CW-M-1.3,CD-M-1.3))
ledge=polygon_solid(ledge_region,FLOOR,25).intersect(under_plane(0))
# Clear every underside envelope from perimeter ledges, including the rear connectors.
clear_shapes=[]
for c in d['components']:
    if c['side']!='bottom':continue
    x,y,xx,yy=c['bounds']
    clear_shapes.append(place(block(x-.65,y-.65,-20,xx-x+1.3,yy-y+1.3,22)))
ledge=ledge.cut(*clear_shapes)
# This box includes provisional growth/assembly room, not just nominal cell size.
bat=config['battery'];battery_dims=bat['reserved_dimensions_mm'];BX,BY=bat['origin_xy_case_mm']
pack_dims=bat['pack_max_dimensions_mm']
assert all(0 < pack < reserve for pack,reserve in zip(pack_dims,battery_dims))
reserve_gauge='battery-reserve-gauge-'+'x'.join(f'{v:g}' for v in battery_dims)+'.stl'
pack_gauge='battery-pack-max-gauge-'+'x'.join(f'{v:g}' for v in pack_dims)+'.stl'
BZ=FLOOR+bat['padding_below_mm']
battery=block(BX,BY,BZ,*battery_dims)
# The wider bay reaches under the rear PCB ledge. Leave a tunnel under that
# ledge, connected above the battery to the rear wall, with 0.4 mm separation.
# The outer wall, floor and ledge's PCB seating surface remain intact.
ledge=ledge.cut(block(BX-.4,BY-.4,FLOOR,battery_dims[0]+.8,battery_dims[1]+.8,
                      BZ+battery_dims[2]+.4-FLOOR))
# Convert the world-space bay to a conservative board-space support exclusion.
battery_reserve=box(BX-M-3,(BY-M)/C-3,BX-M+battery_dims[0]+3,(BY-M+battery_dims[1]+2)/C+3)
forbidden=unary_union(obstacles+[g.buffer(.65) for g,r in hole_geoms]+[battery_reserve])
bosses=[];boss_locations=[]
for y in [9,34,59,84,109,124]:
    for x in [12,57,102,147,192,237,282,327,342]:
        if not Point(x,y).buffer(2.6).disjoint(forbidden):continue
        X,Y=M+x,M+y*C
        boss=cq.Workplane('XY').circle(2.6).extrude(25).translate((X,Y,FLOOR-.05)).val().intersect(under_plane(0))
        if boss.Volume()>3:bosses.append(boss);boss_locations.append([x,y])
case=case.fuse(ledge,*bosses).clean()
# Low locating corners mark the reserved bay without clamping the pouch.
# Retention adhesive and its material/temperature rating remain a pack-specific choice.
locators=[]
for x,sx in [(BX-.7,-1),(BX+battery_dims[0]+.7,1)]:
    for y,sy in [(BY-.7,-1),(BY+battery_dims[1]+.7,1)]:
        locators.extend([block(x-1.2 if sx<0 else x,y-8 if sy>0 else y-1.2,FLOOR-.05,1.2,9.2,1.05),
                         block(x-8 if sx>0 else x-1.2,y-1.2 if sy<0 else y,FLOOR-.05,9.2,1.2,1.05)])
case=case.fuse(*locators).clean()
assert len(bosses)>=12,len(bosses)
# Preserve the outside floor and fixed lip heights while clearing front diodes.
# The bottom surface remains at z=0; only the inside surface is pocketed.
floor_pockets=[];floor_pocket_records=[]
floor_gap=config['floor_component_clearance_mm']
floor_min=config['minimum_floor_thickness_mm']
for ref,shape in bottom_parts:
    bb=shape.BoundingBox()
    if bb.zmin-FLOOR>=floor_gap:continue
    pocket_z=bb.zmin-floor_gap
    assert pocket_z>=floor_min, f'{ref}: insufficient floor thickness at the fixed case profile'
    pocket=block(bb.xmin-floor_gap,bb.ymin-floor_gap,pocket_z,
                 bb.xlen+2*floor_gap,bb.ylen+2*floor_gap,FLOOR-pocket_z+.02)
    assert battery.intersect(pocket).Volume()<1e-5, 'Floor relief must not enter the battery reserve'
    floor_pockets.append(pocket)
    floor_pocket_records.append(dict(ref=ref,floor_thickness_mm=pocket_z,
                                     component_bottom_z=bb.zmin,clearance_mm=floor_gap))
if floor_pockets:case=case.cut(*floor_pockets).clean()
# Open-topped notch for the PCB power switch, beside the direct module USB port.
ports=[]
for ref,width in [('SW87',9.0)]:
    c=next(c for c in d['components'] if c['ref']==ref)
    x,y,xx,yy=c['bounds'];cx=(x+xx)/2+M
    # Leave access for plug shell/finger; rear notch runs down to below the body.
    bottom=max(FLOOR,plane_z(M+y*C,c.get('z_top',0)-c['height'])-.8)
    notch=block(cx-width/2,CD-8,bottom,width,12,30)
    case=case.cut(notch);ports.append(dict(ref=ref,x=cx,width=width,bottom_z=bottom))

# Clear the module/socket internally, then close the exterior around the socket
# with a recessed integral bezel. No panel connector or extension cable.
module=next(c for c in d['components'] if c['ref']=='U1')
x,y,xx,yy=module['bounds'];zt=module['z_top'];h=module['height']
case=case.cut(place(block(x-.3,y-.3,zt-h-.3,xx-x+.6,yy-y+.6,h+.6)))
socket=next(c for c in d['components'] if c['ref']=='USB_SOCKET')
sx,sy,sxx,syy=socket['bounds'];szt=socket['z_top'];sh=socket['height']
case=case.cut(place(block(sx-.3,sy-.3,szt-sh-.3,sxx-sx+.6,syy-sy+.6,sh+.6)))
plug=next(c for c in d['components'] if c['ref']=='USB_PLUG_EXTERNAL')
x,y,xx,yy=plug['bounds'];zt=plug['z_top'];h=plug['height']
case,usb_surround,usb_insertion_sweep=make_surround(
    case,module,socket,plug,config['rear_usb'],place)
socket_axis=-config['module']['usb_axis_below_carrier_mm']
socket_y=M+y*C-socket_axis*S;socket_z=Z0+y*S+socket_axis*C
ports.append(dict(ref='DIRECT_MODULE_USB',x=M+(x+xx)/2,center_z=socket_z,
    width=usb_surround['aperture_width_height_mm'][0],
    height=usb_surround['aperture_width_height_mm'][1],socket_recession_mm=CD-socket_y,
    socket_axis_measured=False,frame='recessed aperture aligned to tilted module'))
case=case.clean()

print('Separate switch/stabilizer plate',flush=True)
plate_holes=[switch_aperture(*s['xy']) for s in d['switches']]
# Continuous pin-row relief avoids fragile webs between individual drill holes.
# The 2.6 mm slots open through the rear edge rather than leaving a thin lip.
module_holes={h['pad']:h['xy'] for h in d['holes'] if h['ref']=='U1'}
for numbers in [('28','12'),('29','13'),('25','26','27')]:
    plate_holes.append(LineString([module_holes[n] for n in numbers]).buffer(1.3))
stabilizers=[]
for s in d['switches']:
    if s['units']<2:continue
    span=100. if s['units']==6.25 else 23.8
    plate_holes.append(stabilizer_apertures(*s['xy'],span))
    stabilizers.append(dict(reference=s['ref'],xy=s['xy'],nominal_span_mm=span,verified=False))
# Clear all connector tails and create light paths through both prototype plates.
for c in d['components']:
    x,y,xx,yy=c['bounds']
    if c['ref'] in ('J1','J5'):plate_holes.append(box(x-.7,y-.7,xx+.7,yy+.7))
    if c['ref'].startswith('LED'):
        plate_holes.append(box((x+xx)/2-1.75,(y+yy)/2-1.5,(x+xx)/2+1.75,(y+yy)/2+1.5))
plate_openings=unary_union(plate_holes)
plate_profile=box(0,0,W,D).difference(plate_openings)
plate_flat=polygon_solid(plate_profile,PLATE_BOTTOM,PLATE_T)
# Integral prototype feet transfer load to the PCB above existing case supports.
# No upper case ledge obstructs the vertical PCB insertion path.
plate_feet=[];plate_support_xy=[]
plate_forbidden=unary_union([plate_openings]+[g.buffer(.6) for g,r in hole_geoms])
for x,y in boss_locations:
    if not Point(x,y).buffer(1.5).disjoint(plate_forbidden):continue
    foot=cq.Workplane('XY').circle(1.4).extrude(PLATE_BOTTOM-T+.02).translate((x,y,T)).val()
    plate_feet.append(foot);plate_support_xy.append([x,y])
assert len(plate_feet)>=3,plate_support_xy
plate=plate_flat.fuse(*plate_feet).clean()
assert plate.isValid() and len(plate.Solids())==1
flat_export(plate_flat,'plate-flat-1.5mm.stl')
flat_export(plate,'plate-supported.stl')
for label,half in zip(('left','right'),halves):flat_export(plate.intersect(half),f'plate-supported-{label}.stl')
cq.exporters.export(plate,str(out/'plate-supported.step'))
# Closed 2D loops for a vendor to review; not an approved production plate.
section=cq.Workplane('XY').add(plate_flat).section(PLATE_BOTTOM+PLATE_T/2)
cq.exporters.export(section,str(out/'plate-diagnostic.dxf'))

print('Cover and keycap envelopes',flush=True)
cover=block(0,0,0,CW,CD,30).intersect(under_plane(T+GAP+COVER_T)).cut(under_plane(T+GAP))
# User's XVX screenshot specifies 5 mm height. Footprint/socket depth are still assumptions.
caps=config['keycaps']
cap_bottom=T+8.6-caps['assumed_socket_insertion_mm']
cap_geoms=[];cap_shapes=[]
for s in d['switches']:
    x,y=s['xy'];w=s['units']*19.05-(19.05-caps['assumed_1u_footprint_mm'][0]);dep=caps['assumed_1u_footprint_mm'][1]
    cap_geoms.append(box(x-w/2-.6,y-dep/2-.6,x+w/2+.6,y+dep/2+.6))
    cap_shapes.append(block(x-w/2,y-dep/2,cap_bottom,w,dep,caps['advertised_height_mm']))
openings=polygon_solid(unary_union(cap_geoms),-5,25)
cover=cover.cut(place(openings))
# Keep a direct light opening above the v8 emitters, including emitters under a row web.
for c in d['components']:
    if c['side']=='top' and c['ref'].startswith('LED'):
        x,y,xx,yy=c['bounds']
        cover=cover.cut(place(block((x+xx)/2-1.75,(y+yy)/2-1.2,T,3.5,2.4,6)))
# Cover feet rest on the plate, above the plate/PCB/case support chain.
feet=[]
all_holes=unary_union(cap_geoms+[plate_openings])
for x,y in plate_support_xy:
    if not Point(x,y).buffer(1.5).disjoint(all_holes):continue
    feet.append(place(cq.Workplane('XY').circle(1.4).extrude(T+GAP-PLATE_TOP+.1).translate((x,y,PLATE_TOP)).val()))
if feet:cover=cover.fuse(*feet).clean()
assert case.isValid() and cover.isValid()
assert len(case.Solids())==1 and len(cover.Solids())==1,(len(case.Solids()),len(cover.Solids()))
flat_export(case,'case.stl')
# Cover is printed un-tilted, underside on the bed; its outside stays flush in assembly.
cover_local=cover.translate((-M,-M,-Z0)).rotate((0,0,0),(1,0,0),-degrees)
cover_bb=cover_local.BoundingBox()
flat_export(cover_local,'cover.stl')
for name,shape in [('case',case),('cover',cover_local)]:
    for side,(x,w) in zip(('left','right'),[(-5,CW/2+5),(CW/2,CW/2+5)]):
        flat_export(shape.intersect(block(x,-10,-10,w,CD+20,60)),f'{name}-{side}.stl')
(out/'battery-size-gauge-200x50x6.stl').unlink(missing_ok=True)
for pattern,current in [('battery-reserve-gauge-*.stl',reserve_gauge),
                        ('battery-pack-max-gauge-*.stl',pack_gauge)]:
    for stale in out.glob(pattern):
        if stale.name!=current:stale.unlink()
flat_export(battery,reserve_gauge)
flat_export(block(0,0,0,*pack_dims),pack_gauge)
for filename,dimensions in ((reserve_gauge,battery_dims),(pack_gauge,pack_dims)):
    if dimensions[0]>250:
        # Butt-join these two gauges to check the full bay on a 256 mm bed.
        half_gauge=block(0,0,0,dimensions[0]/2,dimensions[1],dimensions[2])
        for side in ('left','right'):
            flat_export(half_gauge,filename.removesuffix('.stl')+f'-{side}.stl')
for side,half in zip(('left','right'),halves):
    # A reference file, not a one-piece printable object (separate keycap solids).
    flat_export(compound(cap_shapes).intersect(half),f'keycap-envelopes-{side}.stl')

for ref,shape,side in component_shapes:
    if ref in ('U1','USB_SOCKET','USB_PLUG_EXTERNAL'):
        flat_export(shape,ref.lower()+'-envelope.stl')

print('Assembly and collision checks',flush=True)
asm=cq.Assembly(name=root.name+'-fit')
asm.add(case,name='case',color=cq.Color(.25,.3,.37))
asm.add(cover,name='cover',color=cq.Color(.8,.82,.85,.6))
asm.add(place(board),name='PCB',color=cq.Color(.1,.45,.25))
for ref,s,side in component_shapes:asm.add(place(s),name=ref,color=cq.Color(.5,.5,.5))
asm.add(battery,name='PROVISIONAL-battery-reserved-volume',color=cq.Color(.65,.68,.7,.5))
asm.add(place(plate),name='DIAGNOSTIC-stabilizer-switch-plate',color=cq.Color(.2,.5,.85))
switch_shapes=[]
for s in d['switches']:
    x,y=s['xy']
    # Kailh's 6.4 mm reference starts at the flange, 2.2 mm above the PCB.
    # Stepped envelope permits the 13.95 mm lower body through the plate.
    key=block(x-6.975,y-6.975,T,13.95,13.95,2.2).fuse(
        block(x-7.5,y-7.5,T+2.2,15,15,3.3),
        cq.Workplane('XY').circle(3.25).extrude(3.1).translate((x,y,T+5.5)).val())
    switch_shapes.append((s['ref'],place(key)))
    asm.add(place(key),name=s['ref'],color=cq.Color(.85,.85,.85))
asm.add(place(compound(cap_shapes)),name='XVX-5mm-envelopes-ASSUMED-socket-depth',color=cq.Color(.6,.65,.72,.6))
asm.export(str(out/'fit-assembly.step'))
collisions=[]
for ref,shape in bottom_parts:
    vol=overlap_volume(case,shape)
    if vol>1e-5:collisions.append(dict(ref=ref,case_overlap_mm3=round(vol,6)))
    vol=overlap_volume(battery,shape)
    if vol>1e-5:collisions.append(dict(ref=ref,battery_overlap_mm3=round(vol,6)))
for ref,shape,side in component_shapes:
    if ref not in ('U1','USB_SOCKET','USB_PLUG_EXTERNAL'):continue
    for other,other_shape in bottom_parts:
        if other==ref:continue
        vol=overlap_volume(place(shape),other_shape)
        if vol>1e-4:collisions.append(dict(ref=ref,obstacle=other,overlap_mm3=round(vol,6)))
for c,shape,side in component_shapes:
    vol=overlap_volume(cover,place(shape))
    if vol>1e-5:collisions.append(dict(ref=c,cover_overlap_mm3=round(vol,6)))
# Test complete supported plate and cover, including the added load-bearing feet.
for label,left,right in [('plate_case',place(plate),case),('plate_pcb',place(plate),place(board)),
                         ('plate_cover',place(plate),cover),('battery_case',battery,case),
                         ('battery_pcb',battery,place(board))]:
    vol=overlap_volume(left,right)
    if vol>1e-4:collisions.append(dict(ref=label,overlap_mm3=round(vol,6)))
for ref,shape in switch_shapes:
    for label,other in [('plate',place(plate)),('cover',cover)]:
        vol=overlap_volume(other,shape)
        if vol>1e-4:collisions.append(dict(ref=ref,obstacle=label,overlap_mm3=round(vol,6)))
for ref,shape,side in component_shapes:
    vol=overlap_volume(place(plate),place(shape))
    if vol>1e-4:collisions.append(dict(ref=ref,plate_overlap_mm3=round(vol,6)))
for i,shape in enumerate(pin_shapes):
    vol=overlap_volume(place(plate),place(shape))
    if vol>1e-4:collisions.append(dict(ref=f'pin-{i}',plate_overlap_mm3=round(vol,6)))
# Check the entire female assembly against the PCB and switch solder pins;
# a flat rear-wall mount must not inherit the old PCB-tilted clearance assumption.
for ref,shape,side in component_shapes:
    if ref in ('U1','USB_SOCKET','USB_PLUG_EXTERNAL'):
        vol=overlap_volume(place(board),place(shape))
        if vol>1e-4:collisions.append(dict(ref=ref,obstacle='PCB',overlap_mm3=round(vol,6)))
# Actual volume distance, including pins and board; reserved box already includes growth room.
battery_clearance=min((battery.distance(shape),ref) for ref,shape in bottom_parts+[('PCB',place(board))])
# Optimistic upper bound for the requested flat pack: rear edge touches the
# inside rear wall, with no allowance for ledges, locators, wires or electronics.
# If it fails even this bare-PCB bound, moving it sideways cannot make it fit.
requested_dims=bat.get('requested_nominal_pack_dimensions_mm')
requested_fit=None
if requested_dims:
    best_front_y=CD-WALL-min(requested_dims[:2])
    bare_pcb_height=plane_z(best_front_y)-BZ
    requested_fit=dict(model=bat['requested_model'],nominal_dimensions_mm=requested_dims,
                       datasheet=bat['requested_datasheet'],orientation='flat on padded case floor',
                       best_possible_front_edge_y_mm=best_front_y,
                       optimistic_bare_pcb_height_above_padding_mm=bare_pcb_height,
                       nominal_thickness_shortfall_mm=requested_dims[2]-bare_pcb_height,
                       rejected_even_without_underside_components=requested_dims[2]>bare_pcb_height,
                       note='Necessary geometric bound only; passing it would not establish pack fit.')
pcb_case=case.intersect(place(board)).Volume()
floor_clearance=min((shape.BoundingBox().zmin-FLOOR,ref) for ref,shape in bottom_parts)
floor_by_ref={r['ref']:r['floor_thickness_mm'] for r in floor_pocket_records}
relieved_clearance=min((shape.BoundingBox().zmin-floor_by_ref.get(ref,FLOOR),ref)
                       for ref,shape in bottom_parts)
# Small, matching rear-corner coupons. All XY origins share the same crop;
# board/plate coupons are flat print parts and case is in the assembled tilt.
coupon_x=289.;coupon_y=78.
coupon_local=block(coupon_x,coupon_y,-10,W-coupon_x+2,D-coupon_y+20,40)
flat_export(board.intersect(coupon_local),'fit-coupon-pcb.stl')
flat_export(plate.intersect(coupon_local),'fit-coupon-plate.stl')
flat_export(cover_local.intersect(coupon_local),'fit-coupon-cover.stl')
coupon_world=block(M+coupon_x,M+coupon_y*C,-1,CW-(M+coupon_x)+1,CD-(M+coupon_y*C)+1,35)
flat_export(case.intersect(coupon_world),'fit-coupon-case.stl')
# A 1 mm gauge for setting the module/carrier gap during the soldering trial.
flat_export(block(0,0,0,20,5,config['module']['mounting_gap_mm']),'module-gap-gauge.stl')
report=dict(source_sha256=d['source_sha256'],units='mm',pcb_size=[W,D,T],case_size=[CW,CD,REAR],
            front_lip=FRONT,rear_lip=REAR,tilt_degrees=degrees,pcb_underside_front_origin_z=Z0,
            support_count=len(bosses),support_xy_board=boss_locations,rear_notches=ports,
            cover_support_count=len(feet),
            min_floor_clearance=dict(mm=relieved_clearance[0],reference=relieved_clearance[1]),
            min_unrelieved_floor_clearance=dict(mm=floor_clearance[0],reference=floor_clearance[1]),
            floor_relief_pockets=floor_pocket_records,
            collisions=collisions,pcb_case_overlap_mm3=pcb_case,seam_xy_board=seam,
            battery=dict(**bat,position_xyz_case_mm=[BX,BY,BZ],
                         minimum_reserved_volume_clearance_mm=battery_clearance[0],nearest_reference=battery_clearance[1]),
            requested_battery_fit=requested_fit,
            stack=dict(pcb_top_z=T,plate_bottom_z=PLATE_BOTTOM,plate_top_z=PLATE_TOP,
                       plate_support_xy=plate_support_xy,cover_bottom_z=T+GAP,cover_top_z=T+GAP+COVER_T,
                       switch_stem_top_z=T+8.6),
            stabilizers=stabilizers,
            keycaps=dict(**caps,assumed_unpressed_bottom_z=cap_bottom,travel_checked=False),
            fit_config_sha256=hashlib.sha256(config_path.read_bytes()).hexdigest(),
            case_mounted_components=case_mounted_components,
            measured_inputs=dict(module=config['module'],rear_usb=config['rear_usb']),
            direct_usb=dict(extension_cable_required=False,external_plug_gauge_dimensions_mm=config['rear_usb']['external_plug_housing_dimensions_mm'],
                socket_recession_mm=CD-socket_y,socket_axis_measured=False,
                surround=usb_surround,
                module_floor_clearance_mm=next(shape.BoundingBox().zmin-FLOOR for ref,shape in bottom_parts if ref=='U1')),
            module_fit=dict(module_body_dimensions_mm=[config['module']['pcb_measured_length_width_mm'][0],
                config['module']['model_width_with_allowance_mm'],config['module']['model_total_thickness_limit_mm']],
                mounting_gap_mm=config['module']['mounting_gap_mm'],actual_dimensions_measured=False),
            limitations=['Clone PCB length/width and socket overhang are user measurements; 5 mm total height and 3.5 mm socket axis below carrier remain assumptions.',
                'Recessed USB bezel has a 0.6 mm web and provisional socket-sized aperture; test actual socket, cable insertion and print strength using the coupon.',
                'Module is soldered on short pins at 1 mm gap; no tall sockets. Auxiliary pad registration and solder access require a real-module trial.',
                'Antenna has the rotated v7.5 copper exclusion, but nearby switches, plastic plate, battery and RF performance need hardware tests.',
                'Plate uses generic stabilizer slots; actual stabilizer travel remains unverified.',
                'Keycap underside, socket insertion and travel remain unmeasured.',
                'Battery and its temperature/charge protection remain unselected and unverified.',
                'Component envelopes are approximations, not manufacturer CAD.',
                'Fit coupons are partial mating geometry for hand-held assembly checks, not a standalone keyboard case.'])
(out/'fit-report.json').write_text(json.dumps(report,indent=2)+'\n')
export_previews(out,d,report)
preview=f'''// Generated view. Use the STEP for CAD, STL files for printing (millimetres).
// Keycaps and stabilizer mounting remain unverified. No light simulation is implied.
use <module-envelopes.scad>
show_cover=true;
explode=18;
show_plate=true;
module pcb_frame() {{ translate([{M},{M},{Z0}]) rotate([{degrees},0,0]) children(); }}
color([0.25,0.3,0.37]) import("case.stl");
pcb_frame() color([0.12,0.5,0.25]) import("pcb-bare.stl");
pcb_frame() module_envelopes();
if (show_plate) translate([0,0,explode]) pcb_frame()
    translate([0,0,{T}]) color([0.2,0.5,0.85]) import("plate-supported.stl");
translate([{BX},{BY},{BZ}]) color([0.8,0.65,0.3]) import("{reserve_gauge}");
if (show_cover) translate([0,0,2*explode]) pcb_frame()
    translate([{cover_bb.xmin},{cover_bb.ymin},{cover_bb.zmin}]) color([0.8,0.82,0.85]) import("cover.stl");
'''
(out/'fit.scad').write_text(preview)
(out/'case.scad').write_text('// Generated fit case; build_fit.py is the parametric source.\nimport("case.stl");\n')
print(json.dumps({k:report[k] for k in ('support_count','min_floor_clearance','collisions','pcb_case_overlap_mm3')},indent=2),flush=True)
assert not collisions and pcb_case<1e-4, 'Fit collision: inspect report before using models'
