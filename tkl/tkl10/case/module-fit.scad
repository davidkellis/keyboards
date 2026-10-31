// Left end of the case, with PCB/plate/cover removed to show the direct USB module.
// Orange: module. Yellow: socket and external plug gauge. Blue: Esc and F1.
// All module/cable dimensions are provisional fit limits, not actual-part measurements.
use <module-envelopes.scad>
module pcb_frame() { translate([2.4,2.4,2.1125750051177867]) rotate([5.695609528003503,0,0]) children(); }
color([0.4,0.46,0.53]) intersection() {
  import("case.stl");
  translate([0,77,-1]) cube([75,58,25]);
}
pcb_frame() module_envelopes();
pcb_frame() color([0.25,0.55,0.85]) translate([11.07,111.09,1.6]) {
  linear_extrude(.15) difference() { square([14,14],center=true); square([13.5,13.5],center=true); }
  linear_extrude(.15) text("Esc",size=2.3,halign="center",valign="center");
}
pcb_frame() color([0.25,0.55,0.85]) translate([49.17,111.09,1.6]) {
  linear_extrude(.15) difference() { square([14,14],center=true); square([13.5,13.5],center=true); }
  linear_extrude(.15) text("F1",size=2.3,halign="center",valign="center");
}
