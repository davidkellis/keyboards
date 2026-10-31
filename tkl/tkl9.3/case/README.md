# v9.3 print and assembly guide

**The controller slots and battery-connector cutout are now blind pockets on
the underside.** Their top surface is uninterrupted, with a 0.9 mm roof and
0.3 mm clearance over correctly trimmed pins. LED openings have six flush,
round translucent inserts. The existing M2 screws sit in their recessed seats;
the screw heads remain visible. No decorative lid has been added.

The **plain switch plate** fits inside a **continuous rim on the bottom case**.
There is no top cover, raised typing-row separator, or raised frame on the
plate. The rim is about 1.6 mm above the plate, with a small clearance gap inside
it. The outside walls have no horizontal lid/base seam. A split print still has
the left/right joining seam; bond and finish that seam if it must be invisible.

The footprint remains **355.56 × 133.352 mm**, and the assembled outside height
remains **7.3 mm front / 20.6 mm rear**, excluding feet and keycaps. The plate is
**1.5 mm** thick with its top **2.2 mm above the PCB**. Existing 0.7 mm spacers,
twelve M2 clamp points, ribs, battery bay and direct recessed USB port remain.
This uses the **v9.1 PCB**, copied unchanged into v9.3.
The **v9.2 base can be reused**: `case.stl`, `case-left.stl` and `case-right.stl`
are identical to v9.2. Only the new plate and six inserts need printing if you
already have that base.

## Files to print

| Part | Large printer | 256 mm bed |
| --- | --- | --- |
| Bottom case with rim | `case.stl` | `case-left.stl` + `case-right.stl` |
| Plain switch plate | `plate.stl` | `plate-left.stl` + `plate-right.stl` |
| Flush light windows | `led-diffuser.stl` × **6** | Same file × **6** |
| PCB insertion gauge | `pcb-bare.stl` | `pcb-left.stl` + `pcb-right.stl` |

[Complete kit](tkl-v9.3-print-kit.zip) · [Small samples](tkl-v9.3-fit-coupons.zip)

Start with **`rim-coupon-case.stl`, `rim-coupon-plate.stl`, and
`rim-coupon-pcb.stl`**. These are the actual front-left mating geometry; use
`rim-coupon-assembly.step` to see their relative positions. The rim sample's PCB
STL has the same enlarged switch/module holes as the other insertion gauges;
the assembly STEP retains nominal PCB holes.

Also test the existing rear corner with `fit-coupon-case.stl`,
`fit-coupon-pcb.stl`, `fit-coupon-upper.stl` and `module-gap-gauge.stl`.
The legacy **`upper` coupon filenames now contain only the plain plate**,
including its new blind pin pockets.
They test the module, socket insertion, rear rim and nearby switches together.
`mount-coupon-case.stl`, `mount-coupon-pcb.stl`, `mount-coupon-upper.stl` isolate
the screw/nut stack. Refer to `mount-coupon-assembly.step` for alignment.

Print `led-fit-coupon.stl` and **one** `led-diffuser.stl` to test the light window
before printing six inserts. The opening is 2.3 mm diameter; the insert has a
2.1 mm stem, 3.4 mm flange and a 0.4 mm flange thickness. It installs **from
underneath** so the top is flush. Tack the flange to the underside with a small
amount of filament-compatible adhesive; the nominal clearance is not a press
fit. Keep adhesive out of the light path and let it cure before fitting the PCB.
Use clear/translucent material for the insert; opaque case filament may block
the LEDs. `led-diffuser-assembly.step` shows the orientation. Optical brightness
and diffusion are untested, and the smaller windows change the light pattern.

Print all files at **100% in millimetres**. The main PCB insertion STLs and both
corner PCB samples enlarge switch/module holes by **0.4 mm diameter**. Do not apply
additional slicer hole expansion for the first trial. The manufacturing files
and nominal PCB STEP do not have this enlargement.

The base halves have a 6 mm bonded floor lap; plate halves have a 4 mm stepped
bonded lap with a 0.2 mm glue gap. Bond with a filament-compatible adhesive and
allow it to cure before assembly. `base-split.step` and `plate-split.step` show
the joints in their common coordinates. Full-size, unsplit parts are preferable
when the printer can accommodate them.

