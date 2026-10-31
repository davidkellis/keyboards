# v9 tools

All output paths are revision-local. The checked routed PCB is the primary
artifact. `build_board.py` resets it to an unrouted placement from v7.5, removes
SW9/SW15/SW16 and their diodes, moves U1/SW87 and rotates the antenna exclusion.
`build_schematic.py` recreates the three sheets and UUID paths; `sync_nc_nets.py`
synchronizes intentionally unconnected pads. Do not run these on later manual
edits unless deliberately rebuilding the design.

Python dependencies: KiCad 10 pcbnew, sexpdata, numpy, shapely; CAD uses CadQuery
and trimesh. Current environment has `/tmp/keyboards-v7-work/pylibs` and
`/tmp/keyboards-fit-work/venv`.

Normal export from the checked PCB:

```sh
PYTHONPATH=/tmp/keyboards-v7-work/pylibs /usr/bin/python3 tkl/tkl9/scripts/export_manufacturing.py
/usr/bin/python3 tkl/tkl9/scripts/export_geometry.py tkl/tkl9
/tmp/keyboards-fit-work/venv/bin/python tkl/tkl9/scripts/build_fit.py tkl/tkl9
/tmp/keyboards-fit-work/venv/bin/python tkl/tkl9/scripts/build_print_fit.py
/tmp/keyboards-fit-work/venv/bin/python tkl/tkl9/scripts/check_fit.py tkl/tkl9
/tmp/keyboards-fit-work/venv/bin/python tkl/tkl9/scripts/check_usb_surround.py
QT_QPA_PLATFORM=offscreen openscad -o tkl/tkl9/case/module-fit.png --render --imgsize=1100,850 --camera=430,-55,185,323,110,8 --projection=o --colorscheme=Tomorrow tkl/tkl9/case/module-fit.scad
QT_QPA_PLATFORM=offscreen openscad -o tkl/tkl9/case/usb-surround.png --render --imgsize=1100,850 --camera=0,0,0,75,0,165,100 --projection=o --colorscheme=Tomorrow tkl/tkl9/case/usb-surround.scad
/tmp/keyboards-fit-work/venv/bin/python tkl/tkl9/scripts/package_fit.py
```

`route_board.py prepare/import` exchanges DSN/SES with a local Freerouting run.
It exports antenna zones and explicit optical-hole keepouts. Imported tracks
are clamped to the carrier's 0.18 mm minimum and must pass KiCad clearance checks.
`finish_routing.py` closes residual gaps with checked two-layer A* paths; use
`--start-side bottom` to search from the other copper layer when necessary.
`prune_stubs.py` removes dangling tracks only if no electrical connection is lost.

`validate.py` checks ERC, DRC, schematic parity, netlist/pad agreement and circuit
invariants. `audit_revision.py` independently checks isolation hashes, removed
keys, remaining switch geometry, module placement, assembly side, layers and
no via drills inside SMT lands. `export_manufacturing.py` requires both to pass.

`fit-config.json` contains measured inputs and explicitly provisional dimensions.
`export_geometry.py` extracts actual board drills/placements and exports the
module, socket and external plug gauges. `build_fit.py` makes case/plate/cover,
full/split models, corner coupons, assembly STEP and collision results.
`usb_surround.py` builds the integral recessed bezel and checks cable-housing
insertion clearance. Socket size, web thickness and recess dimensions live in
`fit-config.json`; the PCB/module position is preserved.
`check_usb_surround.py` slices the exported case STL through the bezel at three
depths to check the small aperture and absence of any additional slit.
`check_fit.py` checks all printable meshes and source/config hashes.
`layout_preview.py` draws the module plan, and `package_fit.py` bundles the
validated corner samples and their hashes for printing.
No internal USB extension or female bulkhead is part of v9.

`build_print_fit.py` creates a separate `case/print-fit/` insertion-test kit
from the nominal PCB STEP and drill positions. It enlarges switch and module
holes by 0.4 mm diameter (configurable with `--diameter-extra`, up to 0.6 mm),
exports full/split/corner/single-switch STL gauges, checks material removal and
mesh validity, and bundles the matching case/plate/cover coupons. It also updates
the main case folder's bare PCB, split PCB and coupon STL filenames and records
their hashes in `print-fit-files.json`. Run it after `build_fit.py`, which first
generates nominal geometry. The board, manufacturing files, STEP references and
populated envelope models remain unchanged.
`validate.py` refills zones in memory and does not save changes to the board.
