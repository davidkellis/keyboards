// Design envelopes, not manufacturer CAD. Dimensions require measurement.
module module_envelopes() {
  // U1
  color([0.95,0.48,0.12]) translate([302.19000000000005,42.69,-4.5]) cube([33.83999999999992,19.0,4.0]);
  // USB_MALE
  color([0.95,0.78,0.18]) translate([285.19000000000005,46.44,-5.25]) cube([17.0,11.5,4.5]);
  // USB_REAR: registered to vertical rear case wall
  rotate([-5.695609528003503,0,0]) translate([-2.4,-2.4,-2.1125750051177867])
    color([0.95,0.78,0.18]) translate([327.87,111.35221193128154,4.7]) cube([25.0,20.0,5.999999999999999]);
  // CABLE1
  color([0.95,0.78,0.18]) translate([278.47,50.69,-5.0]) cube([6.720000000000027,3.0,3.0]);
  // CABLE2
  color([0.95,0.78,0.18]) translate([278.47,52.19,-5.0]) cube([3.0,51.0,3.0]);
  // CABLE3
  color([0.95,0.78,0.18]) translate([278.47,92.19,-5.0]) cube([11.0,11.0,3.0]);
  // CABLE4
  color([0.95,0.78,0.18]) translate([286.47,100.19,-5.0]) cube([51.5,3.0,3.0]);
  // CABLE5: registered to vertical rear case wall
  rotate([-5.695609528003503,0,0]) translate([-2.4,-2.4,-2.1125750051177867])
    color([0.95,0.78,0.18]) translate([338.87,103.35221193128154,6.2]) cube([3.0,8.0,4.6000000000000005]);
}
