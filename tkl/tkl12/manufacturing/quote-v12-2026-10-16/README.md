# V12 JLCPCB quote — 2026-10-16

The signed-in checkout estimate for **five PCBs, all five assembled**, is
**$180.26 USD delivered ($36.05 per board)** using lead-free HASL, Economic
bottom-side assembly and UPS Express Saver DDP. No order has been submitted or
paid. Engineering-review extras remain unpriced.

| Cost for five assembled boards | USD |
| --- | ---: |
| PCB fabrication | $29.05 |
| Components | $25.78 |
| Assembly, setup, stencil and related fees | $38.56 |
| Merchandise subtotal | $93.39 |
| UPS Express Saver DDP shipping | $49.73 |
| Checkout customs duties and taxes | $37.14 |
| **Displayed delivered total** | **$180.26** |

The saved V11 estimate from the same date was $179.80 delivered. V12 is **$0.46
more delivered**, with an unchanged $29.05 PCB fabrication price. Its merchandise
subtotal is $0.34 higher: components increase from $25.45 to $25.78 and placement
cost increases by $0.01. The added switch holes/slots do not increase the
displayed fabrication price in this quote. Prices and inventory can change.

## Review the saved draft

[Open the JLCPCB cart](https://cart.jlcpcb.com/shopcart/cart) and find
**tkl-v12-gerbers_Y15**, PCB **Y15-5054573A**, linked PCBA
**SMT026101665061-5054573A**. JLC counts the PCB and its assembly as two linked
checkout items. Only this V12 group was selected for the checkout estimate.
The V10 Y12 and V11 Y14 drafts remain intact and unselected.

The private file identifier in the pre-cart editor URL is redacted in
`hasl-economic/quote-url.txt` and `hasl-economic/record.json`. Use Product Details
in the cart to review the persistent draft. Checkout was
left at its review stage. **Submit Order was not clicked.**

## Configuration and scope

- Five PCBs and five assemblies, one design, single-board delivery format.
- Two copper layers, 350.76 × 129.19 mm, standard TG135 FR-4, 1.6 mm, green mask,
  white silkscreen, 1 oz outer copper, **lead-free HASL**.
- Standard tented 0.3 mm vias, regular outline tolerance, ordinary flying-probe
  bare-board electrical testing; no premium via process or Kelvin test.
- **Economic assembly, Bottom only**, ten exact LCSC purchasing groups and
  **106 placements per board**, including all ten LTW-C230DS LEDs.
- All matched parts are listed RoHS compliant. No component substitutions or
  omissions were made. All ten groups are selected in the saved quote.
- **High-temperature lead-free SAC305 paste**. The site’s tooltip identifies
  Sn96.5%, Ag3.0%, Cu0.5%. The saved remark explicitly requires lead-free solder
  for both SMT and the J1 through-hole connector.
- Normal/free build time: PCB 24 hours for the assembly order; assembly 2–3
  days. UPS’s shipping estimate is 2–4 business days after shipment.
- Production-file and parts-placement confirmation are retained ($1.05 and
  $0.45), with automatic confirmation disabled in their dialogs.
- No cleaning, coating, storage, photo confirmation, functional testing or
  separate stencil order. Required Economic nitrogen reflow remains selected.
- **Paid rail removal is off.** JLC supplies tooling. Any attached rails may
  need user removal before case installation; final rail geometry is subject
  to production-file review.

The customer supplies and installs the clone controller, key switches, battery,
case, keycaps, acrylic optics and mechanical hardware. These are outside the
PCB/PCBA estimate. Changing the hand-installed switch family does not change
this factory assembly BOM.

## Unpriced reverse-LED handling

JLC flags **C575513 / LTW-C230DS** as difficult to process. The quote says the
assembly remark is **“Quote after review”**, and explicitly excludes advanced
option charges from its displayed total. The saved instructions request correct
reverse orientation and a quote for any mandatory fixture/handling charge before
production. Thus **$180.26 is an estimate before any such additional charge**,
not a guaranteed final all-in price. No invented handling allowance is included.

## Manufacturing breakdown

PCB: engineering $4.00, surface finish $2.10, board $21.90 and production-file
confirmation $1.05; **$29.05** total.

PCBA: setup $8.24, stencil $1.55, components $25.78, extended-components fee
$21.63, SMT placement $1.97, placement confirmation $0.45, hand soldering $3.61,
manual assembly $0.20 and nitrogen reflow $0.91; **$64.34** total. Panel and
large-size fees are $0.00. PCBA excluding components is $38.56.

Shipping was priced in checkout for the existing saved destination; personal
address details were omitted from saved evidence. DHL DDP was also checked:
$58.26 shipping + $40.21 duties/taxes gives **$191.86** delivered. UPS DDP gives
the selected **$180.26** estimate. The freight-account option has no quoted rate
and was not selected. No checkout discount was displayed.

## Files and checks

- `tkl-v12-jlc-upload-bundle.zip` and `upload/`: the exact immutable V12 Gerber,
  BOM, CPL and ordering/fabrication snapshots used for this quote.
- `uploaded-file-hashes.json`: SHA-256 hashes checked against current exports.
- `verification.json`: quantities, exact selected matches, assembly side,
  finish, solder, no rail removal and cost arithmetic checks.
- `hasl-economic/configured.json`: selected fabrication and assembly settings.
- `hasl-economic/bom-matches.json`: ten selected exact matches with prices.
- `hasl-economic/final-quote.txt` and `.png`: live manufacturing breakdown.
- `hasl-economic/checkout-final-summary.png`: final checkout totals, cropped
  to exclude personal information.
- `hasl-economic/record.json`: machine-readable totals and persistent draft IDs.

Pre-upload handoff checks passed: 12 mounting drills, ten optical apertures,
172 shared locating slots, 172 added Gateron contact drills, 106 bottom-side
placements, matching archives and current source hashes. PCB, manufacturing
exports and earlier revisions were not changed to obtain this quote. A quote
does not establish physical, electrical, optical or mechanical prototype fit.
