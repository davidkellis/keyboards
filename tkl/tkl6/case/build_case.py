#!/usr/bin/env python3
"""Plate and wedge case for the tkl6 board.

Coordinates: x to the right, y from the front (spacebar) toward the rear (USB).
The case sits flat on the table. Its top edge is 7 mm at the front lip and
20.2 mm at the rear lip. The plate drops onto a ledge just under that edge.
"""

import math
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
    # Studs in KiCad coordinates. The old rear-right stud sat in front of the
    # power-switch slot, and the right-side one sat in front of the USB opening.
    # These stay off the switch holes, the module, the battery pocket, and both
    # rear openings.
    bosses = [
        to_case(kx, ky)
        for kx, ky in (
            (40, 28), (175, 28), (250, 28),
            (55, 50), (160, 50), (250, 50), (340, 50),
            (55, 90), (160, 90), (265, 90),
            (100, 128), (205, 128), (310, 128),
            (55, 142), (175, 142), (280, 142), (355, 142),
        )
    ]
    pcb_x0, pcb_front = to_case(BOARD_X0, BOARD_Y1)
    boss_lines = "\n".join(
        f"    boss({x:.3f}, {y:.3f});" for x, y in bosses
    )
    plate_x, plate_y = to_case(PLATE_X0, PLATE_Y1)
    # Pouch pocket stays on the left, clear of the relocated module.
    dam_x, dam_y = to_case(73.5, 55.2)
    # USB-C opening in the rear wall, right side. Screws flank it, 21 mm apart.
    # The 2 mm wall is too thin for a flange pocket, so the flange sits on the
    # outside face. The opening stays below the PCB.
    port_x = CASE_W - 24.0
    screw_l = CASE_W - 28.5
    screw_r = CASE_W - 7.5
    sw_x = to_case(331.27, BOARD_Y0)[0]
    split_x = to_case(200.0, BOARD_Y0)[0]
    # Cover opening: each keycap, grown so light can pass around it.
    SEAT, DROP = 2.0, 0.4
    COVER_T, LIGHT = 1.8, 1.0
    openings = []
    for kx, ky, u, _rot in load_keys():
        cap_w = u * 19.05 - 1.05
        cap_d = 17.0
        x, y = to_case(kx - cap_w / 2 - LIGHT, ky + cap_d / 2 + LIGHT)
        openings.append(
            f"  translate([{x:.3f}, {y:.3f}, -1]) cube([{cap_w + 2 * LIGHT:.3f}, {cap_d + 2 * LIGHT:.3f}, 40]);"
        )
    key_openings = "\n".join(openings)
    scad = f"""// Wedge shell. Flat on the table.
// Front lip {H_FRONT:.1f} mm, rear lip {H_REAR:.1f} mm.
// Print each half with the flat bottom on the bed, 0.2 mm layers, 4 walls.
Hf = {H_FRONT};
Hr = {H_REAR};
floor_t = {FLOOR};
pcb_t = {PCB_T};
wall = {WALL};
plate_t = {PLATE_T};
ledge = {LEDGE};
W = {CASE_W:.4f};
D = {CASE_D:.4f};
part = is_undef(part) ? "base" : part;
split_x = {split_x:.4f}; // unused; the case prints as one piece
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

// Band under the plate. The plate bottom is 1.2 mm below the rim and the PCB
// top is 3.4 mm below it. A 0.8 mm lip leaves 1.4 mm of room to tuck the board under.
module shelf_band() {{
  difference() {{
    below_z(plate_t);
    below_z(2.0);
  }}
}}

// Plastic over the PCB margin. The inner edge tucks under the plate so the plate has a seat.
module shelf() {{
  difference() {{
    intersection() {{
      difference() {{
        translate([pcb_x - 0.2, pcb_y - 0.2, 0]) cube([pcb_w + 0.4, pcb_d + 0.4, 40]);
        translate([plate_x + 0.8, plate_y + 0.8, -1])
          cube([plate_w - 1.6, plate_d - 1.6, 50]);
      }}
      shelf_band();
    }}
    // The board hangs past the plate at the rear. Leave that strip open.
    translate([pcb_x - 1, plate_y + plate_d - 0.8, -1])
      cube([pcb_w + 2, 40, 50]);
  }}
}}

module plate_opening() {{
  difference() {{
    translate([plate_x, plate_y, 0]) cube([plate_w, plate_d, 40]);
    below_z(plate_t);
  }}
}}

// Everything below the sloped underside of the PCB.
module under_board() {{
  translate([0, 0, Hf - 5])
    rotate([atan((Hr - Hf) / D), 0, 0])
      translate([-20, -40, -80])
        cube([W + 40, D + 120, 80]);
}}

module boss(x, y) {{
  // Tall enough for the rear edge of the stud, then cut to the board slope.
  h = pcb_bottom(y + 3) - floor_t + 0.4;
  if (pcb_bottom(y) - floor_t > 0.4)
    intersection() {{
      translate([x, y, floor_t - 0.2]) cylinder(h=h + 0.2, d=6, $fn=24);
      under_board();
    }}
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

module charge_port() {{
  // 12 x 6 mm opening through the rear wall and the ledge, into the cavity.
  // Screw holes are 21 mm apart and pass through the same wall.
  translate([{port_x:.3f}, pcb_y + pcb_d - seat - 1, 7.1])
    cube([12, D - (pcb_y + pcb_d - seat - 1) + 1, 6]);
  translate([{screw_l:.3f}, D + 1, 10.1])
    rotate([90, 0, 0]) cylinder(h=D - (pcb_y + pcb_d - seat) + 3, d=2.4, $fn=16);
  translate([{screw_r:.3f}, D + 1, 10.1])
    rotate([90, 0, 0]) cylinder(h=D - (pcb_y + pcb_d - seat) + 3, d=2.4, $fn=16);
}}

module power_slot() {{
  // Slide-switch lever, just left of the charging port. Opens into the cavity.
  translate([{sw_x - 4:.3f}, pcb_y + pcb_d - seat - 1, 12.0])
    cube([8, D - (pcb_y + pcb_d - seat - 1) + 1, 3.2]);
}}

seat = {SEAT:.2f};       // ledge under the PCB edge
drop = {DROP:.2f};        // clearance around the PCB so it drops in
cover_t = {COVER_T:.2f};
light = {LIGHT:.2f};

// Volume below a plane parallel to the PCB underside, shifted up by h.
module below_plane(h) {{
  translate([0, 0, h]) under_board();
}}

module base() {{
  union() {{
    difference() {{
      // Wall tops are flush with the top of the PCB, so the cover meets them.
      intersection() {{
        outer();
        below_plane(pcb_t);
      }}
      // Open the interior from the floor up. A cutter clipped to the slope
      // shares a face with the solid and OpenSCAD drops it, so this cube
      // runs through the top and the ledge cut below forms the seat.
      translate([pcb_x + seat, pcb_y + seat, floor_t])
        cube([pcb_w - 2 * seat, pcb_d - 2 * seat, 40]);
      // Ledge top is the PCB underside. The cutter starts just under that
      // plane so it meets the cavity instead of sitting on a shared face.
      intersection() {{
        translate([pcb_x - drop, pcb_y - drop, 0])
          cube([pcb_w + 2 * drop, pcb_d + 2 * drop, 40]);
        difference() {{
          translate([-5, -5, 0]) cube([W + 10, D + 10, 40]);
          below_plane(-0.05);
        }}
      }}
      charge_port();
      power_slot();
    }}
    bosses();
    battery_dam();
  }}
}}

module key_openings() {{
{key_openings}
}}

module cover() {{
  // Same outer size as the case. Sits on the PCB and on the wall tops.
  difference() {{
    intersection() {{
      cube([W, D, 30]);
      difference() {{
        below_plane(pcb_t + cover_t);
        below_plane(pcb_t);
      }}
    }}
    key_openings();
  }}
}}

if (part == "base") base();
if (part == "cover") cover();
"""
    (OUT / "case.scad").write_text(scad)


