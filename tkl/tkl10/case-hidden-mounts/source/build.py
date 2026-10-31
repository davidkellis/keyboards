#!/usr/bin/env python3
"""Alternate v10 enclosure: closed plate, removable floor, internal nut carriers.

Run with /tmp/keyboards-fit-work/venv/bin/python. Original sources are read only.
All CAD geometry uses millimetres; assembly STEP preserves world coordinates.
"""
from pathlib import Path
import hashlib,json,math,sys,shutil
import cadquery as cq
import numpy as np
from shapely.geometry import box,Polygon,Point
from split_geometry import lap_split
from mesh_export import clean_degenerate_facets

OUT=Path(__file__).resolve().parents[1]
ROOT=OUT.parent
REF=OUT/'reference'; REF.mkdir(exist_ok=True)
SRC=ROOT/'case'
cfg=json.loads((SRC/'fit-config.json').read_text())
geo=json.loads((SRC/'board-geometry.json').read_text())
report=json.loads((SRC/'fit-report.json').read_text())
W,D,T=[geo['board'][k] for k in ('width','depth','thickness')]
CW,CD=cfg['fixed_footprint_mm']; WALL=2.; FLOOR=1.2; M=2.4
DEG=report['tilt_degrees']; A=math.radians(DEG); C=math.cos(A); S=math.sin(A)
Z0=report['pcb_underside_front_origin_z']; PT=T+cfg['plate_top_above_pcb_mm']; PB=PT-cfg['plate_thickness_mm']
def block(x,y,z,w,d,h):
    return cq.Workplane('XY').box(w,d,h,centered=False).translate((x,y,z)).val()
def cyl(x,y,z,r,h):
    return cq.Workplane('XY').circle(r).extrude(h).translate((x,y,z)).val()
def place(s):return s.rotate((0,0,0),(1,0,0),DEG).translate((M,M,Z0))
def unplace(s):return s.translate((-M,-M,-Z0)).rotate((0,0,0),(1,0,0),-DEG)
def plane_z(y,z=0):return Z0+(y-M)*math.tan(A)+z/C
def under(z):
    return cq.Workplane('YZ').polyline([(-10,-20),(CD+10,-20),(CD+10,plane_z(CD+10,z)),(-10,plane_z(-10,z))]).close().extrude(CW+20).translate((-10,0,0)).val()
def polysolid(p,z,h):
    ss=[]
    for q in list(p.geoms) if hasattr(p,'geoms') else [p]:
        if q.is_empty:continue
        s=cq.Workplane('XY').polyline(list(q.exterior.coords)[:-1]).close().extrude(h).translate((0,0,z)).val()
        for ring in q.interiors:
            tool=cq.Workplane('XY').polyline(list(ring.coords)[:-1]).close().extrude(h+.2).translate((0,0,z-.1)).val()
            s=s.cut(tool)
        ss.append(s)
    return cq.Compound.makeCompound(ss)
_bounds={}
def bounds(s):
    k=id(s)
    if k not in _bounds:_bounds[k]=(s,s.BoundingBox())
    return _bounds[k][1]
def iv(a,b):
    aa=bounds(a);bb=bounds(b)
    if any(getattr(aa,k+'max')<=getattr(bb,k+'min')+1e-7 or getattr(bb,k+'max')<=getattr(aa,k+'min')+1e-7 for k in ('x','y','z')):return 0.
    return a.intersect(b).Volume()
def hexprism(x,y,z,af,h):
    rr=af/math.sqrt(3)
    return cq.Workplane('XY').polyline([(x+rr*math.cos(i*math.pi/3),y+rr*math.sin(i*math.pi/3)) for i in range(6)]).close().extrude(h).translate((0,0,z)).val()
def require_solid(s,name):
    assert s.isValid() and len(s.Solids())==1,(name,'invalid or disconnected',len(s.Solids()))
    return s
