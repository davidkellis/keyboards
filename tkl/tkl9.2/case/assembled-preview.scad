// v9.2 plain recessed plate. Dimensions in mm; physical fit still requires trial.
use <module-envelopes.scad>
explode=0;
module pcb_frame() { translate([2.4,2.4,2.1125750051177867]) rotate([5.695609528003503,0,0]) children(); }
color([0.25,0.3,0.37]) import("case.stl");
pcb_frame() color([0.12,0.5,0.25]) import("pcb-bare.stl");

translate([0,0,explode]) pcb_frame() translate([0.0,0.3,1.6])
    color([0.6,0.7,0.82]) import("plate.stl");
