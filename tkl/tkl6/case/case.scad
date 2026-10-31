// Wedge shell. Flat on the table.
// Front lip 7.0 mm, rear lip 20.2 mm.
// Print each half with the flat bottom on the bed, 0.2 mm layers, 4 walls.
Hf = 7.0;
Hr = 20.2;
floor_t = 1.2;
pcb_t = 1.6;
wall = 2.0;
plate_t = 1.2;
ledge = 1.2;
W = 354.7600;
D = 133.1900;
part = is_undef(part) ? "base" : part;
split_x = 174.9700; // unused; the case prints as one piece
plate_x = 1.9950;
plate_y = 2.0025;
plate_w = 350.7625;
plate_d = 122.1625;
pcb_x = 2.0000;
pcb_y = 2.0000;
pcb_w = 350.7600;
pcb_d = 129.1900;

function rim(y) = Hf + (Hr - Hf) * y / D;
// Bottom of the 1.6 mm PCB: 1.2 plate + 2.2 switch gap + 1.6 board below the rim.
function pcb_bottom(y) = rim(y) - 5.0;

module outer() {
  hull() {
    cube([W, 0.02, Hf]);
    translate([0, D - 0.02, 0]) cube([W, 0.02, Hr]);
  }
}

module below_z(drop) {
  hull() {
    cube([W, 0.02, Hf - drop]);
    translate([0, D - 0.02, 0]) cube([W, 0.02, Hr - drop]);
  }
}

// Band under the plate. The plate bottom is 1.2 mm below the rim and the PCB
// top is 3.4 mm below it. A 0.8 mm lip leaves 1.4 mm of room to tuck the board under.
module shelf_band() {
  difference() {
    below_z(plate_t);
    below_z(2.0);
  }
}

// Plastic over the PCB margin. The inner edge tucks under the plate so the plate has a seat.
module shelf() {
  difference() {
    intersection() {
      difference() {
        translate([pcb_x - 0.2, pcb_y - 0.2, 0]) cube([pcb_w + 0.4, pcb_d + 0.4, 40]);
        translate([plate_x + 0.8, plate_y + 0.8, -1])
          cube([plate_w - 1.6, plate_d - 1.6, 50]);
      }
      shelf_band();
    }
    // The board hangs past the plate at the rear. Leave that strip open.
    translate([pcb_x - 1, plate_y + plate_d - 0.8, -1])
      cube([pcb_w + 2, 40, 50]);
  }
}

module plate_opening() {
  difference() {
    translate([plate_x, plate_y, 0]) cube([plate_w, plate_d, 40]);
    below_z(plate_t);
  }
}

// Everything below the sloped underside of the PCB.
module under_board() {
  translate([0, 0, Hf - 5])
    rotate([atan((Hr - Hf) / D), 0, 0])
      translate([-20, -40, -80])
        cube([W + 40, D + 120, 80]);
}

module boss(x, y) {
  // Tall enough for the rear edge of the stud, then cut to the board slope.
  h = pcb_bottom(y + 3) - floor_t + 0.4;
  if (pcb_bottom(y) - floor_t > 0.4)
    intersection() {
      translate([x, y, floor_t - 0.2]) cylinder(h=h + 0.2, d=6, $fn=24);
      under_board();
    }
}

module bosses() {
    boss(14.970, 123.190);
    boss(149.970, 123.190);
    boss(224.970, 123.190);
    boss(29.970, 101.190);
    boss(134.970, 101.190);
    boss(224.970, 101.190);
    boss(314.970, 101.190);
    boss(29.970, 61.190);
    boss(134.970, 61.190);
    boss(239.970, 61.190);
    boss(74.970, 23.190);
    boss(179.970, 23.190);
    boss(284.970, 23.190);
    boss(29.970, 9.190);
    boss(149.970, 9.190);
    boss(254.970, 9.190);
    boss(329.970, 9.190);
}

// Keeps a thin pouch cell from sliding into the module. Sits well below the PCB.
module battery_dam() {
  translate([48.47, 95.99, floor_t - 0.2])
    difference() {
      cube([70, 32, 1.4]);
      translate([1.2, 1.2, -0.2]) cube([67.6, 29.6, 2]);
    }
}

module charge_port() {
  // 12 x 6 mm opening through the rear wall and the ledge, into the cavity.
  // Screw holes are 21 mm apart and pass through the same wall.
  translate([330.760, pcb_y + pcb_d - seat - 1, 7.1])
    cube([12, D - (pcb_y + pcb_d - seat - 1) + 1, 6]);
  translate([326.260, D + 1, 10.1])
    rotate([90, 0, 0]) cylinder(h=D - (pcb_y + pcb_d - seat) + 3, d=2.4, $fn=16);
  translate([347.260, D + 1, 10.1])
    rotate([90, 0, 0]) cylinder(h=D - (pcb_y + pcb_d - seat) + 3, d=2.4, $fn=16);
}