def mcu_pin_holes():
    """Case-coordinate cylinders for every drilled hole in U1."""
    text = PCB.read_text()
    token = '\t(footprint "MCU_nice_nano:Nice_Nano_V2"'
    start = text.find(token)
    if start < 0:
        raise SystemExit("module footprint not found")
    depth = 0
    for j in range(start, len(text)):
        depth += (text[j] == "(") - (text[j] == ")")
        if depth == 0 and j > start:
            block = text[start:j + 1]
            break
    else:
        raise SystemExit("module footprint did not close")
    at = re.search(r"\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\)", block)
    ax, ay, rot = (float(at.group(1)), float(at.group(2)), float(at.group(3)))
    ang = math.radians(rot)
    cos, sin = math.cos(ang), math.sin(ang)
    holes = []
    for pad in re.finditer(r"\(pad\b.*?\(drill ([-\d.]+)\)", block, re.S):
        loc = re.search(r"\(at ([-\d.]+) ([-\d.]+)", pad.group(0))
        lx, ly = float(loc.group(1)), float(loc.group(2))
        wx = ax + lx * cos + ly * sin
        wy = ay - lx * sin + ly * cos
        holes.append(to_case(wx, wy))
    if len(holes) < 20:
        raise SystemExit(f"expected the module pin field, found {len(holes)}")
    print(f"module pin holes {len(holes)}")
    return "\n".join(
        "    translate([{x:.3f}, {y:.3f}, -1]) cylinder(h=26, d=1.6, $fn=20);".format(
            x=x, y=y)
        for x, y in holes
    )


