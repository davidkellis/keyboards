# v7.4 four-layer construction

Specify **JLC04161H-7628**, nominal **1.6 mm**, **OSP**, 1 oz outer / 0.5 oz
inner copper, with epoxy-filled, planarized and copper-capped through vias.
Use lead-free SMT paste and lead-free solder for THT/manual operations.
This revision retains the complete v7.2 four-layer construction and routing.

| Layer | KiCad name | Function | Copper, mm |
| --- | --- | --- | ---: |
| L1 | F.Cu | Original front signal copper, USB pair, GND | 0.035 |
| L2 | In1.Cu | Original GND reference with RF exclusions | 0.0152 |
| L3 | In2.Cu | Original inner signal copper and GND | 0.0152 |
| L4 | B.Cu | Original underside components, RF and signal copper | 0.035 |

The three dielectric spacings, top to bottom, are **0.2104 / 1.065 / 0.2104 mm**.
Prepreg is 7628 (nominal Er 4.4); core Er is 4.6. These are the manufacturer's
published constituent values, retained from v7.2. The mechanical design remains
nominal 1.6 mm; confirm the factory's finished thickness and tolerance.

Both original outer signal/reference spacings remain 0.2104 mm. The original
RF keepouts on both internal layers, every signal track/via, and all zone
outlines/rules remain unchanged. No layers are added or remapped. Do not
substitute the 3313 stack or use the six-layer v7.3 fabrication files.

This is a geometry/reference-plane review, not a field-solver qualification.
The inherited nominal USB 90-ohm differential target and RF matching still
require factory review and physical prototype validation. The design-rule
checker verifies connectivity and clearances, not RF impedance.

Source: [JLC's four-layer 1.6 mm, 1 oz / 0.5 oz JLC04161H-7628 construction](https://jlcpcb.com/impedance), checked 2026-09-25.
