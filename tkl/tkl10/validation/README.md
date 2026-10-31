# v10 validation

Final electrical checks: `summary.json`, `erc.json`, `drc.json` and `netlist.xml`.
All 86 unique keys and 407 numbered pads pass; zero errors, warnings, opens
or schematic parity issues. `revision-audit.json` checks source preservation,
coordinates, mounting clearances, standard vias and assembly side.

`handoff-check.json` verifies actual drill exports, assembly lists and ZIP
hashes. `mechanical-revision.json` checks the combined revision.

The mechanical model was built while routing proceeded. After routing,
`fit-provenance-refresh.json` records an exact comparison of every extracted
geometry field, proving that no placement, drill or fit setting changed.
Only the source PCB hash changed. CAD reports and packages then use that final
source hash.

The case directory contains the collision report, 38-mesh topology checks,
independent STL plate/bezel section checks and enlarged-hole gauge validation.
The actual case STL dimensions also match the fixed 355.56 x 133.352 x 20.6 mm
envelope within 0.002 mm. Printability/material strength, real component fit,
firmware, charging and RF performance require physical prototypes.

`routing-history` contains intermediate diagnostics, not the final result.
