# v8.2 cost reduction

Updated 2026-09-25. This revision retains all current features and fit envelopes.
The prior v8.1 exports are preserved in `archive/` and commit `12a14e4`.
Original quotes remain in `JLC_QUOTE_2026-09-25.md`; they are historical prices.
No purchase or production release has been made.

## Changes common to both boards

- Enlarge each 0.20 mm via drill to 0.30 mm, keeping its 0.45 mm copper land.
  This gives a 0.075 mm annular ring, JLC's published preferred POFV value;
  the 0.30/0.45 mm combination is explicitly listed. Older 0.3048/0.6096 mm
  vias remain unchanged. This intentionally updates the annular-ring rule
  from 0.10 to 0.075 mm for this factory process. Trace/space stays 0.127 mm.
- Retain resin filling, planarization and copper capping. The controller
  and charger still have via-in-pad; mask plugging is not an alternative.
- Increase hole-to-copper and hole-to-hole rules to 0.20 mm. Local traces
  near switch center holes are moved outward and ground pours are refilled.
  No outline, component position, component drill or RF signal track changes.
- Replace all 86 Diodes Inc BAT46W-7-F / C83152 with **JSCJ BAT46W / C54110**.
  The manufacturer datasheet specifies the same 0.25 V maximum forward drop
  at 0.1 mA and 0.5 uA maximum leakage at 10 V (25 C); pad 1 remains cathode.
  Maximum package height is 1.25 mm, within the existing 1.35 mm fit envelope.
  This is an exact reviewed manufacturer choice, not permission to substitute
  arbitrary BAT46-labelled or silicon switching diodes. Physical matrix
  operation and temperature margins still need prototype testing.
- Preserve all 142 fitted placements and 31 BOM groups. No component is
  omitted to make the price appear lower.

## Quote settings

4 layers; 350.76 x 129.19 mm; 1.6 mm; FR4 TG135; green mask / white legend;
ENIG 1 microinch; 1 oz outer / 0.5 oz inner; JLC04161H-7628 stack;
epoxy filled and capped; horizontal electroless copper plating;
**minimum via 0.3 mm/(0.4/0.45 mm)**; regular outline tolerance;
ordinary flying-probe electrical test; **4-wire Kelvin: No**.
Select Standard PCBA, Both Sides, five assembled boards, JLC-added rails,
rail removal, standard lead time, self-service parts matching, and manual
production-file/placement confirmation. Keep automatic approval disabled.
The second assembly side retains extra setup, stencil and fixture costs.

Live JLC quote: **$372.59 for five assembled boards**, including estimated
DHL DDP shipping and rail removal, before tax and engineering adjustments.
This saves **$75.95** versus v8.1. See the
[complete comparison](JLC_QUOTE_v8.2_2026-09-25.md) and its saved evidence.

## What still sets the price floor

U1 remains Standard Only in JLC's library. Basic parts do not eliminate the
Standard service's per-line feeder fees. A module or different controller
would require a new circuit/layout, power-supply and mechanical review;
the EBYTE E73 variant examined was also Standard Only. Merely selecting
Economic PCBA leaves U1 out. The top LEDs in v8 require the second assembly
pass. Moving them to the bottom recreates v7's lighting configuration.
The USB special-part fee is only $0.15 for five and is not a useful redesign target.
ENIG is retained for the exposed SWD pogo contacts and the switches to be
soldered later; an OSP discount is not included in these comparable quotes.

All existing mechanical-fit, battery-temperature, firmware, USB/RF and bench
validation holds remain. A zero-violation digital check is not a tested keyboard.

Sources checked 2026-09-25:
- [JLC POFV geometry](https://jlcpcb.com/news/free-via-in-pad-6-20-layer-pcbs-pofv)
- [JLC manufacturing capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)
- [JSCJ BAT46W / C54110 listing and manufacturer datasheet](https://jlcpcb.com/partdetail/55127-BAT46W/C54110)
- [JSCJ datasheet mirror](https://datasheet.lcsc.com/datasheet/pdf/f97c8b3ccdb24c5ba21cb2c31ad9c922.pdf)
