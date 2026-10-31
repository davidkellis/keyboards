# v7.4 four-layer OSP cost reduction

This separate revision uses v7.2's fully routed four-layer board, its original
JLC04161H-7628 stack, OSP finish and lead-free assembly solder. v7.2, v8.2 and
the six-layer v7.3 experiment remain unchanged. All 142 assembly placements,
wireless, USB, charging and lighting are retained.

## Complete assembly quote

The live five-board estimate is **$300.22 including displayed DHL DDP shipping
and rail removal**, before tax, final shipping changes or engineering/fixture
adjustments. It saves $22.95 versus v7.2. JLC disables Economic for the configured
PCB specifications, so the full quote uses Standard bottom-side assembly.
See [the quote and evidence](JLC_QUOTE_v7.4_2026-09-25.md). The cart is unpaid.

## Exact-stack fabrication estimate, 2026-09-25

The signed-in calculator was checked with the exact **JLC04161H-7628** stack,
five boards and 350.76 × 139.19 mm including the existing assembly-rail area.
Settings: 1.6 mm FR4 TG135, green/white, 1 oz outer / 0.5 oz inner copper,
0.30/0.45 mm vias, epoxy fill/cap, regular outline tolerance, ordinary flying
probe test, no four-wire Kelvin test, non-expedited 3–4 day fabrication.

| Construction | Five-board fabrication only |
| --- | ---: |
| v7.2 four-layer ENIG comparison | $103.81 |
| v7.3 six-layer OSP with required special stack | $97.58 |
| **v7.4 four-layer OSP, exact standard stack selected** | **$81.61** |

The four-layer stack adds **no stackup fee**. Breakdown: $25.00 engineering +
$30.10 board + $22.60 filled/capped vias + $3.91 plating = $81.61. OSP adds no
finish charge. Retain filled/capped vias beneath the fine-pitch devices.

This saves **$22.20 per five PCBs** versus the ENIG comparison, and $15.97
versus the six-layer experiment. The figures exclude the existing $1.05
production-file confirmation charge, assembly, shipping, tax and engineering
adjustments. With that confirmation charge alone, fabrication would be $82.66.

Evidence: [calculator capture](fabrication-estimate-four-layer-osp.txt) and
[selected settings](fabrication-estimate-settings.json). This was an unsaved
process/dimension estimate, not a Gerber-reviewed order or complete assembly
quote. The page's bare-board shipping estimate is not assembled-board shipping.
A complete Standard assembly/cart estimate is now recorded above; it remains
subject to the stated review and checkout adjustments.

U1 retains the v7.3 procurement change to **NRF52840-QIAA-R / C190794**, the
same QIAA aQFN73 device/package. The earlier part-page comparison was $5.9160
versus $6.0654 for R7 / C1851953, a $0.747 difference for five parts before
assembly attrition. The quote matches that ordering code. Its listing permits both services, but
JLC disables Economic for the complete configured PCB. Standard is quoted;
reverse-LED fixture charges remain subject to review. Do not omit components
to force a cheaper service.

## OSP assembly and programming

OSP is a flat, lead-free organic finish, not leaded HASL or a metallic contact
coating. J2 uses temporary soldered SWD wires with 1.8 V target reference;
remove the leads before closing the case. Do not rely on bare OSP pogo contacts.
Use lead-free solder for SMT, both THT connectors, programming leads and switches.

Complete plate/keycap/stabilizer fit testing before ordering. Keep boards sealed
and dry and complete user soldering promptly within JLC's OSP handling limits.
The original battery/NTC, firmware and physical RF/USB/charging validation
requirements remain. See [FABRICATION.md](FABRICATION.md) and
[ORDERING.md](ORDERING.md) for the actual manufacturing instructions.

Sources: [JLC surface finishes](https://jlcpcb.com/help/article/jlcpcb-surface-finish),
[JLC stackups](https://jlcpcb.com/impedance), and the preserved
[controller and process study](../../research/cost-options-2026-09-25/README.md).
