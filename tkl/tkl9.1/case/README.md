# v9.1 print and assembly guide

v9.1 has **one integrated switch plate/upper frame**, a reinforced bottom case,
and **12 screw joints through matching holes in the new PCB**. The raised strips
between typing rows are gone. The lower switch grid remains to locate and retain
the switches. Use this set with the **v9.1 PCB**, not the earlier undrilled v9 PCB.

The footprint remains **355.56 × 133.352 mm**. The case including its upper frame
remains **7.3 mm at the front and 20.6 mm at the rear**, excluding keycaps/feet.
The plate is 1.5 mm thick, with its top 2.2 mm above the 1.6 mm PCB. Integral
0.7 mm spacers at the screw points carry the clamping load into PCB supports.
The direct recessed USB opening and battery reserve are retained.

[Complete print kit](tkl-v9.1-print-kit.zip) · [Small fit samples](tkl-v9.1-fit-coupons.zip) · [Mounting map](mounting-plan.svg)

## Print these first

1. `mount-coupon-case.stl`, `mount-coupon-pcb.stl`, `mount-coupon-upper.stl`.
   These isolate the actual nut slot, post, spacer and screw-seat dimensions.
   Center the two 14 mm squares on the 16 mm base around the screw hole. The
   base uses the keyboard's tilt; the squares sit parallel to its post top.
   See `mount-coupon-assembly.step`. This sample has a plain plate square;
   it does not test nearby switch/stabilizer geometry.
2. `single-switch-fit.stl` for a Choc V2 pin insertion test.
3. `fit-coupon-case.stl`, `fit-coupon-pcb.stl`, `fit-coupon-upper.stl` plus
   `module-gap-gauge.stl` for the real clone, corner switches and USB bezel.
   The gauge sets the clone's 1 mm mounting gap; remove it after soldering.
4. Trial-fit your actual plate-mount stabilizers and low-profile caps in the
   upper before soldering. Generic stabilizer slots and assumed cap envelopes
   still need physical travel checks.

All units are millimetres. Print at **100% scale**. Main bare PCB STLs already
add **0.4 mm to switch/module hole diameters**; do not add another slicer hole
expansion for the first trial. Centers, thickness, outline and the 2.5 mm M2
holes are unchanged. The STEP PCB and manufacturing drills remain nominal.
A fit in an enlarged plastic hole does not prove nominal PCB hole clearance.

## Full case files

| Part | Large printer | Printer with a 256 mm bed |
| --- | --- | --- |
| Bottom | `case.stl` | `case-left.stl` + `case-right.stl` |
| Integrated plate and frame | `upper-integrated.stl` | `upper-left.stl` + `upper-right.stl` |
| Bare PCB fit gauge | `pcb-bare.stl` | `pcb-left.stl` + `pcb-right.stl` |

The bottom floor has a **6 mm half-lap overlap** across its center seam. The
integrated upper has a **4 mm half-lap overlap along a stepped seam** between
switch positions. Both have a **0.2 mm glue gap**. These are bonded joints,
not snap fittings: align and bond both plastic halves with an adhesive suitable
for your filament, keeping glue out of switch apertures and mating faces. Let
it cure before assembly. The continuous manufactured FR-4 and distributed
screws provide additional support across the joints; printed PCB halves do not.
If the printer can accommodate it, print each unsplit part for a stronger seam-free result.
`base-split.step` and `upper-split.step` show the halves in their mating positions.

STLs are placed on the bed individually. The bottom has a flat underside. The
upper has feet below its plate and a raised outer frame; inspect its orientation
and use removable support beneath unsupported areas. Keep supports/glue away
from switch clips, recessed screw seats and nut pockets. Thin lap tongues and
nut roofs need complete slicer paths. Start with 0.15 mm layers and verify the
coupon in your chosen filament before committing to the long prints. Material,
printer calibration and layer adhesion determine actual strength.

`pcb-populated*.stl` and `*-envelope.stl` are clearance gauges with approximate
component shapes. They are not insertion fixtures. `fit-assembly.step` is the
complete nominal assembly with screw/nut and component envelopes. No separate
cover or standalone switch plate is needed for v9.1.

## Hardware and assembly

- **12 × M2 × 5 mm button-head screws**, ISO 7380-1 dimensions: 3.8 mm maximum
  head diameter, 1.3 mm maximum head height. A taller socket-cap head will not
  fit the recess. Use ordinary fully threaded screws.
- **12 × M2 DIN 934 hex nuts**, 4.0 mm across flats, 1.6 mm high. The printed
  side pocket is 4.25 mm across flats and 1.8 mm high, with a 1.0 mm roof.

Reference dimensions: [M2 × 5 button-head screw](https://www.vital-parts.co.uk/hex-socket-button-screws-iso-7380-1/6927-hbs73801-m2-5-a4),
[M2 DIN 934 nut](https://www.accu.co.uk/hexagon-nuts/766418-NUT202M2-B).
Check the hardware you receive against these dimensions in the mounting sample.

1. Bond split parts if used. Slide each nut into its post/bracket **from the +X
   side** (right when viewing the keyboard from above). Do this before inserting
   the PCB. The nuts sit beneath a roof so screws clamp the bottom case as well
   as the PCB and upper.
2. Trial-fit the PCB and upper, put a screw through each upper recess and PCB
   mounting hole, and gently tighten in stages. Confirm the base supports meet
   the PCB, the upper spacers meet its top, and every head sits below the plate
   surface. Do not force the plastic flat with a screw. The nominal head recess
   is only 0.1 mm below the plate top, so check print and hardware tolerances.
3. Remove the stack. Fit the plate-mount stabilizers and switches into the upper,
   align their pins through the PCB, and verify switch seating and full keycap
   travel. Then solder the switches to the PCB while the assembly is outside
   the base. The plate grips the switches; solder joins switches to the PCB.
4. Install the clone underneath with the specified short pins and 1 mm gap;
   follow `../BRINGUP.md`. Check solder joints and perform the electrical tests
   before installing a battery.
5. Lower the complete plate/switch/PCB assembly into the base. Guide the clone's
   socket into the recessed USB bezel. Install and gently tighten all 12 screws
   from above, with the keycaps removed, then install the keycaps. Do not attach
   assembly rails inside the case.

The front/central mounts reach the floor; three rear mounts attach to the rear
wall **above** the battery space. Floor ribs avoid the board, solder tails and
battery. This supplies positive clamping instead of relying on loose locating
posts. Avoid overtightening: thin printed lands/roofs can crack or creep. No
measured torque limit, load test or fatigue life has been established.

## Remaining physical checks

The battery reserve remains **270 × 52 × 6.3 mm** at the rear, with a provisional
maximum pack envelope of **264 × 50 × 5.5 mm** inside it. A specific pack and its
charging/protection suitability remain unselected. Do not wedge a pouch against
screws, ribs or solder tails.

Clone body thickness/socket axis, auxiliary pin registration, actual keycap and
stabilizer travel, bezel strength and cable fit still need real-part trials.
The 0.6 mm recessed USB web needs careful slicing and an insertion test. CAD
collision and watertight-mesh checks do not establish printed strength, electrical
operation or a final manufacturing approval. See `fit-report.json` and
`mesh-validation.json` for exactly what was modeled and checked.