exports={}
def export(s,name,flat=False):
    require_solid(s,name)
    if flat:
        b=s.BoundingBox();off=[-b.xmin,-b.ymin,-b.zmin];s=s.translate(tuple(off))
    else:off=[0,0,0]
    cq.exporters.export(s,str(OUT/(name+'.stl')),tolerance=.025,angularTolerance=.12)
    clean_degenerate_facets(OUT/(name+'.stl'))
    b=s.BoundingBox()
    exports[name]={'translation_for_print_mm':off,'bounds_mm':[b.xlen,b.ylen,b.zlen],'volume_mm3':s.Volume()}
    return s

print('Load unchanged v10 reference CAD',flush=True)
case_cache=REF/'original-case.brep'
if not case_cache.exists():
    originals=cq.importers.importStep(str(SRC/'fit-assembly.step')).solids().vals()
    original=max((s for s in originals if s.BoundingBox().xlen>CW-.01),key=lambda s:s.Volume())
    original.exportBrep(str(case_cache))
old_case=cq.Shape.importBrep(str(case_cache))
pcb=cq.importers.importStep(str(SRC/'pcb-bare.step')).val()
plate=cq.importers.importStep(str(SRC/'plate.step')).val()
# Restore material removed by the old twelve top-entered screws. All existing
# switch apertures, stabilizer apertures, blind pin channels and LED holes stay.
fills=[cyl(*p['xy'],T,2.11,PT-T) for p in cfg['mounting']['points']]
plate=plate.fuse(*fills).clean()
require_solid(plate,'unperforated plate')
board=place(pcb)
parts=[]
for c in geo['components']:
    x,y,xx,yy=c['bounds'];h=c['height'];z=c.get('z_top',0)-h if c['side']=='bottom' else T-.03
    parts.append((c['ref'],place(block(x,y,z,xx-x,yy-y,h+.03))))
pins=[]
for pin in geo['pins']:
    x,y=pin['xy'];h=pin['depth'];top=pin.get('top',False)
    s=cyl(x,y,T-.05 if top else -h,pin['diameter']/2,h+.05)
    s=s.fuse(cyl(x,y,T-.03 if top else -.25,pin['collar_diameter']/2,.28))
    pins.append((pin['ref']+'-pin',place(s)))
bat=cfg['battery']; BX,BY=bat['origin_xy_case_mm']
battery=block(BX,BY,FLOOR+bat['padding_below_mm'],*bat['reserved_dimensions_mm'])
electronics=[('PCB',board)]+parts+pins+[('battery-reserve',battery)]

print('Construct integrated rim and removable bottom',flush=True)
# Start from the original perimeter envelope. After the port lips are joined,
# trim the entire upper flush with the plate and round its outside edges.
wall=block(0,0,0,CW,CD,30).intersect(under(T+cfg['plate_top_above_pcb_mm']+cfg['cover_gap_above_plate_mm']+cfg['cover_thickness_mm']))
wall=wall.cut(block(WALL,WALL,-1,CW-2*WALL,CD-2*WALL,40)).clean()
# Bottom edge rebate: 1.5 mm external skirt hides the removable floor joint.
wall=wall.cut(block(1.5,1.5,-.1,CW-3,CD-3,1.5)).clean()
ring=box(-M,-M,W+M,D+M).difference(box(.3,.6,W-.3,D-.3))
bridge=place(polysolid(ring,PB,PT-PB)).intersect(block(0,0,-1,CW,CD,32))
upper=wall.fuse(place(plate),bridge).clean()
require_solid(upper,'upper')
# Isolate the old interior floor and support geometry; drop any old rear-wall
# bracket that becomes disconnected. Battery clearance and floor relief remain.
base=old_case.intersect(block(2.2,2.2,0,CW-4.4,CD-4.4,30)).clean()
base=max(base.Solids(),key=lambda s:s.Volume())
floor_edge=polysolid(box(1.7,1.7,CW-1.7,CD-1.7).difference(box(2.21,2.21,CW-2.21,CD-2.21)),0,FLOOR)
base=base.fuse(floor_edge).clean()
# Replace old front/middle nut wells with solid supports at the same safe holes.
for p in cfg['mounting']['points'][:8]:
    x,y=p['xy']
    support=place(cyl(x,y,-25,3.5,25)).intersect(block(2.2,2.2,FLOOR-.02,CW-4.4,CD-4.4,30))
    base=base.fuse(support).clean()
