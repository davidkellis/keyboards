// v9.3 plain recessed plate. Dimensions in mm; physical fit still requires trial.
use <module-envelopes.scad>
explode=18;
module pcb_frame() { translate([2.4,2.4,2.1125750051177867]) rotate([5.695609528003503,0,0]) children(); }
color([0.25,0.3,0.37]) import("case.stl");
pcb_frame() color([0.12,0.5,0.25]) import("pcb-bare.stl");
pcb_frame() module_envelopes();
translate([0,0,explode]) pcb_frame() translate([0.0,0.3,1.6])
    color([0.6,0.7,0.82]) import("plate.stl");
translate([6.0,78.5,1.7]) color([0.8,0.65,0.3]) import("battery-reserve-gauge-270x52x6.3.stl");
