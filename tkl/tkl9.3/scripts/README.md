# Rebuilding v9.3 mechanics

v9.3 closes the plate's pin clearances underneath and adds six flush translucent
LED inserts. Its base is identical to v9.2. Its electrical sources are exact
copies of v9.1. Use the prior manufacturing handoff; no PCB redesign or rerouting
is part of this revision.

The available CadQuery environment is `/tmp/keyboards-fit-work/venv`; KiCad
`pcbnew` uses `/usr/bin/python3`. These are local environment paths, not bundled
dependencies.

1. `/usr/bin/python3 tkl/tkl9.3/scripts/export_geometry.py tkl/tkl9.3`
2. `/tmp/keyboards-fit-work/venv/bin/python tkl/tkl9.3/scripts/build_fit.py tkl/tkl9.3`
3. `/tmp/keyboards-fit-work/venv/bin/python tkl/tkl9.3/scripts/build_print_fit.py`
4. `/tmp/keyboards-fit-work/venv/bin/python tkl/tkl9.3/scripts/check_fit.py tkl/tkl9.3`
   Also run `/tmp/keyboards-fit-work/venv/bin/python tkl/tkl9.3/scripts/check_surface.py`.
5. `/tmp/keyboards-fit-work/venv/bin/python tkl/tkl9.3/scripts/check_usb_surround.py`
6. `/tmp/keyboards-fit-work/venv/bin/python tkl/tkl9.3/scripts/mount_preview.py`
7. `/tmp/keyboards-fit-work/venv/bin/python tkl/tkl9.3/scripts/layout_preview.py`
8. `/tmp/keyboards-fit-work/venv/bin/python tkl/tkl9.3/scripts/render_previews.py`
9. `/usr/bin/python3 tkl/tkl9.3/scripts/check_revision.py`
10. `/tmp/keyboards-fit-work/venv/bin/python tkl/tkl9.3/scripts/package_fit.py`

The base walls now reach the original upper surface. The plain 1.5 mm plate
retains the existing switch apertures, screw seats and spacers. Its front border
is trimmed 0.3 mm to provide a fitting gap. `recessed_plate` in `fit-config.json`
records this change. The older `cover_*` dimensions remain stack references that
fix the same outside heights; they no longer generate a cover. The inherited
`integrated_upper` configuration supplies the unchanged floor rib settings.

`surface_finish` defines blind pocket depth, the 0.9 mm roof, 1.0 mm maximum
top-side pin projection and the circular diffuser dimensions. `export_geometry`
models the shorter pin tails as a required manual assembly operation; it does
not claim that JLC supplies trimmed connector leads. The controller must be
installed before the closed plate. Diffusers are placed in the assembly STEP
and checked against the plate, PCB, case, switches and electronics. The STL
section audit independently confirms a closed top skin over each clearance
region and verifies that pockets remain open beneath that skin.

The build validates the rim's clearance and checks lifted PCB/plate samples to
detect trapping overhangs. It also checks the existing modeled collisions,
hardware and battery bay. The `upper` names on older coupons are kept for
continuity, but those samples now contain just the plain plate.

`check_revision.py` compares every preserved v9.2 file with its original hash
and confirms unchanged electrical sources, BOM, CPL, mount hardware, battery
reserve and footprint. It does not rerun electrical verification of identical
sources or claim new physical testing.
