#!/usr/bin/env python3
"""Check the exported STL's bezel sections for a single socket-sized aperture."""
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import Polygon, box

root = Path(__file__).resolve().parents[1]
case = root / 'case'
report = json.loads((case / 'fit-report.json').read_text())
geometry = json.loads((case / 'board-geometry.json').read_text())
surround = report['direct_usb']['surround']
socket = next(c for c in geometry['components'] if c['ref'] == 'USB_SOCKET')
cx = (socket['bounds'][0] + socket['bounds'][2]) / 2
cz = socket['z_top'] - socket['height'] / 2
web = surround['bezel_web_thickness_mm']
back_y = surround['bezel_face_y_board_mm'] - web
width, height = surround['aperture_width_height_mm']
pocket_w, pocket_h = surround['housing_recess_width_height_at_bezel_mm']
region = box(cx - pocket_w / 2, cz - pocket_h / 2,
             cx + pocket_w / 2, cz + pocket_h / 2)
mesh = trimesh.load_mesh(case / 'case.stl', process=True)
assert mesh.is_watertight and mesh.volume > 0
mesh.apply_translation([-2.4, -2.4, -report['pcb_underside_front_origin_z']])
mesh.apply_transform(trimesh.transformations.rotation_matrix(
    -math.radians(report['tilt_degrees']), [1, 0, 0]))
sections = []
for fraction in (.15, .5, .85):
    y = back_y + web * fraction
    section = mesh.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])
    material = Polygon()
    for entity in section.entities:
        points = entity.discrete(section.vertices)
        assert np.allclose(points[0], points[-1]), 'Open cross-section'
        polygon = Polygon(points[:, [0, 2]])
        assert polygon.is_valid
        material = material.symmetric_difference(polygon)
    # The larger cable recess must be closed at the web, except for one small
    # socket aperture. This also catches an accidental slit above the port.
    void = region.difference(material)
    assert void.geom_type == 'Polygon' and len(void.interiors) == 0
    expected = [cx - width / 2, cz - height / 2,
                cx + width / 2, cz + height / 2]
    assert np.allclose(void.bounds, expected, atol=.002)
    assert void.within(region.buffer(-.1))
    radius = surround['aperture_corner_radius_mm']
    ideal_area = width * height - (4 - math.pi) * radius ** 2
    assert abs(void.area - ideal_area) < .08
    sections.append(dict(y_board_mm=y, aperture_bounds_xz_mm=list(void.bounds),
                         aperture_area_mm2=void.area, aperture_count=1))
assert not report['collisions'] and report['pcb_case_overlap_mm3'] < 1e-4
assert surround['housing_insertion_sweep_collision_mm3'] < 1e-5
result = dict(
    source_pcb_sha256=report['source_sha256'],
    fit_config_sha256=report['fit_config_sha256'],
    mesh_sha256={name: hashlib.sha256((case / name).read_bytes()).hexdigest()
                 for name in ('case.stl', 'case-right.stl', 'fit-coupon-case.stl')},
    watertight=True, bezel_sections=sections, surround=surround,
    physical_fit_verified=False)
(case / 'usb-opening-validation.json').write_text(json.dumps(result, indent=2) + '\n')
print('USB bezel: three STL sections each have one socket-sized aperture; no extra slit')
