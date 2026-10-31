# v9.1 verification

`release-check.json` links the final PCB hash to electrical, mechanical, mesh,
preservation and archive checks. This is a prototype verification record, not
a hardware qualification.

- ERC: zero errors and warnings.
- DRC: zero errors, warnings, unconnected items and schematic-parity issues.
- Netlist/circuit invariants: 395 numbered pads and 83 unique matrix keys agree.
- Twelve 2.5 mm NPTH mount positions agree across configuration, native PCB and
  exported drill file. The 3.45 mm mounting exclusions contain no electrical
  pads; the nearest pad is another 0.742 mm beyond the exclusion boundary.
- BOM/CPL are byte-identical to v9: seven groups, 99 bottom-side placements.
- CAD: no modeled case/PCB/component/battery/upper/screw collisions; battery
  reserve and outside profile retained. Split joints fit within the full model.
- All 36 STL meshes pass watertight/positive-volume checks; printable parts are
  single solids. Upper and base halves fit a 256 mm bed.
- Recessed USB aperture passes section checks of the actual exported case STL.
- All 423 v9 files in the preservation manifest remain unchanged. The broader
  revision audit verifies 3,560 preserved files including older revisions.
- ZIP member hashes and source hashes match exported artifacts.

The routing progress/cleanup files are intermediate records; `summary.json`
and `release-check.json` describe the final board. `handoff-check.json` covers
manufacturing exports; `revision-audit.json` covers layout/isolation invariants.
Mechanical details and assumptions are in `../case/fit-report.json`.

Not tested: real module pin/socket registration, actual screw/nut/printed fit,
stabilizer/keycap travel, stiffness/strength/creep, firmware, battery charging or
BLE/RF behavior. Print the mounting and component coupons before the full case,
and complete the prototype bring-up before treating this as production ready.
