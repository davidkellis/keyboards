#!/usr/bin/env python3
"""Read-only study of the v10 geometry; outputs are confined to this directory.

Run with a Python environment containing numpy and matplotlib. This is an envelope study,
not printable enclosure CAD or an approved battery pack design.
"""
from pathlib import Path
import hashlib
import json
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Polygon, FancyBboxPatch
import numpy as np

OUT = Path(__file__).resolve().parents[1]
ROOT = OUT.parent
INPUTS = [ROOT / 'case' / name for name in ('fit-config.json', 'fit-report.json', 'board-geometry.json')]
INPUTS += [ROOT / 'case-hidden-mounts' / 'validation.json']
hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in INPUTS}
cfg, fit, geo, validation = [json.loads(p.read_text()) for p in INPUTS]
CW, CD = cfg['fixed_footprint_mm']
M = 2.4
PT = geo['board']['thickness'] + cfg['plate_top_above_pcb_mm']
A = math.radians(fit['tilt_degrees'])
Z0 = fit['pcb_underside_front_origin_z']
H0 = Z0 - M * math.tan(A) + PT / math.cos(A)

# Manufacturer maximum bare-cell envelope, not a protected retail-cell size.
CELL_D, CELL_L = 18.6, 65.2
RADIAL_ALLOWANCE, WALL = .5, 1.5
R = CELL_D / 2 + RADIAL_ALLOWANCE + WALL
POD_L = CELL_L + 8.0  # provisional axial room for tabs, insulation and end walls
PIN_DEPTH, GAP, FLOOR = 1.7, .4, 1.2
POD_X = [75., 205.]
Y_UNDER, Z_CELL = CD - R - .5, R
Y_BEHIND = CD + .8 + R

def origin(a):
    # Preserve the front plate plane at y=0, rather than rotating its height up.
    return H0 + M * math.tan(a) - PT / math.cos(a)

def signed_gap(a, yc):
    # Distance from circle centre to PCB underside, measured normal to PCB.
    distance = (origin(a) - Z_CELL) * math.cos(a) + (yc - M) * math.sin(a)
    return distance - R - PIN_DEPTH

lo, hi = A, math.radians(25)
for _ in range(80):
    mid = (lo + hi) / 2
    if signed_gap(mid, Y_UNDER) < GAP:
        lo = mid
    else:
        hi = mid
B = (lo + hi) / 2
assert abs(signed_gap(B, Y_UNDER) - GAP) < 1e-8
assert all(0 < x < x + POD_L < CW for x in POD_X)
assert Y_UNDER + R <= CD

def yz(y, z, a):
    return M + y * math.cos(a) - z * math.sin(a), origin(a) + y * math.sin(a) + z * math.cos(a)

# Verify the chosen under-PCB spans contain only shallow parts and solder pins.
# A continuous 1.7 mm lower envelope is more conservative than individual pins.
component_limit = 0.
overlap_refs = []
for c in geo['components']:
    if c['side'] != 'bottom' or c['ref'] == 'USB_PLUG_EXTERNAL':
        continue
    x0, y0, x1, y1 = c['bounds']
    z1 = c.get('z_top', 0.)
    z0 = z1 - c['height']
    corners = [yz(y, z, B) for y in (y0, y1) for z in (z0, z1)]
    ys = [p[0] for p in corners]
    if min(ys) <= Y_UNDER + R and max(ys) >= Y_UNDER - R:
        if any(x0 + M <= x + POD_L and x1 + M >= x for x in POD_X):
            overlap_refs.append(c['ref'])
            component_limit = max(component_limit, -z0)
assert component_limit <= PIN_DEPTH
assert max(p['depth'] for p in geo['pins'] if not p.get('top')) <= PIN_DEPTH

