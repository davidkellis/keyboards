# v10 thinner and more compact options

**Updated constraint, 2026-10-02:** the user has purchased the 5044147 pouch and
requires at least 5000 mAh. Retain it unless a thinner replacement with that
capacity is available to buy and fits inside the keyboard without enlarging it.
The thinner-pouch examples below remain historical calculations; no replacement
has yet met the purchase and fit requirements. Do not substitute lower capacity.

`battery-search.json` records the supplier leads and the preliminary envelope
screen. PiJuice PIS-1131 is a buyable 125 × 80 × 4 mm, rated 5000 mAh pack, but
exceeds the current bay width and conflicts with pins in the screened position.
Manufacturer-listed 4547154 (5160 mAh, inferred bare cell 154 × 47 × 4.5 mm)
and 4058126 (5050 mAh, 126 × 58 × 4 mm) are leads only: finished pack dimensions,
stock, price and minimum order are unconfirmed. Passing nominal electronics
clearance does not establish fit against the floor supports, ribs or fasteners.

`fixed-battery-options.json` records the follow-up screen. Lowering the connector
and module alone does not lower the required case height in its 0–4° examples;
the battery and components/pins above it govern. At 4°, current electronics and
the current reserve require approximately 8.0 mm front / 17.3 mm rear plate
height. Keeping today's 5.7 mm front permits less than 0.5 mm rear reduction
without changing the electronics arrangement. These are envelope calculations,
not fitted case designs.

The current direction is to retain the purchased battery, investigate relocating
underside SMD components outside its projection and verify the actual switch
pin/solder and plastic protrusions before modeling any shorter pin envelope.
Footprint reduction through closing key-group gaps remains a possible PCB
revision, with battery/controller fit to be checked. Do not reduce the pouch's
thickness allowance until its complete dimensions are measured, and do not
compress it to achieve fit. Earlier recommendations to source a thinner pouch
in this document have been superseded.

This study reads the existing v10 component and pin envelopes and quantifies
front/rear height tradeoffs. It does not revise printable parts or PCB files.
Open `height-options.png` for the calculated curves; `measurements.json` holds
all assumptions and results. Run `source/study.py` with numpy and matplotlib
to reproduce them.

## Current limits

The latest case is **355.56 × 133.352 mm**, with a measured rounded-shell maximum
of **18.730 mm**. Its switch-plate plane extrapolates to **5.692 mm at the front
and 18.992 mm at the rear**, at a 5.696° angle. Plate-plane heights exclude
switches, keycaps and external feet; the rounded exterior edge lies below that
plane. These different measurements should not be conflated.

The PCB is 350.76 × 129.19 × 1.6 mm. Only 2.4 mm is added at each side, including
the nominal 2 mm wall. Narrowing the enclosure walls offers little footprint
reduction and would work against the earlier stiffness goal.

Front diode pockets already leave approximately 0.836 mm of floor and 0.4 mm
clearance. With the same PCB, battery reserve and front plate height, the analytic
screen permits only about 0.5 mm of rear plate-plane reduction, from 18.99 to
18.50 mm. It therefore does not support simply lowering the rear by several
millimetres while leaving the front as low as today.

## Calculated thickness options

The examples below allow a rebuilt case floor and include a 0.2 mm study margin
above the calculated minimum PCB elevation. They use the same battery location
and 155 × 50 mm plan reserve. A smaller reserve height has not been tied to an
actual pack or verified capacity.

| Option | Typing angle | Front plate plane | Rear plate plane |
|---|---:|---:|---:|
| Current case, reference | 5.7° | 5.7 mm | 19.0 mm |
| Current 6.3 mm battery reserve, flatter case | 4° | 8.0 mm | 17.3 mm |
| Thinner 4.3 mm battery reserve, current electronics | 4° | 6.2 mm | 15.5 mm |
| Thinner 4.3 mm battery reserve, current electronics | 3° | 7.4 mm | 14.4 mm |
| Thinner 4.3 mm reserve plus 3 mm connector-depth target | 0° | 12.1 mm | 12.1 mm |

The 4.3 mm reserve is 2 mm thinner than today's allowance; a nominal 3 mm pouch
with enough allowance for its complete wrapping/protection could be one way to
achieve it. No such pack is approved or sourced by this study. Capacity may fall.

