// Right end of the case, with PCB/plate/cover removed to show cable routing.
// Orange: module. Yellow: plug, cable allowance and rear socket. Blue: End/Up outlines.
// All module/cable dimensions are provisional fit limits, not actual-part measurements.
use <module-envelopes.scad>
module pcb_frame() { translate([2.4,2.4,2.1125750051177867]) rotate([5.695609528003503,0,0]) children(); }
color([0.4,0.46,0.53]) intersection() {
  import("case.stl");
  translate([274,0,-1]) cube([83,135,25]);
}
pcb_frame() module_envelopes();
pcb_frame() color([0.25,0.55,0.85]) translate([320.6325,68.2275,1.6]) {
  linear_extrude(.15) difference() { square([14,14],center=true); square([13.5,13.5],center=true); }
  linear_extrude(.15) text("End",size=2.3,halign="center",valign="center");
}
pcb_frame() color([0.25,0.55,0.85]) translate([320.6325,30.1275,1.6]) {
  linear_extrude(.15) difference() { square([14,14],center=true); square([13.5,13.5],center=true); }
  linear_extrude(.15) text("Up",size=2.3,halign="center",valign="center");
}
