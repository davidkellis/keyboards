# v7 tooling

Use KiCad 10 and its matching system Python with `pcbnew`, plus `sexpdata`.
One way to retain the system KiCad bindings is:

```sh
/usr/bin/python3 -m venv --system-site-packages .venv-kicad
.venv-kicad/bin/pip install -r tkl/tkl7/scripts/requirements.txt
```

**The placement builder discards routing.** Keep the checked-in finished PCB
for normal work. Rebuild only in a branch or with a clean backup:

```sh
python tkl/tkl7/scripts/build_board.py
python tkl/tkl7/scripts/route_usb.py
python tkl/tkl7/scripts/route_power.py
python tkl/tkl7/scripts/routing_exchange.py export /tmp/v7.dsn
java -Xmx6g -jar /path/to/freerouting.jar \
  -de /tmp/v7.dsn -do /tmp/v7.ses -da \
  --gui.enabled=false --api_server.enabled=false \
  --router.layers.routable=true,false,true,true \
  --router.fanout.enabled=false --router.optimizer.enabled=false -mp 12 -mt 2
python tkl/tkl7/scripts/routing_exchange.py import /tmp/v7.ses
```

**Autorouting does not guarantee completion.** The checked-in board required
additional local fanouts and routing after Freerouting. Resolve remaining
connections and DRC in KiCad, preserving the locked reference and USB copper.
The scripts above alone do not recreate the finished routing. Then apply
assembly metadata and rebuild the matching schematic:

```sh
python tkl/tkl7/scripts/finalize_board.py
python tkl/tkl7/scripts/build_schematic.py
python tkl/tkl7/scripts/sync_nc_nets.py
python tkl/tkl7/scripts/validate.py
python tkl/tkl7/scripts/export_manufacturing.py
```

Freerouting 2.4.1 is used locally. Its report can flag false hole-clearance
errors for already connected via-in-pad geometry and duplicate USB-C lands.
KiCad DRC on the imported, zone-filled PCB is the release check. Never waive
KiCad errors on the basis of a router claiming that it finished.

The routing exchange helper corrects a KiCad export limitation: copper-only
B.Cu exclusions become all-routing obstacles in DSN. The PCB retains those
exclusions. In1.Cu is reserved for GND; the manually routed USB pair uses F.Cu.
The reference circuit and USB tracks are locked before the exchange.

The schematic builder retains footprint UUID paths and emits three sheets.
`sync_nc_nets.py` then adds KiCad's generated one-pad NC net names so the PCB
also passes schematic parity checks. `validate.py` runs independent ERC/DRC
and netlist export and checks the matrix and critical circuit assignments.

`manufacturing/parts.json` is the assembly selection source. Finalization adds
its MPN/LCSC fields to the PCB; schematic generation carries them into each
symbol. Export rejects missing/duplicate catalog references, DNP placements,
inconsistent position coordinates and any remaining validation warnings or
errors. It generates Gerbers, separate plated/nonplated drill data, BOM/CPL,
schematic/assembly PDFs and source checksums. It does not place an order or
verify JLC's per-part rotation conventions.

`route_usb.py` and `route_power.py` are placement-stage helpers, not idempotent
edits to a finished board. Do not run them on the checked-in routed design.