The 4°/thin-pouch concept lowers the rear plane about **3.5 mm** while raising
the front about **0.5 mm**. This is the most useful first mechanical direction.
At 3°, the front increases further, so smaller rear height does not mean lower
front typing height. A completely flat case with the battery beneath the key
pins has a considerably higher front than the current inclined case.

Depth increases by less than 0.5 mm for the 4° and 3° examples when preserving
the same end clearances around the less-inclined PCB. Exact case fit, mounting
strength, port openings, hidden nut carriers and supports must be rebuilt and
audited. The table is not proof that the old parts fit at the new elevations.

## Connector and controller options

The PH battery connector uses an 8 mm below-PCB envelope. The
[JST PH manufacturer drawing](https://www.jst-mfg.com/product/pdf/eng/ePH.pdf)
shows an 8 mm top-entry mated profile and a 4.8 mm through-hole side-entry
profile. A side-entry connector needs a footprint/courtyard and mating-lead
check. A short wire lead to an inline connector can remove the vertical body
from beneath the PCB; existing battery holes may permit this without rerouting
the board, but retention, solder access and an appropriate inline location
would need to be designed.

The clone envelope extends 6 mm below the PCB, including its 1 mm mounting gap.
The modeled 5 mm module thickness is still provisional. Measuring the actual
module may recover unused allowance. Recessing the module into a PCB window
could lower its underside, but requires a new PCB/mounting design and checking
the plate, switch pins, socket and antenna. This study's hypothetical 4.5 mm
module depth makes no difference to the plotted thin-pouch results: the battery
and other pins dominate those particular configurations. A controller change
should therefore not be the first step for the 4° concept.

The PCB already uses Kailh Choc V2 switches. They are
[low-profile switches](https://www.kailh.net/products/kailh-choc-v2-low-profile-switch-set).
Changing to a shorter switch/keycap system would be a broader hardware revision,
with new switch footprints, plate apertures and possibly stabilizers. A thinner
PCB might save a fraction of a millimetre, but plate-to-switch geometry and
support must be checked; it cannot substitute for battery/connector clearance.

## Footprint options

Two extra layout gaps can be identified directly from the switch centres and
unit sizes:

- Main-to-navigation gap: SW41 is 1.5u at x=273.0075 and the first navigation
  switch SW49 is 1u at x=301.5825. Their nominal 19.05 mm unit spans leave
  **4.7625 mm** of additional space between groups.
- Function-row gap: function centres y=111.09 versus number-row centres
  y=87.2775 are separated by **23.8125 mm**, or **4.7625 mm** beyond the normal
  19.05 mm row pitch.

Closing these group gaps suggests a roughly **351 × 129 mm** case target,
subject to a new PCB and a successful battery/module/port layout. Those numbers
are layout targets rather than fitted enclosure dimensions. Simply cropping
the current case or moving key holes without rerouting the PCB will not achieve
them. Ordinary spacing between adjacent keycaps should remain sufficient for
full travel and manufacturing tolerances.

A more substantial reduction requires a compact TKL/75%-style arrangement,
particularly moving navigation keys into a narrower column and reorganizing
the arrow/modifier area. That means a new PCB, plate and case. Keeping all 86
keys requires a layout study; this report does not claim a completed 75% layout
or promise a particular footprint. Removing a whole function row would save
more depth but would change the physical key set.

## Recommended sequence

1. Measure the complete current pouch and clone module to replace provisional
   allowances with actual limits.
2. Source a thinner pouch with a documented complete-pack envelope and suitable
   electrical specification, then model a 4° case with the current switches.
3. If smaller width/depth is also required, design a new PCB with the two extra
   group gaps reduced, followed by a fresh battery/controller fit audit.
4. Keep the continuous rounded upper, underside access and distributed supports
   as design goals; do not trade the floor's stiffness for minor height savings.

This screen checks component/pin and battery/floor envelopes only. It omits
structural geometry, detailed battery leads, fasteners, assembly paths and
physical verification. Existing case validation does not carry over to these
new dimensions. All existing PCB and case files are preserved.
