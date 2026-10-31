#!/usr/bin/env python3
"""Plate and wedge case for the tkl5 board.

Coordinates: x to the right, y from the front (spacebar) toward the rear (USB).
The case sits flat on the table. Its top edge is 7 mm at the front lip and
20.2 mm at the rear lip. The plate drops onto a ledge just under that edge.
"""

import re
from pathlib import Path

ROOT = (Path(__file__).resolve().parent / '..').resolve()
PCB = ROOT / "kicad" / "keyboard.kicad_pcb"
OUT = ROOT / "case"

# Board outline, millimetres, KiCad axes (y grows toward the front).
BOARD_X0, BOARD_X1 = 27.03, 377.79
BOARD_Y0, BOARD_Y1 = 20.0, 149.19  # y0 is the rear edge

RIM = 4.0             # plate past the printed hole
WALL = 2.0
FLOOR = 1.2
PLATE_T = 1.2
LEDGE = 1.2           # how far the ledge reaches under the plate edge
PCB_T = 1.6
PLATE_GAP = 2.2       # PCB top to plate bottom, set by the switch body
H_FRONT = 7.0
H_REAR = 20.2
HOLE_LASER = 13.95    # Choc V2 clips in
HOLE_PRINT = 14.15    # extra for a 0.4 mm nozzle

BOARD_W = BOARD_X1 - BOARD_X0
BOARD_D = BOARD_Y1 - BOARD_Y0


def load_switches():
    lines = PCB.read_text().splitlines()
    found = []
    for i, line in enumerate(lines):
        if not line.startswith('\t(footprint "Switch_Keyboard_Kailh:'):
            continue
        for nxt in lines[i:i + 40]:
            if nxt.strip().startswith("(at "):
                m = re.search(r"\(at ([-\d.]+) ([-\d.]+)", nxt)
                found.append((float(m.group(1)), float(m.group(2))))
                break
    return found


def plate_bounds(switches):
    """KiCad rectangle around the switch holes, plus RIM."""
    half = HOLE_PRINT / 2
    xs = [x for x, _ in switches]
    ys = [y for _, y in switches]
    return (min(xs) - half - RIM, min(ys) - half - RIM,
            max(xs) + half + RIM, max(ys) + half + RIM)


# Plate hugs the holes. The case still has to cover the PCB, which is larger.
PLATE_X0, PLATE_Y0, PLATE_X1, PLATE_Y1 = plate_bounds(load_switches())
PLATE_W = PLATE_X1 - PLATE_X0
PLATE_D = PLATE_Y1 - PLATE_Y0

# Case outer edge. The PCB sets it, because the board extends past the plate.
CASE_X0 = BOARD_X0 - WALL
CASE_Y0 = BOARD_Y0 - WALL
CASE_X1 = BOARD_X1 + WALL
CASE_Y1 = BOARD_Y1 + WALL
CASE_W = CASE_X1 - CASE_X0
CASE_D = CASE_Y1 - CASE_Y0


def to_plate(kx, ky):
    """KiCad point to plate point. Plate y=0 is the front edge."""
    return (kx - PLATE_X0, PLATE_Y1 - ky)


def to_case(kx, ky):
    """KiCad point to case point. Case y=0 is the front lip."""
    return (kx - CASE_X0, CASE_Y1 - ky)


def rows_of(switches):
    ys = sorted({round(y, 1) for _, y in switches})
    grouped = []
    for y in ys:
        xs = sorted(x for x, yy in switches if abs(yy - y) < 0.6)
        grouped.append((y, xs))
    return grouped


def choose_seams(switches):
    """One vertical gap per row, near the middle, clear of every switch."""
    seams = []
    for y, xs in rows_of(switches):
        best = None
        for a, b in zip(xs, xs[1:]):
            if b - a - HOLE_LASER < 3.5:
                continue
            mid = (a + b) / 2
            if best is None or abs(mid - 200) < abs(best - 200):
                best = mid
        if y > 130:
            best = 206.0  # empty plate under the right half of the spacebar
        seams.append((y, best))
    return seams


def seam_polyline(switches, seams):
    """Stepped cut from the front edge to the rear edge, in plate coordinates."""
    plate_sw = [to_plate(x, y) for x, y in switches]
    half = HOLE_PRINT / 2
    order = sorted(((to_plate(sx, sy)[0], to_plate(sx, sy)[1]) for sy, sx in seams),
                   key=lambda p: p[1])

    def blocked(x, y):
        return any(abs(x - sx) < half and abs(y - sy) < half for sx, sy in plate_sw)

    pts = [(order[0][0], 0.0)]
    for i, (sx, sy) in enumerate(order):
        pts.append((sx, sy - 8))
        pts.append((sx, sy + 8))
        if i + 1 < len(order):
            ymid = (sy + order[i + 1][1]) / 2
            pts.append((sx, ymid))
            pts.append((order[i + 1][0], ymid))
    pts.append((order[-1][0], PLATE_D))

    # Drop zero-length steps and confirm the cut misses every hole.
    clean = [pts[0]]
    for p in pts[1:]:
        if abs(p[0] - clean[-1][0]) < 1e-6 and abs(p[1] - clean[-1][1]) < 1e-6:
            continue
        clean.append(p)
    for a, b in zip(clean, clean[1:]):
        steps = 40
        for t in range(steps + 1):
            x = a[0] + (b[0] - a[0]) * t / steps
            y = a[1] + (b[1] - a[1]) * t / steps
            if blocked(x, y):
                raise SystemExit(f"seam hits a switch hole at ({x:.2f}, {y:.2f})")
    return clean


