# TKL v8.2 fabrication and assembly instructions

**MECHANICAL HOLD:** the user confirmed that both the Durock V3 and TX AP
stabilizers are plate mount. Their mounting features, clip fit and clearance/
travel with Choc V2 and the actual keycaps remain unverified. The current PCB
has no stabilizer attachment or housing relief cutouts. Quote only; resolve
physical fit and the battery dimensions before production.

Experimental prototype, 2026-09-25. Use these notes with `tkl-v8.2-gerbers.zip`,
`jlcpcb-bom.csv`, `jlcpcb-cpl.csv` and the two assembly PDFs. This package has
passed digital design checks; factory preview and physical tests are pending.

## PCB construction

| Setting | Requirement |
| --- | --- |
| Outline | 350.76 × 129.19 mm; route actual Edge.Cuts contour |
| Layers | 4: F.Cu / In1.Cu / In2.Cu / B.Cu |
| Thickness | Nominal 1.6 mm FR-4 |
| Finish | ENIG |
| Copper | Nominal 1 oz outer / 0.5 oz inner |
| Smallest routed width/clearance | 0.127 mm / 0.127 mm |
| Copper to edge | 0.5 mm perimeter; 0.2 mm at internal NPTH |
| Smallest through via | 0.45 mm diameter / 0.30 mm finished drill |
| Via treatment | Resin filled, planarized and copper capped for all via-in-pad locations; quote all vias filled/capped if selective treatment is unavailable |
| Holes | Separate PTH and NPTH Excellon; no reverse-LED slots in v8 |
| Assembly | 134 bottom SMT + 6 top SMT + 2 bottom-inserted THT connectors |
| Fiducials | FID1–FID3 bottom; FID4–FID6 top; 1 mm copper, no fitted parts |

Revision 8.2 enlarges the 0.20 mm via holes to **0.30 mm** while retaining
0.45 mm copper lands. The 0.075 mm nominal annular ring meets JLC's published
preferred POFV ring. Larger original 0.3048/0.6096 mm vias are retained.
Select the **0.3 mm/(0.4/0.45 mm)** option, FR4 TG135 and ordinary flying-probe
continuity testing; no optional four-wire Kelvin test. Retain epoxy fill/cap,
ENIG, and the specified stack. Local switch-hole routing and ground pours now
have at least 0.20 mm hole clearance. Trace clearance remains 0.127 mm.
See [COST_REDUCTION.md](COST_REDUCTION.md) for the rule source and pricing.

The nominal stack is 0.035 mm F.Cu / 0.2104 mm prepreg / 0.0152 mm In1.Cu /
1.065 mm core / 0.0152 mm In2.Cu / 0.2104 mm prepreg / 0.035 mm B.Cu, with
approximately 0.01 mm solder mask per side. This follows a nominal JLC 7628
1.6 mm construction. Confirm the actual production stack before release.
In1 is GND, with the Nordic RF copper exclusions retained.

The USB pair is nominally 0.25 mm wide with 0.15 mm gap over In1 ground, with
local connector/MCU breakouts. Request review for a **90 ohm differential**
target. An impedance field solver and physical USB signal-integrity test have
not been run. The radio follows Nordic's reference geometry; its RF impedance
and matching also require verification on the selected stack and antenna.

Filled and capped vias are necessary beneath the nRF package and charger
thermal land. Tenting or ordinary mask plugging does not prevent solder loss
into these holes. Preserve the drawn RF keepouts and all mechanical holes.
Do not change trace geometry or substitute a two-layer stack.

All Gerber, drill and placement coordinates use the same origin: the lower
left of the outline, KiCad X=27.03 mm, Y=149.19 mm. Placement coordinates are
millimetres, X right and Y up as viewed from the top. Bottom coordinates are
**not X-mirrored**. The bottom assembly PDF is mirrored for direct underside
inspection. `positions-kicad.csv` is the unmodified native export;
`pad-coordinates.csv` records pad locations/nets for polarity review.

## Assembly details

Use JLC's service capable of this board size, the required via treatment,
both-side SMT and underside THT. All ordered components have exact MPNs and LCSC/JLC
identifiers in the BOM. Availability, handling charges and sourcing eligibility
must be checked in the quote; no inventory was reserved.

- **U1:** Nordic NRF52840-QIAA-R7 aQFN, not a QFN48 substitute. Use the exact
  pad map and orientation in the drawing. X-ray the package and thermal pads.
