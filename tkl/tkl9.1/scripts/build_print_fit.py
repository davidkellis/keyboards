#!/usr/bin/env python3
"""Export print-compensated PCB gauges without changing fabrication geometry."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import shutil
import zipfile

import cadquery as cq
import trimesh

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / 'case'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--diameter-extra', type=float, default=0.4)
args = parser.parse_args()
extra = args.diameter_extra
assert 0 < extra <= 0.6, 'Use 0 < diameter allowance <= 0.6 mm'
OUT = CASE / 'print-fit'
OUT.mkdir(exist_ok=True)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

geometry = json.loads((CASE / 'board-geometry.json').read_text())
fit = json.loads((CASE / 'fit-report.json').read_text())
assert geometry['source_sha256'] == fit['source_sha256'] == sha(ROOT / geometry['source'])
W, D, T = (geometry['board'][k] for k in ('width', 'depth', 'thickness'))
nominal = cq.importers.importStep(str(CASE / 'pcb-bare.step')).val()
assert len(nominal.Solids()) == 1 and nominal.isValid()

def block(x, y, z, w, depth, height):
    return cq.Workplane('XY').box(w, depth, height, centered=False).translate((x, y, z)).val()

holes = [h for h in geometry['holes'] if h['ref'] == 'U1' or
         (h['ref'].startswith('SW') and h['ref'] != 'SW87')]
assert Counter(h['ref'] for h in holes)['U1'] == 29
assert len(holes) == 83 * 4 + 29
cuts = []
removed_volume = 0
for h in holes:
    w, depth = h['size']
    assert abs(w - depth) < 1e-8
    x, y = h['xy']
    cuts.append(cq.Workplane('XY').circle((w + extra) / 2).extrude(T + 2).translate((x, y, -1)).val())
    removed_volume += math.pi * ((w + extra) ** 2 - w ** 2) / 4 * T
board = nominal.cut(*cuts).clean()
assert len(board.Solids()) == 1 and board.isValid()
# All extra removed material must be the intended concentric drill allowance.
assert abs(nominal.Volume() - board.Volume() - removed_volume) < 0.01
assert all(abs(getattr(nominal.BoundingBox(), k) - getattr(board.BoundingBox(), k)) < 1e-6
           for k in ('xmin', 'xmax', 'ymin', 'ymax', 'zmin', 'zmax'))

validation = []
def export(shape, name):
    assert shape.isValid() and len(shape.Solids()) == 1, name
    bb = shape.BoundingBox()
    flat = shape.translate((-bb.xmin, -bb.ymin, -bb.zmin))
    path = OUT / name
    cq.exporters.export(flat, str(path), tolerance=0.01, angularTolerance=0.08)
    mesh = trimesh.load_mesh(path)
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0, name
    assert len(mesh.split()) == 1, name
    assert abs(mesh.volume - shape.Volume()) / shape.Volume() < 0.002, name
    validation.append(dict(file=name, dimensions_mm=mesh.extents.tolist(),
                           watertight=True, solid_shells=1, volume_mm3=float(mesh.volume),
                           source_crop_origin_mm=[bb.xmin, bb.ymin, bb.zmin], sha256=sha(path)))
    print('Validated', name, flush=True)

export(board, 'pcb-bare-easy-fit.stl')
# Use the same stepped seam as the nominal PCB halves.
seam = fit['seam_xy_board']
points = [(-10, -10), (seam[0][0], -10)] + seam + [(seam[-1][0], D + 10), (-10, D + 10)]
left_mask = cq.Workplane('XY').polyline(points).close().extrude(T + 2).translate((0, 0, -1)).val()
left, right = board.intersect(left_mask), board.cut(left_mask)
assert abs(left.Volume() + right.Volume() - board.Volume()) < 0.001
export(left, 'pcb-left-easy-fit.stl')
export(right, 'pcb-right-easy-fit.stl')
export(board.intersect(block(289, 78, -1, W - 289 + 2, D - 78 + 20, T + 2)),
       'fit-coupon-pcb-easy-fit.stl')
switch = next(s for s in geometry['switches'] if s['ref'] == 'SW1')
x, y = switch['xy']
export(board.intersect(block(x - 9, y - 9, -1, 18, 18, T + 2)), 'single-switch-easy-fit.stl')

report = dict(source_pcb_sha256=geometry['source_sha256'],
              nominal_step_sha256=sha(CASE / 'pcb-bare.step'),
              diameter_extra_mm=extra, radial_extra_mm=extra/2,
              enlarged_holes=len(holes), switch_holes=332, module_holes=29,
              pin_centers_unchanged=True, board_outline_and_thickness_unchanged=True,
              expected_removed_volume_mm3=removed_volume,
              actual_removed_volume_mm3=nominal.Volume()-board.Volume(),
              hole_sizes=[dict(nominal_diameter_mm=d, print_diameter_mm=d+extra, count=n)
                          for d,n in sorted(Counter(h['size'][0] for h in holes).items())],
              meshes=validation)
(OUT / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
readme = f'''# v9.1 PCB fit prints with larger holes

Print at 100% in millimetres, flat on the bed. These gauges add **{extra:g} mm
to hole diameters** ({extra/2:g} mm per side); all pin centers, the 1.6 mm board
thickness and the board outline remain unchanged. This allowance compensates
for plastic printing and permits insertion trials; it does not establish the
clearance of manufactured PCB holes. Do not also apply a slicer hole expansion
for the first trial. Printer results still depend on material and calibration.

Start with `single-switch-easy-fit.stl` for one actual Choc V2 switch. Then use
`fit-coupon-pcb-easy-fit.stl` in place of the old rear-corner PCB coupon to test
the actual clone and several switches. Use the matching base, integrated upper and
1 mm module gap gauge; those mating parts are included in this ZIP. The clone
goes underneath, components toward the case floor and USB toward the rear.

The case corner includes the recessed USB bezel: a 10.1 x 3.8 mm socket slot
behind a wider, blind cable-housing recess. Its 0.6 mm web and the provisional
socket dimensions need a physical fit trial. Check thin-wall paths in the
slicer, seat the socket through the bezel, and confirm full cable insertion
without pushing on the module. There is no separate bezel part to attach.

`pcb-left-easy-fit.stl` and `pcb-right-easy-fit.stl` are full PCB halves for a
256 mm bed. `pcb-bare-easy-fit.stl` is the unsplit PCB for a larger printer.
Use the bare gauges to insert real parts. The old populated models contain
printed pin envelopes and are not insertion-test fixtures.

The main case directory also receives these models as `pcb-bare.stl`,
`pcb-left.stl`, `pcb-right.stl`, `fit-coupon-pcb.stl` and `single-switch-fit.stl`.
Only switch pin/locating holes and the 29 module holes are enlarged. Other
holes, nominal STEP references, populated envelope models, KiCad sources and
JLC Gerber/BOM/CPL files are unchanged. Check that every module pin enters vertically without bending;
larger holes can mask small registration errors. Physical confirmation of the
three auxiliary pad positions is especially important before ordering.

Rebuild: `python tkl/tkl9.1/scripts/build_print_fit.py` in the CadQuery environment.
`validation.json` records dimensions, mesh checks, sizes and source hashes.
'''
(OUT / 'README.md').write_text(readme)
files = list(OUT.glob('*.stl')) + [OUT / 'README.md', OUT / 'validation.json']
mating = [CASE / f for f in ('fit-coupon-case.stl', 'fit-coupon-upper.stl',
                            'module-gap-gauge.stl', 'mount-coupon-case.stl',
                            'mount-coupon-pcb.stl', 'mount-coupon-upper.stl')]
archive = OUT / 'tkl-v9.1-easy-fit.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for path in files + mating:
        z.write(path, path.name)
    z.writestr('SHA256.json', json.dumps({p.name: sha(p) for p in files + mating}, indent=2) + '\n')
print(archive)

# Publish insertion-test models under the filenames used in the main print folder.
published = {}
for source, target in {
    'pcb-bare-easy-fit.stl': 'pcb-bare.stl',
    'pcb-left-easy-fit.stl': 'pcb-left.stl',
    'pcb-right-easy-fit.stl': 'pcb-right.stl',
    'fit-coupon-pcb-easy-fit.stl': 'fit-coupon-pcb.stl',
    'single-switch-easy-fit.stl': 'single-switch-fit.stl',
}.items():
    shutil.copyfile(OUT / source, CASE / target)
    assert sha(OUT / source) == sha(CASE / target)
    published[target] = dict(source='print-fit/' + source, sha256=sha(CASE / target))
(CASE / 'print-fit-files.json').write_text(json.dumps(dict(
    diameter_extra_mm=extra, source_pcb_sha256=geometry['source_sha256'],
    files=published), indent=2) + '\n')
print('Published larger-hole STLs in', CASE)
