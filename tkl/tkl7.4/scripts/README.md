# v7.4 tools

Use KiCad 10's system Python with `pcbnew` and `sexpdata` (requirements.txt).
All active tools resolve this revision from their own path. They do not write
into tkl7, tkl8 or tkl7.3. The audit verifies all preserved file sets and hashes.

For the already routed board:

```sh
/usr/bin/python3 tkl/tkl7.4/scripts/export_manufacturing.py
```

This runs `validate.py` (netlist, ERC, zone refill/save, DRC/parity), then
`audit_revision.py` (preservation, four-layer OSP stack, unchanged original
tracks/vias/layers/zones, RF exclusions and mechanical geometry/model equality).
It exports FOUR copper Gerbers, drill data, BOM/CPL, drawings, source hashes
and the supplier handoff. Supplier component rotations still require review.

To deliberately recreate this PCB from the fixed v7.2 parent:

```sh
/usr/bin/python3 tkl/tkl7.4/scripts/derive_v7_4.py
/usr/bin/python3 tkl/tkl7.4/scripts/build_schematic.py
/usr/bin/python3 tkl/tkl7.4/scripts/sync_nc_nets.py
/usr/bin/python3 tkl/tkl7.4/scripts/export_manufacturing.py
```

`derive_v7_4.py` replaces THIS revision's PCB and discards later edits to it.
It verifies the parent checksum, retains the full four-layer stack and copper,
and changes the finish to OSP plus the U1/J2 assembly metadata. It does not
reroute or regenerate placement. Tools under `reference/legacy-v7-tools` are
historical only; do not run them.

`export_geometry.py` derives LED height from the package. `case/build_case.py`
uses it and the shared mechanical generators if a fresh rebuild is needed.
The audit verifies exact geometry and reuses v7.2's STL/STEP/DXF files without
claiming a new physical fit test.

After docs-only changes, `export_manufacturing.py --package-only` verifies
source hashes and refreshes the handoff. Source/layout changes require the
full exporter. Use this local exporter, not the generic shared packaging tool.