- **U2:** BQ24072RGTR, 3 × 3 mm VQFN, with its exposed ground pad soldered.
  The four thermal vias in that land must be filled and capped.
- **D1–D86:** JSCJ BAT46W / C54110 SOD-123. Pad 1 is cathode, connected to ROW.
  Do not substitute a 1N4148-class silicon diode without rechecking 1.8 V
  input-low voltage margin.
- **LED1–LED6:** LTW-C191TS5 (C125123) top-emitting 0603 LEDs. Install on
  TOP, emitting upward between switches. Pad 1 is cathode on BL. The six
  reverse-mount LED holes from v7 have been removed; use the v8 CPL.
- **J1 and J5:** genuine JST B2B-PH-K-S(LF)(SN), inserted from the bottom.
  J1 pin 1 is VBAT positive; J1 pin 2 is GND. J5 is the external NTC connector:
  pin 1 TS and pin 2 GND. Check mating cable polarity; JST housing style alone
  does not specify battery lead polarity.
- **J3 and SW87:** body on bottom, connector mouth/actuator toward the rear
  edge. Solder the USB mechanical tabs as well as electrical pads.
- **C10, C13 and R10:** DNP. Do not populate R10 as a substitute for the
  battery temperature sensor in an assembled keyboard.
- **C14, C15 and C22:** Walsin 0603B105K160CT / C108463, 1 uF +/-10%,
  X7R, 16 V, 0603. This incorporates the stocked replacement selected in
  the JLC quote for the unavailable AVX C597252.
- **J2 and FID1–FID6:** bare programming/optical features, no fitted parts.
- **SW1–SW86:** top-side Kailh Choc V2 soldered switches. They are excluded
  from the JLC BOM/CPL because the switch variant is not selected. They may be
  installed later or explicitly consigned and added to the assembly order.

The CPL uses KiCad rotations. Supplier component-library rotations can differ,
especially for the imported Nordic footprint and bottom parts. **Check the
JLC placement preview against pin 1/polarity in the assembly PDFs and pad CSV**;
this preview has not been performed. Do not infer orientation from MPN text.

RF passives, crystals and DC/DC inductors require the listed electrical
specifications. A generic 10 uH part with a few-mA rating is unsuitable for
L2/L4; the selected parts are rated 100 mA. Crystal load capacitance and RF
capacitor tolerance must be preserved. `parts.json` records these constraints.

## Electrical operating conditions

Battery: protected 1S Li-ion/LiPo, 3.7 V nominal, 4.2 V maximum. The target
capacity is 10 Ah. No battery, antenna, thermistor lead, key switches, keycaps,
case or programming cable is included in the PCBA BOM. Attach a Semitec
103AT-2 or electrically compatible 10 kohm NTC to the cell and connect J5.

The BQ24072 charge setting is approximately 445 mA (R11=2 kohm), with a fixed
500 mA USB input limit. TMR is grounded to disable the charge timers for a
large pack. TD is grounded to retain charge termination. TS monitoring remains
active. The battery pack must provide its own protection circuit. Verify the
exact pack's permitted charge current, temperature limits and NTC curve.

USB power is assumed to come from a known 5 V source permitting at least
500 mA. There is no USB enumeration/suspend current negotiation or BC/PD
charger detection. Consequently this revision is **not a claim of strict
USB 2.0 bus-current compliance**. Additional charger control would be needed
for that requirement. USB data, radio performance and charge temperatures
must be measured on the prototype.

## Supplier references

- [JLCPCB stackups](https://jlcpcb.com/impedance)
- [JLCPCB via treatment](https://jlcpcb.com/help/article/pcb-via-covering)
- [Nordic reference layout](https://nsscprodmedia.blob.core.windows.net/prod/software-and-other-downloads/reference-layouts/nrf52840/nrf52840-qiaa-reference-layout-1_3.zip)
- [TI BQ24072 datasheet](https://www.ti.com/lit/ds/symlink/bq24072.pdf)
- [BAT46W diode specification](https://www.diodes.com/datasheet/download/BAT46W.pdf)
- [Lite-On LED manufacturer drawing](https://optoelectronics.liteon.com/upload/download/DS22-2004-201/LTW-C191TS5.PDF)
- [JLC LTW-C191TS5 assembly listing](https://jlcpcb.com/partdetail/LiteOn-LTWC191TS5/C125123)
