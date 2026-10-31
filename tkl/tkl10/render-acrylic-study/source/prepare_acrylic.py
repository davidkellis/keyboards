#!/usr/bin/env python3
"""Partition the unchanged V10 case for an acrylic appearance study only.

No manufacturing or printing files are changed. The 1.5 mm visual plate uses
the existing stack; switch-clip thickness and a new retention design still
require a physical coupon before any fabrication release.
"""
from pathlib import Path
import base64,hashlib,json,math,struct
import numpy as np
import manifold3d as mf

OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parent
g=json.loads((ROOT/'case/board-geometry.json').read_text())
c=json.loads((ROOT/'case/fit-config.json').read_text())
f=json.loads((ROOT/'case/fit-report.json').read_text())
W,D,T=[g['board'][k] for k in ['width','depth','thickness']]
PT=T+c['plate_top_above_pcb_mm'];PB=PT-c['plate_thickness_mm']
angle=f['tilt_degrees'];z0=f['pcb_underside_front_origin_z'];hashes={}

def read(path):
    b=path.read_bytes();hashes[str(path.relative_to(ROOT))]=hashlib.sha256(b).hexdigest();return b

def manifold(v,faces):
    mesh=mf.Mesh(np.array(v,dtype=np.float32,order='C',copy=True),np.array(faces,dtype=np.uint32,order='C',copy=True),tolerance=.00003)
    mesh.merge();s=mf.Manifold(mesh);assert s.status()==mf.Error.NoError;return s

def stl(path):
    b=read(path);n=struct.unpack_from('<I',b,80)[0]
    v=np.array([struct.unpack_from('<3f',b,96+50*i+12*j) for i in range(n) for j in range(3)])
    u,idx=np.unique(np.round(v,5),axis=0,return_inverse=True);return manifold(u,idx.reshape(-1,3))

def unpack(a):
    return manifold(np.frombuffer(base64.b64decode(a['positions']),dtype='<f4').reshape(-1,3),np.frombuffer(base64.b64decode(a['indices']),dtype='<u4').reshape(-1,3))

def pack(s,name,material):
    assert s.volume()>0 and s.status()==mf.Error.NoError
    m=s.simplify(.001).to_mesh()
    return dict(name=name,material=material,triangles=len(m.tri_verts),positions=base64.b64encode(np.asarray(m.vert_properties[:,:3],dtype='<f4').tobytes()).decode(),indices=base64.b64encode(np.asarray(m.tri_verts,dtype='<u4').tobytes()).decode())

def place(s):return s.rotate((angle,0,0)).translate((2.4,2.4,z0))
def local(s):return s.translate((-2.4,-2.4,-z0)).rotate((-angle,0,0))
def box(x,y,z,w,d,h):return mf.Manifold.cube((w,d,h)).translate((x,y,z))

leds=[p for p in g['components'] if p['ref'].startswith('LED')]
ledxy=[[(p['bounds'][0]+p['bounds'][2])/2,(p['bounds'][1]+p['bounds'][3])/2] for p in leds]
old=stl(ROOT/'case-hidden-mounts/reference/upper-assembly.stl')
raised_data=json.loads(read(ROOT/'case-raised-deck/viewer-assets.json'))
raised=unpack(raised_data['variants']['original'][0])
# STL vertices and the tilted cut plane differ by a few micrometres. A tiny
# overlap avoids retaining opaque, coplanar flakes over the clear top face.
# This is a visual Boolean tolerance, not a new plate thickness specification.
epsilon=.002
tool=place(box(.4,.8,PB-epsilon,W-.8,D-1.2,PT-PB+2*epsilon))
editions={};checks=[]
for edition,upper in [('current',old),('raised',raised)]:
    plate=upper ^ tool;frame=upper-tool
    assert abs(upper.volume()-plate.volume()-frame.volume())<.05
    # Clear input windows replace the six existing empty optical holes. They
    # enter at the original sources, with no invented edge-mounted emitters.
    for x,y in ledxy:
        plate+=place(mf.Manifold.cylinder(PT-PB,1.18,circular_segments=40).translate((x,y,PB))) ^ tool
    section=local(plate).slice(PB+.05)
    for x,y in ledxy:section-=mf.CrossSection.circle(1.4,40).translate((x,y))
    reflector=place(section.extrude(.06).translate((0,0,PB-.08)))
    collectors=[]
    for led,(x,y) in zip(leds,ledxy):
        s=place(mf.Manifold.cylinder(.5,1.03,circular_segments=32).translate((x,y,PB-.25)))
        collectors.append(pack(s,led['ref']+' acrylic input collector','acrylic'))
    editions[edition]=dict(frame=pack(frame,edition+' opaque support frame','shell'),
                           plate=pack(plate,edition+' acrylic switch plate','acrylic'),
                           reflector=pack(reflector,edition+' white reflector backing','reflector'),collectors=collectors)
    checks.append(dict(edition=edition,original_upper_volume_mm3=upper.volume(),
                       frame_volume_mm3=frame.volume(),plate_volume_mm3=plate.volume(),
                       plate_stack_local_z_mm=[PB,PT],visual_boolean_overlap_mm=epsilon,source_count=len(collectors),
                       note='Visual partition; new mechanical retention and actual material thickness are not released.'))

for name in ['case/board-geometry.json','case/fit-config.json','case/fit-report.json']:read(ROOT/name)
report=dict(status='Appearance study, not optical simulation or manufacturing release',source_sha256=hashes,
            pcb_changed=False,led_count=6,led_positions_board_xy_mm=ledxy,
            series_resistors_ohm=1000,visual_plate_thickness_mm=PT-PB,reflector_thickness_mm=.06,
            editions=checks,physical_fit_verified=False,
            limits=['The existing 1.5 mm CAD envelope is retained for visual comparison only; Kailh drawing references 1.2 mm aluminum. Test clips before specifying acrylic thickness.',
                    'Plain clear acrylic does not automatically spread upward LED light uniformly. Entry coupling, surface extraction and holes matter.',
                    'Scattering fields are normalized appearance proxies, not measured optical properties, lux values or an efficiency forecast.',
                    'All acrylic options use the same six source locations and the same initial input budget. Wider modeled spread reduces peak brightness.',
                    'White backing hides the PCB while leaving the six input windows open; its modeled gain is illustrative.',
                    'No acrylic option adds LEDs or makes every legend emit light.',
                    'Actual acrylic support, attachment, pin reliefs, switch clips and full-travel fit need a mechanical prototype.'])
assert all(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha for name,sha in hashes.items())
(OUT/'acrylic-assets.json').write_text(json.dumps(dict(editions=editions,report=report),separators=(',',':')))
(OUT/'acrylic-study.json').write_text(json.dumps(report,indent=2)+'\n')
print('Prepared two case editions with acrylic plate / backing / six input collectors.')