# Two smooth locating pins use the existing 2.5 mm PCB holes, no PCB alteration.
for p in [cfg['mounting']['points'][0],cfg['mounting']['points'][7]]:
    base=base.fuse(place(cyl(*p['xy'],-.1,.9,1.1))).clean()
require_solid(base,'base')

print('Find eight accessible hidden nut-carrier locations',flush=True)
# Each removable carrier has a wide tongue bearing on a pocket in the wall.
# It is installed after the PCB. Two floor dowels prevent inward withdrawal
# when closed; the M2 screw is deliberately not the only lateral restraint.
shoe_bottom=2.8; shoe_top=6.0; nut_seat=3.8; nut_h=1.6
shoe_blank=block(-.95,-5.8,shoe_bottom,9.95,11.6,shoe_top-shoe_bottom)
shoe=shoe_blank.cut(hexprism(5,0,nut_seat,4.25,1.85),block(5,-2.125,nut_seat,7,4.25,1.85),cyl(5,0,shoe_bottom-.1,1.25,shoe_top-shoe_bottom+.2)).clean()
for y in [-4,4]:shoe=shoe.cut(cyl(2.2,y,shoe_bottom-.1,.95,1.1)).clean()
require_solid(shoe,'nut carrier')
slot=block(-1.2,-6.05,shoe_bottom,1.4,12.1,3.4)
def orient(s,side,pos):
    if side=='left':return s.translate((2,pos,0))
    if side=='right':return s.rotate((0,0,0),(0,0,1),180).translate((CW-2,pos,0))
    return s.rotate((0,0,0),(0,0,1),-90).translate((pos,CD-2,0))
mounts=[];shoes=[];hardware=[]
targets=[('left',52),('right',52),('left',84),('right',84),('left',116),('right',116),('rear',64),('rear',272)]
for i,(side,target) in enumerate(targets):
    candidates=sorted(np.arange(target-9,target+9.01,.5),key=lambda a:abs(a-target))
    found=None
    for pos in candidates:
        # Expanded envelope includes clearance for actual solder and print fit.
        trial=orient(block(-.98,-6.15,shoe_bottom-.05,10.4,12.3,shoe_top-shoe_bottom+.4),side,float(pos))
        if any(iv(trial,s)>1e-5 for _,s in electronics):continue
        found=float(pos);break
    if found is None:raise RuntimeError(f'No clear nut-carrier location: {side} {target}')
    mount={'id':f'M{i+1}','side':side,'position_mm':found,'screw':'M2 x 4 button head','nut':'DIN 934 M2, 4 mm AF x 1.6 mm'}
    print(mount,flush=True)
    sh=orient(shoe,side,found);shoes.append((mount['id'],sh))
    upper=upper.cut(orient(slot,side,found)).clean()
    # Remove old support/rib material around the inserted shoe, then add its seat.
    clear=orient(block(-1.1,-6.1,shoe_bottom,10.5,12.2,23),side,found)
    base=base.cut(clear).clean()
    pad=orient(block(.22,-5.7,FLOOR-.02,8.5,11.4,shoe_bottom-FLOOR+.02),side,found)
    base=base.fuse(pad).clean()
    for yy in [-4,4]:base=base.fuse(orient(cyl(2.2,yy,shoe_bottom-.1,.75,.9),side,found)).clean()
    # Recessed head: 1.5 mm seat leaves 0.2 mm below a 1.3 mm head. Screw tip
    # reaches 5.5, 0.1 beyond the nominal nut, inside the open clearance bore.
    base=base.cut(orient(cyl(5,0,-.1,2.15,1.6),side,found),orient(cyl(5,0,-.1,1.25,8),side,found)).clean()
    screw=cyl(5,0,1.5,1,4).fuse(cyl(5,0,.2,1.9,1.3)).clean()
    nut=hexprism(5,0,nut_seat,4,nut_h).cut(cyl(5,0,nut_seat-.1,1,nut_h+.2)).clean()
    hardware += [(mount['id']+'-screw',orient(screw,side,found)),(mount['id']+'-nut',orient(nut,side,found))]
    mounts.append(mount)
