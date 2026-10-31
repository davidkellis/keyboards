"""Integral recessed USB bezel; dimensions are provisional physical-fit inputs."""
import cadquery as cq


def rounded_wire(cx, y, cz, width, height, radius):
    plane = cq.Plane(origin=(cx, y, cz), xDir=(1, 0, 0), normal=(0, 1, 0))
    tool = (cq.Workplane(plane).sketch().rect(width, height).vertices()
            .fillet(radius).finalize().extrude(.1).val())
    return min(tool.Faces(), key=lambda f: f.Center().y).outerWire()


def make_surround(case, module, socket, plug, settings, place):
    """Return the modified case, fit dimensions and a cable insertion sweep."""
    sx, sy, sxx, syy = socket['bounds']
    cx = (sx + sxx) / 2
    cz = socket['z_top'] - socket['height'] / 2
    web = settings['bezel_web_thickness_mm']
    projection = settings['socket_projection_past_bezel_mm']
    face_y = syy - projection
    rear_y = face_y - web
    module_clearance = rear_y - module['bounds'][3]
    assert module_clearance >= .1, 'Bezel would crowd the module body; remeasure/revise'

    margin = settings['opening_clearance_each_side_mm']
    px, py, pxx, pyy = plug['bounds']
    pocket_w = pxx - px + 2 * margin
    pocket_h = plug['height'] + 2 * margin
    slot_clearance = settings['socket_clearance_each_side_mm']
    slot_w = sxx - sx + 2 * slot_clearance
    slot_h = socket['height'] + 2 * slot_clearance
    outer_margin = settings['bezel_margin_mm']
    # This thin front web sits beyond the PCB edge and joins the thicker rear
    # wall all around. It closes the view around the socket without moving U1.
    bezel = (cq.Workplane('XY').box(pocket_w + 2 * outer_margin, web,
                                  pocket_h + 2 * outer_margin, centered=False)
             .translate((cx - pocket_w / 2 - outer_margin, rear_y,
                         cz - pocket_h / 2 - outer_margin)).val())
    case = case.fuse(place(bezel)).clean()

    # The actual through aperture hugs the socket; the larger exterior recess
    # ends on the bezel face and therefore does not expose a cable-sized hole.
    aperture = rounded_wire(cx, rear_y - 1, cz, slot_w, slot_h,
                            settings['socket_slot_corner_radius_mm'])
    aperture = cq.Solid.makeLoft([aperture, aperture.translate((0, web + 2, 0))])
    depth = settings['recess_flare_depth_mm']
    flare = settings['recess_flare_each_side_mm']
    throat = rounded_wire(cx, face_y, cz, pocket_w, pocket_h,
                         settings['recess_corner_radius_mm'])
    mouth = rounded_wire(cx, face_y + depth, cz, pocket_w + 2 * flare,
                         pocket_h + 2 * flare, settings['recess_corner_radius_mm'] + flare)
    recess = cq.Solid.makeLoft([throat, mouth])
    outside = cq.Solid.makeLoft([mouth, mouth.translate((0, 20, 0))])
    case = case.cut(place(aperture), place(recess), place(outside)).clean()
    assert case.isValid() and len(case.Solids()) == 1

    # The whole housing can approach along the tilted connector axis, not just
    # occupy its final seated location. The 0.5 mm pocket margin is retained.
    sweep = (cq.Workplane('XY').box(pxx - px, pyy - py + 12,
                                  plug['height'], centered=False)
             .translate((px, py, plug['z_top'] - plug['height'])).val())
    sweep = place(sweep)
    assert case.intersect(sweep).Volume() < 1e-5, 'Cable insertion is obstructed'
    return case, dict(
        type='integral recessed bezel with rounded socket aperture',
        aperture_width_height_mm=[slot_w, slot_h],
        aperture_corner_radius_mm=settings['socket_slot_corner_radius_mm'],
        housing_recess_width_height_at_bezel_mm=[pocket_w, pocket_h],
        recess_flare_each_side_mm=flare, recess_flare_depth_mm=depth,
        bezel_web_thickness_mm=web, bezel_face_y_board_mm=face_y,
        socket_projection_past_bezel_mm=projection,
        bezel_to_module_body_clearance_mm=module_clearance,
        socket_clearance_each_side_mm=slot_clearance,
        housing_insertion_sweep_collision_mm3=case.intersect(sweep).Volume(),
        dimensions_physically_verified=False), sweep