result = {
    'status': 'dimensioned envelope study; not a print-ready enclosure',
    'source_sha256': hashes,
    'cell_reference': 'https://www.molicel.com/product/inr-18650-m35a/',
    'bare_cell_max_diameter_length_mm': [CELL_D, CELL_L],
    'assumptions': {
        'radial_allowance_mm': RADIAL_ALLOWANCE,
        'pod_wall_mm': WALL,
        'pod_outer_diameter_mm': 2 * R,
        'pod_axial_length_mm': POD_L,
        'pod_axial_extra_for_tabs_insulation_endwalls_mm': 8.,
        'pod_x_intervals_mm': [[x, x + POD_L] for x in POD_X],
        'pin_envelope_below_pcb_mm': PIN_DEPTH,
        'pin_to_housing_clearance_mm': GAP,
        'rubber_feet_and_keycaps_included': False,
        'protected_button_top_cells_or_spring_holders_included': False,
        'pack_protection_and_lead_routing_resolved': False,
    },
    'current_case': {
        'width_depth_mm': [CW, CD],
        'front_plate_plane_height_mm': H0,
        'rear_plate_plane_height_mm': H0 + CD * math.tan(A),
        'actual_rounded_shell_max_height_mm': validation['surface']['overall_height_mm'],
        'tilt_deg': math.degrees(A),
        'battery_reserve_mm': cfg['battery']['reserved_dimensions_mm'],
        'pcb_under_plane_at_proposed_pod_centre_mm': origin(A) + (Y_UNDER - M) * math.tan(A),
    },
    'under_pcb_same_footprint': {
        'width_depth_mm': [CW, CD],
        'cell_centre_yz_mm': [Y_UNDER, Z_CELL],
        'tilt_deg': math.degrees(B),
        'front_plate_plane_height_mm': H0,
        'rear_plate_plane_height_mm': H0 + CD * math.tan(B),
        'housing_clearance_to_continuous_pin_envelope_mm': signed_gap(B, Y_UNDER),
        'components_overlapping_pod_plan_envelope': overlap_refs,
        'deepest_overlapping_component_mm': component_limit,
        'continuous_floor_spacers_fasteners_ports_and_structure_rebuild_required': True,
    },
    'behind_pcb_same_tilt': {
        'width_depth_mm': [CW, Y_BEHIND + R],
        'cell_centre_yz_mm': [Y_BEHIND, Z_CELL],
        'added_depth_mm': Y_BEHIND + R - CD,
        'pod_max_height_mm': 2 * R,
        'tilt_deg': math.degrees(A),
        'pod_to_current_rear_wall_plan_gap_mm': .8,
        'structural_bridges_endcaps_and_wiring_unresolved': True,
    },
    'slimmer_deck': {
        'plate_top_to_nominal_bottom_normal_mm': PT + PIN_DEPTH + GAP + FLOOR,
        'exclusions': 'front transition, stiffening, fasteners, controller, battery connector and other local details',
        'front_existing_floor_min_mm': .8359322746002019,
        'front_existing_diode_clearance_mm': .4,
        'meaning': 'An undercut can reduce the depth of the visible main body, not the desk-to-key height.',
    },
    'validation_scope': 'Analytic circle/plane clearance and component envelope screening only; not full CAD collision, electrical or structural validation.',
}
(OUT / 'measurements.json').write_text(json.dumps(result, indent=2) + '\n')

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10})
fig = plt.figure(figsize=(16, 12), facecolor='#f5f7fb')
gs = fig.add_gridspec(4, 2, height_ratios=[1, 1, 1, 2.3], hspace=.62, wspace=.15)
blue, green, amber, dark = '#4d75a5', '#3b8870', '#eeaa43', '#28354a'

def setup_side(ax, title):
    ax.set_title(title, loc='left', fontweight='bold', color=dark, pad=12)
    ax.set_xlim(-4, 165)
    ax.set_ylim(-3, 37)
    ax.set_aspect('equal')
    ax.axhline(0, color='#718094', lw=1)
    ax.text(1, -2, 'front', ha='left', va='top', fontsize=8)
    ax.text(159, -2, 'rear', ha='right', va='top', fontsize=8)
    ax.axis('off')

def side_deck(ax, a, pouch=False):
    y = np.linspace(0, CD, 300)
    top = H0 + y * math.tan(a)
    pcb = top - PT / math.cos(a)
    bottom = np.zeros_like(y) if pouch else np.maximum(0, pcb - (PIN_DEPTH + GAP + FLOOR) / math.cos(a))
    ax.fill_between(y, bottom, top, color=blue, alpha=.22)
    ax.plot(y, top, color=blue, lw=2.5)
    ax.plot(y, pcb, color=green, lw=1.5)
    ax.plot(y, bottom, color=blue, lw=2)
    ax.plot([CD, CD], [bottom[-1], top[-1]], color=blue, lw=2)
    if pouch:
        ax.add_patch(Rectangle((80.5, 1.7), 50, 6.3, fc=amber, ec='#b67416'))
        ax.text(104, 4.85, 'pouch reserve', ha='center', va='center', fontsize=8)
    else:
        ax.text(47, 1.0, 'undercut / air', color='#687587', fontsize=8)
    return top[-1]

def circle_pod(ax, yc):
    ax.add_patch(Circle((yc, R), R, facecolor=dark, edgecolor=dark))
    ax.add_patch(Circle((yc, R), CELL_D / 2 + RADIAL_ALLOWANCE, fc='#f5f7fb', ec='none'))
    ax.add_patch(Circle((yc, R), CELL_D / 2, fc=amber, ec='#b67416'))
    ax.text(yc, R, '18650', ha='center', va='center', fontsize=8)