def load_keys():
    """Switch center, keycap unit size, and placement rotation."""
    lines = PCB.read_text().splitlines()
    keys = []
    for i, line in enumerate(lines):
        if not line.startswith('\t(footprint "Switch_Keyboard_Kailh:'):
            continue
        name = re.search(r':([^"]+)"', line).group(1)
        um = re.search(r'_([0-9.]+)u', name)
        if not um:
            raise SystemExit(f"no key size in {name}")
        for nxt in lines[i:i + 15]:
            if nxt.strip().startswith("(at "):
                nums = [float(v) for v in re.findall(r"[-\d.]+", nxt)]
                rot = nums[2] if len(nums) > 2 else 0.0
                keys.append((nums[0], nums[1], float(um.group(1)), rot))
                break
    return keys


def plate_to_case(px, py):
    return to_case(px + PLATE_X0, PLATE_Y1 - py)


def pcb_seam(seam):
    """Plate seam extended to the PCB rear edge, in case coordinates."""
    pts = [plate_to_case(x, y) for x, y in seam]
    front = to_case(BOARD_X0, BOARD_Y1)[1]
    rear = to_case(BOARD_X0, BOARD_Y0)[1]
    if pts[0][1] > front + 0.01:
        pts.insert(0, (pts[0][0], front))
    if pts[-1][1] < rear - 0.01:
        pts.append((pts[-1][0], rear))
    return pts


def seam_x_at(seam, case_y):
    for (x0, y0), (x1, y1) in zip(seam, seam[1:]):
        lo, hi = (y0, y1) if y0 <= y1 else (y1, y0)
        if case_y < lo - 1e-6 or case_y > hi + 1e-6 or abs(y1 - y0) < 1e-6:
            continue
        return x0 + (x1 - x0) * (case_y - y0) / (y1 - y0)
    raise SystemExit(f"seam has no x at case y {case_y:.2f}")


