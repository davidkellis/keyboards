# v9 checks before ordering — 2026-09-26

The current PCB passes the checks below. This is an unbuilt prototype:
no hardware has been powered or firmware built/flashed in this session.

## Completed on the actual source and upload files

- Fresh KiCad ERC: zero errors or warnings.
- Fresh KiCad DRC, with zone refill in memory: zero errors/warnings,
  unconnected items or schematic parity issues.
- Numbered pads agree with the schematic netlist; 83 switch/diode pairs have
  unique row/column addresses. Supply, switch, MOSFET, resistor and module
  connections pass the existing circuit invariant checks.
- Revision audit: two layers, 1.6 mm, 99 factory placements all on the bottom,
  ordinary 0.30 mm through-via drills, no via-in-pad requirement, and the prior
  3,137 protected revision files remain intact.
- All seven fabrication source hashes still match the export manifest.
  Gerber ZIP, BOM and CPL hashes still match the files used for the JLC quote.
  Seven BOM groups cover exactly the 99 unique CPL references; all are Bottom.
- The candidate GPIO map has 21 distinct pins: 20 matrix plus backlight control.
- Five new plastic insertion-test meshes passed solid/watertight checks; their
  added cut volume matches exactly the requested hole-diameter enlargement.

See `summary.json`, `handoff-audit.json`, the parent `revision-audit.json`, and
`../../case/print-fit/validation.json` for results. DRC was run without saving
the board. No fabrication holes or uploaded copper files were changed.

ERC/DRC and schematic agreement do not prove the original circuit is correct:
the schematic was generated from the design, and a shared design error could
appear in both. These checks also cannot identify an incorrect clone pin label,
poor radio performance, a faulty part, or an incompatible bootloader.

## Physical checks that can happen before a carrier PCB exists

1. **Mechanical trial:** print the single-switch sample, then the rear-corner
   kit in `../../case/print-fit/`. Insert the actual Choc V2 switches and clone
   without bending pins. Verify both edge rows and all three auxiliary pad
   centers, USB orientation/insertion, the 1 mm module gap, floor clearance and
   plate/cover closure. The enlarged holes compensate for plastic printing;
   their looseness is not evidence that nominal plated holes will fit.
2. **Module-only USB trial:** with no battery attached, check the clone's USB
   bootloader enumeration using a data cable in both orientations. Read its
   reported board/bootloader identity before selecting firmware. This confirms
   only the module and connector, not a working keyboard or BLE link.
3. **Firmware and a small wired matrix:** build the v9-specific ZMK configuration
   for the verified clone, then hand-wire four switches/diodes as SW1, SW2,
   SW64 and SW71. `bench-test-connections.csv` lists the GPIO connections.
   Each path is COLUMN GPIO -> switch -> diode anode -> diode cathode -> ROW
   GPIO. Use BAT46W for a representative test; a different diode does not
   validate BAT46W's electrical margins. The cathode band faces the row.
   With this wiring the scanner direction is `col2row`.
4. Test each key, all pairs, three-key combinations and all four held together
   over USB and BLE; check for missing, phantom or stuck keys. Also exercise
   the optional entries in the CSV to cover P0.09/P0.10 and auxiliary P1.02/
   P1.07, since the first four only cover P1.01. P0.09/P0.10 must be configured
   as GPIO instead of NFC. Verify all remaining row/column lines before
   treating the entire 21-pin module mapping as tested.
5. Characterize the actual clone's switched VCC and backlight control before
   relying on nice!nano behavior. Charging/temperature protection also needs
   the actual clone and a selected protected 1S cell; no pack is approved yet.
   Keep any 500 mA charge boost disabled: the carrier switch is rated 300 mA.
   Follow `../../BRINGUP.md` for later powered carrier tests.

The bench CSV is a wiring plan, not firmware. No UF2 is supplied or tested.
The next substantive electrical milestone is a successful firmware build and
USB/BLE matrix trial on the actual clone. A simulator cannot validate that
clone's undisclosed circuitry or the finished keyboard's RF/mechanical behavior.

JLC's bare-board electrical test can check manufactured copper for opens and
shorts; it does not test keyboard firmware, key scanning, BLE or battery
charging. Factory assembly here excludes the module and all key switches.

Primary references:

- [ZMK new-shield guide](https://zmk.dev/docs/hardware-integration/new-shield)
  explains GPIO selection, matrix direction and transforms.
- [nice!nano pinout](https://nicekeyboards.com/docs/nice-nano/pinout-schematic/)
  is a reference for the genuine module, not proof of clone equivalence.
