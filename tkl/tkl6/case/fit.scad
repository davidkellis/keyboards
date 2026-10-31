// Fit-check parts for the 256 mm bed. Not the copper board.
// pcb-left / pcb-right: 1.6 mm board, cut on the stairstep seam between the
// keys and tilted to sit on the studs. Each switch, pins included, is entirely
// on one half. Drop both halves into the one-piece case; the steps interlock.
// Module pin holes are 1.6 mm. The JST, the slide switch, and its lever hang
// below the right half.
// caps-left / caps-right: Choc-sized blanks. Print flat, then turn the stem
// down through a plate hole. The stem is 13.2 mm and the plate hole is 14.15 mm.
// plug: 11.5 x 17 x 5.5 mm stand-in for the extension-cable male housing.
pcb_t = 1.6;
Hf = 7.0;
Hr = 20.2;
D = 133.1900;
W = 354.7600;
part = is_undef(part) ? "pcb-left" : part;

module keycap(w, d) {
  cube([w, d, 6]);
  translate([(w - 13.2) / 2, (d - 13.2) / 2, 6]) cube([13.2, 13.2, 3.4]);
}

// Same slope as the stud tops in the case.
module under_board() {
  translate([0, 0, Hf - 5])
    rotate([atan((Hr - Hf) / D), 0, 0])
      translate([-20, -40, -80])
        cube([W + 40, D + 120, 80]);
}

// A layer of the given thickness hanging just below the board.
module hang(h) {
  difference() {
    translate([0, 0, 0.2]) under_board();
    translate([0, 0, -h]) under_board();
  }
}

module pcb_half(outline) {
  difference() {
    intersection() {
      linear_extrude(25) polygon(outline);
      difference() {
        translate([0, 0, pcb_t]) under_board();
        under_board();
      }
    }
    children();
  }
}

