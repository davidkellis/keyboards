#!/usr/bin/env python3
"""Embed the existing v10 assembly meshes in an offline, freely orbitable viewer.

Uses only Python's standard library. Never writes PCB, case or order files.
Install the pinned JavaScript dependencies in source/ and run this file.
V10_RENDER_NODE_MODULES may point at an existing installation instead.
"""
from pathlib import Path
import array
import base64
import hashlib
import json
import os
import struct
import subprocess

SRC = Path(__file__).resolve().parent
OUT = SRC.parent
ROOT = OUT.parent
CASE = ROOT / 'case-hidden-mounts'
inputs = {}


def read(path):
    data = path.read_bytes()
    inputs[str(path.relative_to(ROOT))] = hashlib.sha256(data).hexdigest()
    return data


def mesh(name, material):
    path = CASE / 'reference' / (name + '-assembly.stl')
    data = read(path)
    count = struct.unpack_from('<I', data, 80)[0]
    assert len(data) == 84 + 50 * count, path
    lookup, vertices, faces = {}, array.array('f'), array.array('I')
    for i in range(count):
        for j in range(3):
            point = struct.unpack_from('<3f', data, 84 + 50 * i + 12 + 12 * j)
            # Index identical STL vertices; preserve the original float values.
            key = tuple(point)
            if key not in lookup:
                lookup[key] = len(lookup)
                vertices.extend(point)
            faces.append(lookup[key])
    if os.sys.byteorder != 'little':
        vertices.byteswap()
        faces.byteswap()
    return dict(name=name, material=material, triangles=count,
                positions=base64.b64encode(vertices.tobytes()).decode(),
                indices=base64.b64encode(faces.tobytes()).decode())


spec = json.loads(read(ROOT / 'case' / 'board-geometry.json'))
cfg = json.loads(read(ROOT / 'case' / 'fit-config.json'))
fit = json.loads(read(ROOT / 'case' / 'fit-report.json'))
case_fit = json.loads(read(CASE / 'validation.json'))
parts = [mesh('upper', 'shell'), mesh('bottom', 'base'), mesh('bezel', 'shell'),
         mesh('board', 'pcb')]
for i in range(1, 9):
    for part, material in [('carrier', 'carrier'), ('screw', 'metal'), ('nut', 'metal')]:
        parts.append(mesh(f'M{i}-{part}', material))

rows = [
    ['Esc'] + [f'F{i}' for i in range(1, 13)] + ['PrtSc', 'ScrLk', 'Pause'],
    ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace', 'Ins', 'Home', 'PgUp'],
    ['Tab', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', '\\', 'Del', 'End', 'PgDn'],
    ['Caps', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', "'", 'Enter'],
    ['Shift', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/', 'Shift', '↑'],
    ['Ctrl', 'Win', 'Alt', '', 'Alt', 'Fn', 'Ctrl', '←', '↓', '→'],
]
switches = []
for y, labels in zip(sorted({s['xy'][1] for s in spec['switches']}, reverse=True), rows):
    keys = sorted((s for s in spec['switches'] if s['xy'][1] == y), key=lambda s: s['xy'][0])
    assert len(keys) == len(labels), (y, len(keys), len(labels))
    for key, label in zip(keys, labels):
        switches.append(dict(key, label=label, modifier=key['units'] > 1 or y == 111.09 or key['xy'][0] > 290))
assert len(switches) == 86
data = dict(parts=parts, switches=switches, components=spec['components'],
            pins=spec['pins'], board=spec['board'], config=cfg,
            tilt=fit['tilt_degrees'], originZ=fit['pcb_underside_front_origin_z'],
            surface=case_fit['surface'])
data['study'] = json.loads(read(OUT / 'assets.json'))
data['raisedEdition'] = json.loads(read(ROOT / 'case-raised-deck/viewer-assets.json'))

modules = Path(os.environ.get('V10_RENDER_NODE_MODULES', SRC / 'node_modules'))
env = dict(os.environ, NODE_PATH=str(modules))
bundle = subprocess.run([str(modules / '.bin/esbuild'), str(SRC / 'viewer.js'),
                         '--bundle', '--format=iife', '--minify', '--legal-comments=inline',
                         '--target=es2022'], env=env, check=True, capture_output=True, text=True).stdout
template = (SRC / 'template.html').read_text()
html = template.replace('__MODEL_DATA__', json.dumps(data, separators=(',', ':')))
html = html.replace('__VIEWER_SCRIPT__', bundle.replace('</script', '<\\/script'))
(OUT / 'index.html').write_text(html)
(OUT / 'THREE-LICENSE.txt').write_bytes((modules / 'three' / 'LICENSE').read_bytes())
assert all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h for p, h in inputs.items())
manifest = dict(source_sha256=inputs, source_files_unchanged=True,
                exact_case_meshes=['upper', 'bottom', 'bezel'],
                key_count=86, screw_count=8,
                source_triangles=sum(p['triangles'] for p in parts),
                standalone_html_bytes=(OUT / 'index.html').stat().st_size,
                illustrative=['XVX and ultra-flat profile approximations; mounted heights depend on engagement',
                              'case lighting concepts and light distribution', 'switch bodies and stabilizers', 'USB-C socket details',
                              'component appearance', 'colours and surface finish'],
                keycap_sources='Joe Scotto Flat and Glass MX meshes, CC BY-NC-SA 4.0; see reference/',
                case_geometry_note='Edition 1 uses exact v10 meshes. Edition 2 uses case-raised-deck prototype geometry; lighting alternatives remain optical concepts.',
                physical_fit_verified=False)
(OUT / 'provenance.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps({k: v for k, v in manifest.items() if k != 'source_sha256'}, indent=2))