module power_slot() {
  // Slide-switch lever, just left of the charging port. Opens into the cavity.
  translate([302.240, pcb_y + pcb_d - seat - 1, 12.0])
    cube([8, D - (pcb_y + pcb_d - seat - 1) + 1, 3.2]);
}

seat = 2.00;       // ledge under the PCB edge
drop = 0.40;        // clearance around the PCB so it drops in
cover_t = 1.80;
light = 1.00;

// Volume below a plane parallel to the PCB underside, shifted up by h.
module below_plane(h) {
  translate([0, 0, h]) under_board();
}

module base() {
  union() {
    difference() {
      // Wall tops are flush with the top of the PCB, so the cover meets them.
      intersection() {
        outer();
        below_plane(pcb_t);
      }
      // Open the interior from the floor up. A cutter clipped to the slope
      // shares a face with the solid and OpenSCAD drops it, so this cube
      // runs through the top and the ledge cut below forms the seat.
      translate([pcb_x + seat, pcb_y + seat, floor_t])
        cube([pcb_w - 2 * seat, pcb_d - 2 * seat, 40]);
      // Ledge top is the PCB underside. The cutter starts just under that
      // plane so it meets the cavity instead of sitting on a shared face.
      intersection() {
        translate([pcb_x - drop, pcb_y - drop, 0])
          cube([pcb_w + 2 * drop, pcb_d + 2 * drop, 40]);
        difference() {
          translate([-5, -5, 0]) cube([W + 10, D + 10, 40]);
          below_plane(-0.05);
        }
      }
      charge_port();
      power_slot();
    }
    bosses();
    battery_dam();
  }
}

