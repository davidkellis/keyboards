# TKL v8.2 — top LEDs, larger vias

The v8.2 cost revision uses 0.30 mm via holes with 0.45 mm lands and
JSCJ BAT46W / C54110 matrix diodes. It retains wireless, charging, lighting,
the four-layer stack and all mechanical fit envelopes. Switch-hole copper
clearances are also increased to 0.20 mm. See the
[cost comparison and quote settings](manufacturing/COST_REDUCTION.md).


V8 retains v7's controller, power circuit, 86-key layout and four-layer PCB.
Six **LTW-C191TS5 / C125123** white LEDs now sit on top between the switch
bodies. The reverse-LED apertures are removed. The upper three emitters moved
to the gap between key rows. The existing six 1 kohm resistors and PWM control
remain; the LED type's brightness and forward voltage differ from v7.

The board is routed, with zero ERC/DRC violations, zero open connections and
zero schematic parity issues. See [validation](validation/summary.json).
There are 134 bottom SMT placements, six top SMT placements and two bottom
THT connectors. Both faces have assembly fiducials. This requires assembly on
both sides and may cost more than v7.

**Do not release fabrication yet.** Both the Durock V3 and TX AP sets are
confirmed as plate mount. They need verified mounting features and a physical
clearance/travel test with the Choc V2 switches and actual keycaps. See the
[parts record](../mechanical/OWNED_PARTS.md). Neither PCB has stabilizer
body relief cutouts. Electrical checks do not establish mechanical fit.
The diagnostic plate/case prototype preserves **7.3 mm front / 20.6 mm rear**
assembled lip heights and the **355.56 × 133.35 mm** footprint. Its wide rear
battery reserve is **270 × 52 × 6.3 mm**, with a provisional finished-pack
envelope of **264 × 50 × 5.5 mm**. No battery capacity or retail pack is
approved. See [battery details](case/BATTERY.md) for purchase candidates and
remaining mechanical/charging-temperature checks.

- [JLCPCB ordering guide](manufacturing/ORDERING.md)
- [Gerber/drill ZIP](manufacturing/tkl-v8.2-gerbers.zip), [BOM](manufacturing/jlcpcb-bom.csv),
  [placement file](manufacturing/jlcpcb-cpl.csv), [fabrication notes](manufacturing/FABRICATION.md)
- [PCB](kicad/keyboard.kicad_pcb), [schematic](kicad/keyboard.kicad_sch)
- [Print and fit guide](case/README.md), [assembly STEP](case/fit-assembly.step)
- [Battery, power and firmware bring-up](BRINGUP.md)

## What the lighting experiment can show

Top emitters avoid clipping by a hole through a 1.6 mm PCB. These LEDs are
nominally 0.55 mm high and have a 130° viewing angle; see
[Lite-On's data sheet](https://optoelectronics.liteon.com/upload/download/DS22-2004-201/LTW-C191TS5.PDF)
and [JLCPCB's part listing](https://jlcpcb.com/partdetail/LiteOn-LTWC191TS5/C125123).
Placing them between switch bodies gives light an open path into the gaps.
This is an engineering expectation, not a measured improvement in uniformity.
Six LEDs across 86 keys will still produce bright and dark areas.

The v8 plate and cover add small windows above the top emitters. Compare an opaque
cover with a translucent cover or removable diffuser using identical battery
voltage, PWM duty and exposure. Test with the actual switches/keycaps installed,
including the navigation cluster and spacebar. A translucent print is not an
optically characterized light guide. More LEDs or a designed diffuser may be
needed for uniform legend illumination.

V7 remains available for comparison. Do not mix its BOM, Gerbers or CPL with
v8. Firmware still needs a custom ZMK board definition; stock nice!nano firmware
does not match this board. The 500 mA USB input limitation documented in the
bring-up guide is unchanged.

## Regenerating deliverables

The finished routed PCB is the source of truth. Use the KiCad system Python
with `sexpdata` installed to run `scripts/validate.py` and
`scripts/export_manufacturing.py`. Mechanical instructions are in
[the shared generator guide](../mechanical/README.md).
