#!/usr/bin/env python3
"""Prepare source keycaps and boolean lighting concepts for visualization only.

Requires numpy + manifold3d. Source v10 fabrication geometry stays read-only.
"""
from pathlib import Path
import base64
import hashlib
import json
import math
import struct
import xml.etree.ElementTree as ET
import zipfile
import numpy as np
import manifold3d as mf

OUT = Path(__file__).resolve().parents[1]
ROOT = OUT.parent
REF = OUT / 'reference'
CASE = ROOT / 'case-hidden-mounts'
geo = json.loads((ROOT / 'case/board-geometry.json').read_text())
fit = json.loads((ROOT / 'case/fit-report.json').read_text())
cfg = json.loads((ROOT / 'case/fit-config.json').read_text())
source_hashes = {}


def manifold(v, f):
    mesh = mf.Mesh(np.asarray(v, dtype=np.float32), np.asarray(f, dtype=np.uint32), tolerance=0.00002)
    mesh.merge()
    result = mf.Manifold(mesh)
    assert result.status() == mf.Error.NoError, result.status()
    assert result.volume() > 0
    return result


def read_stl(path):
    data = path.read_bytes()
    source_hashes[str(path.relative_to(ROOT))] = hashlib.sha256(data).hexdigest()
    n = struct.unpack_from('<I', data, 80)[0]
    vertices, faces, lookup = [], [], {}
    for i in range(n):
        face = []
        for j in range(3):
            point = struct.unpack_from('<3f', data, 96 + 50 * i + 12 * j)
            k = tuple(round(a, 5) for a in point)
            if k not in lookup:
                lookup[k] = len(vertices)
                vertices.append(point)
            face.append(lookup[k])
        faces.append(face)
    return np.array(vertices), np.array(faces)


