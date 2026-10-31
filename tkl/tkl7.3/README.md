# TKL v7.3 — six-layer OSP cost prototype

This is a separate revision derived from the fully routed **v7.2** in
[`../tkl7`](../tkl7/README.md). The existing v7.2 and
[v8.2](../tkl8/README.md) directories are unchanged. Their file hashes are
recorded in [the preservation manifest](reference/preserved-revisions-sha256.json).

Changes in this revision:

- Six layers using **JLC06161H-7628**, nominal **1.6 mm** (JLC states
  1.5544 mm actual, ±10%). Two GND planes
  are added inside the original stack; old In2 signal copper moves to In4.
- **OSP finish and lead-free assembly solder**, replacing ENIG. Filled/capped
  vias remain required. JLC's six-layer process includes these vias without
  the four-layer surcharge.
- U1 uses **NRF52840-QIAA-R / C190794** instead of the R7 reel listing. The
  same QIAA package, pinout and configuration-7 circuitry are retained.
- J2 uses **temporary soldered 1.8 V SWD wires**. Bare OSP programming pads
  are not approved as recurring pogo contacts. Remove the wires before closing
  the case. Plan prompt switch soldering and keep unused boards sealed/dry.

The footprint, all component positions/holes, 86 switches, six reverse LEDs,
charging circuit and wireless features are retained. The case remains
355.56 × 133.35 mm, with 7.3 mm front / 20.6 mm rear assembled lip heights.
The old signal tracks and vias are preserved; RF keepouts cover all four
internal layers. [Stackup details](manufacturing/STACKUP.md).

The exact stack requires Standard assembly and adds a stackup fee. Its current
five-board fabrication estimate is **$97.58**, only $6.23 below the four-layer
ENIG comparison. A four-layer OSP design is estimated lower at $81.61; this
six-layer experiment is not the lowest-cost option. These figures exclude
assembly, shipping and production-file confirmation. [Cost details](manufacturing/COST_REDUCTION.md).

## Files

- [KiCad project](kicad/keyboard.kicad_pro) and [routed PCB](kicad/keyboard.kicad_pcb).
- [Gerber/drill ZIP](manufacturing/tkl-v7.3-gerbers.zip).
- [JLC BOM](manufacturing/jlcpcb-bom.csv) and [CPL](manufacturing/jlcpcb-cpl.csv).
- [Complete manufacturing handoff](manufacturing/tkl-v7.3-jlcpcb-handoff.zip).
- [Fabrication instructions](manufacturing/FABRICATION.md),
  [ordering guide](manufacturing/ORDERING.md), and [cost study](manufacturing/COST_REDUCTION.md).
- [Schematic PDF](manufacturing/schematic.pdf), [top assembly](manufacturing/assembly-top.pdf)
  and [bottom assembly](manufacturing/assembly-bottom.pdf).
- [Electrical validation](validation/summary.json) and [revision/fit audit](validation/revision-audit.json).
- [Case, plate and PCB fit models](case/README.md), including
  [the complete printable fit archive](case/tkl-v7.3-fit-test.zip).
- [Power and firmware bring-up](BRINGUP.md).

The fit models are reused only after an independent equality check of the
source-derived mechanical geometry. Internal copper changes do not change
these envelope models. Existing v7.2 prints remain useful.

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
/usr/bin/python3 tkl/tkl7.3/scripts/export_manufacturing.py
```

The exporter refills and saves zones, runs ERC/DRC and schematic parity,
checks revision isolation/copper/fit, and requires zero errors and warnings.
See [scripts/README.md](scripts/README.md) before rebuilding anything.
