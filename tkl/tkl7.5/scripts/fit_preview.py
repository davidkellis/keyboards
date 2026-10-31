#!/usr/bin/env python3
"""Generate views of the measured-coordinate, provisional module envelopes."""
import argparse
import json
from pathlib import Path


def export_previews(out, geometry, report):
    world_bounds={c['ref']:c['world_bounds'] for c in report.get('case_mounted_components',[])}
    lines = ["// Design envelopes, not manufacturer CAD. Dimensions require measurement.",
             "module module_envelopes() {"]
    for c in geometry['components']:
        if not c.get('user_installed'):
            continue
        x, y, xx, yy = c['bounds']
        z = c['z_top'] - c['height']
        color = '[0.95,0.48,0.12]' if c['ref'] == 'U1' else '[0.95,0.78,0.18]'
        if c['ref'] in world_bounds:
            a,b,z,aa,bb,zz=world_bounds[c['ref']]
            lines.extend([f"  // {c['ref']}: registered to vertical rear case wall",
                          f"  rotate([{-report['tilt_degrees']},0,0]) translate([-2.4,-2.4,{-report['pcb_underside_front_origin_z']}])",
                          f"    color({color}) translate([{a},{b},{z}]) cube([{aa-a},{bb-b},{zz-z}]);"])
            continue
        lines.extend([f"  // {c['ref']}",
                      f"  color({color}) translate([{x},{y},{z}]) cube([{xx-x},{yy-y},{c['height']}]);"])
    lines.append('}')
    (out / 'module-envelopes.scad').write_text('\n'.join(lines) + '\n')
    z0 = report['pcb_underside_front_origin_z']
    tilt = report['tilt_degrees']
    preview = f'''// Right end of the case, with PCB/plate/cover removed to show cable routing.
// Orange: module. Yellow: plug, cable allowance and rear socket. Blue: End/Up outlines.
// All module/cable dimensions are provisional fit limits, not actual-part measurements.
use <module-envelopes.scad>
module pcb_frame() {{ translate([2.4,2.4,{z0}]) rotate([{tilt},0,0]) children(); }}
color([0.4,0.46,0.53]) intersection() {{
  import("case.stl");
  translate([274,0,-1]) cube([83,135,25]);
}}
pcb_frame() module_envelopes();
'''
    for ref, label in [('SW42', 'End'), ('SW76', 'Up')]:
        key = next(s for s in geometry['switches'] if s['ref'] == ref)
        x, y = key['xy']
        preview += f'''pcb_frame() color([0.25,0.55,0.85]) translate([{x},{y},1.6]) {{
  linear_extrude(.15) difference() {{ square([14,14],center=true); square([13.5,13.5],center=true); }}
  linear_extrude(.15) text("{label}",size=2.3,halign="center",valign="center");
}}
'''
    (out / 'module-fit.scad').write_text(preview)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('revision', type=Path)
    out = parser.parse_args().revision / 'case'
    export_previews(out, json.loads((out / 'board-geometry.json').read_text()),
                    json.loads((out / 'fit-report.json').read_text()))