def dxf_polyline(points, closed=True):
    n = len(points)
    out = ["0", "LWPOLYLINE", "8", "0", "90", str(n), "70", "1" if closed else "0"]
    for x, y in points:
        out += ["10", f"{x:.4f}", "20", f"{y:.4f}"]
    return out


def write_dxf(switches):
    ents = []
    # Outline, 1.5 mm corner radius approximated with 4 segments per corner.
    r = 1.5
    w, d = PLATE_W, PLATE_D
    outline = [
        (r, 0), (w - r, 0),
        (w, r), (w, d - r),
        (w - r, d), (r, d),
        (0, d - r), (0, r),
    ]
    ents += dxf_polyline(outline)
    for kx, ky in switches:
        cx, cy = to_plate(kx, ky)
        h = HOLE_LASER / 2
        ents += dxf_polyline([
            (cx - h, cy - h), (cx + h, cy - h),
            (cx + h, cy + h), (cx - h, cy + h),
        ])
    body = "\n".join([
        "0", "SECTION", "2", "HEADER",
        "9", "$INSUNITS", "70", "4",
        "0", "ENDSEC",
        "0", "SECTION", "2", "ENTITIES",
        *ents,
        "0", "ENDSEC",
        "0", "EOF",
        "",
    ])
    (OUT / "plate-laser.dxf").write_text(body)


def scad_points(pts):
    return "[" + ",".join(f"[{x:.4f},{y:.4f}]" for x, y in pts) + "]"


def write_plate_scad(switches, seam):
    holes = [to_plate(x, y) for x, y in switches]
    # Both outlines walk the seam from the front edge to the rear edge.
    # Reversing it on the right half makes the polygon cross itself.
    left = [(0, 0)] + seam + [(0, PLATE_D)]
    right = [(PLATE_W, PLATE_D)] + list(reversed(seam)) + [(PLATE_W, 0)]
    hole_sq = []
    for cx, cy in holes:
        h = HOLE_PRINT / 2
        hole_sq.append(
            f"    translate([{cx:.4f},{cy:.4f}]) square([{HOLE_PRINT:.2f},{HOLE_PRINT:.2f}], center=true);"
        )
    holes_scad = "\n".join(hole_sq)
    scad = f"""// Printed plate halves. Holes are {HOLE_PRINT:.2f} mm so a 0.4 mm nozzle
// still clips a Kailh Choc V2. Laser-cut the DXF instead if you can:
// that file uses the true {HOLE_LASER:.2f} mm opening.
plate_t = {PLATE_T};
part = is_undef(part) ? "left" : part;

module holes() {{
{holes_scad}
}}

module half(outline) {{
  linear_extrude(plate_t)
    difference() {{
      polygon(outline);
      holes();
    }}
}}

if (part == "left") half({scad_points(left)});
if (part == "right") half({scad_points(right)});
"""
    (OUT / "plate.scad").write_text(scad)


