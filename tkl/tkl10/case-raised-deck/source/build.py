#!/usr/bin/env python3
"""Second V10 enclosure: unchanged switch plate with raised, rounded key wells.

Manifold boolean meshes are mechanical prototypes, in millimetres. Original
CAD and all manufacturing files are read-only. No hidden relocation of keys.
"""
from pathlib import Path
import base64
import hashlib
import json
import math
import shutil
import struct
import numpy as np
import manifold3d as mf
from shapely.geometry import box, Polygon
from shapely.ops import unary_union

OUT = Path(__file__).resolve().parents[1]
ROOT = OUT.parent
OLD = ROOT / 'case-hidden-mounts'
STUDY = ROOT / 'render-keycaps-lighting'
REF = OUT / 'reference'
PRINT = OUT / 'prints'
for p in [REF, PRINT]: p.mkdir(exist_ok=True)
cfg = json.loads((ROOT/'case/fit-config.json').read_text())
geo = json.loads((ROOT/'case/board-geometry.json').read_text())
fit = json.loads((ROOT/'case/fit-report.json').read_text())
design = json.loads((OUT/'design-config.json').read_text())
assets = json.loads((STUDY/'assets.json').read_text())
CW, CD = cfg['fixed_footprint_mm']
W, D, T = [geo['board'][k] for k in ['width', 'depth', 'thickness']]
PT = T + cfg['plate_top_above_pcb_mm']
PB = PT - cfg['plate_thickness_mm']
A = math.radians(fit['tilt_degrees'])
C, S = math.cos(A), math.sin(A)
Z0 = fit['pcb_underside_front_origin_z']
TIP = T + design['switch_tip_above_pcb_top_mm']
CAP_BASE = TIP - design['socket_engagement_mm']
TOP = CAP_BASE - design['rest_skirt_shadow_gap_mm']
RAISE = TOP - PT
hashes = {}
exports = []
discarded_numerical_slivers = []


def read(path):
    b = path.read_bytes()
    hashes[str(path.relative_to(ROOT))] = hashlib.sha256(b).hexdigest()
    return b


def manifold(v, f):
    m = mf.Mesh(np.array(v, dtype=np.float32, order='C', copy=True), np.array(f, dtype=np.uint32, order='C', copy=True), tolerance=0.00003)
    m.merge()
    s = mf.Manifold(m)
    assert s.status() == mf.Error.NoError, s.status()
    return s


def stl(path):
    b = read(path)
    n = struct.unpack_from('<I', b, 80)[0]
    v = np.array([struct.unpack_from('<3f', b, 96+50*i+12*j) for i in range(n) for j in range(3)])
    vv, inv = np.unique(np.round(v, 5), axis=0, return_inverse=True)
    return manifold(vv, inv.reshape(-1, 3))


def unpack(part):
    return manifold(np.frombuffer(base64.b64decode(part['positions']), dtype='<f4').reshape(-1, 3),
                    np.frombuffer(base64.b64decode(part['indices']), dtype='<u4').reshape(-1, 3))


def pack(s, name, material):
    assert s.status() == mf.Error.NoError and s.volume() > 0
    s=s.simplify(.001)
    m = s.to_mesh()
    return dict(name=name, material=material, triangles=len(m.tri_verts),
                positions=base64.b64encode(np.asarray(m.vert_properties[:, :3], dtype='<f4').tobytes()).decode(),
                indices=base64.b64encode(np.asarray(m.tri_verts, dtype='<u4').tobytes()).decode())


def place(s):
    return s.rotate((fit['tilt_degrees'], 0, 0)).translate((2.4, 2.4, Z0))


def local(s):
    return s.translate((-2.4, -2.4, -Z0)).rotate((-fit['tilt_degrees'], 0, 0))


def block(x, y, z, w, d, h):
    return mf.Manifold.cube((w, d, h)).translate((x, y, z))


def plane_z(y, z):
    return Z0 + (y-2.4)*math.tan(A) + z/C


def section(p):
    contours = []
    for q in list(p.geoms) if hasattr(p, 'geoms') else [p]:
        if q.is_empty: continue
        # CrossSection Positive fill needs consistently wound outer / inner rings.
        from shapely.geometry.polygon import orient
        q = orient(q, sign=1)
        contours.append(np.asarray(q.exterior.coords)[:-1])
        contours.extend(np.asarray(r.coords)[:-1] for r in q.interiors)
    return mf.CrossSection(contours, mf.FillRule.Positive)


def solid(p, z, h):
    return section(p).extrude(h).translate((0, 0, z))


def rounded_rect(x0, y0, x1, y1, r):
    return box(x0+r, y0+r, x1-r, y1-r).buffer(r, quad_segs=20)


