// Printed plate halves. Holes are 14.15 mm so a 0.4 mm nozzle
// still clips a Kailh Choc V2. Laser-cut the DXF instead if you can:
// that file uses the true 13.95 mm opening.
plate_t = 1.2;
part = is_undef(part) ? "left" : part;

module holes() {
    translate([261.1063,30.1250]) square([14.15,14.15], center=true);
    translate([39.6500,68.2250]) square([14.15,14.15], center=true);
    translate([68.2250,111.0875]) square([14.15,14.15], center=true);
    translate([106.3250,111.0875]) square([14.15,14.15], center=true);
    translate([339.6875,87.2750]) square([14.15,14.15], center=true);
    translate([15.8375,68.2250]) square([14.15,14.15], center=true);
    translate([211.1000,68.2250]) square([14.15,14.15], center=true);
    translate([158.7125,49.1750]) square([14.15,14.15], center=true);
    translate([220.6250,87.2750]) square([14.15,14.15], center=true);
    translate([49.1750,87.2750]) square([14.15,14.15], center=true);
    translate([68.2250,87.2750]) square([14.15,14.15], center=true);
    translate([182.5250,87.2750]) square([14.15,14.15], center=true);
    translate([173.0000,111.0875]) square([14.15,14.15], center=true);
    translate([277.7750,111.0875]) square([14.15,14.15], center=true);
    translate([125.3750,87.2750]) square([14.15,14.15], center=true);
    translate([173.0000,68.2250]) square([14.15,14.15], center=true);
    translate([249.2000,68.2250]) square([14.15,14.15], center=true);
    translate([206.3375,30.1250]) square([14.15,14.15], center=true);
    translate([153.9500,68.2250]) square([14.15,14.15], center=true);
    translate([44.4125,49.1750]) square([14.15,14.15], center=true);
    translate([320.6375,30.1250]) square([14.15,14.15], center=true);
    translate([82.5125,49.1750]) square([14.15,14.15], center=true);
    translate([130.1375,30.1250]) square([14.15,14.15], center=true);
    translate([268.2500,87.2750]) square([14.15,14.15], center=true);
    translate([13.4563,11.0750]) square([14.15,14.15], center=true);
    translate([115.8500,68.2250]) square([14.15,14.15], center=true);
    translate([139.6625,49.1750]) square([14.15,14.15], center=true);
    translate([120.6125,49.1750]) square([14.15,14.15], center=true);
    translate([101.5625,49.1750]) square([14.15,14.15], center=true);
    translate([339.6875,68.2250]) square([14.15,14.15], center=true);
    translate([87.2750,87.2750]) square([14.15,14.15], center=true);
    translate([77.7500,68.2250]) square([14.15,14.15], center=true);
    translate([225.3875,30.1250]) square([14.15,14.15], center=true);
    translate([187.2875,30.1250]) square([14.15,14.15], center=true);
    translate([87.2750,111.0875]) square([14.15,14.15], center=true);
    translate([339.6875,111.0875]) square([14.15,14.15], center=true);
    translate([11.0750,87.2750]) square([14.15,14.15], center=true);
    translate([106.3250,87.2750]) square([14.15,14.15], center=true);
    translate([320.6375,87.2750]) square([14.15,14.15], center=true);
    translate([163.4750,87.2750]) square([14.15,14.15], center=true);
    translate([111.0875,30.1250]) square([14.15,14.15], center=true);
    translate([63.4625,49.1750]) square([14.15,14.15], center=true);
    translate([339.6875,11.0750]) square([14.15,14.15], center=true);
    translate([320.6375,11.0750]) square([14.15,14.15], center=true);
    translate([68.2250,11.0750]) square([14.15,14.15], center=true);
    translate([320.6375,68.2250]) square([14.15,14.15], center=true);
    translate([92.0375,30.1250]) square([14.15,14.15], center=true);
    translate([192.0500,111.0875]) square([14.15,14.15], center=true);
    translate([142.0437,11.0750]) square([14.15,14.15], center=true);
    translate([134.9000,111.0875]) square([14.15,14.15], center=true);
    translate([39.6500,11.0750]) square([14.15,14.15], center=true);
    translate([320.6375,111.0875]) square([14.15,14.15], center=true);
    translate([168.2375,30.1250]) square([14.15,14.15], center=true);
    translate([49.1750,111.0875]) square([14.15,14.15], center=true);
    translate([230.1500,68.2250]) square([14.15,14.15], center=true);
    translate([58.7000,68.2250]) square([14.15,14.15], center=true);
    translate([234.9125,49.1750]) square([14.15,14.15], center=true);
    translate([215.8625,11.0750]) square([14.15,14.15], center=true);
    translate([258.7250,111.0875]) square([14.15,14.15], center=true);
    translate([149.1875,30.1250]) square([14.15,14.15], center=true);
    translate([273.0125,11.0750]) square([14.15,14.15], center=true);
    translate([22.9812,30.1250]) square([14.15,14.15], center=true);
    translate([53.9375,30.1250]) square([14.15,14.15], center=true);
    translate([273.0125,68.2250]) square([14.15,14.15], center=true);
    translate([153.9500,111.0875]) square([14.15,14.15], center=true);
    translate([239.6750,111.0875]) square([14.15,14.15], center=true);
    translate([301.5875,11.0750]) square([14.15,14.15], center=true);
    translate([96.8000,68.2250]) square([14.15,14.15], center=true);
    translate([18.2187,49.1750]) square([14.15,14.15], center=true);
    translate([134.9000,68.2250]) square([14.15,14.15], center=true);
    translate([301.5875,87.2750]) square([14.15,14.15], center=true);
    translate([244.4375,11.0750]) square([14.15,14.15], center=true);
    translate([196.8125,49.1750]) square([14.15,14.15], center=true);
    translate([301.5875,68.2250]) square([14.15,14.15], center=true);
    translate([192.0500,68.2250]) square([14.15,14.15], center=true);
    translate([30.1250,87.2750]) square([14.15,14.15], center=true);
    translate([177.7625,49.1750]) square([14.15,14.15], center=true);
    translate([220.6250,111.0875]) square([14.15,14.15], center=true);
    translate([301.5875,111.0875]) square([14.15,14.15], center=true);
    translate([144.4250,87.2750]) square([14.15,14.15], center=true);
    translate([239.6750,87.2750]) square([14.15,14.15], center=true);
    translate([201.5750,87.2750]) square([14.15,14.15], center=true);
    translate([265.8688,49.1750]) square([14.15,14.15], center=true);
    translate([11.0750,111.0875]) square([14.15,14.15], center=true);
    translate([215.8625,49.1750]) square([14.15,14.15], center=true);
    translate([72.9875,30.1250]) square([14.15,14.15], center=true);
}

