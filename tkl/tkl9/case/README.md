# v9 fit printing

All STL files are in millimetres. Print at 100%; do not scale to fit. The STEP
assembly retains assembled coordinates; individual STL files lie on the print bed.
These are fit prototypes with approximate component bodies, not production approval.

**The PCB insertion-test STLs in this folder now have larger holes:**
`pcb-bare.stl`, `pcb-left.stl`, `pcb-right.stl`, `fit-coupon-pcb.stl` and
`single-switch-fit.stl`. These add 0.4 mm to switch and module hole diameters
while preserving all pin centers, board thickness and the outline. Start with
the 18 × 18 mm single-switch sample, then the rear-corner sample. The same models
are also in the [larger-hole fit kit](print-fit/tkl-v9-easy-fit.zip).
See the [printing instructions](print-fit/README.md). STEP references retain
nominal drill sizes; the populated STL models remain component-envelope gauges.

## Print these first

| File | Purpose |
| --- | --- |
| `single-switch-fit.stl` | Small 18 × 18 mm insertion sample with enlarged holes |
| `fit-coupon-case.stl` | Rear/right case corner, USB opening and power-switch opening |
| `fit-coupon-pcb.stl` | Matching carrier section with enlarged switch/module holes at actual pin centers |
| `fit-coupon-plate.stl` | Matching switch plate with module solder-tail clearances |
| `fit-coupon-cover.stl` | Matching cover, with the three deleted key positions closed |
| `module-gap-gauge.stl` | Temporary 1 mm mounting-gap gauge, 20 × 5 mm |
| `u1-envelope.stl` | Assumed 33 × 19 × 5 mm module body gauge; includes width allowance |
| `usb_socket-envelope.stl` | Provisional protruding socket gauge |
| `usb_plug_external-envelope.stl` | External plug housing gauge, 17 × 11.5 × 6.6 mm |

Use the actual clone and cable for the decisive trial. Ream undersized printed
holes rather than scaling the coupon. Position the clone underneath the carrier,
USB rearward and components toward the floor, at a 1 mm mounting gap. Compare
all edge pads and the three auxiliary pads before soldering any real PCB.
The plate relief assumes pin tails no more than 1 mm above the carrier.

Register the PCB against the rear/right ledges, then place the plate and cover.
The four coupons are partial mating geometry intended to be held together for a
fit check; they are not a standalone closed case. Confirm the USB plug seats
fully in both orientations and cannot lever the module against the floor or
PCB. Check the port opening and PCB stack with the cover installed. The module
is ultimately held by its short soldered pin connections; the gap gauge is
removed. Connector load and module attachment strength remain physical-test items.

## Full keyboard models

`case.stl`, `cover.stl`, `plate-supported.stl`, and `pcb-bare.stl` represent the
complete assembly. Each has matching `-left` / `-right` fit-print versions for
a 256 mm bed. Splits are plain diagnostic seams; they do not constitute a
validated permanent joining system. `plate-flat-1.5mm.stl` omits the printed feet.
`plate-diagnostic.dxf` is a review drawing, not a released machining drawing.
`pcb-populated.stl` includes component and pin envelopes and may require support.
Use the bare PCB STLs above to insert real components; populated models include
printed pin geometry and are not insertion-test fixtures.
`fit-assembly.step` is the assembled reference. `fit.scad` is an exploded viewer.

The outside case is 355.56 × 133.352 mm, 7.3 mm at the front and 20.6 mm at the
rear including the cover. The PCB remains 1.6 mm and the plate 1.5 mm. Battery
reserve and print gauges remain provisional: 270 × 52 × 6.3 mm reserve for a
pack envelope no larger than 264 × 50 × 5.5 mm, with no pack selected.

## Measurements still needed

Measured: clone PCB 33 × 18 mm; USB socket projects 0.84 mm past its end.
Assumed: total module body height 5 mm, socket axis 3.5 mm below the carrier,
1 mm carrier/module gap, and nominal registration of the auxiliary pads.
The 19 mm model width includes 1 mm overall allowance. The socket face is about
1.22 mm recessed behind the rear exterior at the assumed axis. An integral
recessed bezel closes the wall around it: the rounded through-slot is
10.1 × 3.8 mm, with 0.3 mm nominal clearance per side around the assumed
9.5 × 3.2 mm socket. The larger flared pocket is a blind exterior recess for
the cable housing, with a 12.5 × 7.6 mm throat; it is not a large through-hole.
The model clears an 11.5 × 6.6 mm housing along its insertion path.

The bezel is included in `case.stl`, `case-right.stl` and `fit-coupon-case.stl`;
there is no separate insert to attach. See the [exterior preview](usb-surround.png)
(module omitted to show the aperture). Print the corner coupon first. The
0.6 mm bezel web fits between the measured module PCB end and socket face,
leaving only 0.14 mm modeled clearance to the module body. Socket width, height
and vertical position remain assumed, so inspect the slicer's thin-wall paths
and test the actual clone and cable before printing the full case. The bezel
must not press against the module or prevent full USB insertion. The PCB
position, outside case dimensions, plate and cover stack are preserved.

The copper antenna exclusion is rotated from v7.5, with no copper pads/tracks/
vias allowed inside. This does not certify BLE performance near the remaining
switches or a battery. Use the nonconductive prototype plate. Switch, stabilizer
and keycap envelopes retain the earlier unverified travel assumptions.
