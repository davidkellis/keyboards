# Controller and fabrication cost options

Investigated 2026-09-25 using JLC's signed-in parts pages and a separate,
unsaved fabrication calculator. This is a feasibility study, not a new PCB
revision or a complete assembly quote. v7.2/v8.2 sources, manufacturing files,
and saved cart quotes are unchanged.

**Follow-up:** the isolated [v7.3 experiment](../../tkl7.3/README.md) now exists.
Selecting its required JLC06161H-7628 stack adds **$33.08**, bringing six-layer
OSP fabrication to **$97.58**, with Standard assembly required. The $64.50
unspecified-stack estimate below does not price that revision. Four-layer OSP
at $81.61 is the cheaper fabrication candidate. See the
[exact-stack check](../../tkl7.3/manufacturing/COST_REDUCTION.md).

## Same controller, alternative procurement code

| JLC code | Nordic part | Quantity 1–9 unit price | Available order quantity | Assembly eligibility shown |
| --- | --- | ---: | ---: | --- |
| C1851953 (current) | NRF52840-QIAA-R7 | $6.0654 | 2,482 | Standard Only |
| C190794 (candidate) | NRF52840-QIAA-R | $5.9160 | 49,004 | Economic and Standard |

Both are the same QIAA aQFN73 package; R/R7 distinguish reel ordering formats.
At five pieces the component-only difference is $0.747. Neither alternative
changes the current dense package's PCB routing requirements. Verify the actual
supplied silicon build code against firmware errata during prototype bring-up.

The earlier conclusion that the current U1 listing forces Standard assembly is
correct for C1851953, but does not apply to every procurement code for this MCU.
Economic eligibility alone is not proof of a lower complete price. The current
BOM has 26 Extended and five Basic groups. JLC's Economic fee is about $3 per
Extended group, versus the saved Standard quote's $1.50 per group, including
Basic parts. A complete new BOM/assembly quote is needed to compare services.
v8's two assembly sides still require Standard; v7's reverse LED fixture remains
subject to factory review.

The nRF52840 QFAA/QFN48 version does not provide USB and has a 1.7–3.6 V supply
limit, despite inaccurate USB/voltage fields in some distributor listings.
It would not retain the current USB and VDDH design. The E73-2G4M08S1C module
checked costs $7.626 each and is Standard Only; any saving would have to come
from removing support circuitry/PCB complexity, not its purchase price alone.

## Fabrication calculator comparison

Five PCBs, 350.76 × 139.19 mm including the current assembly rails, 1.6 mm,
green, 1 oz outer / 0.5 oz inner copper, 0.30/0.45 mm vias, filled/capped vias,
ordinary electrical test, regular outline tolerance, no expedited lead time.
The six-layer selected options and dimensions are saved in `fab-selected.json`.

| Construction | Fabrication only | Saving from current construction | Displayed fabrication lead time |
| --- | ---: | ---: | --- |
| Four layers, ENIG | $103.81 | — | 3–4 days |
| Four layers, OSP | $81.61 | $22.20 | 3–4 days |
| Six layers, ENIG | $86.70 | $17.11 | 8–9 days |
| Six layers, OSP | $64.50 | $39.31 | 8–9 days |

These exclude the saved order's $1.05 production-file confirmation charge,
assembly, shipping, tax, and any engineering adjustments. The first row
therefore reconciles with the saved $104.86 fabrication quote. They are manual
dimension/process estimates, not quotes generated from revised six-layer files.

Six layers remove the $22.60 filled/capped-via surcharge and the $3.91 plating
line, while engineering increases $8 and the board charge increases $1.40.
The saving is $17.11. This option needs a real KiCad layer/stackup revision,
RF/USB reference-plane and impedance review, and regenerated/validated exports.
Six layers can retain 1.6 mm total thickness and the existing case footprint.
Do not order the existing four-layer Gerbers as six layers.

OSP removes the $22.20 ENIG line. It supports fine-pitch soldering, but the
exposed Tag-Connect programming contacts and delayed user soldering of switches
need a suitable assembly/programming plan. It is not yet an approved finish
change. Do not substitute HASL on the existing fine-pitch design just for price.

A two-layer carrier with a suitable nRF52840 module is another design candidate,
but no layout, mechanical fit, power review, or total-cost advantage has been
established. Removing via-in-pad would require addressing both U1 and U2.

## Sources

- [Current U1 listing](https://jlcpcb.com/partdetail/NRF52840-QIAA-R7/C1851953)
- [Alternative U1 listing](https://jlcpcb.com/partdetail/NRF52840-QIAA-R/C190794)
- [Nordic order codes](https://docs-be.nordicsemi.com/bundle/nRF52840_PS_v1.8/raw/resource/enus/nRF52840_PS_v1.8.pdf)
- [Nordic package differences, including QFN48 USB limitations](https://blog.nordicsemi.com/getconnected/qfn-and-aqfn-options-for-the-nrf52840)
- [JLC assembly fees](https://jlcpcb.com/help/article/pcb-assembly-price)
- [JLC assembly capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities)
- [JLC free filled/capped vias on six and higher layer counts](https://jlcpcb.com/news/free-via-in-pad-6-20-layer-pcbs-pofv)
- [JLC surface finishes](https://jlcpcb.com/help/article/jlcpcb-surface-finish)

Prices and stock are observations at the time of this study and are not reserved.
