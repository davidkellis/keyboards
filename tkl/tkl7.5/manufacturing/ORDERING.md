# Quoting v7.5

Upload `tkl-v7.5-gerbers.zip`; select two layers, 1.6 mm, OSP, ordinary tented
through vias and lead-free assembly. Request five boards and five bottom-side
assemblies when comparing against the prior five-board batch. Upload
`jlcpcb-bom.csv` and `jlcpcb-cpl.csv` on the assembly stage.

The expected import is **seven BOM groups / 102 placements per PCB**. U1 and
SW1–SW86 must be absent from the factory assembly list: the user installs these.
Only the carrier's small components and battery connector are ordered here.

Compare complete Economic and Standard totals after component matching. Do not
assume Economic is eligible or less expensive, and retain reverse-LED fixture
review. Use standard lead time and ordinary electrical testing. Avoid filled/
capped vias, special via plating, Kelvin testing or ENIG upgrades unless the
fabricator identifies a concrete need. Keep placement/file review enabled for
this unbuilt prototype. Request rail removal to preserve case fit.

No live quote, stock reservation, cart update, purchase or production release
has been performed for v7.5. The old $300.22 v7.4 estimate is not a v7.5 quote.
Before production, resolve the actual clone/cable dimensions, charging/temperature
protection, firmware and mechanical fit holds in `BRINGUP.md` and the case guide.
