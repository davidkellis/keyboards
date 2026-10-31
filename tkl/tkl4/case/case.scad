// Wedge shell. Flat on the table.
// Front lip 7.0 mm, rear lip 20.2 mm.
// Print each half with the flat bottom on the bed, 0.2 mm layers, 4 walls.
Hf = 7.0;
Hr = 20.2;
floor_t = 1.2;
wall = 2.0;
plate_t = 1.2;
ledge = 1.2;
W = 354.7600;
D = 133.1900;
part = is_undef(part) ? "left" : part;
split_x = 174.9700; // straight joint; the plate seam steps across it
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

// Band between the top of the PCB and the underside of the plate.
module shelf_band() {
  difference() {
    below_z(plate_t);
    below_z(3.1);
  }
}

// Plastic over the PCB margin. The inner edge tucks under the plate so the plate has a seat.
module shelf() {
  intersection() {
    difference() {
      translate([pcb_x - 0.2, pcb_y - 0.2, 0]) cube([pcb_w + 0.4, pcb_d + 0.4, 40]);
      translate([plate_x + ledge, plate_y + ledge, -1])
        cube([plate_w - 2 * ledge, plate_d - 2 * ledge, 50]);
    }
    shelf_band();
  }
}

module plate_opening() {
  difference() {
    translate([plate_x, plate_y, 0]) cube([plate_w, plate_d, 40]);
    below_z(plate_t);
  }
}

module boss(x, y) {
  h = pcb_bottom(y) - floor_t;
  if (h > 0.4)
    translate([x, y, floor_t - 0.2]) cylinder(h=h + 0.2, d=6, $fn=24);
}

module bosses() {
    boss(10.000, 10.000);
    boss(344.760, 10.000);
    boss(10.000, 123.190);
    boss(344.760, 123.190);
    boss(177.380, 10.000);
    boss(177.380, 103.190);
    boss(26.000, 66.595);
    boss(328.760, 66.595);
}

// Keeps a thin pouch cell from sliding into the module. Sits well below the PCB.
module battery_dam() {
  translate([48.47, 95.99, floor_t - 0.2])
    difference() {
      cube([70, 32, 1.4]);
      translate([1.2, 1.2, -0.2]) cube([67.6, 29.6, 2]);
    }
}

module usb_slot() {
  translate([24.120, D - wall - 1, 8.5])
    cube([16, wall + 2, 7]);
}

module shell() {
  difference() {
    union() {
      difference() {
        outer();
        translate([pcb_x, pcb_y, floor_t]) cube([pcb_w, pcb_d, 40]);
      }
      shelf();
      bosses();
      battery_dam();
    }
    usb_slot();
    plate_opening();
  }
}

module pinned() {
  difference() {
    shell();
    for (y = [30, 70, 110])
      translate([split_x, y, -1]) cylinder(h=floor_t + 2, d=3.2, $fn=20);
  }
}

if (part == "left")
  intersection() {
    pinned();
    translate([-1, -1, -1]) cube([split_x + 1, D + 2, 40]);
  }
if (part == "right")
  intersection() {
    pinned();
    translate([split_x, -1, -1]) cube([W, D + 2, 40]);
  }
