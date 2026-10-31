# v9.1 tools

The routed PCB is the checked source. All outputs stay in this revision.
`build_board.py` resets v9.1 from the preserved routed v9 board, adds twelve
board-only mounting NPTHs with 3.45 mm radius copper exclusions, and clips routes
locally. **Do not run it merely to export files**: it replaces routing edits.
The electrical schematic is inherited from v9 with unchanged UUIDs/connectivity.
The older schematic/placement constructors are retained for reference, not the
normal v9.1 rebuild path.

## Environment

KiCad 10 `pcbnew` uses `/usr/bin/python3`. This build used the CadQuery environment
at `/tmp/keyboards-fit-work/venv`, containing CadQuery 2.8, shapely 2.1, numpy,
sexpdata and trimesh. Its compatible packages are made visible to system Python
with `PYTHONPATH=/tmp/keyboards-fit-work/venv/lib/python3.14/site-packages`.
These temporary paths are environment-specific, not bundled dependencies.
OpenSCAD uses `QT_QPA_PLATFORM=offscreen` for headless image rendering.

## From the checked PCB

```sh
PYTHONPATH=/tmp/keyboards-fit-work/venv/lib/python3.14/site-packages /usr/bin/python3 tkl/tkl9.1/scripts/export_manufacturing.py
/usr/bin/python3 tkl/tkl9.1/scripts/export_geometry.py tkl/tkl9.1
/tmp/keyboards-fit-work/venv/bin/python tkl/tkl9.1/scripts/build_fit.py tkl/tkl9.1
/tmp/keyboards-fit-work/venv/bin/python tkl/tkl9.1/scripts/build_print_fit.py
/tmp/keyboards-fit-work/venv/bin/python tkl/tkl9.1/scripts/check_fit.py tkl/tkl9.1
/tmp/keyboards-fit-work/venv/bin/python tkl/tkl9.1/scripts/check_usb_surround.py
/tmp/keyboards-fit-work/venv/bin/python tkl/tkl9.1/scripts/layout_preview.py
/tmp/keyboards-fit-work/venv/bin/python tkl/tkl9.1/scripts/mount_preview.py
QT_QPA_PLATFORM=offscreen openscad --render -o tkl/tkl9.1/case/module-fit.png --imgsize=1100,850 --camera=430,-55,185,323,110,8 --projection=o --colorscheme=Tomorrow tkl/tkl9.1/case/module-fit.scad
QT_QPA_PLATFORM=offscreen openscad --render -o tkl/tkl9.1/case/usb-surround.png --imgsize=1100,850 --camera=0,0,0,75,0,165,100 --projection=o --colorscheme=Tomorrow tkl/tkl9.1/case/usb-surround.scad
QT_QPA_PLATFORM=offscreen openscad --render -o tkl/tkl9.1/case/upper-preview.png --imgsize=1400,750 --camera=440,-260,320,178,66,3 --projection=o --colorscheme=Tomorrow tkl/tkl9.1/case/upper-preview.scad
QT_QPA_PLATFORM=offscreen openscad --render -o tkl/tkl9.1/case/base-preview.png --imgsize=1400,800 --camera=475,-320,400,178,66,8 --projection=o --colorscheme=Tomorrow tkl/tkl9.1/case/base-preview.scad
QT_QPA_PLATFORM=offscreen openscad --render -o tkl/tkl9.1/case/assembled-exploded.png --imgsize=1400,900 --camera=500,-350,410,177,66,12 --projection=o --colorscheme=Tomorrow tkl/tkl9.1/case/fit.scad
/tmp/keyboards-fit-work/venv/bin/python tkl/tkl9.1/scripts/package_fit.py
python tkl/tkl9.1/scripts/check_handoff.py
```

`export_manufacturing.py` runs ERC/DRC, netlist/parity and circuit checks plus an
independent revision audit before exporting. Audit checks preservation hashes,
switch/module placement, board thickness/layers, mount coordinates, electrical
pad separation from mounting exclusions, assembly side and no via drills in SMT
lands. Mounting holes are excluded from component placement files.

After intentionally resetting or changing routing, `finish_routing.py` closes
connections with two-layer A* paths while respecting the new mounting keepouts.
`clean_mount_routing.py` removes redundant branch tails only when the resulting
board remains connected and has no DRC errors. Each mutation trial uses a fresh
pcbnew process to avoid SWIG ownership problems. Fill and save zones before
exporting Gerbers. The inherited batch `prune_stubs.py` may reject a batch that
needs individual cleanup; it restores its input in that case.

## Mechanics

`fit-config.json` records fixed dimensions, mount positions, actual measurements
and provisional envelopes. `export_geometry.py` extracts the PCB drills and
placements. `build_fit.py` generates nominal PCB STEP/STL, the integrated upper,
base, lap-jointed halves, component/mount coupons, assembly STEP and collision
report. `mount_geometry.py` implements the side-loaded nuts, screw recesses,
spacers, battery-clearing rear brackets and trimmed floor ribs.
`split_geometry.py` cuts bonded lap seams without adding to the outside envelope.

`build_print_fit.py` then enlarges only the 361 switch/module holes by 0.4 mm
**diameter** in plastic insertion gauges, publishing main-folder PCB STL names
and a separate ZIP. The manufactured PCB and STEP remain nominal. `check_fit.py`
checks meshes, single-piece connectivity, split print bounds and source hashes.
`check_usb_surround.py` checks the actual case STL aperture at three depths.
`package_fit.py` bundles the validated small samples and hash manifest.

Physical fit, torque, material strength, charging, RF and firmware tests remain
separate from CAD/DRC checks. Start with the mounting and component coupons.

`check_handoff.py` verifies the exported NPTH mount coordinates, archive/source
hashes and unchanged v9 BOM/CPL. `mount_preview.py` draws the mounting map.
