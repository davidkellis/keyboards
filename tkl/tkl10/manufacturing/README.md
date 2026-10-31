# v10 manufacturing files

Use this revision's [Gerber ZIP](tkl-v10-gerbers.zip),
[BOM](jlcpcb-bom.csv) and [CPL](jlcpcb-cpl.csv) together. The
[prototype handoff](tkl-v10-prototype-handoff.zip) also includes the schematic,
assembly drawings and fabrication/ordering notes.

The board has 86 switches with the user-installed clone between Esc and F1,
twelve non-plated M2 mounting holes, and 102 bottom-side factory placements
in seven BOM groups. Three key/diode pairs return and H9/H12 move relative to
v9.1. Use the matching v10 mechanical parts.

`manifest.json` records the exact source hashes. `matrix-map.csv` gives the
86 matrix addresses and physical positions; `../reference/firmware-pins.csv`
gives the clone GPIO assignments. The custom keyboard firmware is not built
by these files.

ERC, DRC, schematic/netlist parity and circuit-invariant checks passed with
zero errors, warnings or unconnected items. The separate export check verifies
the twelve mounting drill coordinates, BOM/CPL count and archive hashes.
These checks are not prototype hardware, charging or radio tests.

See [ORDERING.md](ORDERING.md) for lead-free HASL, lead-free solder and
bottom-only assembly settings. No v10 live quote or order has been created;
stock, reverse-LED handling and total delivered cost need a new factory quote.
