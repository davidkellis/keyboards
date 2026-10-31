// Generated view. Use the STEP for CAD, STL files for printing (millimetres).
// Keycaps and stabilizer mounting remain unverified. No light simulation is implied.
use <module-envelopes.scad>
show_cover=true;
explode=18;
show_plate=true;
module pcb_frame() { translate([2.4,2.4,2.1125750051177867]) rotate([5.695609528003503,0,0]) children(); }
color([0.25,0.3,0.37]) import("case.stl");
pcb_frame() color([0.12,0.5,0.25]) import("pcb-bare.stl");
pcb_frame() module_envelopes();
if (show_plate) translate([0,0,explode]) pcb_frame()
    translate([0,0,1.6]) color([0.2,0.5,0.85]) import("plate-supported.stl");
translate([6.0,78.5,1.7]) color([0.8,0.65,0.3]) import("battery-reserve-gauge-270x52x6.3.stl");
if (show_cover) translate([0,0,2*explode]) pcb_frame()
    translate([-2.4000000000000004,-1.9930164674760817,3.799999999999999]) color([0.8,0.82,0.85]) import("cover.stl");
