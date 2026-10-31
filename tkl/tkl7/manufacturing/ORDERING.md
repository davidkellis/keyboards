# Ordering TKL v7.2 from JLCPCB

**You can obtain a quote now. Hold production until the stabilizer and case fit
and battery temperature compatibility are resolved.** The user confirmed that both the Durock V3 and TX AP sets are
**plate mount**. Both need verified mounting features and a clearance/travel
test with the Choc V2 switches and actual keycaps. This PCB has
no stabilizer housing relief cutouts. Final keycap/stabilizer travel and battery approval
remain unverified. The printable samples are in [../case](../case/README.md).

## Three files to upload

| JLCPCB upload | File |
| --- | --- |
| PCB fabrication | `tkl-v7.2-gerbers.zip` |
| Assembly bill of materials | `jlcpcb-bom.csv` |
| Component placement / CPL | `jlcpcb-cpl.csv` |

The outer `tkl-v7.2-jlcpcb-handoff.zip` is a convenient package to share with
an assembly engineer. Extract it first: upload the **inner Gerber ZIP** to
the PCB quotation form, and the two CSV files at the assembly stage.
Do not mix files from different revisions.

## Website steps

1. Open [JLCPCB's PCB/PCBA quotation](https://cart.jlcpcb.com/quote) and upload
   the Gerber ZIP. Check that the preview shows **350.76 × 129.19 mm, four layers**.
2. Choose **FR-4, 1.6 mm, ENIG** and your prototype quantity. The design uses
   via-in-pad beneath fine-pitch parts: request **resin filling, planarization
   and copper capping** as detailed in `FABRICATION.md`. Ordinary tenting or
   mask plugging is insufficient. Confirm the quoted stackup and the USB/RF
   geometry with their engineering review before approving fabrication.
   Select **0.3 mm/(0.4/0.45 mm)** minimum-via option, **FR4 TG135**,
   **Flying Probe Fully Test**, and **4-Wire Kelvin Test: No**. Retain
   epoxy-filled/capped vias, ENIG and JLC04161H-7628 stackup. Keep manual
   production-file and placement confirmation enabled. See
   [COST_REDUCTION.md](COST_REDUCTION.md) for exact settings and limitations.
3. Enable PCB Assembly. Select **Standard PCBA / Bottom Side**. The live
   2026-09-25 quote marks U1 (NRF52840-QIAA-R7 / C1851953) **Standard Only**;
   Economic PCBA would omit the controller. Board size and mixed SMT/THT alone
   do not require Standard. Request insertion of
   J1 and J5 from the bottom; confirm this in the quote if the form does not
   expose a separate THT choice. Supply `FABRICATION.md` with the order notes.
4. Upload `jlcpcb-bom.csv` and `jlcpcb-cpl.csv`. There should be **31 BOM lines
   and 142 fitted placements per board**: 140 bottom SMT components and two bottom-inserted THT connectors.
5. Review every matched MPN and LCSC number. The BOM specifies the diodes;
   you do not need to buy those separately. Do not accept automatic changes
   to crystals, RF parts, the charger, diodes or inductors without checking
   the specification in `parts.json`.
   D1–D86 now specify **JSCJ BAT46W / C54110**. C14/C15/C22 specify **C108463**.
6. Review the component placement preview against `assembly-top.pdf`,
   `assembly-bottom.pdf` and `pad-coordinates.csv`. Check LED/diode polarity,
   U1/U2 pin 1, bottom-side orientation and the USB/switch facing the rear.
   KiCad rotations and JLC's library rotations may differ. The preliminary
   supplier preview was checked for side and gross alignment on 2026-09-25.
   Final pin/polarity confirmation remains pending; no stock is reserved.
7. Resolve supplier questions and the physical fit test before paying or
   releasing production. Start with prototypes; firmware, charging, USB,
   radio and lighting still need bench validation.

## What JLC assembles, and what you provide

The BOM covers the controller, charging/power electronics, matrix diodes,
LEDs, USB socket, power switch, antenna socket and battery/NTC PCB connectors.
It excludes your **86 key switches**, keycaps, stabilizers, case, battery,
battery leads, external 10 kohm NTC, external 2.4 GHz antenna and SWD programmer.
Solder your Choc V2 switches after the plate/fit arrangement is settled. If you
want JLC to install the switches too, arrange customer-supplied-part consignment
and have them add the exact variant to their assembly order.

JLC assembles a PCB; it does not automatically install your case and keycaps
or produce a working flashed keyboard. A custom ZMK board configuration and
firmware flashing are still required. See `../BRINGUP.md`.

The battery is a **protected 1S 3.7 V nominal / 4.2 V maximum Li-ion/LiPo pack**,
not a USB power bank. Nominal charging is about 445 mA. A 10 Ah pack's physical
size is not implied by its capacity. The thin 7.3 / 20.6 mm case reserves
**270 × 52 × 6.3 mm** across its rear for a finished body up to
**264 × 50 × 5.5 mm**, with 0.5 mm padding below. No retail pack is selected;
capacity remains unconfirmed. See [battery details](../case/BATTERY.md) for sourcing and fit limits.
The selected pack's allowed charging
range must be matched to the existing nominal 0–50 °C NTC window or the
circuit revised. Battery/temperature protection approval remains a production hold.

## Supplier instructions checked 2026-09-24

- [How to place a PCBA order](https://jlcpcb.com/help/article/how-do-i-place-a-pcba-order)
- [Assembly capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities)
- [Pick-and-place requirements](https://jlcpcb.com/help/article/pick-place-file-for-pcb-assembly)
- [Via covering options](https://jlcpcb.com/help/article/pcb-via-covering)
