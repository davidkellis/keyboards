# v7.3 cost reduction study

This distinct revision preserves v7.2 and v8.2. It uses six copper layers,
JLC06161H-7628, nominal 1.6 mm, OSP and lead-free assembly solder. The original
outer signal/reference spacing is retained, and RF keepouts extend onto the
two added internal ground layers. All 142 assembly placements remain.

## Exact stackup changes the cost conclusion

The signed-in fabrication calculator was checked on 2026-09-25 for five boards,
including 350.76 × 139.19 mm rail area, 1.6 mm, 1 oz outer / 0.5 oz inner copper,
0.30/0.45 mm vias, epoxy fill/cap, regular outline tolerance, ordinary electrical
test and non-expedited production. These are dimension/process estimates,
not complete quotes for this revised Gerber/BOM package.

| Construction | Fabrication only |
| --- | ---: |
| v7.2 four layers, ENIG comparison | $103.81 |
| Four layers, OSP comparison | $81.61 |
| Six layers, OSP, unspecified stack (earlier estimate) | $64.50 |
| **v7.3 six layers, OSP, required JLC06161H-7628** | **$97.58** |

Selecting the exact stack adds a **$33.08 stackup fee**. The v7.3 breakdown is
$33.00 engineering + $31.50 board + $33.08 stackup, with no separate OSP or
filled/capped-via surcharge. The saving versus four-layer ENIG is therefore
**$6.23 per five PCBs**, not the earlier $39.31 estimate. This six-layer revision
is **$15.97 more than the four-layer OSP estimate**. For minimum fabrication
cost, four-layer OSP is the better candidate; the six-layer experiment does
not establish a lowest-cost design.

Figures exclude the existing $1.05 production-file confirmation charge,
assembly, shipping, tax and engineering adjustments. Six-layer non-expedited
fabrication was 8–9 days instead of 3–4 days. A faster build costs more.

The exact-stack evidence is [the calculator capture](fabrication-estimate-six-layer-osp.txt)
and [selected settings](fabrication-estimate-settings.json). JLC's stack dialog
also states that this special stack **does not support Economic assembly**,
and gives an actual thickness of **1.5544 mm ±10%** under the 1.6 mm option.
Use Standard assembly and verify physical fit against actual board thickness.

U1 is now C190794 / NRF52840-QIAA-R, same QIAA aQFN73 package, listed at
$5.9160 versus $6.0654 for C1851953 / R7: another **$0.747 per five** in part
purchase cost. Actual assembly attrition/fees must be recalculated. The part's
Economic eligibility does not override the stack's Standard-only restriction.

No final assembled/shipped total is claimed for v7.3. The preserved v7.2 total
was $323.17 for five; subtracting process/component differences is only an
estimate and does not account for fixtures, shipping repricing or other
engineering adjustments. Reverse LED fixture review remains required.

## OSP operating changes

J2 is now documented as temporary solder-wire SWD access, using 1.8 V target
reference. No bare-OSP pogo mating contact is assumed. Use lead-free solder,
remove leads before closing the case, and solder switches promptly after
receipt/opening within JLC's OSP handling limits. Keep unused boards sealed.
The plate/stabilizer fit should be settled before ordering the OSP boards.

The PCB contains no finished-contact connector fingers. All existing physical
fit, battery/NTC, firmware and RF/USB/charging validation limitations remain.

Sources and earlier calculator/part-page evidence are in the
[shared cost study](../../research/cost-options-2026-09-25/README.md).
[Fabrication requirements](FABRICATION.md) and [stackup](STACKUP.md) take
precedence over calculator defaults. Do not order the old four-layer
Gerbers with a six-layer dropdown selection.
