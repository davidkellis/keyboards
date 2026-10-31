"""Assess a reported USB housing against the current under-PCB mounting geometry."""
import math


def assess_usb_housing(geometry, config, tilt_degrees, pcb_origin_z):
    usb = config['usb_extension']
    height = usb['male_housing_reported_thickness_mm']
    axis = config['module']['usb_axis_below_carrier_mm']
    sine = math.sin(math.radians(tilt_degrees))
    cosine = math.cos(math.radians(tilt_degrees))
    male = next(c for c in geometry['components'] if c['ref'] == 'USB_MALE')
    module = next(c for c in geometry['components'] if c['ref'] == 'U1')
    ymin = male['bounds'][1]
    floor = config['minimum_floor_thickness_mm']
    gap = config['floor_component_clearance_mm']
    bottom = pcb_origin_z + ymin * sine - (axis + height / 2) * cosine
    max_height = 2 * ((pcb_origin_z + ymin * sine - floor - gap) / cosine - axis)
    top = -axis + height / 2
    # Give the housing 0.2 mm beneath the PCB, then find the minimum rearward
    # shift that could meet floor thickness and floor clearance at this tilt.
    pcb_gap = 0.2
    lower_axis = max(axis, height / 2 + pcb_gap)
    shifted_bottom = pcb_origin_z + ymin * sine - (lower_axis + height / 2) * cosine
    rearward = max(0.0, (floor + gap - shifted_bottom) / sine)
    x, y, xx, yy = module['bounds']
    y += rearward
    yy += rearward
    module_top = module['z_top'] - (lower_axis - axis)
    module_bottom = module_top - module['height']
    blocked_pins = set()
    for pin in geometry['pins']:
        if pin.get('top') or module_top <= -pin['depth'] or module_bottom >= 0:
            continue
        px, py = pin['xy']
        distance_sq = max(x - px, 0, px - xx) ** 2 + max(y - py, 0, py - yy) ** 2
        if distance_sq < (pin['diameter'] / 2) ** 2:
            blocked_pins.add(pin['ref'])
    return dict(
        reported_housing_thickness_mm=height,
        thickness_source=usb['male_housing_thickness_source'],
        assumed_socket_axis_below_pcb_mm=axis,
        assumed_housing_centered_on_socket=True,
        minimum_housing_world_z_mm=bottom,
        required_floor_thickness_mm=bottom - gap,
        minimum_allowed_floor_thickness_mm=floor,
        required_floor_clearance_mm=gap,
        maximum_thickness_at_current_socket_axis_mm=max_height,
        pcb_intrusion_mm=max(0.0, top),
        fits_current_arrangement=bottom - gap >= floor and top <= 0,
        rearward_trial=dict(
            pcb_clearance_mm=pcb_gap,
            socket_axis_below_pcb_mm=lower_axis,
            minimum_displacement_mm=rearward,
            module_solder_pin_overlap_refs=sorted(blocked_pins),
            suitable_without_further_redesign=not blocked_pins,
            implemented=False,
        ),
        limitation='Screening at assumed module/socket height; rearward trial does not validate routing, mounts or the whole assembly.',
    )
