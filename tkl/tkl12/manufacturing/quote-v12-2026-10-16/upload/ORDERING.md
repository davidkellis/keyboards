# V12 JLC upload settings

Use `tkl-v12-gerbers.zip`, `jlcpcb-bom.csv` and `jlcpcb-cpl.csv` from this
directory. Do not mix Gerbers or placement files from an older revision.

- Five PCBs and five assemblies for the intended quote.
- Single design, single PCB; two copper layers; 1.6 mm FR-4; green solder mask.
- Lead-free HASL surface finish; lead-free assembly solder.
- Economic assembly, **Bottom only**, normal build time.
- Standard material, copper weights and fabrication tolerances; tented standard
  vias, no filled/capped vias, no optional Kelvin test or expedited service.
- All ten LEDs fitted. LED7–LED10 are removed/bypassed by the user only if the
  six-source optical experiment succeeds. Do not mark them DNP without bridges.
- User fits the controller clone, all key switches, battery and mechanical parts.
- Confirm reverse-mount LED fixture/handling acceptance and charge in the actual
  quote. One-sided placement does not remove special reverse-LED handling.
- Leave paid rail removal unselected for the initial quote, as previously
  requested; review actual rail geometry against the case before purchase.

Stock and lead time are not reserved. BOM identifiers are design selections, not
a live stock or price guarantee. The component BOM and assembly count match V11; the new holes need a
new fabrication quote. No order is authorized or placed by these exports.

Check that the Gerber preview includes both shared side slots at every key and
two extra Gateron contact holes. These do not add any factory components.
Read SWITCHES.md before selecting a non-Kailh-V2 plate/keycap combination.
