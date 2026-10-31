# V12 prototype fabrication notes

Two-layer, 1.6 mm FR-4, lead-free HASL; lead-free component assembly, bottom only.
Maintain the board outline, 86 switch patterns, twelve 2.5 mm unplated M2 holes,
and ten unplated oval reverse-LED apertures (2.1 × 2.8 mm).
The current V12 layout uses two staggered interior rows of five LEDs; use the
matching current Gerbers and CPL together. Use only the V12 files in this package.

Do not plug, plate over or fill the optical slots. Reverse LEDs shine up through
the slots. The entire acrylic optical path above the board is user installed.
No edge-lit acrylic sheet is fitted beneath the PCB in this design.

Follow BOM and CPL polarity. LED pad 1 is cathode; pad 2 is anode. D87 pad 1 is
the boost rectifier cathode. R10 is the mandatory 100 ohm current-sense resistor.
LED7–LED10 are populated on the ten-LED build; future wire bypass is user rework.
Do not silently omit an LED or bridge the current-sense resistor.

The clone and key switches are excluded from the factory BOM/CPL. The carrier
has an antenna copper exclusion and M2 hardware clearances; preserve them.
This package is a prototype handoff with software rule checks, not measured
confirmation of optics, regulator stability, charging, RF or mechanical fit.

## Three-family soldered switch pattern

Preserve ALL original Choc V2 holes and lands. There are 172 additional plated
1.5 mm Gateron contact holes and 172 nonplated horizontal locating slots, each
2.32 x 1.90 mm. Do not round the locating slots into single holes, plate them,
or merge them with another hole. The NPTH drill file specifies their CNC route.
Review actual slot geometry in CAM; see SWITCHES.md for the top-view coordinates.

Only C2 moves relative to final V11. The component and switch nets are unchanged.
The alternate contacts are duplicates of pads 1 and 2 on each switch, both wired;
the user installs ONE switch family per position. No factory hot-swap sockets.
