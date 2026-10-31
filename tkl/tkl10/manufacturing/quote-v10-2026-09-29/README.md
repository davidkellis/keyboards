# v10 live JLCPCB quotes — 2026-09-29

**Lowest displayed delivered total: $163.83 for five v10 assembled carrier
PCBs ($32.77 each), using lead-free HASL and Economic bottom-side assembly.**
OSP with Standard assembly is $191.87 delivered, a $28.04 increase.
Both are fresh website quotes with the exact v10 Gerber/BOM/CPL files, not
projections from v9. Neither order was submitted or paid.

| USD for five boards | HASL / Economic | OSP / Standard |
| --- | ---: | ---: |
| PCB fabrication | 29.05 | 28.55 |
| Components, all seven groups | 22.61 | 22.69 |
| Assembly/setup/stencil/handling shown | 29.14 | 50.06 |
| Merchandise subtotal | **80.80** | **101.30** |
| UPS Express Saver DDP shipping | 50.25 | 50.61 |
| Checkout customs duties and taxes | 32.78 | 39.96 |
| **Displayed checkout total** | **163.83** | **191.87** |
| Per assembled carrier, rounded | **32.77** | **38.37** |

**Unresolved charge:** both quotes label the assembly remark “Quote after
review.” Reverse-mount LED handling or fixtures may therefore add a charge,
and associated taxes may change. The displayed checkout total is not a
factory-reviewed final invoice. No rail-removal charge was requested or listed.

Both configurations request lead-free SMT and J1 through-hole solder. All
seven matched part descriptions state ROHS; no stock shortfall was shown.
There are 102 placements per board: 86 diodes, six reverse LEDs, seven
resistors, one MOSFET, one slide switch and one JST connector. The exact BOM
references and selected parts were checked against the uploaded v10 files.
No substitutions, rotations or placements were changed during quoting.

The clone controller, 86 key switches, battery, printed case/plate, keycaps,
stabilizers, screws and other mechanical hardware are customer supplied and
installed. Firmware programming and keyboard functional testing are excluded.
At the user's reported $4 per clone, buying five clones would add about $20
before any module shipping or tax.

## Saved quotes

- [HASL / Economic quote](https://cart.jlcpcb.com/smt-order/?pcbFileNo=REDACTED):
  PCB **Y12-5054573A**, assembly **SMT026092962803-5054573A**.
- [OSP / Standard quote](https://cart.jlcpcb.com/smt-order/?pcbFileNo=REDACTED):
  PCB **Y13-5054573A**, assembly **SMT026092962834-5054573A**.
- [JLCPCB cart](https://cart.jlcpcb.com/shopcart/cart).

At the user’s request, only **v10 HASL/Economic Y12** remains in the cart,
selected for checkout. The OSP/Standard Y13 comparison and older v9/Y11 item
were removed. The remaining single order contains linked PCB and assembly
lines, each with quantity five. OSP evidence below is retained only as a
historical comparison; it is no longer a cart option. See `cart-final.json`,
`cart-final.txt` and `cart-final.png` for the verified final cart state.

## Shipping comparison at the saved destination

| Displayed delivered total | HASL / Economic | OSP / Standard |
| --- | ---: | ---: |
| UPS Express Saver DDP | 163.83 | 191.87 |
| DHL Express DDP | 165.93 | 193.98 |
| FedEx Express DDP | 208.50 | 236.55 |

These are actual-address checkout totals, including the separate checkout
customs/tax line. The country-level shipping preview in the cart is not the
delivered price. No coupon was applied; checkout preview did not expose a
coupon application control before Submit Order.

## Configuration and evidence

Two layers, 1.6 mm FR-4, green mask/white silkscreen, 1 oz outer copper,
0.30 mm minimum-drill through vias, tented, ordinary PCB electrical test,
production-file and placement confirmation, single-side bottom assembly,
high-temperature solder paste with explicit lead-free solder requirement,
and no paid depaneling. OSP/Standard adds factory tooling rails to
350.76 × 139.19 mm; the required finished outline is 350.76 × 129.19 mm.
Any retained rails must be removed before installing the PCB in the case.

The quote includes all six reverse-mount LTW-C230DS LEDs and J1's through-hole
assembly. The user-installed module and switches are absent from the factory
BOM by design. CAD and placement previews do not establish physical hardware
fit, charging behavior, RF range or firmware function; see the v10 bring-up
and fabrication documents.

Each configuration subdirectory contains the selected services, matched BOM,
placement preview, manufacturing breakdown and sanitized checkout/carrier
summaries. `record.json` files include hashes of the exact three uploads.
Shipping addresses and credentials were not stored in this report.
