# TKL v7.4 — four-layer OSP, lead-free assembly

This is a separate revision derived from the fully routed **v7.2** in
[`../tkl7`](../tkl7/README.md). Existing v7.2, [v8.2](../tkl8/README.md) and
[the six-layer v7.3 experiment](../tkl7.3/README.md) are unchanged; their file
hashes are recorded in [the preservation manifest](reference/preserved-revisions-sha256.json).

- **Four layers, JLC04161H-7628, nominal 1.6 mm**: v7.2's exact copper routing,
  layer assignments, dielectric construction and RF keepouts are retained.
- **OSP finish and lead-free assembly solder** replace ENIG. Filled/capped
  vias remain required beneath the fine-pitch devices.
- **NRF52840-QIAA-R / C190794** retains v7.3's cheaper ordering code for the
  same controller/package, with no controller feature or pinout changes.
- **Temporary soldered 1.8 V SWD wires** replace the bare-pad pogo workflow
  for OSP. Remove the wires before closing the case; use lead-free solder.

All component positions/holes, 86 switches, six reverse LEDs, charging, USB and
wireless features are retained. The case remains 355.56 × 133.35 mm, with
7.3 mm front / 20.6 mm rear assembled lip heights. [Stackup details](manufacturing/STACKUP.md).

The live JLC estimate for **five assembled boards is $300.22 delivered**,
including displayed DHL DDP shipping and rail removal, before tax and any
engineering/fixture charges after review. It is saved in the cart, unpaid.
This is $22.95 below v7.2. Economic assembly is disabled for the configured
PCB specifications. [Full quote and evidence](manufacturing/JLC_QUOTE_v7.4_2026-09-25.md).
The fabrication-only comparison remains $81.61 before $1.05 file confirmation.
[Cost details](manufacturing/COST_REDUCTION.md).

## Files

- [KiCad project](kicad/keyboard.kicad_pro) and [routed PCB](kicad/keyboard.kicad_pcb).
- [Gerber/drill ZIP](manufacturing/tkl-v7.4-gerbers.zip).
- [JLC BOM](manufacturing/jlcpcb-bom.csv) and [CPL](manufacturing/jlcpcb-cpl.csv).
- [Complete manufacturing handoff](manufacturing/tkl-v7.4-jlcpcb-handoff.zip).
- [Fabrication instructions](manufacturing/FABRICATION.md),
  [ordering guide](manufacturing/ORDERING.md), and [cost study](manufacturing/COST_REDUCTION.md).
- [Schematic PDF](manufacturing/schematic.pdf), [top assembly](manufacturing/assembly-top.pdf)
  and [bottom assembly](manufacturing/assembly-bottom.pdf).
- [Electrical validation](validation/summary.json) and [revision/fit audit](validation/revision-audit.json).
- [Case, plate and PCB fit models](case/README.md), including
  [the complete printable fit archive](case/tkl-v7.4-fit-test.zip).
- [Power and firmware bring-up](BRINGUP.md).

The fit models are reused only after an independent equality check of the
source-derived mechanical geometry. The finish and procurement changes do not
change these envelope models. Existing v7.2 prints remain useful.

## Prototype limitations

Digital checks do not establish that the keyboard has been physically tested.
Plate-mount stabilizer/keycap travel, battery dimensions/temperature limits,
firmware, RF, USB and charging still require prototype validation. There are
no stabilizer housing relief cutouts in the PCB. Start with the small
[fit coupons](case/stabilizer-test/README.md).

The provisional finished battery limit is **264 × 50 × 5.5 mm**; no capacity
or retail pack is approved. Charging is approximately 445 mA with a fixed
500 mA USB input assumption, as described in [BRINGUP.md](BRINGUP.md).

The assembly BOM contains 142 placements in 31 groups: 140 bottom SMT parts
and two bottom-inserted THT connectors. It excludes the key switches, battery,
NTC lead, antenna, case and keycaps. No firmware image or completed physical
keyboard is included. Manufacturing files are for prototype quotation and
engineering review; the existing physical-fit holds remain.

## Reproduce and export

Use KiCad 10's system Python plus `sexpdata`. Normal re-export:

```sh
/usr/bin/python3 tkl/tkl7.4/scripts/export_manufacturing.py
```

The exporter refills and saves zones, runs ERC/DRC and schematic parity,
checks revision isolation/copper/fit, and requires zero errors and warnings.
See [scripts/README.md](scripts/README.md) before rebuilding anything.
