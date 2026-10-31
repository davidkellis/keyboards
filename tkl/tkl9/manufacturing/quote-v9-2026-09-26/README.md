# Current cart: v9 without rail removal — 2026-09-26

The revised **Y11-5054573A** / **SMT026092661681-5054573A** batch replaces Y10.
The cart contains only this one five-board batch. Rail/depanel removal is **No**;
the prior $3.31 after-review charge is absent. Assembly notes explicitly retain
lead-free HASL, lead-free solder, reverse-LED review, the finished outline, and
customer installation of the module and key switches. Nothing was ordered or paid.

Merchandise remains **$80.34** ($29.05 PCB + $51.29 assembly); the old rail charge
was outside that subtotal. Saved evidence is in [no-rails](hasl-economic/no-rails/).
The previous UPS checkout was $163.20 and DHL $165.30, including displayed freight
and duties/taxes. Those shipping figures were recorded before this cart revision;
checkout determines the current total. The separate LED assembly remark remains
**Quote after review** and any resulting handling charge is still unknown.

JLC's [capabilities table](https://jlcpcb.com/capabilities/pcb-assembly-capabilities)
says rails are not necessary for Economic assembly. The quoted Economic board is
350.76 × 129.19 mm, with no added rails. If engineering proposes rails, resolve
that change before production so the finished board fits the case.

The comparison below preserves the earlier quotes **with rail removal selected**;
its $166.51 total is superseded for the current cart. Older OSP/Y10 cart items
are no longer present.

# Live v9 JLCPCB quotes — 2026-09-26

**Lowest complete configuration checked: $166.51 for five assembled v9 carrier
boards**, including shipping, checkout's displayed customs duties/taxes, and the
separately listed rail-removal charge. This uses **lead-free HASL and Economic
bottom-side assembly**, with the exact existing v9 Gerbers, BOM and CPL.
The original OSP/Standard configuration is **$194.45** on the same basis.
The saving is **$27.94 per batch**, with no PCB layout or LED changes.

These are historical comparison quotes. The cart now contains only the revised
HASL/Economic Y11 batch described above. Checkout was opened to price delivery to the
saved address and compare carriers. **Neither Submit Order nor payment was
performed.** There was no purchase or production release. Personal shipping
address details are omitted from repository evidence.

| USD, five boards | OSP / Standard | Lead-free HASL / Economic |
| --- | ---: | ---: |
| PCB fabrication, including file confirmation | 28.55 | 29.05 |
| Components | 22.27 | 22.20 |
| Assembly, stencil, setup, feeders and other included fees | 49.95 | 29.09 |
| **Merchandise subtotal** | **100.77** | **80.34** |
| UPS Express Saver DDP, actual-address checkout | 50.60 | 50.24 |
| Checkout line: Customs duties & taxes | 39.77 | 32.62 |
| **Checkout displayed Grand Total** | **191.14** | **163.20** |
| Rail removal, listed separately for charging after review | 3.31 | 3.31 |
| **Total including listed rail removal** | **194.45** | **166.51** |
| Per assembled carrier | 38.89 | 33.30 |

**Unpriced item:** the reverse-mount LED assembly remark still says **Quote after
review**. No extra fixture/manual handling charge is included. Such charges,
and tax recalculation on fees added during review, remain unknown. These are
live checkout figures plus the displayed rail fee, not a guaranteed
post-engineering invoice. No coupon is included; the preview before Submit
Order did not offer coupon application.

The user installs the nRF52840 clone and 83 switches. Buying five additional
clones at the user's reported $4 each brings the cheaper option to **about
$186.51**, excluding clone shipping/tax and future JLC review fees. Batteries,
case, keycaps, switches, stabilizers and module mounting hardware are separate.

## Verified configuration

- Five PCBs and five bottom assemblies; two-layer FR-4, 350.76 × 129.19 mm
  finished outline, 1.6 mm, green/white, 1 oz, tented 0.30 mm through vias.
  Ordinary electrical testing; no ENIG, via fill/cap, special via plating or
  Kelvin-test upgrade.
