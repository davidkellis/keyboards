// Exterior of the actual case STL, with the module omitted to show the aperture.
// The small opening is a through-slot; the larger pocket stops on the recessed bezel.
translate([-32.52,-131,-11]) color([0.32,0.43,0.56]) intersection() {
  import("case.stl");
  translate([16,113,-1]) cube([35,23,25]);
}