def write_fit_scad(seam):
    """Printable PCB halves, keycap blanks, and a sample charging plug.

    The PCB is the real 1.6 mm outline, split on the stairstep seam so every
    switch hole stays on one half. The module, its USB receptacle, the battery
    connector, and the slide switch are on the face that points at the floor.
    """
    # Stairstep seam between the keys, same cut as the plate. Each switch,
    # including every pin hole, stays on one half. The case is one piece, so
    # the two prints drop in side by side and the steps lock them together.
    pcb_x, pcb_front = to_case(BOARD_X0, BOARD_Y1)
    pcb_rear = to_case(BOARD_X0, BOARD_Y0)[1]
    gap = 0.3
    x0, x1 = pcb_x + gap, pcb_x + BOARD_W - gap
    y0, y1 = pcb_front + gap, pcb_rear - gap
    full = pcb_seam(seam)
    cut = [(seam_x_at(full, y0), y0)]
    for x, y in full:
        if y0 + 1e-6 < y < y1 - 1e-6:
            cut.append((x, y))
    cut.append((seam_x_at(full, y1), y1))
    left = [(x0, y0)] + cut + [(x0, y1)]
    right = [(x1, y1)] + list(reversed(cut)) + [(x1, y0)]

    keys = load_keys()
    if len(keys) != 86:
        raise SystemExit(f"expected 86 key sizes, found {len(keys)}")
    if any(abs(rot) > 0.1 for *_, rot in keys):
        raise SystemExit("a switch is rotated; keycap axes need a swap")

    def cap_size(u):
        # 1u Choc cap is 18.0 x 17.0 on the 19.05 mm pitch. Wider keys grow in x.
        return (u * 19.05 - 1.05, 17.0)

    def disk_crosses(cx, cy, radius):
        for (ax, ay), (bx, by) in zip(cut, cut[1:]):
            if abs(ax - bx) < 1e-6:
                if (abs(cx - ax) < radius
                        and min(ay, by) < cy + radius and max(ay, by) > cy - radius):
                    return True
            elif (abs(cy - ay) < radius
                    and min(ax, bx) < cx + radius and max(ax, bx) > cx - radius):
                return True
        return False

    holes = {"left": [], "right": []}
    caps = {"left": [], "right": []}
    switch_holes = ((0, 0, 5.05), (0, -5.9, 1.6), (5, -3.8, 1.6), (-5, 5.15, 2.0))
    for kx, ky, u, rot in keys:
        cx, cy = to_case(kx, ky)
        side = "left" if cx < seam_x_at(cut, cy) else "right"
        ang = math.radians(rot)
        cos, sin = math.cos(ang), math.sin(ang)
        for lx, ly, diameter in switch_holes:
            hx = cx + lx * cos + ly * sin
            hy = cy - lx * sin + ly * cos
            if disk_crosses(hx, hy, diameter / 2 + 0.4):
                raise SystemExit(
                    f"switch at ({kx:.2f}, {ky:.2f}) is cut by the seam")
        holes[side].append((kx, ky, rot))
        caps[side].append(cap_size(u))

    def pack(items):
        gap = 3.0
        bed = 248.0
        x = y = gap
        row_h = 0.0
        placed = []
        for w, d in sorted(items, key=lambda s: -s[0]):
            if x + w + gap > bed:
                x = gap
                y += row_h + gap
                row_h = 0.0
            placed.append((x, y, w, d))
            x += w + gap
            row_h = max(row_h, d)
        if y + row_h + gap > 250:
            raise SystemExit("keycaps do not fit the printer bed")
        return placed

    packed = {side: pack(items) for side, items in caps.items()}

    # Choc V2 holes, local to the switch. Small drills are opened slightly so
    # a printed hole stays open for the switch pins. The center matches KiCad.

    def hole_lines(switches):
        lines = []
        for kx, ky, rot in switches:
            ang = math.radians(rot)
            cos, sin = math.cos(ang), math.sin(ang)
            for lx, ly, diameter in switch_holes:
                wx = kx + lx * cos + ly * sin
                wy = ky - lx * sin + ly * cos
                x, y = to_case(wx, wy)
                lines.append(
                    "    translate([{x:.3f}, {y:.3f}, -1]) cylinder(h=26, d={d:.2f}, $fn=24);".format(
                        x=x, y=y, d=diameter)
                )
        return "\n".join(lines)

    def cap_lines(items):
        return "\n".join(
            "    translate([{x:.3f}, {y:.3f}, 0]) keycap({w:.3f}, {d:.3f});".format(
                x=x, y=y, w=w, d=d)
            for x, y, w, d in items
        )

    # Every module pin, opened to 1.6 mm so a printed hole will take the pin.
    # The solid module stand-in is omitted so the real board can sit flat.
    mcu_holes = mcu_pin_holes()
    # JST-PH body and the slide switch, including a lever that enters the rear slot.
    def hanging(x, y, w, d, h):
        return (
            "    intersection() {{\n"
            "      translate([{x:.3f}, {y:.3f}, 0]) cube([{w:.3f}, {d:.3f}, 25]);\n"
            "      hang({h:.2f});\n"
            "    }}".format(x=x, y=y, w=w, d=d, h=h)
        )

    jst = hanging(*to_case(311.00, 25.25), 8, 4.5, 6)
    slide = hanging(*to_case(326.27, 25.50), 10, 5, 3)
    # Lever reaches through the rear wall and into the switch slot.
    lever = hanging(*to_case(327.27, 23.00), 8, 5.5, 2.5)

    scad = f"""// Fit-check parts for the 256 mm bed. Not the copper board.
// pcb-left / pcb-right: 1.6 mm board, cut on the stairstep seam between the
// keys and tilted to sit on the studs. Each switch, pins included, is entirely
// on one half. Drop both halves into the one-piece case; the steps interlock.
// Module pin holes are 1.6 mm. The JST, the slide switch, and its lever hang
// below the right half.
// caps-left / caps-right: Choc-sized blanks. Print flat, then turn the stem
// down through a plate hole. The stem is 13.2 mm and the plate hole is 14.15 mm.
// plug: 11.5 x 17 x 5.5 mm stand-in for the extension-cable male housing.
pcb_t = 1.6;
Hf = {H_FRONT};
Hr = {H_REAR};
D = {CASE_D:.4f};
W = {CASE_W:.4f};
part = is_undef(part) ? "pcb-left" : part;

module keycap(w, d) {{
  cube([w, d, 6]);
  translate([(w - 13.2) / 2, (d - 13.2) / 2, 6]) cube([13.2, 13.2, 3.4]);
}}

// Same slope as the stud tops in the case.
module under_board() {{
  translate([0, 0, Hf - 5])
    rotate([atan((Hr - Hf) / D), 0, 0])
      translate([-20, -40, -80])
        cube([W + 40, D + 120, 80]);
}}

// A layer of the given thickness hanging just below the board.
module hang(h) {{
  difference() {{
    translate([0, 0, 0.2]) under_board();
    translate([0, 0, -h]) under_board();
  }}
}}

module pcb_half(outline) {{
  difference() {{
    intersection() {{
      linear_extrude(25) polygon(outline);
      difference() {{
        translate([0, 0, pcb_t]) under_board();
        under_board();
      }}
    }}
    children();
  }}
}}

module pcb_left() {{
  pcb_half({scad_points(left)}) {{
{hole_lines(holes["left"])}
  }}
}}

module pcb_right() {{
  union() {{
    pcb_half({scad_points(right)}) {{
{hole_lines(holes["right"])}
{mcu_holes}
    }}
{jst}
{slide}
{lever}
  }}
}}

if (part == "pcb-left") pcb_left();
if (part == "pcb-right") pcb_right();
if (part == "caps-left") {{
{cap_lines(packed["left"])}
}}
if (part == "caps-right") {{
{cap_lines(packed["right"])}
}}
if (part == "plug") cube([17, 11.5, 5.5]);
"""
    (OUT / "fit.scad").write_text(scad)
    print(f"fit keys left {len(caps['left'])}, right {len(caps['right'])}")


def main():
    switches = load_switches()
    if len(switches) != 86:
        raise SystemExit(f"expected 86 switches, found {len(switches)}")
    seams = choose_seams(switches)
    seam = seam_polyline(switches, seams)
    write_dxf(switches)
    write_plate_scad(switches, seam)
    write_case_scad()
    write_fit_scad(seam)
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