def ring_points(inset, height):
    # Constant world-XY footprint; all contour vertices lie on the tilted plane.
    r = design['outer_corner_radius_mm']-inset
    pts = []
    for x, y, start in [(CW-inset-r, CD-inset-r, 0),
                         (inset+r, CD-inset-r, 90),
                         (inset+r, inset+r, 180),
                         (CW-inset-r, inset+r, 270)]:
        for j in range(17):
            t = math.radians(start+90*j/16)
            px, py = x+r*math.cos(t), y+r*math.sin(t)
            pts.append([px, py, plane_z(py, height)])
    return pts


def outer_envelope():
    # Explicit loft keeps smooth continuous vertical walls and a 2.5 mm roll-over.
    r = design['top_edge_roll_radius_mm']
    rings = [ring_points(0, 1.18), ring_points(0, TOP-r)]
    for j in range(1, 25):
        t = math.pi/2*j/24
        rings.append(ring_points(r*(1-math.cos(t)), TOP-r+r*math.sin(t)))
    v = [p for row in rings for p in row]
    n = len(rings[0]); f = []
    for k in range(len(rings)-1):
        for j in range(n):
            a=k*n+j; b=k*n+(j+1)%n; c=b+n; d=a+n
            f.extend([[a,b,c],[a,c,d]])
    # Convex rounded contour: triangle fans close both end faces.
    for k, flip in [(0, True), (len(rings)-1, False)]:
        center=np.mean(np.array(rings[k]),axis=0);idx=len(v);v.append(center.tolist())
        for j in range(n):
            tri=[idx,k*n+j,k*n+(j+1)%n]
            f.append(tri[::-1] if flip else tri)
    return manifold(v, f)


def export(s, name, print_orientation=False, require_connected=True):
    assert s.status() == mf.Error.NoError and s.volume()>0, name
    if require_connected: assert len(s.decompose())==1, (name, 'disconnected')
    s=s.simplify(.001)
    if print_orientation:
        s=local(s).rotate((180,0,0))
        b=s.bounding_box();s=s.translate((-b[0],-b[1],-b[2]))
    m=s.to_mesh()
    # STL stores float32. Re-import that representation before the final
    # 1-micron simplification to remove Boolean slivers lost in float rounding.
    s=manifold(m.vert_properties[:,:3],m.tri_verts).simplify(.001)
    if require_connected: assert len(s.decompose())==1,(name,'STL round-trip disconnected')
    m=s.to_mesh();v=m.vert_properties[:,:3];f=m.tri_verts
    _,inverse=np.unique(v,axis=0,return_inverse=True);faces=inverse[f]
    edges=np.sort(np.concatenate([faces[:,[0,1]],faces[:,[1,2]],faces[:,[2,0]]]),axis=1)
    _,edge_counts=np.unique(edges,axis=0,return_counts=True)
    p=v[f];areas=np.linalg.norm(np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]),axis=1)
    assert np.all(edge_counts==2) and np.all(areas>1e-10),(name,'nonmanifold or zero-area STL facets')
    path=(PRINT if print_orientation else REF)/(name+'.stl')
    with path.open('wb') as out:
        out.write(b'V10 Edition 2 prototype; millimetres'.ljust(80,b' '));out.write(struct.pack('<I',len(f)))
        for face in f:
            p=v[face];normal=np.cross(p[1]-p[0],p[2]-p[0]);norm=np.linalg.norm(normal)
            if norm: normal/=norm
            out.write(struct.pack('<12fH',*normal,*p.flatten(),0))
    b=s.bounding_box()
    exports.append(dict(file=str(path.relative_to(OUT)), triangles=len(f), volume_mm3=s.volume(),
                        bounds_mm=[b[i+3]-b[i] for i in range(3)], connected_components=len(s.decompose()),
                        manifold_status=str(s.status()), minimum_z_mm=b[2]))


def clean_split(s, name):
    pieces = sorted(s.decompose(), key=lambda p:p.volume(), reverse=True)
    if len(pieces)>1:
        removed=sum(p.volume() for p in pieces[1:])
        assert removed<.0001,(name,'substantial disconnected material',removed)
        discarded_numerical_slivers.append(dict(part=name,volume_mm3=removed,count=len(pieces)-1))
    return pieces[0]


upper=stl(OLD/'reference/upper-assembly.stl')
bottom=stl(OLD/'reference/bottom-assembly.stl')
bezel=stl(OLD/'reference/bezel-assembly.stl')
board=stl(OLD/'reference/board-assembly.stl')
battery=stl(OLD/'reference/battery-assembly.stl')
read(STUDY/'assets.json')
read(ROOT/'case/board-geometry.json');read(ROOT/'case/fit-config.json');read(ROOT/'case/fit-report.json')

