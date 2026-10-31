# v7.5 tools

The checked routed PCB is the primary source. Tools affect only this revision.
Python dependencies: KiCad 10 `pcbnew`, `sexpdata`, `numpy`, `shapely`; CAD uses
CadQuery, Shapely and trimesh. The current environment has routing dependencies
in `/tmp/keyboards-v7-work/pylibs` and a CAD venv at `/tmp/keyboards-fit-work/venv`.

Export the existing routed design:

```sh
PYTHONPATH=/tmp/keyboards-v7-work/pylibs /usr/bin/python3 tkl/tkl7.5/scripts/export_manufacturing.py
/usr/bin/python3 tkl/tkl7.5/scripts/export_geometry.py tkl/tkl7.5
/tmp/keyboards-fit-work/venv/bin/python tkl/tkl7.5/scripts/build_fit.py tkl/tkl7.5
/tmp/keyboards-fit-work/venv/bin/python tkl/tkl7.5/scripts/check_fit.py tkl/tkl7.5
QT_QPA_PLATFORM=offscreen openscad -o tkl/tkl7.5/case/module-fit.png --imgsize=950,1100 --camera=489,-193,372,316,68,7 --projection=o --colorscheme=Tomorrow tkl/tkl7.5/case/module-fit.scad
```

`validate.py` runs ERC, DRC and schematic parity, compares independent netlist
pads and checks module/power/matrix wiring. `audit_revision.py` checks old-file
hashes, exact switch geometry, one assembly side, two copper layers and via
drills outside SMT lands. Rebuild geometry after any PCB serialization change;
the collision report checks the PCB's SHA-256.

`build_board.py` **replaces** the current PCB with an unrouted placement from
v7.4 and the v6 module footprint. `build_schematic.py` makes the three schematic
sheets and footprint paths. `route_board.py` exports/imports Freerouting files;
`finish_routing.py` is a checked A* fallback for incomplete connections. The
completed route needed vertical preferred direction on F.Cu and horizontal on
B.Cu, explicit optical-hole keepouts, nine checked final connections and trimming
of three unused stubs. Router output alone does not establish a manufacturable board.

The case generators are revision-local copies of the shared tools, extended
with clone/cable envelopes, a plug-floor relief and rear receptacle cradle.
They use conservative geometry and do not substitute for actual-part measurements.
`fit_preview.py` regenerates the module/cable OpenSCAD views from the exported
geometry and fit report without rerunning the solid modelling operations.
`usb_fit.py` assesses the reported housing against the current socket axis,
floor clearance and a rearward-relocation trial. `build_fit.py` additionally
intersects the reported housing with the PCB/case and exports its separate gauge.
The passing main assembly uses a 4.5 mm target; the reported 6.6 mm cable fails.