require_solid(base,'supported removable floor')
require_solid(upper,'upper with wall slots')

print('Preserve direct USB opening in a removable rear bezel',flush=True)
# A separate rear insert allows the PCB/module to enter from below. It retains
# the original socket aperture, plug recess and provisional clearances.
socket=next(c for c in geo['components'] if c['ref']=='USB_SOCKET')
sx=(socket['bounds'][0]+socket['bounds'][2])/2+M
bx0=sx-13; bx1=sx+13; by0=CD-4.2
bezel_region=block(bx0,by0,0,bx1-bx0,CD-by0,25)
bezel=old_case.intersect(bezel_region).clean()
# Join the reference bezel to two slim legs extending down to the floor; these
# legs accept locating pins from the base and block rearward removal when shut.
for x in [bx0,bx1-2.5]:bezel=bezel.fuse(block(x,CD-2,1.4,2.5,2,17)).clean()
bezel=bezel.intersect(block(0,0,0,CW,CD,30).intersect(under(PB-.2))).clean()
bezel=bezel.cut(block(bx0,by0,-.1,bx1-bx0,CD-by0,1.5)).clean()
require_solid(bezel,'rear USB insert')
cut_region=block(bx0-.15,by0-.15,-.1,bx1-bx0+.3,CD-by0+.3,31).intersect(under(PB-.05))
upper=upper.cut(cut_region).clean()
# The gap is covered by internal side flanges. These sit outside the board's
# insertion rectangle, and are part of the removable bezel, not the upper.
for x in [bx0-1.2,bx1]:
    flange=block(x,CD-2.85,1.5,1.2,.65,3.5)
    bezel=bezel.fuse(flange,block(x if x==bx1 else bx0-.15,CD-2.85,1.5,.15,.9,3.5)).clean()
    upper=upper.cut(block(x-.15,CD-3.0,-.1,1.5,1.7,5.5)).clean()
bezel=bezel.cut(place(block(-.25,-.25,-.25,W+.5,D+.5,T+.5))).clean()
# Keep the small upper USB lip on the shell. The remaining U-shaped insert
# withdraws down normal to the PCB (slightly rearward), with short side flanges
# in open-bottom guide pockets. The path keeps the tilted socket/body clear.
# Its open top clears the socket; a closed aperture would trap the module.
usb_split=socket['z_top']+cfg['rear_usb']['socket_clearance_each_side_mm']
fixed_usb_cap=old_case.intersect(bezel_region).cut(under(usb_split)).clean()
upper=upper.fuse(fixed_usb_cap).clean()
bezel=bezel.intersect(under(usb_split-.15)).clean()
# The original rounded aperture narrows at its upper corners. Open those
# corners through the removable U's top so the full socket width can exit.
sx0,sy0,sx1,sy1=socket['bounds']
bezel=bezel.cut(place(block(sx0-.3,sy0-2,socket['z_top']-socket['height']/2,
                           sx1-sx0+.6,25,15))).clean()
base=base.cut(block(bx0-1.4,by0-.2,FLOOR,bx1-bx0+2.8,CD-by0+.3,30)).clean()
for x in [bx0+1.25,bx1-1.25]:
    bezel=bezel.cut(cyl(x,CD-1,1.3,.75,2.2)).clean()
    # Pins cannot be at the very narrow floor edge: add local ears beneath them.
    base=base.fuse(block(x-1,CD-2.4,0,2,2.0,1.2),cyl(x,CD-1,1.1,.55,2)).clean()
# The power-switch opening has a fixed upper lip and a lower floor-mounted lip.
power=next(c for c in geo['components'] if c['ref']=='SW87')
x,y,xx,yy=power['bounds'];cx=(x+xx)/2+M
bottom=max(FLOOR,plane_z(M+y*C,power.get('z_top',0)-power['height'])-.8)
upper=upper.cut(block(cx-4.5,CD-8,-.1,9,12,31).intersect(under(.6))).clean()
# The floor carries the lower part of the switch surround, so PCB insertion
# remains possible while the installed rear wall has only an actuator slot.
base=base.fuse(block(cx-4.3,CD-2.2,0,8.6,2.2,bottom)).clean()
for name,s in [('upper',upper),('base',base),('bezel',bezel)]:require_solid(s,name)