def read_3mf(path):
    data = path.read_bytes()
    source_hashes[str(path.relative_to(ROOT))] = hashlib.sha256(data).hexdigest()
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read('3D/3dmodel.model'))
    ns = {'m': 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
    vertices = [[float(p.attrib[k]) for k in ('x', 'y', 'z')] for p in root.findall('.//m:vertex', ns)]
    faces = [[int(p.attrib[k]) for k in ('v1', 'v2', 'v3')] for p in root.findall('.//m:triangle', ns)]
    return np.array(vertices), np.array(faces)


def pack(v, f, **extra):
    return dict(positions=base64.b64encode(np.asarray(v, dtype='<f4').tobytes()).decode(),
                indices=base64.b64encode(np.asarray(f, dtype='<u4').tobytes()).decode(),
                triangles=len(f), **extra)


def packed(s, **extra):
    assert s.status() == mf.Error.NoError and not s.is_empty()
    m = s.to_mesh()
    return pack(m.vert_properties[:, :3], m.tri_verts, **extra)


caps = {}
measurements = []
for profile in ['flat', 'glass']:
    caps[profile] = {}
    for u in ['1.00', '1.25', '1.50', '1.75', '2.00', '2.25', '2.75', '6.25']:
        p = REF / f'{profile}-{u}u.{"3mf" if profile == "flat" else "stl"}'
        v, f = read_3mf(p) if profile == 'flat' else read_stl(p)
        lo, hi = v.min(axis=0), v.max(axis=0)
        # Both releases are face-down print models. Wide Glass caps have
        # stabilizer bosses 0.9 mm longer than their central switch socket;
        # align by that central socket so every key's top stays at one height.
        v[:, 0] -= (lo[0] + hi[0]) / 2
        v[:, 1] = -(v[:, 1] - (lo[1] + hi[1]) / 2)
        central = v[(np.abs(v[:, 0]) < 3.3) & (np.abs(v[:, 1]) < 3.3)]
        socket_z = central[:, 2].max()
        v[:, 2] = socket_z - v[:, 2]
        original = manifold(v, f)
        simplified = original.simplify(0.025)
        caps[profile][str(float(u))] = packed(simplified, height=float(socket_z - lo[2]),
                                            bounds=(hi - lo).tolist(), source_file=p.name)
        measurements.append(dict(profile=profile, units=float(u), source_bounds_mm=(hi-lo).tolist(),
                                 central_socket_to_top_mm=float(socket_z-lo[2]),
                                 source_triangles=len(f), viewer_triangles=simplified.num_tri(),
                                 maximum_surface_simplification_mm=0.025))
        print(profile, u, len(f), '->', simplified.num_tri(), flush=True)

upper = manifold(*read_stl(CASE / 'reference/upper-assembly.stl'))
a = math.radians(fit['tilt_degrees'])
c, s = math.cos(a), math.sin(a)
z0 = fit['pcb_underside_front_origin_z']
matrix = np.array([[1, 0, 0, 2.4], [0, c, -s, 2.4], [0, s, c, z0]])


def placed(shape):
    return shape.transform(matrix)


def cylinder(x, y, z, r, h):
    return mf.Manifold.cylinder(h, r, circular_segments=40).translate((x, y, z))


def capsule(x, y, z, length, width, height, vertical=False):
    d = (length-width)/2
    one = cylinder(x if vertical else x-d, y-d if vertical else y, z, width/2, height)
    two = cylinder(x if vertical else x+d, y+d if vertical else y, z, width/2, height)
    return (one + two).hull()


leds = [p for p in geo['components'] if p['ref'].startswith('LED')]
filled = upper
for led in leds:
    x, y, xx, yy = led['bounds']
    filled += placed(cylinder((x+xx)/2, (y+yy)/2, 2.28, 1.18, 1.54))

cut = filled
diffusers = []
window_report = []
for led in leds:
    x, y, xx, yy = led['bounds']
    cx, cy = (x+xx)/2, (y+yy)/2
    vertical = cy < 50
    ox = cx+2.25 if led['ref'] == 'LED2' else cx
    # Slender visible outlets fit the gaps even for the square printed caps.
    top = capsule(ox, cy, 3.66, 11, 0.65, 0.14, vertical)
    intake = cylinder(cx, cy, 2.30, 1.05, 0.12)
    diffuser = (top + intake).hull()
    cutter = (capsule(ox, cy, 3.62, 11.12, 0.77, 0.30, vertical) + cylinder(cx, cy, 2.22, 1.12, 0.12)).hull()
    cut -= placed(cutter)
    diffusers.append(packed(placed(diffuser), name=led['ref']+'-pill', material='lightWindow'))
    window_report.append(dict(ref=led['ref'], source_xy_mm=[cx, cy], outlet_xy_mm=[ox, cy],
                              outlet_length_width_mm=[11, 0.65], vertical=vertical))

deck_tool = placed(mf.Manifold.cube((geo['board']['width']-.8, geo['board']['depth']-1.2, 1.65))
                   .translate((.4, .8, 2.22)))
deck = filled ^ deck_tool
deck_frame = filled - deck_tool
# A lower-edge insert, which needs redirected / additional light sources.
band_tool = mf.Manifold.cube((400, 180, .85)).translate((-10, -10, .6))
halo_band = upper ^ band_tool
halo_shell = upper - band_tool
led2 = next(p for p in leds if p['ref'] == 'LED2')
x,y,xx,yy=led2['bounds'];cx,cy=(x+xx)/2,(y+yy)/2
nav_top = capsule(320,48,3.66,28,1.2,.14)
nav_guide = (nav_top + cylinder(cx,cy,2.3,1.05,.12)).hull()
nav_tool = (capsule(320,48,3.62,28.12,1.32,.3) + cylinder(cx,cy,2.22,1.12,.12)).hull()
nav_shell = (upper + placed(cylinder(cx,cy,2.28,1.18,1.54))) - placed(nav_tool)
variants = {
    'nav': [packed(nav_shell, name='navigation-lightbar-shell', material='shell'),
            packed(placed(nav_guide), name='navigation-lightguide', material='lightWindow')],
    'pills': [packed(cut, name='pill-window-shell', material='shell')] + diffusers,
    'deck': [packed(deck_frame, name='frosted-deck-frame', material='shell'),
             packed(deck, name='frosted-key-deck', material='frostedDeck')],
    'halo': [packed(halo_shell, name='halo-upper-shell', material='shell'),
             packed(halo_band, name='lower-edge-diffuser', material='halo')],
}
report = dict(status='Visual concepts, not manufacturing releases or optical simulations',
              source_sha256=source_hashes, scotto_keycaps=measurements, pill_windows=window_report,
              switch=dict(part='CPG1353S01D02-01 / Deep Sea Silent MINI tactile family',
                          source='https://www.kailhswitch.com/uploads/15927/files/CPG1353S01D02-01-data-sheet.pdf',
                          total_travel_mm=2.8, exposed_cross_stem_mm=3.1,
                          flange_to_stem_top_mm=6.4, pcb_to_flange_mm=2.2,
                          led_offset_after_rotation_board_xy_mm=[0,-4.93],
                          physical_sample_verified=False),
              limits=['No switch/keycap seating or full-travel clearance is certified.',
                      'Scotto Flat is 6.7 mm overall; Glass MX is 5.7 mm from central socket opening to top. Wide Glass stabilizer bosses extend another 0.9 mm. Neither is claimed lower than a nominal 5 mm XVX cap.',
                      'Pills collect the six existing LED positions; LED2 outlet shifts 2.25 mm to clear the right Shift edge.',
                      'Frosted key deck retains six light pools; uniform illumination is not assumed.',
                      'Navigation lightbar routes LED2 to a 28 x 1.2 mm outlet at local x=320,y=48. An optical coupon must establish whether the current LED provides useful brightness after this approximately 38 mm route.',
                      'Lower halo needs new light sources or a proven redirection system; current LEDs emit upward through PCB slots.',
                      'Per-key illuminated legends need new LEDs, routing and power/firmware design.',
                      'No PCB or printable production case files have been revised.'])
assets = dict(caps=caps, variants=variants, notes=report)
(OUT/'assets.json').write_text(json.dumps(assets, separators=(',', ':')))
(OUT/'geometry-study.json').write_text(json.dumps(report, indent=2)+'\n')
assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == h for p,h in source_hashes.items())
print('Concept assets saved', (OUT/'assets.json').stat().st_size, flush=True)
