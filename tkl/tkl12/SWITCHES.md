# V12 mounting pattern

All coordinates below are **top view**, in millimeters from the switch center.
Positive X is right; positive Y points toward the front of the keyboard in the
native KiCad view. All 86 switch footprints have zero rotation.

| Feature | Center coordinates | Finished hole / slot | Copper |
| --- | --- | --- | --- |
| Original Choc contact 1 | (0, -5.9) | 1.2 mm plated | 2.2 mm diameter, unchanged |
| Original Choc contact 2 | (5, -3.8) | 1.2 mm plated | 2.2 mm diameter, unchanged |
| Original center post | (0, 0) | 5.05 mm nonplated | Unchanged |
| Original Choc V2 corner post | (-5, 5.15) | 1.6 mm plated mechanical hole | 2.6 mm diameter, unchanged |
| Gateron contact 1 | (2.54, -5.08) | 1.5 mm plated | 2.4 mm diameter |
| Gateron contact 2 | (-3.81, -2.54) | 1.5 mm plated | 2.4 mm diameter |
| Left shared side locator | (-5.29, 0) | Horizontal capsule 2.32 × 1.90 mm, nonplated | None |
| Right shared side locator | (5.29, 0) | Horizontal capsule 2.32 × 1.90 mm, nonplated | None |

The slots' centerline endpoints are ±5.08 and ±5.50 mm. They contain the
nominal Choc V1 1.9 mm hole envelopes at ±5.5 mm and Gateron 1.7 mm hole
envelopes at ±5.08 mm. The larger shared center hole does not center a Choc V1
post tightly: its two side pegs and the plate provide location. Keep the plate
installed when soldering. The slots are alignment clearances, not press fits.

Each alternate contact shares the same pad number and matrix net as its Choc
counterpart. Both sets are routed. Populate **one switch per position**; no jumpers,
diode changes or firmware matrix changes are needed. This is not a socket footprint.

## Exact references

- Our Kailh Choc V2 silent tactile Whale: [CPG1353S01D02-01 drawing](https://www.kailhswitch.com/uploads/15927/files/CPG1353S01D02-01-data-sheet.pdf).
- Kailh Choc V1 reference: [CPG135001D01-16](https://m.kailhswitch.com/Content/upload/pdf/202215927/CPG135001D01-16.pdf?rnd=121).
- Gateron Low Profile 3.0 Grey Heron: **KS-33BHB10B050NW-G13**, [manufacturer drawing](https://www.gateron.com/u_file/2505/21/file/GateronKS-33LowProfile30GreyHeronSwitchKS-33BHB10B050NW-KS-33B.pdf).
- Gateron Low Profile 3.0 Silver: **KS-33BS10B043NW-Y92B**, [manufacturer drawing](https://www.gateron.com/u_file/2610/12/file/GATERONKS-33LowProfile30MechanicalSilverSwitchSet.pdf).
- Gateron Low Profile Silent 3.0 Red: **KS-33GJH10B045NW-X5B**, [manufacturer drawing](https://www.gateron.com/u_file/2610/12/file/GATERONKS-33LowProfileSilent30MechanicalRedSwitchKS-33GJH10B045NW-X5B.pdf).

Copies of these drawings are in `reference/manufacturer-drawings/`.
Kailh's drawings label their recommended PCB view **Pattern Side** (bottom).
Gateron's PCB layout is the opposite view. V12 uses the corrected top-view
Gateron contacts, matching KiCad's standard MX contact chirality. The earlier
V11 feasibility screen's mirrored Gateron contacts must not be fabricated.
`reference/corrected-clearance-screen.json` records the corrected screen;
`reference/pattern.json` and the routed board are the final implementation.

## Mechanical limits

Kailh Choc V2 keeps its 2.2 mm plate-top height above the PCB and existing
center, contacts and support post. Choc V1's nominal seating height is also
2.2 mm, but it takes two-slot Choc caps instead of our MX-stem XVX caps.
Its stabilizers and cap spacing must be selected for this 19.05 mm layout.

The checked Gateron 3.0 drawings specify a **2.5 mm plate-top height**. Their
longer travel and different installed stem heights require a separate plate
and case clearance check. Their LED windows face the same edge as Kailh in
V12, but brightness through the acrylic plate and keycaps is not established.
Silent Red's travel/height differs from Heron and Silver; test the exact part.
Do not assume a raised case designed around one cap skirt clears another.

No claim is made for Gateron 1.0/2.0, Cherry Low Profile, TTC Mini or all
Lofree/NuPhy/Keychron variants. Match an exact engineering drawing or a sample.
Normal-height MX switches also need a different mechanical stack and are not a
supported complete-keyboard option merely because two contacts line up.

For JLC, the 1.9 mm slots exceed its published 1.0 mm minimum nonplated slot
width. Its regular nonplated-slot tolerance is ±0.2 mm, so nominal drawing
coverage is not a guarantee of real fit. Verify the routed slots in the Gerber
viewer and run a physical coupon before relying on another switch family.
Source: [JLCPCB manufacturing capabilities](https://jlcpcb.com/capabilities/pcb-capabilities/).
