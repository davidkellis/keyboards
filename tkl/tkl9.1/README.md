# TKL v9.1 — screwed plate/PCB/base assembly

v9.1 preserves v9 electronics and key positions while adding an integrated upper
plate/frame, twelve coordinated M2 mounting points, floor ribs and bonded lap
joints for split prints. The raised separators between typing rows are removed.
The lower switch grid remains. Outside footprint and the **7.3 mm front / 20.6 mm
rear** case profile are unchanged.

- [Print files and assembly guide](case/README.md) · [Complete print ZIP](case/tkl-v9.1-print-kit.zip)
- [Nominal complete assembly](case/fit-assembly.step)
- [PCB source](kicad/keyboard.kicad_pcb)
- [Manufacturing upload guide](manufacturing/ORDERING.md)
- [Electrical bring-up](BRINGUP.md)
- [Rebuild instructions](scripts/README.md)

Use v9.1's PCB and case together: the new case requires twelve matching 2.5 mm
NPTH holes. Copper was cleared/rerouted around them; switches, module, LEDs,
outline, thickness and circuit are retained from v9. The factory BOM remains
seven groups / 99 bottom-side placements. The user installs the clone and
switches. No JLC cart change, order or quote is part of this revision.

The v9 directory was copied and hash-recorded before work; earlier revisions
remain intact. `validation/summary.json` and `validation/revision-audit.json`
record electrical and isolation checks. `case/fit-report.json` records mechanical
clearance checks and assumptions. `case/mesh-validation.json` records printable
mesh checks. Test the small mounting and component coupons first.

This is an unbuilt prototype. Actual screw/nut fit, printed stiffness, switch and
stabilizer travel, clone registration/USB fit, custom firmware, charging and RF
behavior have not been established by CAD or design-rule checks.
