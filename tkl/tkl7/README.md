# TKL v7.2 — integrated nRF52840 PCB

The v7.2 cost revision uses 0.30 mm via holes with 0.45 mm lands and
JSCJ BAT46W / C54110 matrix diodes. It retains wireless, charging, lighting,
the four-layer stack and all mechanical fit envelopes. Switch-hole copper
clearances are also increased to 0.20 mm. See the
[cost comparison and quote settings](manufacturing/COST_REDUCTION.md).


The 86-key PCB is fully routed. KiCad 10.0.6 reports **zero ERC violations,
zero DRC violations, zero open connections and zero schematic/PCB parity
issues**. The separate netlist/circuit audit checks 578 numbered pads and
86 unique matrix positions. See [validation/summary.json](validation/summary.json).

This is a **prototype fabrication package**. No physical board has been built
or tested. JLCPCB's component preview/engineering review, firmware bring-up,
RF/USB measurements and the final battery/case fit remain to be done.

## Files to use

- [KiCad project](kicad/keyboard.kicad_pro), [PCB](kicad/keyboard.kicad_pcb)
  and [three-sheet schematic](kicad/keyboard.kicad_sch).
- [Gerber/drill ZIP](manufacturing/tkl-v7.2-gerbers.zip),
  [JLCPCB BOM](manufacturing/jlcpcb-bom.csv) and
  [placement/CPL](manufacturing/jlcpcb-cpl.csv).
- [Fabrication and assembly instructions](manufacturing/FABRICATION.md).
- [Schematic PDF](manufacturing/schematic.pdf),
  [bottom assembly drawing](manufacturing/assembly-bottom.pdf),
  [top assembly drawing](manufacturing/assembly-top.pdf).
- [Part specifications and sourcing](manufacturing/parts.json),
  [assembly exceptions](manufacturing/assembly-notes.csv),
  [source checksums and verification](manufacturing/manifest.json).
- [Power, firmware and prototype bring-up](BRINGUP.md).
- Current copper previews: [top](front.svg), [underside](back.svg).

## What changed from the checkpoint

The previous two-layer layout had unfinished connections and incorrect
controller power/charger wiring. The new board retains the switch layout and
uses four layers to preserve Nordic's configuration-7 reference circuit.
The controller, crystals, decoupling and RF network were moved together onto
the underside. DEC3 is isolated, DEC4/DEC6 share their proper capacitor net,
and both DC/DC stages include their required components.

USB-C has two 5.1 kohm CC resistors, flow-through USBLC6 protection and a
manually routed data pair. The charging path uses a BQ24072, a real three-pin
load switch and separate battery/temperature-sensor connectors. All remaining
matrix, power and control connections are routed. The schematic now matches
the board, with exact assembly part numbers attached.

All 140 SMT components and the two battery/NTC connectors are on the underside.
The 86 soldered Kailh Choc V2 switches go on top. The JLC BOM excludes the key
switches; choose their feel and arrange consignment separately if JLC is also
to install them. No diodes need to be bought separately: the BOM includes
86 JSCJ BAT46W / C54110 Schottky diodes suitable for 1.8 V matrix inputs. Six LTW-C230DS
reverse-mount white LEDs shine through slots under the selected keys.

## Battery and ordering decisions

The battery connection expects a **protected single-cell Li-ion/LiPo pack,
3.7 V nominal, 4.2 V maximum**. A 10,000 mAh pack is electrically supported;
its dimensions still need to be matched to the case. This is a cell pack
connection, not a USB power-bank output. Connect a battery-mounted 10 kohm
NTC to J5. Charging is disabled without the NTC; R10 remains unpopulated.

Nominal charge current is approximately 445 mA. Budget roughly 25–30 hours
for a full 10 Ah charge, longer with thermal/input limiting. The charge timer
is disabled to allow this duration; voltage termination and temperature
monitoring remain enabled. The load switch allows charging while switched off.

The charger uses a fixed 500 mA USB input limit. It does **not** implement
USB enumeration/suspend current negotiation or charger detection. Use a known
5 V source that permits at least 500 mA; strict USB 2.0 bus-current compliance
would require additional charger control. USB data still needs prototype
verification. This limitation is explicit in the fabrication instructions.

JLCPCB must quote a 1.6 mm, four-layer ENIG board with **filled, planarized,
copper-capped vias in component pads**, underside SMT and two underside THT
connectors. Ordinary via tenting is insufficient. Review the supplier preview
against the assembly drawings before releasing production. Part identities
have been checked; live sourcing and placement rotations are not a completed
JLCPCB order.

The [case and printable PCB models](case/README.md) have now been rebuilt
from this routed board. Their component-envelope collision checks pass.
**Production remains on hold:** both the Durock V3 and TX AP sets are now
confirmed as plate mount. They need verified mounting features and a fit/travel
check with the Choc V2 switches and actual keycaps. See the
[parts record](../mechanical/OWNED_PARTS.md). No stabilizer body relief cutouts exist
in this PCB. Start with the [small fit sample](case/stabilizer-test/README.md).
The diagnostic plate/case prototype preserves **7.3 mm front / 20.6 mm rear**
assembled lip heights and the **355.56 × 133.35 mm** footprint. Its wide rear
battery reserve is **270 × 52 × 6.3 mm**, with a provisional finished-pack
envelope of **264 × 50 × 5.5 mm**. No battery capacity or retail pack is
approved. See [battery details](case/BATTERY.md) for purchase candidates and
remaining mechanical/charging-temperature checks.

Follow the [JLCPCB ordering guide](manufacturing/ORDERING.md) for the three
uploads, or use the [complete handoff archive](manufacturing/tkl-v7.2-jlcpcb-handoff.zip)
when sharing files with an assembly engineer. A separate
[v8 lighting experiment](../tkl8/README.md) places six emitters on top.
Legacy `keyboard-plate.*` and `tklplate.stl` outside `case/` are not cleared
manufacturing files. Stock nice!nano firmware is not suitable for this board.

## Rechecking or exporting

Use the system Python containing KiCad's `pcbnew` bindings and install
[scripts/requirements.txt](scripts/requirements.txt). Then run:

```sh
python tkl/tkl7/scripts/validate.py
python tkl/tkl7/scripts/export_manufacturing.py
```

The export script requires every validation count to be zero, checks that
the BOM covers exactly the fitted references, verifies CPL coordinates and
excludes DNP parts. See [tooling instructions](scripts/README.md) before
using any placement-generation scripts: rebuilding placement erases routing.

The original project state is preserved in commit `60e54d7`.
