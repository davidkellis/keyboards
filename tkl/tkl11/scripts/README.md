# V11 source and checks

Use the final routed `kicad/keyboard.kicad_pcb` for exports. Do not run a reset
builder merely to regenerate manufacturing files.

The design was derived in isolated steps: `build_v11.py` resets from preserved
v10, `finish_board.py` shortens the switch loop/adds the bleeder, and
`relocate_driver.py` moves the complete driver group away from the case's rear
support lip. `escape_driver.py` supplies standard via fanout for the four
non-switch driver pins. `move_sense_resistor.py` places R10 beside C1. These are **one-time mutations of their preceding stage**, not
idempotent export commands. Routing runs between these transformations. Their
final result is already in the checked PCB. `move_led1.py` records the subsequent
single-LED move. `apply_staggered_led_layout.py` applies the later shared-guidance
layout to the archived pre-staggered board, moving eight LEDs and updating their
series order. These are also one-time transforms; use the routed board for exports.
`escape_led2.py` adds the conventional via outside LED2's cathode land after
opening a small gap in COL7's old route; both nets are routed and checked afterward.
`escape_led10.py` supplies a matching ordinary via outside LED10's anode land,
then the remaining link is routed from the front. No via holes enter solder lands.
`finish_routing.py` performs
DRC-gated two-layer routing; `cleanup_floating_branches.py` and
`clean_mount_routing.py` trim only redundant copper with connectivity rollback.

The working environment for this revision is `/tmp/tkl-v11-env/bin/python`,
Python 3.14 with system KiCad 10 pcbnew, sexpdata, numpy, shapely, manifold3d,
trimesh and Pillow. Paths are local environment details, not bundled dependencies.

Normal electrical checks and export, without resetting the board:

```sh
/tmp/tkl-v11-env/bin/python tkl/tkl11/scripts/validate.py
/tmp/tkl-v11-env/bin/python tkl/tkl11/scripts/audit_revision.py
/tmp/tkl-v11-env/bin/python tkl/tkl11/scripts/export_geometry.py tkl/tkl11
/tmp/tkl-v11-env/bin/python tkl/tkl11/scripts/check_mechanical.py
/tmp/tkl-v11-env/bin/python tkl/tkl11/scripts/build_artifacts.py
/tmp/tkl-v11-env/bin/python tkl/tkl11/scripts/export_manufacturing.py
/tmp/tkl-v11-env/bin/python tkl/tkl11/scripts/check_handoff.py
```

If electrical symbols/net assignments change, deliberately regenerate with
`build_schematic.py` followed by `sync_nc_nets.py` before checking/exporting.
The custom TPS61169 symbol pins are independently compared with explicit TI
pin assignments in `validate.py`.

`audit_revision.py` compares original interfaces with v10, all factory sides,
current-sense and string topology, and all 386 possible six-through-ten-source
wire-bypass configurations. `check_mechanical.py` checks all ten LED envelopes
and seven driver component envelopes against the actual v10 hidden-mount case, battery and nut
carrier assembly meshes with 0.4 mm clearance. It does not certify acrylic plate
mounting, real component fit, switches, lighting or firmware.