- Seven exact BOM groups matched and selected, with 99 placements per board
  (98 SMT plus J1 through-hole). No stock shortfalls were shown. LED1–LED6 remain
  C575513 / LTW-C230DS. No component was omitted to lower the Economic price.
  Different resistor purchase overage explains its $0.07 lower component total.
- Lead-free high-temperature paste, lead-free J1 solder and reverse-LED
  orientation/fixture review explicitly requested. File and placement
  confirmations and removal of any assembly rails selected.
- Economic was disabled for OSP but enabled for lead-free HASL with this same
  board. Standard adds rails, giving 350.76 × 139.19 mm manufacturing size;
  Economic uses JLC-added tooling holes and quotes the finished dimensions.
  Engineering review must preserve the finished outline and case fit.
- Included PCB lead time: 24 hours at no surcharge. Economic assembly: 2–3 days;
  Standard: 4–5 days. Advanced options add one day. Site holiday notices apply.

## Shipping correction

The cart's country-level freight preview was $45.75 for either batch and omitted
later checkout duties/taxes. It produced $129.40 HASL or $149.83 OSP totals with
rails. **Use the actual-address checkout figures above instead of those cart
previews or the earlier $150–170 estimate.**

| Checkout Grand Total, before separate $3.31 rail fee | OSP | HASL |
| --- | ---: | ---: |
| DHL Express DDP | 193.25 | 165.30 |
| **UPS Express Saver DDP** | **191.14** | **163.20** |
| FedEx Express DDP | 235.82 | 207.87 |

UPS has slightly higher freight than DHL but lower displayed duties/taxes, so
its complete total is lower. Own-carrier-account handling prices are not
inclusive freight. Postal/direct-line service was unavailable for this shipment.

## Cost reduction decision

Keep one assembly side and use the quoted HASL/Economic option if proceeding
after prototype/engineering review. The largest batch costs are freight
($50.24), displayed duties/taxes ($32.62), PCB fabrication ($29.05), assembly
fees ($29.09), and components ($22.20).

The BAT46W diodes cost $10.2366, five PCM12SMTR power switches $8.9075, and all
reverse LEDs including overage $2.1536. A cheaper power switch or diode selection
is a more useful component-cost investigation than LED unit-price savings.
Substitutions require footprint, mechanical and electrical verification in a
separate revision.

Moving only LEDs to the top requires two-sided factory assembly. Inference:
that likely increases costs by losing the current single-sided Economic setup,
unless avoided LED review charges outweigh extra processing. No top-LED v9.1
PCB or invented placement file was created. A cheaper future top-LED design
would need to preserve one assembly side by relocating the other components,
or leave LEDs for customer installation.

## Saved quotes and evidence

| Option | PCB reference | PCBA reference | Saved quote |
| --- | --- | --- | --- |
| OSP / Standard | Y9-5054573A | SMT026092661469-5054573A | [JLC quote](https://cart.jlcpcb.com/smt-order/?pcbFileNo=REDACTED) |
| HASL / Economic | Y10-5054573A | SMT026092661487-5054573A | [JLC quote](https://cart.jlcpcb.com/smt-order/?pcbFileNo=REDACTED) |

[OSP record](record.json) and [HASL record](hasl-economic/record.json) retain
configuration, breakdowns and SHA-256 hashes of the identical upload files.
Each folder contains BOM matches, full factory quote, cart preview, checkout
carrier comparisons and order-review text. Placement images show the top view;
they are quote previews, not production polarity/orientation approval.

`estimate.py`, `estimate.json` and `public-parts.json` retain the pre-login
estimate for audit only; the live records supersede them. Older revisions and
quotes were not changed. The baseline manufacturing package specifies OSP;
the separate HASL quote explicitly records the alternate finish. Use consistent
finish instructions if ordering that option.

Reference: [JLC assembly fee explanation](https://jlcpcb.com/help/article/pcb-assembly-price).
Actual totals above come from the user's live quotes and checkout; rates can
differ slightly from the public fee table.