# One main typing well, one navigation well, a T-shaped arrow well, and the
# function clusters. No narrow ornamental bars between typing rows.
opens=cfg['integrated_upper']['openings']
typing=box(*opens['typing']);nav=box(*opens['navigation'])
row_keys=sorted([k for k in geo['switches'] if k['xy'][1]>100],key=lambda k:k['xy'][0])
groups=[]
for k in row_keys:
    if not groups or k['xy'][0]-groups[-1][-1]['xy'][0]>20: groups.append([])
    groups[-1].append(k)
functions=[box(g[0]['xy'][0]-9.6,101.99,g[-1]['xy'][0]+9.6,120.19) for g in groups]
arrows=unary_union([box(291.9825,1.9775,349.2825,20.1775),box(311.0325,11.0,330.2325,39.2275)])
well_polys=[typing,nav,arrows]+functions
well_polys=[p.buffer(-.65,join_style=1).buffer(.65,quad_segs=12) for p in well_polys]
wells=unary_union(well_polys)

envelope=outer_envelope()
# Preserve the old interior, carriers, port lips and lower wall geometry.
inner=rounded_rect(2,2,CW-2,CD-2,1)
low_void=solid(inner,-20,60)
top_of_low_void=place(block(-20,-20,-30,CW+40,CD+40,PT+.03+30))
addition=envelope-(low_void ^ top_of_low_void)
well_tool=place(solid(wells,PT-.15,TOP-PT+20))
addition-=well_tool
# A gentle 0.35 mm chamfer on the well edges avoids a sharp top lip. Opening
# only grows toward the top, so the nominal 0.6 mm skirt clearance stays valid.
ch=design['well_top_chamfer_mm']
for k in range(12):
    delta=ch*(k+1)/12
    tool=place(solid(wells.buffer(delta,quad_segs=12),TOP-ch+ch*k/12,20))
    addition-=tool
raised=upper+addition
assert raised.status()==mf.Error.NoError and len(raised.decompose())==1

variants={}
variants['original']=[pack(raised,'raised-upper','shell')]
variants['perkey']=variants['original']
for name in ['pills','nav','deck','halo']:
    parts=assets['variants'][name]
    if name=='nav':
        shell=unpack(parts[0])+addition
        # Keep the existing under-plate guide route; only its last section rises.
        outlet=rounded_rect(306,47.4,334,48.6,.58)
        tool=place(solid(outlet.buffer(.06),PT-.2,RAISE+.5))
        shell-=tool
        guide=unpack(parts[1])+place(solid(outlet,PT-.14,RAISE+.14))
        variants[name]=[pack(shell,'raised-navigation-shell','shell'),pack(guide,'raised-navigation-lightguide','lightWindow')]
    elif name=='deck':
        # The raised deck is frosted too; other frame surfaces remain opaque.
        deck_zone=place(block(.4,.8,PT-.15,W-.8,D-1.2,RAISE+.3))
        raised_deck=addition ^ deck_zone
        frame=unpack(parts[0])+(addition-deck_zone)
        deck=unpack(parts[1])+raised_deck
        variants[name]=[pack(frame,'raised-frosted-frame','shell'),pack(deck,'raised-frosted-deck','frostedDeck')]
    else:
        variants[name]=[pack(unpack(parts[0])+addition,'raised-'+parts[0]['name'],parts[0]['material'])]+parts[1:]

print('Validate retained parts and nominal key travel',flush=True)
collisions=[]
for name,s in [('bottom',bottom),('bezel',bezel),('PCB',board),('battery-reserve',battery)]:
    vol=(addition ^ s).volume()
    assert vol<.005,(name,vol)
    collisions.append(dict(part=name,added_material_intersection_mm3=vol))
for i in range(1,9):
    for kind in ['carrier','screw','nut']:
        s=stl(OLD/f'reference/M{i}-{kind}-assembly.stl')
        vol=(addition ^ s).volume();assert vol<.005,(i,kind,vol)

travel_checks=[]
for key in geo['switches']:
    x,y=key['xy'];w=key['units']*19.05-1.05
    # Conservative rectangular envelope contains every XVX appearance mesh,
    # including its widest skirt, through all 2.8 mm of downward motion.
    min_z=TIP-3.1-design['total_switch_travel_mm']
    sweep=place(block(x-w/2,y-8.5,min_z,w,17,TIP-1.5+5-min_z))
    vol=(raised ^ sweep).volume();assert vol<.005,(key['ref'],vol)
    travel_checks.append(dict(key=key['ref'],swept_cap_case_intersection_mm3=vol))

export(raised,'upper-assembly')
export(raised,'plate-upper',True)
export(unpack(variants['nav'][0]),'upper-navigation-assembly')
export(unpack(variants['nav'][0]),'plate-upper-navigation',True)
export(unpack(variants['nav'][1]),'navigation-guide-assembly')

