# v10 print files

Use the **v10 base, plate and PCB together**. The controller is now underneath
Esc/F1, USB at the rear left, and three rear-right keys have returned. H9 and
H12 moved; previous bases/plates are not a matching set.

Print first:

1. `mount-coupon-case.stl`, `mount-coupon-pcb.stl`, `mount-coupon-upper.stl`:
   test M2 × 5 button screws and standard DIN 934 M2 nuts (4 mm across flats,
   1.6 mm thick). Side-load each nut before placing the PCB.
2. `single-switch-fit.stl`: check the larger holes with a real Choc V2 switch.
3. `fit-coupon-case.stl`, `fit-coupon-pcb.stl`, `fit-coupon-upper.stl` and
   `module-gap-gauge.stl`: matching **rear-left** module/USB samples.
4. `led-fit-coupon.stl` and `led-diffuser.stl`: check the flush light insert.

For a 256 mm bed print `case-left.stl` + `case-right.stl`, and `plate-left.stl`
+ `plate-right.stl`. These have bonded lap joints, not snap joints; dry-fit,
align and bond before assembly. Full-size `case.stl` and `plate.stl` need a
larger bed. STLs use millimetres and are placed individually on the bed. Review
support needs in your slicer, particularly nut roofs and underside plate
pockets. The 0.6 mm USB bezel web needs a physical strength/fit test.

`pcb-bare.stl`, `pcb-left.stl`, `pcb-right.stl` and PCB coupons are plastic
insertion gauges with **0.4 mm added to switch/module hole diameters only**.
Print at 100%, without additional slicer hole expansion for the first trial.
STEP PCB references and manufacturing drills remain nominal. The populated
PCB STLs show printed component/pin envelopes; they cannot accept real pins.

The plate is 1.5 mm thick above its 0.7 mm spacers. Its plain top sits 1.6 mm
below the rim. Hidden pin channels have a 0.9 mm roof and 0.3 mm clearance above
pins protruding at most 1 mm beyond the PCB. **Solder and test the controller
before fitting the plate/switches**, and trim both J1 tails. Ordinary header
pins may be used with their plastic strip removed and the 1 mm gap gauge;
do not use tall female header sockets. Remove the temporary gauge afterward.

Print six `led-diffuser.stl` inserts in clear/translucent material. The 2.1 mm
stems fit the 2.3 mm holes; 3.4 mm flanges sit underneath. Tack the flanges with
compatible adhesive, keeping the optical faces clear. Brightness is untested.

The battery reserve is 155 × 50 × 6.3 mm at case x=83, y=80.5, z=1.7 mm.
The intended pack is advertised as 147 × 44 × 5 mm; maximum complete-pack
allowance is 149 × 46 × 5.5 mm, including wrapping/protection. Gauges for both
allowance and reserve are included. Do not compress the pouch to achieve fit.
Wire routing, connector polarity and protection must be checked on the parts.

The USB opening surrounds the module socket directly: 10.1 × 3.8 mm rounded
through-slot and a wider blind plug recess. There is no extension cable.
Module maximum thickness/socket-axis and cable insertion remain provisional;
the supplied corner trial is the way to verify them before a full print/order.

`fit-assembly.step` preserves assembled coordinates. `assembled-preview.png`
shows the actual generated case and plate with keys omitted. The tiny LED
inserts and screws are shown installed; controller envelope models are design
allowances, not manufacturer CAD. Fit/rule checks do not establish print
strength, keycap travel, stabilizer fit, charging or radio performance.
