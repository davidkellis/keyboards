# v7.3 tools

Use KiCad 10's system Python with `pcbnew` and `sexpdata` (requirements.txt).
All active tools resolve this revision from their own path. They do not write
into tkl7 or tkl8. Keep those parent directories unchanged: the audit checks
all of their file hashes and the file set against the preservation manifest.

For the already routed board, run:

```sh
/usr/bin/python3 tkl/tkl7.3/scripts/export_manufacturing.py
```

This runs `validate.py` (netlist, ERC, zone refill/save, DRC/parity) and
`audit_revision.py` (parent preservation, six-layer stack, original signal
copper/vias, RF exclusions, mechanical geometry and fit-model provenance).
Then it exports all SIX copper Gerbers plus drill data, BOM/CPL, drawings,
source hashes and the supplier handoff. No purchase or production release
is performed. The supplier's final component rotations are still to be checked.

To deliberately recreate the PCB from the fixed v7.2 parent:

```sh
/usr/bin/python3 tkl/tkl7.3/scripts/derive_v7_3.py
/usr/bin/python3 tkl/tkl7.3/scripts/build_schematic.py
/usr/bin/python3 tkl/tkl7.3/scripts/sync_nc_nets.py
/usr/bin/python3 tkl/tkl7.3/scripts/export_manufacturing.py
```

`derive_v7_3.py` replaces THIS revision's PCB and discards later edits to it.
It verifies the parent checksum, moves the existing In2 copper to In4, adds
two internal ground planes with RF exclusions, and sets OSP, six layers and
the current assembly metadata. It does not reroute or regenerate placement.
The obsolete four-layer placement/router tools are under
`reference/legacy-v7-tools` for historical inspection only; do not run them.

The local `export_geometry.py` derives LED height from the actual reverse-mount
package, rather than a directory name. `case/build_case.py` uses this extractor
and the shared mechanical generators if a fresh mechanical rebuild is needed.
For this revision the audit verifies geometry equality and reuses the v7.2
STL/STEP/DXF files without inventing a new fit result.

After a docs-only change, `export_manufacturing.py --package-only` verifies
source hashes and refreshes the handoff. Source/layout changes require the
full exporter. The generic `../package_handoff.py` is not the exporter for
this six-layer revision.
