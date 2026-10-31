# v10 third enclosure study: rear 18650 battery housings

This is a separate dimensional study of two cells with their long axes running
left–right along the rear. It does not change either existing case, the PCB,
manufacturing files or the JLCPCB order. It is not a printable enclosure release.

Open `comparison.png` or `comparison.svg` for the side-section and plan-view
comparison. `measurements.json` records the inputs, calculations and assumptions.

## What can become thinner

Removing the pouch can let the lower shell follow the inclined PCB more closely,
leaving air below the main body and placing the batteries in rear support pods.
That can make the main deck look slimmer. The cell diameter, however, increases
the required rear maximum: it does not reduce overall keyboard height.

The current rounded enclosure is 355.56 × 133.352 mm and has a measured maximum
height of 18.730 mm, excluding key switches/keycaps and external feet. Its
switch-plate plane extrapolates to 5.692 mm at the front and 18.992 mm at the rear,
at a 5.696° angle. The rounded outside edge lies below that plane.

| Arrangement | Rear height | Overall depth | Typing angle |
|---|---:|---:|---:|
| Current pouch enclosure | 18.7 mm measured shell maximum | 133.4 mm | 5.7° |
| Two pods under rear PCB, same footprint and front plate height | about 31.1 mm rear plate plane | 133.4 mm | about 10.8° |
| Two pods behind PCB, current plate position | 22.6 mm pod envelope | 156.8 mm | 5.7° |

The concept heights are envelope estimates, not measured finished rounded CAD.
Rubber pads, fasteners and any larger cell holder could increase them. The rear
extension option deliberately exceeds the previously retained footprint to show
the tradeoff; it is not an accepted replacement design.

## Envelope assumptions and checks

- Reference bare cell maximum: **18.6 mm diameter × 65.2 mm length**, from the
  [Molicel M35A manufacturer page](https://www.molicel.com/product/inr-18650-m35a/),
  consulted 2026-10-02. Protected/button-top cells and holders may be larger.
- Each provisional housing: **73.2 mm axial length × 22.6 mm outside diameter**.
  This allows 0.5 mm radially beyond the reference cell and a 1.5 mm plastic wall.
  The extra 8 mm of axial length is provisional space for insulation, tabs and
  end walls; no specific terminal or protection-board assembly has been fitted.
- Housing spans across the keyboard: x=75–148.2 mm and x=205–278.2 mm.
  These avoid the rear-left module/USB and rear-right connector/power switch in
  plan. Antenna performance is not validated by a geometric clearance check.
- The under-PCB calculation reserves a continuous 1.7 mm solder/pin envelope
  below the PCB and 0.4 mm to the outside of the housing. The script screens
  component envelopes in these spans and checks their depths against this bound.
  This is conservative compared with isolated pins, and requires a complete
  mounting/floor/port redesign before a real case can use it.
- At the current angle, the PCB underside at the proposed under-PCB pod centre
  is only about 14.0 mm above the desk; the proposed pod top is 22.6 mm high.
  The collision cannot be fixed merely by removing the pouch or thinning a wall.
- A nominal shallow region of the main deck could occupy about 7.1 mm normal
  to the PCB (plate/PCB stack + pins + clearance + 1.2 mm bottom). This excludes
  ribs, mounts and local pockets. The clone extends approximately 6 mm below
  the PCB in the existing envelope; the battery connector extends 8 mm below.
  Those still need deeper local housings.
- The current front diode pockets already leave about 0.836 mm of floor and
  0.4 mm component clearance. Removing the pouch therefore offers essentially
  no front-height reduction with the current PCB position and electronics.

## Mechanical direction

For an 18650 variant that preserves the current typing angle, use two enclosed,
rounded rear pods behind the PCB, a shallow main bottom with local electronics
pockets, and reinforced bridges carrying loads from the upper shell to the pods.
Keep the underside-access fastening concept and the uninterrupted upper surface.
The housing and ribs must support the keyboard independently of the cells;
the cells need insulated retention without bearing typing loads. Rubber contact
patches and a removable lower battery access cover need detailed design.

The illustrations omit ribs, fasteners, local connector pockets, pack wiring
and access-cover geometry. No stiffness, thermal, electrical, assembly-path or
physical-fit validation has been performed for this new concept. The original
case's validation does not apply to it.

## Battery system

The intended electrical topology is **1S2P**: parallel cells retain single-cell
voltage and their capacities add. Two nominal 3.5 Ah cells would provide roughly
7 Ah before tolerances. Capacity alone does not establish charger compatibility.

Use a professionally assembled matched, protected pack with a documented shape
and charging requirements as the basis for detailed design.
[Adafruit's pack guidance](https://learn.adafruit.com/li-ion-and-lipoly-batteries/multi-battery-packs)
explains the matching required for parallel lithium cells. This study is not an
instruction to directly parallel arbitrary loose cells. The split-pod wiring,
protection location and suitable pack source remain unresolved.

The actual Tenstar clone's charger IC, current setting, termination behavior and
protection must be checked. Official nice!nano specifications are not proof that
this clone supports a proposed pack. No PCB change has been assumed necessary
or ruled out for the eventual charging/protection solution.

## Reproduce

Run `source/study.py` with Python, numpy and matplotlib. The script reads four
existing configuration/report files and checks that their hashes stay unchanged.
It writes only this study's measurements and illustrations. Its validation is
limited to analytic envelopes; there is no printable STL in this directory.
