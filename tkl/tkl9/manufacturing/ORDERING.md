# Ordering the current v9 prototype

The current unpaid JLC cart has one batch: **Y11-5054573A**, paired with
**SMT026092661681-5054573A**, for five boards and five bottom-side assemblies.
It uses **two layers, 1.6 mm, lead-free HASL, Economic assembly, high-temperature
lead-free solder, green mask, white silkscreen, 1 oz copper and ordinary tented
through vias**. The live order remark explicitly overrides OSP in the original
uploaded manufacturing notes. The PCB layout and upload files are unchanged.

**Depanel boards & edge rail before delivery: No.** The $3.31 after-review removal
charge has been removed. Economic assembly does not normally need added rails;
finished size remains 350.76 × 129.19 mm. Preserve that outline if engineering
proposes any processing changes. File and component placement review remain enabled.

The expected factory assembly is **seven BOM groups / 99 placements per PCB**.
The user installs U1 and all 83 key switches. Only the carrier's small components
and battery connector are ordered here. Keep matched `tkl-v9-gerbers.zip`,
`jlcpcb-bom.csv` and `jlcpcb-cpl.csv` together if making a fresh quote.

Current merchandise subtotal is **$80.34**. Prior checkout totals before rail
removal were **$163.20 UPS** or **$165.30 DHL**, including displayed shipping and
customs duties/taxes; checkout prices can change. Reverse-LED handling still says
**Quote after review**. Its eventual charge and any related tax remain unknown.
See [quote evidence](quote-v9-2026-09-26/README.md). No order or payment was submitted.

Fresh [pre-order checks](../validation/preorder-2026-09-26/README.md) passed ERC,
DRC, netlist agreement and upload integrity. The actual clone, custom firmware,
mechanical fit, BLE performance and charging behavior are not yet validated.
Use the new [plastic fit kit](../case/print-fit/tkl-v9-easy-fit.zip) and follow
[bring-up](../BRINGUP.md) before treating this prototype as a working design.

Avoid filled/capped vias, special via plating, Kelvin-test or ENIG upgrades unless
engineering identifies a concrete need. The original OSP/Standard quote is kept
only as a historical price comparison and is no longer in the cart.
