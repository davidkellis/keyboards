# V10 Edition 2 — raised key wells

This is a separate mechanical prototype for the existing V10 PCB, battery,
controller and concealed underside mounting system. The original
`case-hidden-mounts/` is Edition 1 and remains intact.

Open the [case comparison studio](../render-case-editions/index.html) and
switch **Case edition** between Edition 1 and Edition 2. The keycap and
lighting controls work with both. Use **Key travel preview** to lower the
keys through their full 2.8 mm travel while the case stays fixed.

## What changed

The outer deck and borders between key groups rise **3.25 mm**, ending
**0.15 mm below the nominal underside of the XVX Skyline R2 keycap skirts**
at rest. From the outside, the case now conceals the blue switch bases,
clear housings and exposed stem gap. The wide typing well remains open
between keys, so this is not a sealed surface beneath every keycap.

There are eight broad wells: the main typing block, navigation block,
T-shaped arrows, Esc, three function clusters and the three rear-right
keys. No thin ornamental separators have been added between typing rows.
The outer top rolls down through a nominal 2.5 mm radius, with 3 mm plan
corners and a gentle chamfer around the key wells. There is no raised
decorative rim above the deck and no new perimeter assembly seam on top.

| Dimension | Edition 1 | Edition 2 |
| --- | --- | --- |
| Footprint | 355.56 × 133.352 mm | Same |
| Nominal top plane, front / rear | 5.692 / 18.992 mm | 8.958 / 22.258 mm |
| Switch seating plate | Existing 1.5 mm plate | Same plate, same height |
| PCB, switch and keycap positions | Existing V10 | Unchanged |
| Overall assembled height at the key tops | Existing V10 | Unchanged |
| Battery reserve | 155 × 50 × 6.3 mm | Unchanged |

The raised deck is cosmetic structure above the original switch seating
plate. Switches clip into the small lower apertures, not the large upper
key wells. Moving the switch seating plane upward would change the PCB
stack and is not part of this design.

## Fit assumptions and checks

The height target is the existing approximate 5 mm XVX profile with 3 mm
socket engagement. Its underside has not been measured. One fixed case
cannot be flush with every keycap profile: ScottoCaps have different skirt
heights and will stand farther above this deck. All profiles remain in the
viewer so that difference is visible rather than silently changing the case.

Key-well boundaries provide **0.6 mm nominal lateral skirt clearance** for
the XVX footprint. The model checks a conservative solid envelope around
each of the 86 caps through the full 2.8 mm motion, including socket
engagement from 1.5 to 3.1 mm. At maximum modeled engagement, the cap clears
the original lower plate by 0.5 mm at full travel. No raised-case
intersection was found in those nominal envelopes.

Added material was also checked against the PCB, battery reserve, bottom,
USB insert and all eight sets of mounting hardware. These are geometry
checks, not confirmation of physical switch clips, keycap seating, FDM
tolerances, rattle or stiffness. Print the front coupon before a full upper.
The original PCB, Gerbers, BOM, CPL and JLC order are unchanged.

## Print a small trial first

Use **[prints/front-fit-coupon.stl](prints/front-fit-coupon.stl)**. It contains
the actual raised front-left corner, lower switch plate and portions of
the first two key rows. Fit actual Whale switches and XVX caps, check that
the skirts align with the deck, then press and release the keys fully.
Adjustments should follow that physical result before printing a full case.

The printing STLs are in millimetres, rotated with the raised top facing
the bed, with minimum Z at zero. **Support is needed inside the recessed
key wells beneath the lower switch plate**: the raised top is 3.25 mm below
that plate in the inverted printing orientation. Preview the supports in
the slicer and test removal on the coupon. Do not bridge the entire main
well unsupported. The small vertical shadow gap makes this coupon useful
for checking the printer's actual tolerance.

For the rear USB fit trial, print `usb-fit-coupon-upper.stl` with the copied
`usb-coupon-bottom.stl`, `usb-coupon-pcb.stl` and `usb-bezel.stl`. The gauge
belongs to the existing V10 fit trial, with enlarged plastic pin holes.
Use the actual controller and cable to check the opening.

## Full prototype files

For a 256 mm bed, print `plate-upper-left.stl` and
`plate-upper-right.stl`. Their maximum XY bounds are approximately
186.83 × 134.66 mm. The original staggered bonded seam and 4 mm lower-plate
half-lap are retained, with a 0.2 mm adhesive gap. The new raised webs share
that seam. Bond and finish the halves before installing switches; a split
print still needs finishing to hide its center seam.

For a large printer, `plate-upper.stl` is the whole upper. Reuse the existing
bottom, USB insert and eight nut carriers; copies of their print STLs are
included under `prints/`. Hardware remains **8 × M2 × 4 mm button-head
screws and 8 × DIN 934 M2 nuts**. Assembly and servicing follow the
[original concealed-mount instructions](../case-hidden-mounts/README.md).

The optional `plate-upper-navigation*.stl` parts correspond to the displayed
light-bar concept. Its terminal light pipe must rise to the new deck; this
is an optical prototype, not a proven lighting solution. Other lighting
concepts remain appearance studies. Do not assume the six existing LEDs
will produce the illustrated brightness.

Files under `reference/` use common assembly coordinates and are diagnostic
meshes, not bed-normalized print parts. The source is a boolean mesh design;
this edition does not claim an editable native STEP assembly.

## Rebuild

Install `source/requirements.txt` in a Python virtual environment and run
`python source/build.py` from this directory. `design-config.json` holds
the height and radius assumptions. `validation.json` records the geometry
checks and source hashes. `print-validation.json` independently checks the
written STL meshes. The comparison studio has its own build and browser
verification scripts under `../render-case-editions/source/`.
