# Clone-controller cost and feasibility study

**A user-installed ~$4 nRF52840 module is a credible cost-reduction direction.**
Replacing the controller and its support circuits removes about $60.94 from
the five-board v7.4 parts/feeder bill; five $4 modules leave $40.94 savings.
Using a verified module's USB and charger as well increases that identifiable
saving to $64.69. These are calculations from existing quote lines, not prices
for a completed replacement PCB. No module carrier or firmware has been built
or tested, and none of the existing PCB revisions has been altered.

The user will solder the modules after JLC assembles the small components.
Module prices below are the user's $4 clone / $25 genuine assumptions; separate
module freight, tax, mounting hardware and new interface parts are excluded.

## Cost evidence

The [saved v7.4 quote](../../tkl7.4/manufacturing/JLC_QUOTE_v7.4_2026-09-25.md)
is $300.22 for five boards including estimated DHL DDP shipping and rail removal.
Its final-review/fixture and tax exclusions still apply. It contains $70.82 in
parts and $46.50 in feeder charges for 31 distinct groups. Actual SMT placement
is only $4.21; reducing distinct part types is a much bigger opportunity than
reducing a few placement operations.

| Five-board line-item comparison | Keep carrier USB/charger; module replaces controller/RF | Use module controller, USB and charger, conditional |
| --- | ---: | ---: |
| Complete BOM groups removed | 15 | 24 |
| Removed quoted component cost | $38.44 | $48.69 |
| Removed Standard feeder fees | $22.50 | $36.00 |
| Total removed before buying modules | $60.94 | $84.69 |
| Five clones at $4 | $20.00 | $20.00 |
| **Net identifiable saving with clones** | **$40.94** | **$64.69** |
| Five genuine boards at $25 | $125.00 | $125.00 |
| **Net additional cost with genuine boards** | **$64.06** | **$40.31** |

The $29.58 U1 line alone is not the whole controller cost. The module also
replaces crystals, RF matching, the antenna connector and dedicated decoupling
parts. The external antenna, excluded from the original quote, could also be
eliminated if the module antenna works in the case; no saving is credited for it.
Already-owned modules may need no new cash expenditure, but this table still
counts their $4 value for a fair design comparison.

Only completely removed BOM groups receive credit. Shared capacitor groups
remain at their original price in the first scenario; the shared battery/NTC
connector group remains at its original price in the second. New quantities,
attrition and service fees must be requoted. A carrier may need new power/interface
components, so these savings are not guaranteed reductions to a final bill.

Reproduce the [calculation](calculate.py) with Python 3. Outputs are
[cost-comparison.json](cost-comparison.json),
[removed-quote-groups.csv](removed-quote-groups.csv),
[candidate-pinmap.csv](candidate-pinmap.csv) and [feasibility.json](feasibility.json).
The script uses the saved quote and records source hashes. It does not upload
files, modify the saved cart or generate manufacturing outputs.

## GPIO and firmware feasibility

The current 86-key matrix needs 11 row plus nine column signals. Its six LEDs
share one PWM output: **21 GPIO total**. The genuine nice!nano v2 exposes 18
edge GPIO and three auxiliary pads, exactly enough. The official auxiliary pads
are **P1.01, P1.02 and P1.07**. An earlier question incorrectly called the first
two P0.09/P0.10; those are edge pins. The user confirmed auxiliary pads are
present, but the actual clone's routing/labels are still unverified.

The provisional map retains most v7.4 assignments. ROW1 and ROW2 move from
P0.13/P0.15 to P0.09/P0.10, since the former pair is not exposed as free edge
GPIO on nice!nano v2. Firmware must configure the NFC-capable P0.09/P0.10 as
GPIO and preserve the module's internal power-control assignments. The three
extra pads need three explicit solder connections, not just the edge headers.
The pin-map calculation checks that all 21 assignments are unique and present
on the official pinout. This is logical feasibility, not clone hardware validation.