module key_openings() {
  translate([236.433, 22.627, -1]) cube([53.338, 19.000, 40]);
  translate([31.645, 60.727, -1]) cube([20.000, 19.000, 40]);
  translate([60.220, 103.590, -1]) cube([20.000, 19.000, 40]);
  translate([98.320, 103.590, -1]) cube([20.000, 19.000, 40]);
  translate([331.683, 79.778, -1]) cube([20.000, 19.000, 40]);
  translate([3.070, 60.727, -1]) cube([29.525, 19.000, 40]);
  translate([203.095, 60.727, -1]) cube([20.000, 19.000, 40]);
  translate([150.708, 41.677, -1]) cube([20.000, 19.000, 40]);
  translate([212.620, 79.778, -1]) cube([20.000, 19.000, 40]);
  translate([41.170, 79.778, -1]) cube([20.000, 19.000, 40]);
  translate([60.220, 79.778, -1]) cube([20.000, 19.000, 40]);
  translate([174.520, 79.778, -1]) cube([20.000, 19.000, 40]);
  translate([164.995, 103.590, -1]) cube([20.000, 19.000, 40]);
  translate([269.770, 103.590, -1]) cube([20.000, 19.000, 40]);
  translate([117.370, 79.778, -1]) cube([20.000, 19.000, 40]);
  translate([164.995, 60.727, -1]) cube([20.000, 19.000, 40]);
  translate([241.195, 60.727, -1]) cube([20.000, 19.000, 40]);
  translate([198.333, 22.627, -1]) cube([20.000, 19.000, 40]);
  translate([145.945, 60.727, -1]) cube([20.000, 19.000, 40]);
  translate([36.407, 41.677, -1]) cube([20.000, 19.000, 40]);
  translate([312.633, 22.627, -1]) cube([20.000, 19.000, 40]);
  translate([74.507, 41.677, -1]) cube([20.000, 19.000, 40]);
  translate([122.132, 22.627, -1]) cube([20.000, 19.000, 40]);
  translate([250.720, 79.778, -1]) cube([39.050, 19.000, 40]);
  translate([3.070, 3.577, -1]) cube([24.762, 19.000, 40]);
  translate([107.845, 60.727, -1]) cube([20.000, 19.000, 40]);
  translate([131.657, 41.677, -1]) cube([20.000, 19.000, 40]);
  translate([112.607, 41.677, -1]) cube([20.000, 19.000, 40]);
  translate([93.558, 41.677, -1]) cube([20.000, 19.000, 40]);
  translate([331.683, 60.727, -1]) cube([20.000, 19.000, 40]);
  translate([79.270, 79.778, -1]) cube([20.000, 19.000, 40]);
  translate([69.745, 60.727, -1]) cube([20.000, 19.000, 40]);
  translate([217.382, 22.627, -1]) cube([20.000, 19.000, 40]);
  translate([179.282, 22.627, -1]) cube([20.000, 19.000, 40]);
  translate([79.270, 103.590, -1]) cube([20.000, 19.000, 40]);
  translate([331.683, 103.590, -1]) cube([20.000, 19.000, 40]);
  translate([3.070, 79.778, -1]) cube([20.000, 19.000, 40]);
  translate([98.320, 79.778, -1]) cube([20.000, 19.000, 40]);
  translate([312.633, 79.778, -1]) cube([20.000, 19.000, 40]);
  translate([155.470, 79.778, -1]) cube([20.000, 19.000, 40]);
  translate([103.083, 22.627, -1]) cube([20.000, 19.000, 40]);
  translate([55.457, 41.677, -1]) cube([20.000, 19.000, 40]);
  translate([331.683, 3.577, -1]) cube([20.000, 19.000, 40]);
  translate([312.633, 3.577, -1]) cube([20.000, 19.000, 40]);
  translate([55.457, 3.577, -1]) cube([29.525, 19.000, 40]);
  translate([312.633, 60.727, -1]) cube([20.000, 19.000, 40]);
  translate([84.032, 22.627, -1]) cube([20.000, 19.000, 40]);
  translate([184.045, 103.590, -1]) cube([20.000, 19.000, 40]);
  translate([84.032, 3.577, -1]) cube([120.013, 19.000, 40]);
  translate([126.895, 103.590, -1]) cube([20.000, 19.000, 40]);
  translate([26.882, 3.577, -1]) cube([29.525, 19.000, 40]);
  translate([312.633, 103.590, -1]) cube([20.000, 19.000, 40]);
  translate([160.232, 22.627, -1]) cube([20.000, 19.000, 40]);
  translate([41.170, 103.590, -1]) cube([20.000, 19.000, 40]);
  translate([222.145, 60.727, -1]) cube([20.000, 19.000, 40]);
  translate([50.695, 60.727, -1]) cube([20.000, 19.000, 40]);
  translate([226.907, 41.677, -1]) cube([20.000, 19.000, 40]);
  translate([203.095, 3.577, -1]) cube([29.525, 19.000, 40]);
  translate([250.720, 103.590, -1]) cube([20.000, 19.000, 40]);
  translate([141.183, 22.627, -1]) cube([20.000, 19.000, 40]);
  translate([260.245, 3.577, -1]) cube([29.525, 19.000, 40]);
  translate([3.070, 22.627, -1]) cube([43.813, 19.000, 40]);
  translate([45.933, 22.627, -1]) cube([20.000, 19.000, 40]);
  translate([260.245, 60.727, -1]) cube([29.525, 19.000, 40]);
  translate([145.945, 103.590, -1]) cube([20.000, 19.000, 40]);
  translate([231.670, 103.590, -1]) cube([20.000, 19.000, 40]);
  translate([293.582, 3.577, -1]) cube([20.000, 19.000, 40]);
  translate([88.795, 60.727, -1]) cube([20.000, 19.000, 40]);
  translate([3.070, 41.677, -1]) cube([34.288, 19.000, 40]);
  translate([126.895, 60.727, -1]) cube([20.000, 19.000, 40]);
  translate([293.582, 79.778, -1]) cube([20.000, 19.000, 40]);
  translate([231.670, 3.577, -1]) cube([29.525, 19.000, 40]);
  translate([188.808, 41.677, -1]) cube([20.000, 19.000, 40]);
  translate([293.582, 60.727, -1]) cube([20.000, 19.000, 40]);
  translate([184.045, 60.727, -1]) cube([20.000, 19.000, 40]);
  translate([22.120, 79.778, -1]) cube([20.000, 19.000, 40]);
  translate([169.757, 41.677, -1]) cube([20.000, 19.000, 40]);
  translate([212.620, 103.590, -1]) cube([20.000, 19.000, 40]);
  translate([293.582, 103.590, -1]) cube([20.000, 19.000, 40]);
  translate([136.420, 79.778, -1]) cube([20.000, 19.000, 40]);
  translate([231.670, 79.778, -1]) cube([20.000, 19.000, 40]);
  translate([193.570, 79.778, -1]) cube([20.000, 19.000, 40]);
  translate([245.958, 41.677, -1]) cube([43.813, 19.000, 40]);
  translate([3.070, 103.590, -1]) cube([20.000, 19.000, 40]);
  translate([207.857, 41.677, -1]) cube([20.000, 19.000, 40]);
  translate([64.983, 22.627, -1]) cube([20.000, 19.000, 40]);
}

module cover() {
  // Same outer size as the case. Sits on the PCB and on the wall tops.
  difference() {
    intersection() {
      cube([W, D, 30]);
      difference() {
        below_plane(pcb_t + cover_t);
        below_plane(pcb_t);
      }
    }
    key_openings();
  }
}

if (part == "base") base();
if (part == "cover") cover();
