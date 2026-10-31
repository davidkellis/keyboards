# V12 source and checks

The final routed `../kicad/keyboard.kicad_pcb` is the source for exports.
Do not rerun `build_v12.py` merely to export: it deliberately resets from the
archived V11 baseline and clips routing for the new holes.

V12 uses KiCad 10 and Python with pcbnew, sexpdata, numpy, shapely and trimesh.
This workstation's environment is `/tmp/tkl-v11-env/bin/python`.

Normal checks and exports, from the keyboards workspace:

```sh
/tmp/tkl-v11-env/bin/python tkl/tkl12/scripts/validate.py
/tmp/tkl-v11-env/bin/python tkl/tkl12/scripts/audit_revision.py
/tmp/tkl-v11-env/bin/python tkl/tkl12/scripts/export_geometry.py tkl/tkl12
/tmp/tkl-v11-env/bin/python tkl/tkl12/scripts/check_mechanical.py
/tmp/tkl-v11-env/bin/python tkl/tkl12/scripts/build_models.py
/tmp/tkl-v11-env/bin/python tkl/tkl12/scripts/export_manufacturing.py
/tmp/tkl-v11-env/bin/python tkl/tkl12/scripts/check_handoff.py
```

`build_schematic.py` deliberately regenerates the unchanged circuit with V12
footprint references; follow it with `sync_nc_nets.py` if regeneration is needed.
`route_v12.py` resumes two-layer routing and checks each batch using KiCad DRC.
`escape_sw3.py` records the one-time off-land via escape beside D3 and opens
adjacent tracks for rerouting. `remove_orphan_copper.py` removes only isolated,
DRC-reported signal islands with no component pads. `cleanup_floating_branches.py` removes redundant branches with connectivity
rollback. `trim_tails.py` trims the remaining warned ends to their actual copper
contacts. `finish_routing.py` is the inherited single-connection fallback.

`audit_revision.py` checks all original pad UUIDs and drill/land geometry against
the saved V11 source; the sole component movement is C2. It checks the added
pattern against the manufacturer's top-view convention and independent KiCad MX
coordinates, nominal shared locator coverage, the complete matrix and assembly
catalog, the unchanged boost switching loop, and all 386 six-to-ten-LED bypass
populations. `validate.py` checks schematic parity, ERC, DRC and circuit nets.
`check_handoff.py` checks the actual exported drills and packages.
