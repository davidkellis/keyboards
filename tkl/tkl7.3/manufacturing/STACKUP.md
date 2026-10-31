# v7.3 six-layer construction

Specify **JLC06161H-7628**, nominal **1.6 mm**, **OSP**, 1 oz outer / 0.5 oz
inner copper, with epoxy-filled, planarized and copper-capped through vias.
Use lead-free SMT paste and lead-free solder for THT/manual operations.
The original four-layer files cannot be ordered as this construction.

| Layer | KiCad name | Function | Copper, mm |
| --- | --- | --- | ---: |
| L1 | F.Cu | Original front signal copper, USB pair, GND | 0.035 |
| L2 | In1.Cu | Original GND reference | 0.0152 |
| L3 | In2.Cu | Added GND plane | 0.0152 |
| L4 | In3.Cu | Added GND plane | 0.0152 |
| L5 | In4.Cu | Original In2 signal copper and GND | 0.0152 |
| L6 | B.Cu | Original underside components, RF and signal copper | 0.035 |

The five dielectric spacings, top to bottom, are **0.2104 / 0.4 / 0.2028 /
0.4 / 0.2104 mm**. Prepreg is 7628 (nominal Er 4.4); core Er is 4.6.
Use the manufacturer's named construction. JLC's selector explicitly states
**1.5544 mm actual thickness, tolerance ±10%**, under its nominal 1.6 mm option.
The CAD fit envelope remains 1.6 mm; verify the manufactured thickness and
switch/plate stack in the physical prototype. Do not request a different custom
stack to make the constituent thicknesses add to exactly 1.6 mm.

The selector classifies this as a **special stackup requiring Standard PCBA**.
Its $33.08 stackup fee is included in the $97.58 five-board fabrication estimate
recorded in [COST_REDUCTION.md](COST_REDUCTION.md).

The USB pair and its original adjacent In1 reference plane retain the original
geometry and 0.2104 mm spacing. The old bottom-adjacent In2 layer is now In4,
also 0.2104 mm from B.Cu. Thus changing to the factory's default 3313 stack
would change the intended signal/reference spacing and is not allowed.

The imported Nordic antenna-match/feed keepout is replicated on all four
internal layers. New ground planes must not enter that void. The reference
outer RF geometry and all signal tracks/vias remain unchanged. New ground
planes connect through existing plated ground pads and vias.

This is a geometry/reference-plane review, not a field-solver qualification.
The inherited nominal USB 90-ohm differential target and RF matching still
require factory review and physical prototype validation. The design-rule
checker verifies connectivity and clearances, not RF impedance.

Source: [JLC's six-layer 1.6 mm, 1 oz / 0.5 oz JLC06161H-7628 construction](https://jlcpcb.com/impedance), checked 2026-09-25.
