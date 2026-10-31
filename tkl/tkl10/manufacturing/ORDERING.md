# Ordering v10

This is a **new revision**, not the existing v9 cart item. No v10 order or live
quote has been created. v9 prices are historical and do not establish this
revision's current price, stock, shipping or reverse-LED charges.

Upload these three files together:

1. `tkl-v10-gerbers.zip` for PCB fabrication, including the relocated mounting holes.
2. `jlcpcb-bom.csv` for component selection.
3. `jlcpcb-cpl.csv` for component placement.

Use two layers, 1.6 mm FR-4, green mask, white silkscreen, 1 oz copper and lead-free
HASL. Request Economic **bottom-only** assembly with lead-free high-temperature
solder. Expected assembly: **seven BOM groups, 102 placements per board**. The
user installs the clone and the 86 switches. Compare current pricing only after
all parts and assembly processes are matched.

Use normal 0.30 mm minimum-drill through vias, tented on both sides, without
filled/capped-via processing, special via plating, a Kelvin test or an ENIG
upgrade. Keep ordinary PCB electrical testing and file/placement review.

Set **Depanel boards & edge rail before delivery: No** for the initial quote.
If engineering requires rails, review their removal method and finished outline;
rails cannot remain attached inside this case. Reverse-LED handling and any
through-hole work must be included in the factory quote.

The v10 PCB and case mount pattern must be used together; an old v9 PCB has no
matching mounting holes. Do not send the compensated plastic STL gauges to a
PCB fabricator. Those holes are intentionally larger for a printer fit trial.

Before ordering, print the mounting sample and switch/module corner sample in
`../case`. Check real hardware and plate-mount stabilizer travel. A clean DRC
cannot establish physical fit, firmware behavior, charging behavior or RF range.
See `../BRINGUP.md` and `../validation/summary.json`.