# Preserve the established staggered seam and plate half-lap. The new raised
# webs share its 0.2 mm bonded butt seam; the lower plate retains the 4 mm lap.
rows=sorted(set(round(k['xy'][1],4) for k in geo['switches']));seam=[]
for i,y in enumerate(rows):
    xs=sorted(k['xy'][0] for k in geo['switches'] if abs(k['xy'][1]-y)<.01)
    xx=min([(a+b)/2 for a,b in zip(xs,xs[1:]) if b-a>18],key=lambda x:abs(x-W/2))
    lo=-20 if i==0 else (rows[i-1]+y)/2
    hi=D+20 if i==len(rows)-1 else (rows[i+1]+y)/2
    seam.extend([(xx,lo),(xx,hi)])
left=Polygon([(-20,-20)]+seam+[(-20,D+20)])
domain=box(-20,-20,W+20,D+20);mid=(PB+PT)/2;gap=.2;overlap=4
for model_name,model in [('plate-upper',raised),('plate-upper-navigation',unpack(variants['nav'][0]))]:
    halves=[]
    for j,side in enumerate(['left','right']):
        core=left.buffer(-overlap/2-gap/2,join_style=2) if j==0 else domain.difference(left.buffer(overlap/2+gap/2,join_style=2))
        outside=left.buffer(-gap/2,join_style=2) if j==0 else domain.difference(left.buffer(gap/2,join_style=2))
        lap=left.buffer(overlap/2-gap/2,join_style=2) if j==0 else domain.difference(left.buffer(-overlap/2+gap/2,join_style=2))
        mask=solid(core,PB-.01,PT-PB+.02)+solid(outside,-30,PB+30)+solid(outside,PT,30)
        mask+=solid(lap,PB,mid-gap/2-PB) if j==0 else solid(lap,mid+gap/2,PT-mid-gap/2)
        half=clean_split(model ^ place(mask),model_name+'-'+side);halves.append(half)
        export(half,model_name+'-'+side,True)
    assert (halves[0] ^ halves[1]).volume()<.01

# Small physical trial of the actual front perimeter and switch seating plate.
coupon=raised ^ block(0,0,-1,46,44,40)
export(coupon,'front-fit-coupon',True)
rear_coupon=raised ^ block(13,90,-1,41,CD-90,40)
export(rear_coupon,'usb-fit-coupon-upper',True)
for name in ['case-bottom.stl','case-bottom-left.stl','case-bottom-right.stl','nut-carrier.stl','usb-bezel.stl','led-diffuser.stl','usb-coupon-bottom.stl','usb-coupon-pcb.stl']:
    read(OLD/name);shutil.copy2(OLD/name,PRINT/name)

report=dict(status='Mechanical prototype; physical fit and optics unverified',edition=design['edition'],
            target_keycaps=design['target_keycaps'],raised_by_mm=RAISE,top_board_local_z_mm=TOP,
            skirt_rest_board_local_z_mm=CAP_BASE,rest_shadow_gap_mm=CAP_BASE-TOP,
            nominal_top_plane_front_rear_mm=[plane_z(0,TOP),plane_z(CD,TOP)],
            original_top_plane_front_rear_mm=[plane_z(0,PT),plane_z(CD,PT)],
            footprint_mm=[CW,CD],keycap_clearance_each_side_mm=.6,full_travel_mm=2.8,
            minimum_cap_to_original_plate_at_full_travel_mm=TIP-3.1-2.8-PT,
            pcb_changed=False,pcb_and_battery_moved=False,top_screw_holes=False,
            grouped_key_wells=len(well_polys),thin_typing_row_separators=False,
            added_material_checks=collisions,travel_checks=travel_checks,
            exports=exports,source_sha256=hashes,physical_fit_verified=False,
            discarded_numerical_slivers=discarded_numerical_slivers,
            stl_surface_simplification_budget_mm=.002,
            limits=['XVX geometry and 3 mm engagement remain nominal assumptions, not measured underside CAD.',
                    'The flat top targets the XVX skirt; alternate caps remain selectable but will not all sit flush.',
                    'Grouped key wells conceal the switches from outside; gaps between keys remain open for travel.',
                    'The switch seating plate remains 1.5 mm; do not press switches into the raised cosmetic openings.',
                    'Raised top / skirt height does not raise the PCB, battery, switches or keycap tops.',
                    'The light bar needs a longer terminal light pipe; brightness requires a physical test.',
                    'Split shells require bonding and finishing; no top-to-body perimeter seam is introduced.'])
assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
(OUT/'viewer-assets.json').write_text(json.dumps(dict(variants=variants,report=report),separators=(',',':')))
print(json.dumps({k:report[k] for k in ['raised_by_mm','top_board_local_z_mm','nominal_top_plane_front_rear_mm','grouped_key_wells']},indent=2),flush=True)
print('Saved Edition 2 prototype meshes and viewer assets',flush=True)
