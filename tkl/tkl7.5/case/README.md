# v7.5 module and USB-extension fit prototype

The PCB preserves v7.4's footprint and switch layout. The outside case/cover
remains **355.56 × 133.352 mm; 7.3 mm front / 20.6 mm rear**, at 5.696° tilt.
The 1.5 mm diagnostic switch plate and cover remain part of the stack.

The module is between End and Up, with USB facing left, components toward the
floor and antenna to the right. It is 2.7 mm farther rearward than v6. This is
a fit design for the **following envelopes**. The PCB size and socket overhang
now use your measurements; component heights remain provisional. See the
[measurement record](MEASUREMENTS.md) for the seller drawings and missing dimensions.

| Item | Model limit |
| --- | --- |
| Module including connector | 33.84 × 19.0 × 4.0 mm; 33 × 18 mm PCB, 0.84 mm socket projection, width allowance |
| Module-to-carrier gap | 0.5 mm; no tall sockets |
| Plug housing beyond module end | 17 × 11.5 × 4.5 mm |
| Flexible cable diameter | 3.0 mm maximum within the modelled route |
| Rear receptacle envelope | 25 × 20 × 6 mm; includes full flange width, provisional height |
| Rear mounting holes | 17 mm centres; 3.2 mm clearance holes, actual insert thread unverified |

The USB centre is assumed 3.0 mm below the carrier underside: a 0.5 mm mounting
gap, approximately 1 mm clone PCB, and connector centre another 1.5 mm below it.
Measure this offset as well as housing height. A differently positioned socket
can invalidate the plug clearance even if overall module thickness is below 4 mm.
The male must be a **slim, data-capable USB-C extension**, not merely a charging lead.
The older 5.5 mm-tall plug envelope is not approved for this mounting geometry.
The male housing is now reported as **6.6 mm thick**, superseding the earlier
5.6 mm estimate. It **does not fit this mounting arrangement**: at the assumed
socket axis it intrudes 0.30 mm into the PCB, and would require a 0.053 mm floor
to maintain clearance. Theoretical height limit is about 5.10 mm at that axis,
before tolerances. The main fit model continues to use a **4.5 mm slim-plug target**;
the reported cable has a separate failed-fit assessment and a 6.6 mm print gauge.
A trial rearward shift requires 12.54 mm and conflicts with End-area switch pins.

The model gives about **0.67 mm module-to-floor clearance**. A local 0.103 mm
internal floor relief below the male plug leaves approximately 1.097 mm of floor
and **0.40 mm clearance**. The outside bottom stays flat. Existing front-diode
reliefs retain approximately 0.836 mm floors. The generated report is authoritative
for the model; print tolerance, insulation and actual connector dimensions still matter.

The cable runs left of the module, toward the rear outside the battery reserve,
then across to the rear receptacle. Its boxes are conservative routing envelopes,
not a flexible cable simulation. Check bend radius, strain relief and actual
plug insertion with the purchased cable. The rear receptacle now mounts against
the vertical rear wall on 17 mm screw centres, with a support beneath a full
25 mm flange-width reserve. Height and thread still need confirmation. The
listed 300 mm cable's surplus length is not included in the direct-route model.

## Printable / CAD files

- [Module/cable preview](module-fit.png): right end of the case with PCB, plate
  and cover removed. Orange is the module, yellow is the cable/connector envelope,
  and blue outlines mark End and Up. Open `module-fit.scad` for a movable view.
- `case.stl`, `cover.stl`, `plate-supported.stl`: full-size fit parts.
- `case-left.stl` / `case-right.stl`, `cover-left.stl` / `cover-right.stl`,
  `plate-supported-left.stl` / `plate-supported-right.stl`: 256 mm-bed fit trials.
- `pcb-bare.stl` or `pcb-left.stl` / `pcb-right.stl`: nominal real board drills;
  ream printed holes rather than scale the whole PCB.
- `pcb-populated.stl` and split versions: approximate factory component envelopes.
  The separately installed module and USB cable are shown in the assembly STEP.
- `u1-envelope.stl`, `usb_male-envelope.stl`, `usb_rear-envelope.stl`: separate
  dimensional gauges. Each is normalized to its own print bed; use STEP for positions.
- `usb_male-reported-6.6mm-gauge.stl`: the reported cable housing size, for
  comparison only; it does not fit the current mount. `usb_male-envelope.stl`
  remains the 4.5 mm target housing.
- `fit-assembly.step`: case, PCB, plate, module, USB/cable, keycap and battery envelopes
  in their assembled coordinates. `pcb-bare.step` is the bare carrier model.
- `fit-report.json` and `mesh-validation.json`: collision and print-mesh checks.

Print the separate module and plug gauges first, then place them with the bare PCB
and case right half. The supports/retention are prototype features. Use a thin
insulating mounting shim and soldered pins/wires. Trim module pins above the
carrier so they do not intrude into the plate's 0.7 mm underside gap.

The battery reserve remains 270 × 52 × 6.3 mm for a finished protected pack up to
264 × 50 × 5.5 mm; no retail battery or capacity is approved. Generic plate-mount
stabilizer cutouts and XVX keycap underside/travel remain unverified; the plate is
a diagnostic fit prototype. The intended case/plate materials are nonconductive;
metal near the module antenna needs separate RF review.