ax = fig.add_subplot(gs[0, :])
setup_side(ax, 'A  Current pouch design — same scale in all side views')
side_deck(ax, A, pouch=True)
ax.text(137, 17.5, '18.7 mm actual rear maximum\n5.7° tilt', fontsize=9, va='center', color=dark)

ax = fig.add_subplot(gs[1, :])
setup_side(ax, 'B  Battery feet underneath the PCB — keep the current footprint')
rear = side_deck(ax, B)
circle_pod(ax, Y_UNDER)
ax.text(137, 28, f'{rear:.1f} mm rear plate plane\n{math.degrees(B):.1f}° tilt', fontsize=9, va='center', color=dark)
ax.text(25, 28, 'Front plate height retained\nHousing + solder pins must clear the PCB', fontsize=9, color=dark)

ax = fig.add_subplot(gs[2, :])
setup_side(ax, 'C  Battery feet behind the PCB — preserve the current tilt and key heights')
side_deck(ax, A)
circle_pod(ax, Y_BEHIND)
# Schematic structural link only; mechanical fastening is not modeled.
ax.plot([CD, Y_BEHIND - R + 2], [10, 10], color=blue, lw=3)
ax.text(20, 28, f'Adds {2 * R + .8:.1f} mm of depth; pods stand {2 * R:.1f} mm tall', fontsize=9, color=dark)

def plan(ax, behind):
    yc = Y_BEHIND if behind else Y_UNDER
    ax.add_patch(FancyBboxPatch((0, 0), CW, CD, boxstyle='round,pad=0,rounding_size=3', fc='#e1e9f2', ec=blue, lw=1.8))
    for sw in geo['switches']:
        x, y = sw['xy']
        ax.add_patch(Rectangle((x + M - 6.8, y + M - 6.8), 13.6, 13.6, fc='white', ec='#a7b6c8', lw=.45))
    for x in POD_X:
        ax.add_patch(FancyBboxPatch((x, yc-R), POD_L, 2*R, boxstyle='round,pad=0,rounding_size=2', fc=dark, ec=dark, alpha=.8))
        ax.add_patch(Rectangle((x+4, yc-CELL_D/2), CELL_L, CELL_D, fc=amber, ec='none', alpha=.92))
        ax.text(x + POD_L / 2, yc, '18650', fontsize=9, ha='center', va='center')
    ax.add_patch(Rectangle((23.02, 98.59), 19, 33, ec=green, fc=green, alpha=.65))
    ax.annotate('controller / USB', xy=(32.5, 129), xytext=(3, 173), arrowprops={'arrowstyle': '-', 'color':green}, color=green, fontsize=9)
    ax.annotate('power switch', xy=(302.4, 130), xytext=(277, 173), arrowprops={'arrowstyle':'-', 'color':green}, color=green, fontsize=9)
    ax.set_title('C  Behind the PCB' if behind else 'B  Under the rear rows (transparent view)', loc='left', fontsize=12, fontweight='bold', color=dark)
    ax.set_xlim(-3, CW + 3)
    ax.set_ylim(-5, 183)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.text(CW/2, -8, f'{CW:.1f} mm wide  •  {Y_BEHIND+R if behind else CD:.1f} mm overall depth', ha='center', va='top', fontsize=10)

plan(fig.add_subplot(gs[3, 0]), False)
plan(fig.add_subplot(gs[3, 1]), True)
fig.suptitle('v10 • Third enclosure study: two rear 18650 housings', x=.055, ha='left', y=.98, fontsize=20, fontweight='bold', color=dark)
fig.text(.055, .945, 'Dimensioned concepts, not production CAD. Cells run left–right; blue = case/plate, green = PCB, amber = battery.', fontsize=11, color='#52627a')
fig.text(.055, .04, 'Pod assumption: 73.2 mm long × 22.6 mm outside diameter. Bare cell: Ø18.6 × 65.2 mm. Rubber feet and keycaps excluded.\nLocal pockets for the controller and tall battery connector are required; side sections do not show those pockets, ribs or fasteners.\nA thinner main deck is possible, but the rear maximum grows. The plastic housing carries the load; the cell must not be a structural member.', fontsize=10, color='#52627a', linespacing=1.6)
fig.subplots_adjust(left=.055, right=.95, top=.90, bottom=.12)
fig.savefig(OUT / 'comparison.png', dpi=160, facecolor=fig.get_facecolor())
fig.savefig(OUT / 'comparison.svg', facecolor=fig.get_facecolor())
plt.close(fig)
assert hashes == {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in INPUTS}
print(json.dumps({'rear_under_mm': result['under_pcb_same_footprint']['rear_plate_plane_height_mm'], 'tilt_under_deg': math.degrees(B), 'rear_behind_mm': 2*R, 'depth_behind_mm': Y_BEHIND+R, 'source_files_unchanged': True}, indent=2))