module half(outline) {
  linear_extrude(plate_t)
    difference() {
      polygon(outline);
      holes();
    }
}

if (part == "left") half([[0.0000,0.0000],[178.9750,0.0000],[178.9750,3.0875],[178.9750,19.0875],[178.9750,20.5875],[177.7625,20.5875],[177.7625,22.0875],[177.7625,38.0875],[177.7625,39.6375],[168.2375,39.6375],[168.2375,41.1875],[168.2375,57.1875],[168.2375,58.6875],[163.4750,58.6875],[163.4750,60.1875],[163.4750,76.1875],[163.4750,77.7375],[173.0000,77.7375],[173.0000,79.2875],[173.0000,95.2875],[173.0000,99.1875],[163.4750,99.1875],[163.4750,103.0875],[163.4750,119.0875],[163.4750,122.1625],[0.0000,122.1625]]);
if (part == "right") half([[350.7625,122.1625],[163.4750,122.1625],[163.4750,119.0875],[163.4750,103.0875],[163.4750,99.1875],[173.0000,99.1875],[173.0000,95.2875],[173.0000,79.2875],[173.0000,77.7375],[163.4750,77.7375],[163.4750,76.1875],[163.4750,60.1875],[163.4750,58.6875],[168.2375,58.6875],[168.2375,57.1875],[168.2375,41.1875],[168.2375,39.6375],[177.7625,39.6375],[177.7625,38.0875],[177.7625,22.0875],[177.7625,20.5875],[178.9750,20.5875],[178.9750,19.0875],[178.9750,3.0875],[178.9750,0.0000],[350.7625,0.0000]]);
