# TKL v9 — direct rear USB-C module

An isolated 83-key follow-up to v7.5. The three keys above Insert/Home/Page Up
(SW9, SW15, SW16) and their diodes are removed. All other switch positions and
switch drills, the 350.76 × 129.19 mm PCB outline and 1.6 mm thickness are retained.

The user-installed TENSTAR nRF52840 clone sits underneath the vacated area, with
its USB-C socket facing the rear case opening. No internal USB extension cable,
panel receptacle or cable cradle is used. The power switch moves left to clear
the module; the battery connector stays in its original position. A copper
exclusion on both layers follows the antenna end between the Home/Page Up area.

**Fit/electrical prototype, not production approved.** Actual module thickness,
auxiliary-pad registration, socket axis, plug insertion, RF, firmware, battery
charging and stabilizer/keycap travel need physical verification.

## Start with the corner fit sample

Download the [larger-hole fit kit](case/print-fit/tkl-v9-easy-fit.zip) and follow the
[print guide](case/README.md): four small coupons and the 1 mm gap gauge.
The PCB gauge enlarges switch and module holes by 0.4 mm diameter for plastic
printing, with unchanged pin centers; an 18 mm single-switch sample and full
PCB halves are also included. STEP references and fabrication drills remain
unchanged.
They let you try the real clone, a normal USB cable, PCB/plate stack and rear
opening without printing the full keyboard. The model uses measured 33 × 18 mm
clone PCB dimensions and 0.84 mm socket overhang, but assumes 5 mm total module
thickness and a socket axis 3.5 mm below the carrier at a 1 mm mounting gap.
The recessed USB bezel has a rounded 10.1 × 3.8 mm through-slot around the
socket. Its larger blind exterior recess permits an 11.5 × 6.6 mm external
plug housing with 0.5 mm clearance on each side, while closing the surrounding
view into the case. The integral 0.6 mm web and assumed socket dimensions need
the corner-coupon trial. These are fit targets, not a claim about every cable
or clone.

The full case retains the 355.56 × 133.352 mm footprint and 7.3 / 20.6 mm
front/rear heights including the cover. The plate and cover close the three
removed key positions. Plate slots clear the module's solder-pin ends. Use a
nonconductive plate for this prototype; metal near the antenna is not validated.

Electrical checks pass with zero ERC/DRC errors, warnings, unconnected nets or
schematic mismatches. Printable STL meshes pass, with no modeled fit collisions.
The 5 mm module envelope has 4.49 mm clearance above the case floor.

## Design and outputs

- [KiCad PCB](kicad/keyboard.kicad_pcb) and [schematic](kicad/keyboard.kicad_sch).
- [Fit assembly STEP](case/fit-assembly.step), [module view](case/module-fit.png),
  and [print guide](case/README.md).
- [Electrical checks](validation/summary.json), [revision audit](validation/revision-audit.json),
  [fit report](case/fit-report.json), and [mesh checks](case/mesh-validation.json).
- [Prototype quote package](manufacturing/tkl-v9-prototype-handoff.zip),
  [Gerbers](manufacturing/tkl-v9-gerbers.zip), [BOM](manufacturing/jlcpcb-bom.csv)
  and [CPL](manufacturing/jlcpcb-cpl.csv). Use matched v9 files only.

The original manufacturing package specifies two copper layers and OSP. The
current [JLC cart configuration](manufacturing/ORDERING.md) explicitly substitutes
lead-free HASL for lower-cost Economic bottom-only assembly, with lead-free solder
and no paid rail removal. The copper layout and upload files are unchanged.
JLC fits 99 placements in seven BOM groups (98 SMT plus one through-hole battery
connector); the user fits the clone and 83 switches. The savings relative to
v7.5 are three diodes and the eliminated extension cable/panel mount. See the
[saved quote](manufacturing/quote-v9-2026-09-26/README.md) for current cart details;
reverse-LED handling costs remain subject to review.

[Fresh pre-order checks and a bench-test plan](validation/preorder-2026-09-26/README.md)
record the passing electrical/export checks and what still requires the actual
clone, switches and firmware. No hardware test or firmware build is claimed.

The battery circuit is unchanged from v7.5: charging lives on the clone, the
300 mA power switch disconnects both battery operation and charging, and no
carrier NTC/power-path circuit is present. Read [bring-up](BRINGUP.md).
The existing battery reserve is preserved; no 10,000 mAh pack is approved.

## Rebuild

[Revision-local tools](scripts/README.md) document the generation and checks.
`build_board.py` deliberately resets v9 to an unrouted placement; normal export
uses the checked routed PCB. Prior revisions are protected by a 3,137-file hash
manifest. No v7.5 or earlier source is edited by these tools.
