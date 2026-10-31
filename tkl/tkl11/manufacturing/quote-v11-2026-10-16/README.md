# V11 JLCPCB quote — 2026-10-16

The lowest displayed delivered estimate for **five PCBs, all five assembled**, is
**$179.80 USD ($35.96 per board)** using lead-free HASL and Economic bottom-side
assembly. This is a live checkout estimate, before any engineering-review extras.
No order has been submitted or paid.

| Cost for five boards | USD |
| --- | ---: |
| PCB fabrication | $29.05 |
| Components | $25.45 |
| Assembly, setup, stencil and related fees | $38.55 |
| Merchandise subtotal | $93.05 |
| UPS Express Saver DDP shipping | $49.73 |
| Checkout customs duties and taxes | $37.02 |
| **Displayed delivered total** | **$179.80** |

All prices were read from the signed-in JLCPCB quote and checkout pages for the
saved destination. Personal address details are omitted from the evidence files.
Taxes and shipping were compared in checkout, rather than inferred from the PCB
quote's country-level shipping estimate. No applicable discount was displayed in
the checkout review used for this estimate.

## Saved draft

[Open JLCPCB cart](https://cart.jlcpcb.com/shopcart/cart) and review
**tkl-v11-gerbers_Y14**, PCB **Y14-5054573A**, PCBA
**SMT026101663623-5054573A**. The private file identifier in the original
pre-cart editor URL is redacted in `hasl-economic/quote-url.txt` and
`hasl-economic/record.json`. That transient URL did not reopen the saved draft
correctly after saving to cart. Use the cart's Product Details for review.

The V10 Y12 draft remains intact and unselected. Only the V11 PCB/PCBA group was
included in this checkout estimate; JLC counts the PCB and its linked assembly
as two checkout items. Nothing was purchased.

## Configuration

- Five PCBs and five assemblies, one design, single-board delivery format.
- Two copper layers, 350.76 × 129.19 mm, 1.6 mm standard TG135 FR-4, green mask,
  white silkscreen, 1 oz outer copper.
- Lead-free HASL, tented standard 0.3 mm through vias, standard outline tolerance,
  ordinary flying-probe electrical test; no premium material or via process.
- Economic assembly, bottom only; all **106 placements per board** selected.
- All ten exact BOM groups match the exported LCSC identifiers and are listed
  RoHS compliant. All ten LEDs are populated; no substitution or omitted parts.
- High-temperature solder paste. The saved assembly instructions explicitly
  require **lead-free solder for SMT and J1 through-hole joints**.
- Normal/free build time: PCB 24 h for the PCBA order, assembly 2–3 days; no paid
  acceleration. Delivery estimate is 2–4 business days after shipment for UPS.
- Production-file and placement confirmation retained ($1.05 and $0.45);
  automatic confirmation disabled in the corresponding quote dialogs.
- No cleaning, coating, storage, photo confirmation, extra functional testing or
  separate stencil purchase. Required Economic nitrogen reflow remains selected.
- **Paid rail removal is off.** Tooling is added by JLC. Any attached tooling
  rails must be removed by the user as needed before installing the PCB in its
  case; final rail shape is subject to JLC production-file review.

The customer supplies and installs the clone controller module, key switches,
battery, USB extension, acrylic optical parts, case, keycaps and hardware.
These items are outside this PCB/PCBA quote.

## Unresolved engineering-review charge

JLC flags LTW-C230DS (C575513) reverse-mount LEDs as difficult to process and
states that advanced assembly options may add charges after review. The final
quote explicitly labels the assembly remark **“Quote after review”** and excludes
such charges from its Total Price. The saved remark requests correct reverse
orientation and asks JLC to quote any required fixture/handling charge before
production. Therefore **$179.80 is not a guaranteed final all-in price**; any
reviewed handling/fixture charge and its associated taxes remain additional.
No arbitrary allowance has been invented for that charge.

## Shipping comparison

| Carrier | Shipping | Duties / taxes | Delivered estimate |
| --- | ---: | ---: | ---: |
| UPS Express Saver DDP | $49.73 | $37.02 | **$179.80** |
| DHL Express DDP | $58.25 | $40.09 | $191.39 |
| FedEx Express DDP | $77.01 | $50.31 | $220.37 |

These are the prepaid carrier options shown for the saved address. Customer
freight-account shipping is not a costed alternative and was not selected.

## Manufacturing breakdown

PCB: engineering $4.00, surface finish $2.10, board $21.90,
production-file confirmation $1.05; total $29.05.

PCBA: setup $8.24, stencil $1.55, components $25.45, extended-components fee
$21.63, SMT assembly $1.96, placement confirmation $0.45, hand soldering $3.61,
manual assembly $0.20, nitrogen reflow $0.91; total $64.00. Panel and large-size
fees are $0.00. Assembly excluding component purchase is $38.55.

For comparison, the previous V10 estimate saved on 2026-09-29 was $163.83
including shipping and checkout taxes, with $80.80 merchandise. This V11 quote
is $15.97 higher delivered and $12.25 higher for merchandise. These are quotes
from different dates, so component prices, shipping and tax calculations can
also differ. The V11 PCB fabrication cost remains $29.05.

## Bundle and evidence

`tkl-v11-jlc-upload-bundle.zip` contains an immutable snapshot of the exact V11
Gerbers ZIP, BOM, CPL and fabrication/ordering notes uploaded for this quote.
`uploaded-file-hashes.json` records their SHA-256 hashes. Source revisions and
manufacturing exports were not changed by quoting.

`hasl-economic/` contains the configured quote, all selected BOM matches,
placement previews, saved cart parameters and BOM, manufacturing breakdown,
carrier comparisons and cropped checkout total screenshots. The saved BOM has
10 selected groups and no unselected parts. `verification.json` records checks.

The board passed the existing handoff check and source/ZIP hash comparison
before upload. This quote is not a physical validation of the prototype's
optical, electrical, RF or mechanical performance.