module pcb_left() {
  pcb_half([[2.3000,2.3000],[180.9700,2.3000],[180.9700,5.0900],[180.9700,21.0900],[180.9700,22.5900],[179.7575,22.5900],[179.7575,24.0900],[179.7575,40.0900],[179.7575,41.6400],[170.2325,41.6400],[170.2325,43.1900],[170.2325,59.1900],[170.2325,60.6900],[165.4700,60.6900],[165.4700,62.1900],[165.4700,78.1900],[165.4700,79.7400],[174.9950,79.7400],[174.9950,81.2900],[174.9950,97.2900],[174.9950,101.1900],[165.4700,101.1900],[165.4700,105.0900],[165.4700,121.0900],[165.4700,124.1650],[165.4700,130.8900],[2.3000,130.8900]]) {
    translate([41.645, 70.227, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([41.645, 76.127, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([46.645, 74.027, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([36.645, 65.077, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([70.220, 113.090, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([70.220, 118.990, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([75.220, 116.890, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([65.220, 107.940, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([108.320, 113.090, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([108.320, 118.990, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([113.320, 116.890, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([103.320, 107.940, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([17.832, 70.227, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([17.832, 76.127, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([22.832, 74.027, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([12.832, 65.077, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([160.708, 51.177, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([160.708, 57.078, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([165.708, 54.977, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([155.708, 46.027, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([51.170, 89.278, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([51.170, 95.177, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([56.170, 93.077, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([46.170, 84.127, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([70.220, 89.278, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([70.220, 95.177, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([75.220, 93.077, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([65.220, 84.127, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([127.370, 89.278, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([127.370, 95.177, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([132.370, 93.077, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([122.370, 84.127, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([155.945, 70.227, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([155.945, 76.127, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([160.945, 74.027, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([150.945, 65.077, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([46.407, 51.177, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([46.407, 57.078, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([51.407, 54.977, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([41.407, 46.027, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([84.507, 51.177, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([84.507, 57.078, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([89.507, 54.977, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([79.507, 46.027, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([132.132, 32.127, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([132.132, 38.028, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([137.132, 35.927, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([127.132, 26.977, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([15.451, 13.077, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([15.451, 18.977, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([20.451, 16.877, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([10.451, 7.927, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([117.845, 70.227, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([117.845, 76.127, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([122.845, 74.027, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([112.845, 65.077, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([141.657, 51.177, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([141.657, 57.078, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([146.657, 54.977, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([136.657, 46.027, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([122.607, 51.177, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([122.607, 57.078, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([127.607, 54.977, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([117.607, 46.027, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([103.558, 51.177, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([103.558, 57.078, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([108.558, 54.977, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([98.558, 46.027, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([89.270, 89.278, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([89.270, 95.177, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([94.270, 93.077, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([84.270, 84.127, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([79.745, 70.227, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([79.745, 76.127, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([84.745, 74.027, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([74.745, 65.077, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([89.270, 113.090, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([89.270, 118.990, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([94.270, 116.890, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([84.270, 107.940, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([13.070, 89.278, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([13.070, 95.177, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([18.070, 93.077, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([8.070, 84.127, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([108.320, 89.278, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([108.320, 95.177, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([113.320, 93.077, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([103.320, 84.127, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([165.470, 89.278, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([165.470, 95.177, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([170.470, 93.077, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([160.470, 84.127, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([113.083, 32.127, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([113.083, 38.028, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([118.083, 35.927, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([108.083, 26.977, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([65.457, 51.177, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([65.457, 57.078, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([70.457, 54.977, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([60.457, 46.027, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([70.220, 13.077, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([70.220, 18.977, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([75.220, 16.877, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([65.220, 7.927, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([94.032, 32.127, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([94.032, 38.028, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([99.032, 35.927, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([89.032, 26.977, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([144.039, 13.077, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([144.039, 18.977, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([149.039, 16.877, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([139.039, 7.927, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([136.895, 113.090, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([136.895, 118.990, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([141.895, 116.890, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([131.895, 107.940, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([41.645, 13.077, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([41.645, 18.977, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([46.645, 16.877, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([36.645, 7.927, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([170.232, 32.127, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([170.232, 38.028, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([175.232, 35.927, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([165.232, 26.977, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([51.170, 113.090, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([51.170, 118.990, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([56.170, 116.890, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([46.170, 107.940, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([60.695, 70.227, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([60.695, 76.127, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([65.695, 74.027, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([55.695, 65.077, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([151.183, 32.127, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([151.183, 38.028, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([156.183, 35.927, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([146.183, 26.977, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([24.976, 32.127, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([24.976, 38.028, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([29.976, 35.927, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([19.976, 26.977, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([55.933, 32.127, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([55.933, 38.028, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([60.933, 35.927, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([50.933, 26.977, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([155.945, 113.090, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([155.945, 118.990, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([160.945, 116.890, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([150.945, 107.940, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([98.795, 70.227, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([98.795, 76.127, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([103.795, 74.027, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([93.795, 65.077, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([20.214, 51.177, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([20.214, 57.078, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([25.214, 54.977, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([15.214, 46.027, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([136.895, 70.227, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([136.895, 76.127, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([141.895, 74.027, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([131.895, 65.077, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([32.120, 89.278, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([32.120, 95.177, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([37.120, 93.077, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([27.120, 84.127, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([146.420, 89.278, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([146.420, 95.177, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([151.420, 93.077, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([141.420, 84.127, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([13.070, 113.090, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([13.070, 118.990, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([18.070, 116.890, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([8.070, 107.940, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([74.983, 32.127, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([74.983, 38.028, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([79.983, 35.927, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([69.983, 26.977, -1]) cylinder(h=26, d=2.00, $fn=24);
  }
}

module pcb_right() {
  union() {
    pcb_half([[352.4600,130.8900],[165.4700,130.8900],[165.4700,124.1650],[165.4700,121.0900],[165.4700,105.0900],[165.4700,101.1900],[174.9950,101.1900],[174.9950,97.2900],[174.9950,81.2900],[174.9950,79.7400],[165.4700,79.7400],[165.4700,78.1900],[165.4700,62.1900],[165.4700,60.6900],[170.2325,60.6900],[170.2325,59.1900],[170.2325,43.1900],[170.2325,41.6400],[179.7575,41.6400],[179.7575,40.0900],[179.7575,24.0900],[179.7575,22.5900],[180.9700,22.5900],[180.9700,21.0900],[180.9700,5.0900],[180.9700,2.3000],[352.4600,2.3000]]) {
    translate([263.101, 32.127, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([263.101, 38.028, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([268.101, 35.927, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([258.101, 26.977, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([341.683, 89.278, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([341.683, 95.177, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([346.683, 93.077, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([336.683, 84.127, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([213.095, 70.227, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([213.095, 76.127, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([218.095, 74.027, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([208.095, 65.077, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([222.620, 89.278, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([222.620, 95.177, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([227.620, 93.077, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([217.620, 84.127, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([184.520, 89.278, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([184.520, 95.177, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([189.520, 93.077, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([179.520, 84.127, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([174.995, 113.090, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([174.995, 118.990, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([179.995, 116.890, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([169.995, 107.940, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([279.770, 113.090, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([279.770, 118.990, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([284.770, 116.890, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([274.770, 107.940, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([174.995, 70.227, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([174.995, 76.127, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([179.995, 74.027, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([169.995, 65.077, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([251.195, 70.227, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([251.195, 76.127, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([256.195, 74.027, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([246.195, 65.077, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([208.333, 32.127, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([208.333, 38.028, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([213.333, 35.927, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([203.333, 26.977, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([322.633, 32.127, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([322.633, 38.028, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([327.633, 35.927, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([317.633, 26.977, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([270.245, 89.278, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([270.245, 95.177, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([275.245, 93.077, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([265.245, 84.127, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([341.683, 70.227, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([341.683, 76.127, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([346.683, 74.027, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([336.683, 65.077, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([227.382, 32.127, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([227.382, 38.028, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([232.383, 35.927, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([222.382, 26.977, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([189.282, 32.127, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([189.282, 38.028, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([194.282, 35.927, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([184.282, 26.977, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([341.683, 113.090, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([341.683, 118.990, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([346.683, 116.890, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([336.683, 107.940, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([322.633, 89.278, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([322.633, 95.177, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([327.633, 93.077, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([317.633, 84.127, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([341.683, 13.077, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([341.683, 18.977, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([346.683, 16.877, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([336.683, 7.927, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([322.633, 13.077, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([322.633, 18.977, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([327.633, 16.877, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([317.633, 7.927, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([322.633, 70.227, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([322.633, 76.127, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([327.633, 74.027, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([317.633, 65.077, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([194.045, 113.090, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([194.045, 118.990, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([199.045, 116.890, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([189.045, 107.940, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([322.633, 113.090, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([322.633, 118.990, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([327.633, 116.890, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([317.633, 107.940, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([232.145, 70.227, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([232.145, 76.127, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([237.145, 74.027, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([227.145, 65.077, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([236.907, 51.177, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([236.907, 57.078, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([241.907, 54.977, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([231.907, 46.027, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([217.857, 13.077, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([217.857, 18.977, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([222.857, 16.877, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([212.857, 7.927, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([260.720, 113.090, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([260.720, 118.990, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([265.720, 116.890, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([255.720, 107.940, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([275.008, 13.077, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([275.008, 18.977, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([280.008, 16.877, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([270.008, 7.927, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([275.008, 70.227, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([275.008, 76.127, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([280.008, 74.027, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([270.008, 65.077, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([241.670, 113.090, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([241.670, 118.990, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([246.670, 116.890, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([236.670, 107.940, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([303.582, 13.077, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([303.582, 18.977, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([308.582, 16.877, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([298.582, 7.927, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([303.582, 89.278, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([303.582, 95.177, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([308.582, 93.077, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([298.582, 84.127, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([246.432, 13.077, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([246.432, 18.977, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([251.432, 16.877, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([241.432, 7.927, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([198.808, 51.177, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([198.808, 57.078, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([203.808, 54.977, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([193.808, 46.027, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([303.582, 70.227, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([303.582, 76.127, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([308.582, 74.027, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([298.582, 65.077, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([194.045, 70.227, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([194.045, 76.127, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([199.045, 74.027, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([189.045, 65.077, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([179.757, 51.177, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([179.757, 57.078, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([184.757, 54.977, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([174.757, 46.027, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([222.620, 113.090, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([222.620, 118.990, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([227.620, 116.890, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([217.620, 107.940, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([303.582, 113.090, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([303.582, 118.990, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([308.582, 116.890, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([298.582, 107.940, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([241.670, 89.278, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([241.670, 95.177, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([246.670, 93.077, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([236.670, 84.127, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([203.570, 89.278, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([203.570, 95.177, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([208.570, 93.077, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([198.570, 84.127, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([267.864, 51.177, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([267.864, 57.078, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([272.864, 54.977, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([262.864, 46.027, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([217.857, 51.177, -1]) cylinder(h=26, d=5.05, $fn=24);
    translate([217.857, 57.078, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([222.857, 54.977, -1]) cylinder(h=26, d=1.60, $fn=24);
    translate([212.857, 46.027, -1]) cylinder(h=26, d=2.00, $fn=24);
    translate([308.830, 59.110, -1]) cylinder(h=26, d=1.6, $fn=20);
    translate([311.370, 59.110, -1]) cylinder(h=26, d=1.6, $fn=20);
    translate([313.910, 59.110, -1]) cylinder(h=26, d=1.6, $fn=20);
    translate([316.450, 59.110, -1]) cylinder(h=26, d=1.6, $fn=20);
    translate([318.990, 59.110, -1]) cylinder(h=26, d=1.6, $fn=20);
    translate([321.530, 59.110, -1]) cylinder(h=26, d=1.6, $fn=20);
    translate([324.070, 59.110, -1]) cylinder(h=26, d=1.6, $fn=20);
    translate([326.610, 59.110, -1]) cylinder(h=26, d=1.6, $fn=20);
    translate([329.150, 59.110, -1]) cylinder(h=26, d=1.6, $fn=20);
    translate([331.690, 59.110, -1]) cylinder(h=26, d=1.6, $fn=20);
    translate([334.230, 59.110, -1]) cylinder(h=26, d=1.6, $fn=20);
    translate([336.770, 59.110, -1]) cylinder(h=26, d=1.6, $fn=20);
    translate([336.770, 43.870, -1]) cylinder(h=26, d=1.6, $fn=20);
    translate([334.230, 43.870, -1]) cylinder(h=26, d=1.6, $fn=20);
    translate([331.690, 43.870, -1]) cylinder(h=26, d=1.6, $fn=20);
    translate([329.150, 43.870, -1]) cylinder(h=26, d=1.6, $fn=20);
    translate([326.610, 43.870, -1]) cylinder(h=26, d=1.6, $fn=20);
    translate([324.070, 43.870, -1]) cylinder(h=26, d=1.6, $fn=20);
    translate([321.530, 43.870, -1]) cylinder(h=26, d=1.6, $fn=20);
    translate([318.990, 43.870, -1]) cylinder(h=26, d=1.6, $fn=20);
    translate([316.450, 43.870, -1]) cylinder(h=26, d=1.6, $fn=20);
    translate([313.910, 43.870, -1]) cylinder(h=26, d=1.6, $fn=20);
    translate([311.370, 43.870, -1]) cylinder(h=26, d=1.6, $fn=20);
    translate([308.830, 43.870, -1]) cylinder(h=26, d=1.6, $fn=20);
    translate([333.670, 56.570, -1]) cylinder(h=26, d=1.6, $fn=20);
    translate([333.670, 54.030, -1]) cylinder(h=26, d=1.6, $fn=20);
    translate([333.670, 51.490, -1]) cylinder(h=26, d=1.6, $fn=20);
    translate([306.290, 59.110, -1]) cylinder(h=26, d=1.6, $fn=20);
    translate([306.290, 43.870, -1]) cylinder(h=26, d=1.6, $fn=20);
    }
    intersection() {
      translate([285.970, 125.940, 0]) cube([8.000, 4.500, 25]);
      hang(6.00);
    }
    intersection() {
      translate([301.240, 125.690, 0]) cube([10.000, 5.000, 25]);
      hang(3.00);
    }
    intersection() {
      translate([302.240, 128.190, 0]) cube([8.000, 5.500, 25]);
      hang(2.50);
    }
  }
}

if (part == "pcb-left") pcb_left();
if (part == "pcb-right") pcb_right();
if (part == "caps-left") {
    translate([3.000, 3.000, 0]) keycap(118.013, 17.000);
    translate([124.013, 3.000, 0]) keycap(41.813, 17.000);
    translate([168.825, 3.000, 0]) keycap(32.288, 17.000);
    translate([204.113, 3.000, 0]) keycap(27.525, 17.000);
    translate([3.000, 23.000, 0]) keycap(27.525, 17.000);
    translate([33.525, 23.000, 0]) keycap(27.525, 17.000);
    translate([64.050, 23.000, 0]) keycap(22.762, 17.000);
    translate([89.813, 23.000, 0]) keycap(18.000, 17.000);
    translate([110.813, 23.000, 0]) keycap(18.000, 17.000);
    translate([131.812, 23.000, 0]) keycap(18.000, 17.000);
    translate([152.812, 23.000, 0]) keycap(18.000, 17.000);
    translate([173.812, 23.000, 0]) keycap(18.000, 17.000);
    translate([194.812, 23.000, 0]) keycap(18.000, 17.000);
    translate([215.812, 23.000, 0]) keycap(18.000, 17.000);
    translate([3.000, 43.000, 0]) keycap(18.000, 17.000);
    translate([24.000, 43.000, 0]) keycap(18.000, 17.000);
    translate([45.000, 43.000, 0]) keycap(18.000, 17.000);
    translate([66.000, 43.000, 0]) keycap(18.000, 17.000);
    translate([87.000, 43.000, 0]) keycap(18.000, 17.000);
    translate([108.000, 43.000, 0]) keycap(18.000, 17.000);
    translate([129.000, 43.000, 0]) keycap(18.000, 17.000);
    translate([150.000, 43.000, 0]) keycap(18.000, 17.000);
    translate([171.000, 43.000, 0]) keycap(18.000, 17.000);
    translate([192.000, 43.000, 0]) keycap(18.000, 17.000);
    translate([213.000, 43.000, 0]) keycap(18.000, 17.000);
    translate([3.000, 63.000, 0]) keycap(18.000, 17.000);
    translate([24.000, 63.000, 0]) keycap(18.000, 17.000);
    translate([45.000, 63.000, 0]) keycap(18.000, 17.000);
    translate([66.000, 63.000, 0]) keycap(18.000, 17.000);
    translate([87.000, 63.000, 0]) keycap(18.000, 17.000);
    translate([108.000, 63.000, 0]) keycap(18.000, 17.000);
    translate([129.000, 63.000, 0]) keycap(18.000, 17.000);
    translate([150.000, 63.000, 0]) keycap(18.000, 17.000);
    translate([171.000, 63.000, 0]) keycap(18.000, 17.000);
    translate([192.000, 63.000, 0]) keycap(18.000, 17.000);
    translate([213.000, 63.000, 0]) keycap(18.000, 17.000);
    translate([3.000, 83.000, 0]) keycap(18.000, 17.000);
    translate([24.000, 83.000, 0]) keycap(18.000, 17.000);
    translate([45.000, 83.000, 0]) keycap(18.000, 17.000);
    translate([66.000, 83.000, 0]) keycap(18.000, 17.000);
    translate([87.000, 83.000, 0]) keycap(18.000, 17.000);
    translate([108.000, 83.000, 0]) keycap(18.000, 17.000);
    translate([129.000, 83.000, 0]) keycap(18.000, 17.000);
    translate([150.000, 83.000, 0]) keycap(18.000, 17.000);
}
if (part == "caps-right") {
    translate([3.000, 3.000, 0]) keycap(51.338, 17.000);
    translate([57.338, 3.000, 0]) keycap(41.813, 17.000);
    translate([102.150, 3.000, 0]) keycap(37.050, 17.000);
    translate([142.200, 3.000, 0]) keycap(27.525, 17.000);
    translate([172.725, 3.000, 0]) keycap(27.525, 17.000);
    translate([203.250, 3.000, 0]) keycap(27.525, 17.000);
    translate([3.000, 23.000, 0]) keycap(27.525, 17.000);
    translate([33.525, 23.000, 0]) keycap(18.000, 17.000);
    translate([54.525, 23.000, 0]) keycap(18.000, 17.000);
    translate([75.525, 23.000, 0]) keycap(18.000, 17.000);
    translate([96.525, 23.000, 0]) keycap(18.000, 17.000);
    translate([117.525, 23.000, 0]) keycap(18.000, 17.000);
    translate([138.525, 23.000, 0]) keycap(18.000, 17.000);
    translate([159.525, 23.000, 0]) keycap(18.000, 17.000);
    translate([180.525, 23.000, 0]) keycap(18.000, 17.000);
    translate([201.525, 23.000, 0]) keycap(18.000, 17.000);
    translate([222.525, 23.000, 0]) keycap(18.000, 17.000);
    translate([3.000, 43.000, 0]) keycap(18.000, 17.000);
    translate([24.000, 43.000, 0]) keycap(18.000, 17.000);
    translate([45.000, 43.000, 0]) keycap(18.000, 17.000);
    translate([66.000, 43.000, 0]) keycap(18.000, 17.000);
    translate([87.000, 43.000, 0]) keycap(18.000, 17.000);
    translate([108.000, 43.000, 0]) keycap(18.000, 17.000);
    translate([129.000, 43.000, 0]) keycap(18.000, 17.000);
    translate([150.000, 43.000, 0]) keycap(18.000, 17.000);
    translate([171.000, 43.000, 0]) keycap(18.000, 17.000);
    translate([192.000, 43.000, 0]) keycap(18.000, 17.000);
    translate([213.000, 43.000, 0]) keycap(18.000, 17.000);
    translate([3.000, 63.000, 0]) keycap(18.000, 17.000);
    translate([24.000, 63.000, 0]) keycap(18.000, 17.000);
    translate([45.000, 63.000, 0]) keycap(18.000, 17.000);
    translate([66.000, 63.000, 0]) keycap(18.000, 17.000);
    translate([87.000, 63.000, 0]) keycap(18.000, 17.000);
    translate([108.000, 63.000, 0]) keycap(18.000, 17.000);
    translate([129.000, 63.000, 0]) keycap(18.000, 17.000);
    translate([150.000, 63.000, 0]) keycap(18.000, 17.000);
    translate([171.000, 63.000, 0]) keycap(18.000, 17.000);
    translate([192.000, 63.000, 0]) keycap(18.000, 17.000);
    translate([213.000, 63.000, 0]) keycap(18.000, 17.000);
    translate([3.000, 83.000, 0]) keycap(18.000, 17.000);
    translate([24.000, 83.000, 0]) keycap(18.000, 17.000);
    translate([45.000, 83.000, 0]) keycap(18.000, 17.000);
}
if (part == "plug") cube([17, 11.5, 5.5]);
