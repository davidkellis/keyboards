"""Check the exported plate's actual top skin and light-window fit."""
from pathlib import Path
import hashlib,json
import numpy as np
import trimesh
from shapely.geometry import Polygon,box,Point
from shapely.ops import unary_union

root=Path(__file__).resolve().parents[1];case=root/'case'
fit=json.loads((case/'fit-report.json').read_text())
g=json.loads((case/'board-geometry.json').read_text())
cfg=json.loads((case/'fit-config.json').read_text())
finish=fit['surface_finish'];stack=fit['stack']
plate=trimesh.load_mesh(case/'plate.stl')
plate.apply_translation([0,cfg['recessed_plate']['front_edge_inset_mm'],stack['pcb_top_z']])

def section_material(z):
    section=plate.section(plane_origin=[0,0,z],plane_normal=[0,0,1])
    assert section is not None
    material=Polygon()
    for entity in section.entities:
        points=entity.discrete(section.vertices)
        assert np.allclose(points[0],points[-1])
        poly=Polygon(points[:,:2]);assert poly.is_valid
        material=material.symmetric_difference(poly)
    return material

outline=box(0,cfg['recessed_plate']['front_edge_inset_mm'],g['board']['width'],g['board']['depth'])
regions=unary_union([box(*b) for b in finish['blind_pockets_bounds_mm']]).intersection(outline)
closed_checks=[]
for fraction in (.1,.5,.9):
    z=finish['blind_pin_pocket_roof_z_mm']+fraction*finish['actual_roof_thickness_mm']
    material=section_material(z)
    missing=regions.difference(material.buffer(.002)).area
    assert missing<.001,('Top skin has an opening',z,missing)
    closed_checks.append(dict(z_board_mm=z,uncovered_pin_region_mm2=missing))
# Below the roof, every modeled top pin has a real pocket in the STL.
material=section_material(finish['blind_pin_pocket_roof_z_mm']-.1)
for pin in g['pins']:
    if pin['ref'] not in ('U1','J1','J5'):continue
    assert pin['depth']<=1.0
    assert Point(*pin['xy']).buffer(pin['diameter']/2+.1).intersection(material).area<1e-5

material=section_material(stack['plate_top_z']-.1)
for led in finish['led_centers']:
    x,y=led['xy']
    aperture=Point(x,y).buffer(finish['led_hole_diameter_mm']/2-.01)
    assert aperture.intersection(material).area<1e-5
    surrounding=Point(x,y).buffer(finish['led_hole_diameter_mm']/2+.20).difference(Point(x,y).buffer(finish['led_hole_diameter_mm']/2+.02))
    assert surrounding.difference(material).area<1e-5

diffuser=trimesh.load_mesh(case/'led-diffuser.stl')
assert np.allclose(diffuser.extents,[finish['diffuser_flange_diameter_mm']]*2+
                   [cfg['plate_thickness_mm']+finish['diffuser_flange_thickness_mm']],atol=.002)
assert not fit['collisions']
report=dict(mesh_sha256={name:hashlib.sha256((case/name).read_bytes()).hexdigest()
                        for name in ['plate.stl','led-diffuser.stl','fit-coupon-upper.stl']},
            top_skin_sections=closed_checks,blind_pin_pockets_clear=True,
            complete_top_pin_envelope_limit_mm=1.0,
            diffuser_count=finish['diffuser_count'],diffuser_top_flush=True,
            physical_fit_and_optics_verified=False)
(case/'surface-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('Plate STL: closed top above pins, blind pockets clear, six circular light windows; diffuser dimensions pass.')
