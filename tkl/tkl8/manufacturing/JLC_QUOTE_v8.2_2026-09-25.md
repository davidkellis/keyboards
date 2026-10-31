# JLCPCB v8.2 quote — 2026-09-25

Five fully populated electronics boards: **$372.59 including the displayed
DHL DDP shipping estimate and $3.31 rail removal**, before tax or engineering
adjustments. The previous v8.1 equivalent was $448.54: **$75.95 saved**.
The quote is saved in the signed-in cart; it has not been purchased, inventory
is not reserved, and production is not released.

| USD, five assembled boards | v7.1 | v7.2 | v8.1 | v8.2 |
| --- | ---: | ---: | ---: | ---: |
| PCB fabrication | 151.75 | 104.86 | 151.75 | 104.86 |
| Assembly including parts | 198.69 | 169.63 | 248.11 | 219.05 |
| Merchandise | 350.44 | 274.49 | 399.86 | 323.91 |
| DHL DDP shipping estimate | 45.37 | 45.37 | 45.37 | 45.37 |
| Rail removal, after review | 3.31 | 3.31 | 3.31 | 3.31 |
| Comparable total | **399.12** | **323.17** | **448.54** | **372.59** |

Shipping was checked with only the relevant batch selected. If both batches
are wanted, the carrier selector also offers UPS DDP at $78.24 for ten boards
combined, versus $90.74 for the two separate DHL shipments. The combined
$683.26 figure is an arithmetic estimate including both rail-removal fees,
not a completed combined-order quote; the default combined DHL quote is higher. JLC's cart subtotal
omits the $3.31 rail-removal charge until review. Tax, assembly-remark adjustments
and any additional fixture charge are not included. In particular, v7's reverse
LED fixture is explicitly requested for review and has no automatic price yet.

## Why the price fell

The 0.30 mm drill revision removes $22.60 small-hole, $19.77 optional Kelvin
and $4.52 higher-Tg material charges: $46.89 less for fabrication. Epoxy fill/cap,
ENIG, the four-layer stack and ordinary flying-probe electrical testing remain.
The JSCJ diode line is $10.5996 for 438 pieces including assembly attrition,
versus $39.6720 for the former Diodes Inc part. Assembly totals drop $29.06
including line-item rounding. All 31 BOM groups and 142 placements remain.

V8's second assembly side still costs $49.42 more overall than v7. A large
further reduction would require changing the controller/assembly architecture
or choosing some user assembly. The current nRF52840 is Standard Only.

## Saved configuration and evidence

PCB reference `Y6-5054573A`; PCBA reference `SMT026092563153-5054573A`.
Use the new [Gerber ZIP](tkl-v8.2-gerbers.zip), [BOM](jlcpcb-bom.csv) and
[CPL](jlcpcb-cpl.csv) together; the former v8.1 files are archived.
The new quotes coexist with the older comparison drafts in the cart.
Only v7.2 is selected after the comparison; older drafts are unselected.

See [the evidence record](quote-v8.2-2026-09-25/record.json), saved settings,
complete charge breakdown, BOM matches and placement screenshots beside it.
Exact manufacturer/part IDs were checked for every BOM group; USB J3 was
explicitly selected after upload. Side/count and gross placement checks pass;
final factory pin/polarity review is still required. Confirm Production File and
Confirm Parts Placement are enabled with manual approval selected.

Zero ERC/DRC errors or warnings, zero open connections and zero schematic-parity
issues were verified for both revisions. The 86 key positions, all component
holes, CPL coordinates and mechanical envelopes match the previous revision.
Existing fit, battery, firmware and bench-test holds are unchanged.