A board with only 18 usable GPIO would not directly support this matrix; even
a fully reassigned 9x9 matrix handles only 81 keys before reserving lighting.
ZMK supports inexpensive 74HC595 output expansion with direct MCU inputs for
wake interrupts if needed. It is unnecessary if all 21 module GPIO prove usable.
See the [official pinout](https://nicekeyboards.com/docs/nice-nano/pinout-schematic/)
and [ZMK shift-register guidance](https://zmk.dev/docs/hardware-integration/shift-registers).

The repository's v6 already attempted a 21-GPIO nice!nano carrier and connected
the auxiliary pads. It is useful reference material, not a ready-to-order design;
the later board work addressed incomplete routing and power issues. A new module
revision should retain validated switch geometry while reviewing the circuitry
and producing a custom ZMK shield/keymap. A bootloader alone is not keyboard firmware.

## USB, charging and the slim case

The best cost outcome uses the module's own USB, antenna and power circuitry,
but this is not yet approved for the intended battery. The genuine manufacturer
specifies 100/500 mA charging; this does not establish clone charge current, cell
temperature protection or permitted pack capacity. At 100 mA a hypothetical
10 Ah pack requires at least 100 hours by capacity/current arithmetic, before
taper and keyboard consumption. The final case-fitting pack remains unselected.
Do not silently remove the current carrier's cell-temperature monitoring.
See [genuine specifications](https://nicekeyboards.com/nice-nano/) and
[battery guidance](https://nicekeyboards.com/docs/nice-nano/).

Retaining BQ24072 charging preserves an important design option, but needs a
deliberate interface. Raw USB data/VBUS are not normal Pro Micro header signals;
the existing carrier USB cannot simply be connected to ordinary module GPIO.
The two chargers must not be casually connected in parallel. The carrier's
approximately 4.4 V VSYS output must not be assumed safe on a clone's battery
input. Module power entry, USB access and disabling/isolation of the module
charger require its actual circuit, with thermal and battery tests afterward.
The first cost column is therefore a removable-parts budget, not a wiring recipe.

Published first-hand SuperMini reverse engineering documents variation in sleep
current and a battery-divider connection that differs from its drawing. This
does not establish that all clones have those faults. It does mean exact
board identity, battery reporting and standby current need checking rather
than assuming every listing is electrically identical. Source:
[SuperMini board investigation](https://github.com/sasodoma/nrf52840-promicro).

The rear-right underside, outside the battery reserve ending at case X=276 mm,
is a plausible location while preserving 7.3/20.6 mm front/rear case heights.
The existing model has approximately 10.44 mm vertical floor-to-PCB space at
board Y=96 mm and 12.82 mm at Y=120 mm, before intervening parts and mountings.
The official nice!nano is 3.2 mm thick, but clone dimensions and sockets differ.
This is enough to justify a detailed fit study, not proof of fit. Switch tails,
insulation, the USB opening, battery and module antenna copper/metal keepout all
need explicit modelling. No new case, plate, module model or fit-test STL has
been generated by this study.

## Further PCB and assembly reductions

- Start from the user's four-layer OSP, lead-free preference. Moving the dense
  MCU and RF circuit onto a module makes a later two-layer carrier plausible,
  subject to routing/EMI review and a complete price comparison.
- The current $22.60 filled/capped-via fee is a candidate saving only after
  **all** via-in-pad needs are removed. Retaining the unchanged BQ24072 footprint
  retains its exposed-pad thermal vias. Removing U1 alone does not remove the need.
- A carrier with no bottom-terminated ICs may avoid the current $8.25 X-ray fee.
  This and the via charge are not credited in the table; requote the actual layout.
- Check both Economic and Standard after the BOM is simplified. Economic is
  disabled for the current configured PCB specs; the exact limiting option was
  not identified. Eligibility and lower total cost are not established yet.
- The current switch costs $8.23 and matrix diodes $10.60 per five-board batch.
  A cheaper switch and conventional silicon matrix diodes are further candidates
  with a 3.3 V module, after mechanical and GPIO-threshold/leakage checks. Neither
  is substituted in this study. The existing BAT46 diodes were selected for the
  integrated board's 1.8 V GPIO and should not be blindly replaced there.
- Reverse-LED support tooling remains a separate unpriced risk on v7; installing
  a module does not remove it. Top-side LEDs on the v8 concept would still need
  a two-sided assembly quote if everything else remains below.

## Exact clone identification still needed

These user-supplied AliExpress links did not expose usable product details in
either the browser or web reader during this investigation. No listing variant,
dimensions, charge IC or pinout is certified from the URL alone:

- https://www.aliexpress.us/item/3256806824240477.html
- https://www.aliexpress.us/item/3256806085566324.html
- https://www.aliexpress.us/item/3256809703964768.html
- https://www.aliexpress.us/item/3256812138541521.html

Clear front/back photos and PCB markings from one owned module are the next
input for selecting a footprint and power architecture. Bench checks then cover
all selected GPIO, USB bootloader, charging, sleep/wake current and BLE reception
in the intended mounting position. Preserve v7.2/v8.2/v7.3/v7.4 and place an
eventual module carrier in its own revision directory.