The STL parts are individually placed on the bed. The base has a flat floor.
The plate has spacers and blind clearance pockets on its underside. For a
smoother visible surface, try printing with the **visible face down on a smooth
build plate**; the small coupon should establish the best orientation for your
printer. Keep supports and adhesive out of switch clips, screw seats and pin
pockets. Start with 0.15 mm layers for the plate and 0.1 mm for the tiny light
inserts; inspect the pockets and thin roofs in the slicer.

## Hardware and assembly

Each keyboard uses **12 M2 × 5 mm button-head machine screws** (0.4 mm pitch,
head no larger than 3.8 mm diameter × 1.3 mm high) and **12 DIN 934 M2 hex nuts**
(4 mm across flats × 1.6 mm thick). No additional fasteners or nut inserts are
needed for this revision. Use the matching driver specified for your screws.

1. Bond any split prints. Slide the nuts into the case supports from the +X
   side before fitting the PCB. Nut slots are 4.25 mm across flats × 1.8 mm high.
2. With the PCB unpowered, trim the **two J1 battery-connector pin tails** to
   no more than **1.0 mm above the PCB's top surface**, including the solder
   envelope. Trim exposed metal rather than removing the solder joint. Remove
   the clippings and inspect the joints. The factory BOM/CPL has not changed;
   this is a manual finishing step.
3. Solder the clone underneath **before fitting the plate and switches**, using
   the 1 mm gap gauge. Its top-side pins, solder and auxiliary connections must
   also stay within 1.0 mm above the PCB. The pocket ceiling is 1.3 mm above the
   PCB, leaving 0.3 mm nominal clearance. Remove the gauge after soldering and
   follow `../BRINGUP.md`. Top-side controller pads become inaccessible once the
   plate and switches are installed; later service may require desoldering keys.
4. Dry-fit plate, PCB and screws. The plate should clear the rim without force,
   its feet should meet the PCB, and the screw heads should sit below the plate
   top. The nominal head recess only provides 0.1 mm below the top surface.
   Confirm that the blind roofs do not rest on solder joints or bent pins.
5. Bond the six translucent inserts to the plate underside, test flush seating,
   and allow the adhesive to cure. Outside the case, install the plate-mount
   stabilizers and switches in the
   plate, insert their pins through the PCB and test full keycap travel before
   soldering. The switch clips attach to the plate; their pins solder to the PCB.
   Support the assembly clear of the installed controller while soldering.
   Perform the electrical checks before connecting a battery.
6. Guide the module's USB socket into the recessed rear bezel while lowering
   the plate/PCB assembly inside the rim. Check the real insertion motion with
   the corner sample first. Tighten the twelve screws gently and progressively,
   with keycaps removed. Fit the keycaps afterward.

The screws clamp the plate and PCB to the base using the existing supports;
the rim is not a friction fit or a snap latch. Do not wedge the plate against
the walls to prevent rattle. Check the dry assembly for rocking, flex and loose
contacts before deciding whether any local cushioning is needed.

## Validation limits

`fit-report.json` records modeled component/plate/case collisions, rim gaps,
and checks that the raised rim does not block upward movement of the plate or
bare PCB. That insertion check excludes the USB module; guiding the real socket
into the existing recessed port still requires the physical corner trial.
`mesh-validation.json` checks printable mesh integrity and split bed bounds.
`surface-validation.json` independently sections the exported plate STL to
check the closed top skin and open underside pockets. It also checks the round
light windows and insert dimensions. Actual lead trimming and glue fit remain
physical checks.

The front border is inset 0.3 mm to clear the tilted plate from the vertical
wall. Model clearances are approximately 0.32 mm front, 0.40 mm each side and
0.63 mm rear, measured horizontally at the closest plate surface. Printed fit
depends on shrinkage and calibration. The fitting line is inside the rim and
remains visible from above; separate removable parts are not literally seamless.

The battery reserve remains 270 × 52 × 6.3 mm, with a provisional maximum complete
pack of 264 × 50 × 5.5 mm. Exact battery suitability, clone/socket thickness,
stabilizer and keycap travel, printed stiffness and electronics remain physical
checks. The narrow USB bezel is still provisional. Existing CAD checks are not
a substitute for those tests.
