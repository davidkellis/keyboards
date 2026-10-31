# v10 sources and rebuild

The checked, routed `kicad/keyboard.kicad_pcb` is the normal source for exports.
`build_board.py` is a **reset**: it starts from v9.1, restores six switch/diode
footprints from v7.5, moves the clone to (57.15, 37.49) mm, moves H9/H12 and
clips routes around changed regions. Do not run it merely to export files.

This environment uses KiCad 10 via `/usr/bin/python3` and CadQuery 2.8 through
`/tmp/keyboards-fit-work/venv/bin/python`. Routing also uses shapely/numpy via
`PYTHONPATH=/tmp/keyboards-fit-work/venv/lib/python3.14/site-packages` with the
system Python. Paths are environment-specific; dependencies are not bundled.

## Electrical

After a deliberate reset, use `finish_routing.py`; its `--start-side bottom`
option can route remaining paths from the other side. It accepts each new path
only after a KiCad DRC/connectivity check. `cleanup_floating_branches.py` removes complete leaf chains with checked rollback.
`merge_close_vias.py` removes redundant same-net drilled holes.
`prune_stubs.py` bisects rejected cleanup batches;
`clean_mount_routing.py` removes/trims remaining redundant tails with checked
rollback. On this KiCad installation, removal edits use S-expressions to avoid
unsafe native object ownership when removing items through pcbnew.

Generate the schematic with `build_schematic.py`, then `sync_nc_nets.py`.
`validate.py` checks ERC, DRC, schematic parity, every numbered pad against an
exported netlist, independent controller pin assignments and all 86 unique
switch/diode matrix addresses. `audit_revision.py` checks source preservation,
all original switch coordinates/drills, new module/mount placement, two layers,
standard vias, antenna/mount keepouts and bottom-only factory placement.

`export_manufacturing.py` runs those checks before writing Gerbers, drill files,
BOM, CPL, matrix map, drawings, schematic PDF and source-hashed handoff archives.
Follow it with `check_handoff.py`. Fabrication notes and ordering settings live
in `manufacturing`; no live quote is implied by these exports.

## Mechanical

From the final PCB, in order:

```sh
/usr/bin/python3 tkl/tkl10/scripts/export_geometry.py tkl/tkl10
/tmp/keyboards-fit-work/venv/bin/python tkl/tkl10/scripts/build_fit.py tkl/tkl10
/tmp/keyboards-fit-work/venv/bin/python tkl/tkl10/scripts/build_print_fit.py
/tmp/keyboards-fit-work/venv/bin/python tkl/tkl10/scripts/check_fit.py tkl/tkl10
/tmp/keyboards-fit-work/venv/bin/python tkl/tkl10/scripts/check_surface.py
/tmp/keyboards-fit-work/venv/bin/python tkl/tkl10/scripts/check_usb_surround.py
/tmp/keyboards-fit-work/venv/bin/python tkl/tkl10/scripts/check_revision.py
/tmp/keyboards-fit-work/venv/bin/python tkl/tkl10/scripts/fit_preview.py tkl/tkl10
/tmp/keyboards-fit-work/venv/bin/python tkl/tkl10/scripts/layout_preview.py
/tmp/keyboards-fit-work/venv/bin/python tkl/tkl10/scripts/mount_preview.py
/tmp/keyboards-fit-work/venv/bin/python tkl/tkl10/scripts/render_previews.py
/tmp/keyboards-fit-work/venv/bin/python tkl/tkl10/scripts/package_fit.py
```

`fit-config.json` contains the current measurements, fit allowances, battery
bay, twelve screw locations and pin/LED surface details. The builder validates
intersections with the actual generated solids, including hardware, battery,
switches, pins and module envelopes. `check_surface.py` independently sections
the exported plate STL; `check_usb_surround.py` sections the actual USB bezel.
`check_fit.py` checks mesh topology, positive volumes and split-bed bounds.

If **only routing** changes after CAD generation, `refresh_fit_provenance.py`
can re-extract the final PCB and update provenance only when every geometry
field compares exactly equal. Any geometric/configuration change requires a
full rebuild. Regenerate dependent reports/packages after a provenance refresh.

The software preview renderer uses actual meshes and a depth buffer; no X
server or GPU context is required. Individual printed parts are bed-normalized;
STEP assemblies preserve their assembled coordinates.