def write_case_scad():
    # Bosses in case coordinates, inset from the PCB corners and clear of the module.
    pcb_x0, pcb_front = to_case(BOARD_X0, BOARD_Y1)
    inset = 8.0
    bosses = [
        (pcb_x0 + inset, pcb_front + inset),
        (pcb_x0 + BOARD_W - inset, pcb_front + inset),
        (pcb_x0 + inset, pcb_front + BOARD_D - inset),
        (pcb_x0 + BOARD_W - inset, pcb_front + BOARD_D - inset),
        (pcb_x0 + BOARD_W / 2, pcb_front + inset),
        (pcb_x0 + BOARD_W / 2, pcb_front + BOARD_D - 28),
        (pcb_x0 + 24, pcb_front + BOARD_D / 2),
        (pcb_x0 + BOARD_W - 24, pcb_front + BOARD_D / 2),
    ]
    boss_lines = "\n".join(
        f"    boss({x:.3f}, {y:.3f});" for x, y in bosses
    )
    plate_x, plate_y = to_case(PLATE_X0, PLATE_Y1)
    # USB opening, centered on the module, in the rear wall.
    usb_x = to_case(57.15, BOARD_Y0)[0]
    # Pouch pocket, to the right of the module.
    dam_x, dam_y = to_case(73.5, 55.2)
    split_x = to_case(200.0, BOARD_Y0)[0]
    scad = f"""// Wedge shell. Flat on the table.
// Front lip {H_FRONT:.1f} mm, rear lip {H_REAR:.1f} mm.
// Print each half with the flat bottom on the bed, 0.2 mm layers, 4 walls.
Hf = {H_FRONT};
Hr = {H_REAR};
floor_t = {FLOOR};
wall = {WALL};
plate_t = {PLATE_T};
ledge = {LEDGE};
W = {CASE_W:.4f};
D = {CASE_D:.4f};
part = is_undef(part) ? "left" : part;
split_x = {split_x:.4f}; // straight joint; the plate seam steps across it
plate_x = {plate_x:.4f};
plate_y = {plate_y:.4f};
plate_w = {PLATE_W:.4f};
plate_d = {PLATE_D:.4f};
pcb_x = {pcb_x0:.4f};
pcb_y = {pcb_front:.4f};
pcb_w = {BOARD_W:.4f};
pcb_d = {BOARD_D:.4f};

function rim(y) = Hf + (Hr - Hf) * y / D;
// Bottom of the 1.6 mm PCB: 1.2 plate + 2.2 switch gap + 1.6 board below the rim.
function pcb_bottom(y) = rim(y) - 5.0;

module outer() {{
  hull() {{
    cube([W, 0.02, Hf]);
    translate([0, D - 0.02, 0]) cube([W, 0.02, Hr]);
  }}
}}

module below_z(drop) {{
  hull() {{
    cube([W, 0.02, Hf - drop]);
    translate([0, D - 0.02, 0]) cube([W, 0.02, Hr - drop]);
  }}
}}

// Band between the top of the PCB and the underside of the plate.
module shelf_band() {{
  difference() {{
    below_z(plate_t);
    below_z(3.1);
  }}
}}

// Plastic over the PCB margin. The inner edge tucks under the plate so the plate has a seat.
module shelf() {{
  intersection() {{
    difference() {{
      translate([pcb_x - 0.2, pcb_y - 0.2, 0]) cube([pcb_w + 0.4, pcb_d + 0.4, 40]);
      translate([plate_x + ledge, plate_y + ledge, -1])
        cube([plate_w - 2 * ledge, plate_d - 2 * ledge, 50]);
    }}
    shelf_band();
  }}
}}

module plate_opening() {{
  difference() {{
    translate([plate_x, plate_y, 0]) cube([plate_w, plate_d, 40]);
    below_z(plate_t);
  }}
}}

module boss(x, y) {{
  h = pcb_bottom(y) - floor_t;
  if (h > 0.4)
    translate([x, y, floor_t - 0.2]) cylinder(h=h + 0.2, d=6, $fn=24);
}}

module bosses() {{
{boss_lines}
}}

// Keeps a thin pouch cell from sliding into the module. Sits well below the PCB.
module battery_dam() {{
  translate([{dam_x:.2f}, {dam_y:.2f}, floor_t - 0.2])
    difference() {{
      cube([70, 32, 1.4]);
      translate([1.2, 1.2, -0.2]) cube([67.6, 29.6, 2]);
    }}
}}

module usb_slot() {{
  translate([{usb_x - 8:.3f}, D - wall - 1, 8.5])
    cube([16, wall + 2, 7]);
}}

module shell() {{
  difference() {{
    union() {{
      difference() {{
        outer();
        translate([pcb_x, pcb_y, floor_t]) cube([pcb_w, pcb_d, 40]);
      }}
      shelf();
      bosses();
      battery_dam();
    }}
    usb_slot();
    plate_opening();
  }}
}}

module pinned() {{
  difference() {{
    shell();
    for (y = [30, 70, 110])
      translate([split_x, y, -1]) cylinder(h=floor_t + 2, d=3.2, $fn=20);
  }}
}}

if (part == "left")
  intersection() {{
    pinned();
    translate([-1, -1, -1]) cube([split_x + 1, D + 2, 40]);
  }}
if (part == "right")
  intersection() {{
    pinned();
    translate([split_x, -1, -1]) cube([W, D + 2, 40]);
  }}
"""
    (OUT / "case.scad").write_text(scad)


def main():
    switches = load_switches()
    if len(switches) != 86:
        raise SystemExit(f"expected 86 switches, found {len(switches)}")
    seams = choose_seams(switches)
    seam = seam_polyline(switches, seams)
    write_dxf(switches)
    write_plate_scad(switches, seam)
    write_case_scad()
    print(f"plate {PLATE_W:.1f} x {PLATE_D:.1f} mm, rim {RIM:.1f} mm past the holes")
    print(f"case  {CASE_W:.1f} x {CASE_D:.1f} mm, lip {H_FRONT} front / {H_REAR} rear")
    print(f"  plate edge to case outer, left {PLATE_X0 - CASE_X0:.1f} mm, right {CASE_X1 - PLATE_X1:.1f} mm")
    print(f"  plate edge to case outer, front {CASE_Y1 - PLATE_Y1:.1f} mm, rear {PLATE_Y0 - CASE_Y0:.1f} mm")
    print(f"switches {len(switches)}")
    # Heights at the spacebar and the function-row, for the build notes.
    slope = (H_REAR - H_FRONT) / CASE_D
    for label, ky in (("spacebar", 138.1125), ("function row", 38.1)):
        case_y = to_case(0, ky)[1]
        rim = H_FRONT + slope * case_y
        print(f"  {label}: case deck {rim:.1f} mm, PCB underside {rim - 5:.1f} mm")


if __name__ == "__main__":
    main()
