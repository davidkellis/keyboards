// Right end of the case, with PCB/plate/cover removed to show the direct USB module.
// Orange: module. Yellow: socket and external plug gauge. Blue: retained navigation keys.
// All module/cable dimensions are provisional fit limits, not actual-part measurements.
use <module-envelopes.scad>
module pcb_frame() { translate([2.4,2.4,2.1125750051177867]) rotate([5.695609528003503,0,0]) children(); }
color([0.4,0.46,0.53]) intersection() {
  import("case.stl");
  translate([290,77,-1]) cube([67,58,25]);
}
pcb_frame() module_envelopes();
pcb_frame() color([0.25,0.55,0.85]) translate([301.5825,87.2775,1.6]) {
  linear_extrude(.15) difference() { square([14,14],center=true); square([13.5,13.5],center=true); }
  linear_extrude(.15) text("Insert",size=2.3,halign="center",valign="center");
}
pcb_frame() color([0.25,0.55,0.85]) translate([320.6325,87.2775,1.6]) {
  linear_extrude(.15) difference() { square([14,14],center=true); square([13.5,13.5],center=true); }
  linear_extrude(.15) text("Home",size=2.3,halign="center",valign="center");
}
pcb_frame() color([0.25,0.55,0.85]) translate([339.6825,87.2775,1.6]) {
  linear_extrude(.15) difference() { square([14,14],center=true); square([13.5,13.5],center=true); }
  linear_extrude(.15) text("PgUp",size=2.3,halign="center",valign="center");
}