print('Make perimeter flush with the plate; round outer edges and corners',flush=True)
TOP_RADIUS=2.5
CORNER_RADIUS=3.0
# Round a simple outer envelope before intersecting the detailed shell. This
# keeps the larger blends independent of the interior ribs and port topology.
envelope=block(0,0,0,CW,CD,30).intersect(under(PT)).clean()
corner_edges=[]
for edge in envelope.Edges():
    vv=[v.Center() for v in edge.Vertices()]
    if not vv:continue
    on_x=any(all(abs(v.x-x)<1e-5 for v in vv) for x in (0,CW))
    on_y=any(all(abs(v.y-y)<1e-5 for v in vv) for y in (0,CD))
    if on_x and on_y:corner_edges.append(edge)
assert len(corner_edges)==4
envelope=envelope.fillet(CORNER_RADIUS,corner_edges).clean()
top_edges=[e for e in envelope.Edges() if e.Vertices() and
           all(abs(v.Center().z-plane_z(v.Center().y,PT))<1e-5 for v in e.Vertices())]
assert len(top_edges)==8
envelope=envelope.fillet(TOP_RADIUS,top_edges).clean()
require_solid(envelope,'rounded exterior envelope')
upper=upper.intersect(envelope).clean()
require_solid(upper,'flush rounded upper')
assert unplace(upper).BoundingBox().zmax<=PT+1e-5,'Material protrudes above plate'
vertices=[v.Center() for v in upper.Vertices()]
edge_heights=[max(v.z for v in vertices if abs(v.y-y)<1e-5) for y in (0,CD)]
surface={'raised_rim_mm':0,'top_edge_radius_mm':TOP_RADIUS,'vertical_corner_radius_mm':CORNER_RADIUS,
         'rounded_edge_count':len(top_edges)+len(corner_edges),'rounded_top_edge_count':len(top_edges),
         'rounded_vertical_edge_count':len(corner_edges),'top_local_z_mm':PT,
         'bottom_skirt_corner_diagonal_thickness_mm':1.5*math.sqrt(2)-CORNER_RADIUS*(math.sqrt(2)-1),
         'nominal_plate_plane_front_rear_mm':[plane_z(0,PT),plane_z(CD,PT)],
         'outer_wall_top_front_rear_mm':edge_heights,'overall_height_mm':upper.BoundingBox().zmax,
         'previous_rim_above_plate_mm':cfg['cover_gap_above_plate_mm']+cfg['cover_thickness_mm']}

print('Export prototype parts and reference assembly',flush=True)
# Upper is printed flat face down. The full-size model remains bigger than a
# 256 mm print bed; the split files preserve the rounded perimeter.
upper_local=unplace(upper)
upper_print=upper_local.rotate((0,0,0),(1,0,0),180)
export(upper_print,'plate-upper',True)
export(base,'case-bottom',True)
export(shoe,'nut-carrier',True)
export(bezel,'usb-bezel',True)
shutil.copy2(SRC/'led-diffuser.stl',OUT/'led-diffuser.stl')
assembly=cq.Assembly(name='v10-hidden-mount-prototype')
for name,s,col in [('plate-upper',upper,(.23,.34,.43)),('case-bottom',base,(.14,.20,.26)),('usb-bezel',bezel,(.23,.34,.43)),('unchanged-v10-PCB',board,(.1,.4,.25)),('battery-reserve',battery,(.85,.65,.24))]:
    assembly.add(s,name=name,color=cq.Color(*col))
for name,s in shoes:assembly.add(s,name=name+'-carrier',color=cq.Color(.8,.48,.16))
for name,s in hardware:assembly.add(s,name=name,color=cq.Color(.65,.68,.7))
for name,s in parts:assembly.add(s,name=name,color=cq.Color(.2,.23,.26))
assembly.export(str(OUT/'assembly.step'))
for name,s in [('upper',upper),('bottom',base),('bezel',bezel),('board',board),('battery',battery)]+[(n+'-carrier',s) for n,s in shoes]+hardware:
    s.exportBrep(str(REF/(name+'.brep')))
    cq.exporters.export(s,str(REF/(name+'-assembly.stl')),tolerance=.035,angularTolerance=.15)
    clean_degenerate_facets(REF/(name+'-assembly.stl'))

print('Check final solids against PCB, parts, pins, battery and each other',flush=True)
collisions=[]
structure=[('upper',upper),('base',base),('bezel',bezel)]+shoes+hardware
for i,(name,s) in enumerate(structure):
    print('Check structure',name,flush=True)
    for other,t in electronics:
        v=iv(s,t)
        if v>1e-4:collisions.append({'part':name,'obstacle':other,'volume_mm3':v})
    for other,t in structure[:i]:
        v=iv(s,t)
        if v>1e-4:collisions.append({'part':name,'obstacle':other,'volume_mm3':v})
# Switch body envelopes and moving keycap envelope use the established v10 fit
# assumptions. Final travel/actual stabilizers must be physically checked.
switches=[]
for s in geo['switches']:
    x,y=s['xy']
    sw=block(x-6.975,y-6.975,T,13.95,13.95,2.2).fuse(block(x-7.5,y-7.5,T+2.2,15,15,3.3),cyl(x,y,T+5.5,3.25,3.1))
    switches.append(place(sw))
    for name,solid in [('upper',upper),('bezel',bezel)]:
        v=iv(place(sw),solid)
        if v>1e-4:collisions.append({'part':name,'obstacle':s['ref'],'volume_mm3':v})
movement=[]
# Only the perimeter can obstruct a populated PCB moving down away from the
# plate. Use that simpler solid for all wall checks; separately check actual
# upper-pin channels during the first millimetre of withdrawal.
insertion_wall=upper.cut(place(block(-.02,-.02,T-.02,W+.04,D+.04,8))).clean()
pin_channels=[(n,s) for n,s in pins if bounds(s).zmax>plane_z(bounds(s).ymin,T)]
for dz in [.2,.5,1,2,5,12,25]:
    print('Check insertion',dz,flush=True)
    # The bare populated PCB enters with the nut carriers and bezel removed.
    for name,s in [('PCB',board)]+parts+pins:
        moved=s.translate((0,0,-dz));b=bounds(moved)
        # This rectangle is wholly inside the wall, including the rebates.
        if b.xmin>=2.05 and b.xmax<=CW-2.05 and b.ymin>=2.05 and b.ymax<=CD-2.05:
            v=0.
        else:v=iv(moved,insertion_wall)
        if v>1e-4:movement.append({'part':name,'down_mm':dz,'upper_intersection_mm3':v})
    if dz<=1:
        for name,s in pin_channels:
            v=iv(s.translate((0,0,-dz)),upper)
            if v>1e-4:movement.append({'part':name,'down_mm':dz,'pin_channel_intersection_mm3':v})
    # The battery is attached to, and travels with, the removable bottom.
    for name,s in [('PCB',board)]+parts+pins:
        v=iv(base.translate((0,0,-dz)),s)
        if v>1e-4:movement.append({'part':'bottom','down_mm':dz,'obstacle':name,'intersection_mm3':v})
result={'prototype':True,'physical_fit_verified':False,'pcb_changed':False,'external_dimensions_mm':[CW,CD],'front_rear_heights_mm':edge_heights,'surface':surface,'plate_thickness_mm':PT-PB,'mounts':mounts,'hardware_count':{'M2x4_button_screws':8,'DIN934_M2_nuts':8,'printed_nut_carriers':8},'nut_nominal_engagement_mm':1.6,'battery_reserve_mm':bat['reserved_dimensions_mm'],'collisions':collisions,'insertion_collisions':movement,'exports':exports,'tilt_degrees':DEG,'pcb_origin_z':Z0}
(OUT/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print('COLLISIONS',json.dumps(collisions,indent=2),flush=True)
print('MOVEMENT',json.dumps(movement,indent=2),flush=True)
print('Primary model exported',flush=True)
