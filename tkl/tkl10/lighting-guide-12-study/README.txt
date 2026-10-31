V10 — ten-source light-guide study, twelve-source maximum
2026-10-15

This study supersedes the lighting recommendation in lighting-engineering-study.
The user's maximum is twelve backlight LEDs. Ten is the first optical prototype;
twelve is a comparison at the same measured lighting input power. Existing PCB,
case, battery and earlier studies are preserved. This is not a fabrication release.

DESIGN BASIS

Use ten efficient, single-die, side-emitting white LEDs, five at the front long
edge and five at the rear long edge of a thin optical guide. Both banks point
inward. Compare twelve sources (six per edge) if the ten-source sample has dark
regions. Count is total physical backlight LEDs, not twelve per side. The two
layouts have different source spacing; twelve is not simply two additions to
the ten-source drawing. Existing reverse-mount LEDs point vertically and are
not the intended source for this edge-coupled guide.

The full keyboard layout illustration uses actual V10 switch centers. Source
positions and native switch-channel output locations are conceptual. The drawing
is NOT a full-size guide cutting file or a PCB placement release. Edge coupling,
module antenna clearance, diode locations, pin reliefs, mounting bosses and the
battery envelope still need a complete mechanical design. Keep factory parts on
the bottom side where possible to preserve the Economic assembly objective;
JLC compatibility and the cost of a particular driver/package are not quoted.

MANUFACTURING CONSTRAINT — updated 2026-10-15

All factory-installed parts must remain on the bottom side: side-emitting LEDs,
matrix diodes, lighting driver, inductor, rectifier if needed, resistors,
capacitors, power switch and factory-fitted battery connector. The LEDs emit
parallel to the PCB into the guide below it; this does not require top-side LED
placement. The optical guide, reflector and mask are installed mechanically
after soldering. The user still fits the key switches and controller module.
No separate LED daughterboard, upright adapter or factory cable assembly is
part of the baseline. Use one LED part number for all sources, common JLC Basic
passives where suitable, and lead-free HASL with lead-free solder. Evaluate
Economic eligibility before selecting the exact LED and driver footprints.

JLC publishes single-side Economic placement, 0.4 mm minimum IC lead pitch and
0.5 mm minimum BGA ball pitch. The previously proposed TPS61162A has 0.4 mm BGA
pitch, so exclude it from this Economic/HASL baseline. Single-side placement by
itself is not sufficient to guarantee Economic service or the earlier price.

For the ten-source version, compare one ten-LED series string using a leaded
driver such as TPS61169 (5-pin SC70, 2.7–5.5 V input, up to 38 V output) against
other Economic-compatible solutions. Physical LED positions can still form two
edge banks even if electrically they are one string. Verify the exact LED's
maximum forward voltage, output margin, low-current regulation, input power,
supplier stock and quote. Do not extend that single string to twelve LEDs
without a new voltage calculation: twelve high-Vf white LEDs can exceed 38 V.
For twelve sources, evaluate two separately regulated six-LED strings using
compatible leaded drivers or another suitable package. The cheapest complete
solution has not yet been selected or quoted. Existing budget numbers remain
input-power targets, not measurements of TPS61169 or a selected circuit.

Prototype ordinary clear optical PMMA with polished transport faces and local
underside extraction dots at each switch's light-entry channel. Begin at 1.0 mm
on the bench; compare 0.8 and 1.5 mm to identify coupling and thickness losses.
No thickness has yet been fitted to the current case. A 1.5 mm bench sample does
not authorize raising the case or consuming the battery clearance.

Use a separate white reflector below, reflective non-input edges, and an upper
mask with a white guide-facing surface and dark outward surface. Admit light
only toward the switch's LED channel. Keep tiny air gaps at the polished guide
faces and put adhesive at mounting margins, not across transport faces. A local
diffuser at an output may help, but a blanket diffuser can waste light behind
opaque PCB or switch material. Compare both with and without local diffusion.
Do not globally frost the guide. Light around a switch is not evidence that the
legend is lit. The opaque Whale base makes the native LED passage important.

Below-PCB guide placement is the current concept: local extraction sends light
up through new PCB apertures aligned with the switches' native LED passages.
The LED emitting window and the guide's thin edge overlap vertically, on the
same side of the PCB. Light enters across a small lateral gap. See
diagrams/edge-coupling-section.svg. This separate optical sheet is different
from the earlier idea of using the acrylic switch plate ABOVE the PCB as the
guide. A bottom-mounted side-emitter cannot directly inject into that upper
plate through opaque FR4. An upper guide would need a designed optical coupler
around/through the board, or different LED placement; neither is established
by this study. Below-board placement still needs a complete interference and
clearance check before it can be called mechanically feasible in this case.
That needs PCB changes. Existing copper planes cannot pass the light. The switch
footprint's manufacturer drawing is a pattern-side view; verify its handedness
with an actual switch before using the provisional +4.93 mm channel offset.
Do not route the production board from the illustrative output markers.

ELECTRICAL CONCEPT

The earlier electrical reference uses two regulated series strings of five
LEDs (ten total) or six (twelve total). The manufacturing constraint above now
also requires evaluating one ten-LED string with a leaded driver.
Feed a boost/current driver from the protected, switched cell supply, rather
than adding this load to the clone's 3.3 V output. Two regulated channels prevent
one string hogging current. At 3 V per LED the strings are approximately 15 or
18 V, not a higher-voltage battery. Preserve RF clearance and check boost noise,
startup current, power switch rating and the clone's unverified USB/charge path.

TI TPS61162A is an electrical reference, excluded from the low-cost baseline:
2.7–6.5 V input,
dual current sinks, 26.5 V nominal overvoltage protection, PWM input, 9-ball DSBGA.
Its datasheet states about 1.2 mA typical operating no-load current and 1 uA
typical shutdown. Low-current efficiency and matching need measurements; the
advertised peak efficiency is not a low-load guarantee. The small BGA may be a
poor JLC cost choice and violates the published Economic BGA pitch limit, so
qualify a package/availability alternative before PCB
release. Do not assume minimum 1–4 mA accuracy from its 20 mA test specifications.

This driver converts PWM input to analog LED-current dimming; it is not simple
on/off 20 mA pulses into the LEDs. EN may be tied to VIN in PWM mode; holding PWM
low for more than 20 ms shuts it down. The existing P0.31 backlight signal could
therefore remain the only required control pin. Do not PWM the converter's power
supply or use the old output MOSFET as the series-string current regulator.
Retain a defined PWM-low state during boot. Select ISET, L, C and compensation
only after testing the exact LED, operating current and full battery range.

LED candidates are Everlight BL-3806 and Nichia NSSW506H families. Both have
side-view packages suited to thin guide entry. Exact suffix, white point, package,
low-current flux, emitter height and procurement need confirmation. Nichia also
offers two-die side-view parts: those are NOT the single-die candidate here.
Do not choose only by mcd: the radiation pattern and coupled lumens matter.

POWER TARGETS, NOT BRIGHTNESS CLAIMS

The calculator uses battery-side lighting power, including driver losses. It
does not equate ten LEDs with a guaranteed brightness or runtime. At 40 mW input,
5000 mAh nominal / 80% usable, 3.7 V average cell voltage, 0.7 mA other active
load, 0.1 mA unlit load and 3% monthly self-discharge, expect approximately
53 days at 6 lit hours/day or 28 days at 12. At 80 mW, about 28 or 15 days.
At 160 mW, about 15 or 7.5 days. These are estimates until the actual clone,
battery capacity, LED current and complete driver input power are measured.

For source-current sizing only, the calculator assumes 85% conversion of power
after a 1.2 mA fixed driver allowance and 3.0 V per LED. This is an explicit
engineering assumption, not measured efficiency. At 40 mW input that implies
roughly 1.01 mA per LED for ten LEDs or 0.84 mA for twelve. Runtime depends on
the input power, so changing count at fixed power leaves runtime unchanged.
Do not add the driver allowance a second time to the runtime calculation.
Ambient dimming / idle-off can save energy; the quoted 6–12 hours are actual
light-on hours and already exclude idle-off time. An ambient sensor would need
additional circuit and firmware work; no such sensor is assumed in this budget.

The MX Keys teardown documents a separate backlight guide. Logitech documents
ambient-dependent brightness, proximity wake and a low-battery light cutoff.
The exact ten-LED count for the user's referenced revision was not independently
verified. Those controls and the optical stack matter alongside source count.

FULL-DEPTH OPTICAL TEST KIT

The new coupon is 70.152 x 129.19 mm, with eighteen outputs in three columns and
six rows. Two sources enter the FRONT and REAR short edges, centered across its
width. This reproduces the full keyboard's depth and approximately one fifth
of its width: nine windows per source, compared with 8.6 keys/source for ten
sources over the complete keyboard. Side boundaries are reflective in this
coupon; the full keyboard is continuous and will mix across regions. This is
an approximate screening sample, not an optical equivalence proof.

Use the same ordinary PMMA stock, LED pair, alignment, reflector and current for
all tests. Start with one solid guide, then the perforated variant. Perforations
are generic switch center, support and two pin clearances, rotated to allow the
provisional north-side channel. Real PCB diode reliefs and other components are
not included. Passing this test is necessary but insufficient for full-board fit.

coupons/*CUT.svg: millimeters; RED nominal cut contours.
coupons/*ETCH.svg: millimeters; BLACK underside etch dots.
coupons/*-solid.dxf or *-perforated.dxf: CUT and ETCH layers; $INSUNITS=4 (mm).
SVG origin is top-left; DXF y is inverted so the drawing opens upright.
All have the same outer datum. No tool offset, laser kerf, feeds or G-code applied.
Etch first while the stock remains intact, then cut the perimeter and reliefs.
Keep both sources centered on the actual optical thickness with about 0.3 mm
mechanical separation at the entry edge. The LED beam dimensions must overlap
the thickness; package thickness alone does not define emitter center height.

The sparse/medium/dense patterns are deliberately experimental. Dots increase
away from both entry edges and toward the strip's sides. There is no ray-traced
or measured brightness map. Milling 0.1–0.36 mm dots may require an engraving
tool; laser settings depend on machine and material. A shallow engraving is
intended, not through-holes. Check a small scrap first. The solid guide, opaque
mask, and perforated guide are alternatives/test layers, not all stacked guides.
The mask/backing include the same pin holes in the perforated version. This kit
does not include a load-bearing switch carrier; support the switch at the normal
plate/PCB relationship above the mask. Never clamp a switch onto the optical
guide. A single physical switch/cap can be moved between output windows to
screen transmission before building an eighteen-switch fixture.

QUALIFICATION BEFORE PRODUCTION PCB

1. Test the real Whale switch and XVX cap over one illuminated window. Try both
   handedness/orientation interpretations. Confirm the legend, rather than the
   gaps around the key, is readable; ensure full 2.8 mm nominal switch travel.
2. At the same total measured LED/input power compare three etch densities,
   solid vs perforated guide, reflector, and local diffuser. Use locked camera
   exposure and white balance; avoid saturation. A camera is a relative meter,
   not a calibrated luminance measurement.
3. Measure near/middle/far outputs through the same cap. Provisional uniformity
   goal: darkest comparable legend at least half the brightest, with no direct
   LED glare. A 5–15 cd/m2 night-use legend target is provisional, not measured
   performance or a universal ergonomic requirement. Check actual readability.
4. For the two-source test use about one fifth of the full ten-source LED output
   power, or about one sixth for the twelve-source comparison, not the entire
   keyboard power into two LEDs. Log actual LED V and I. A bench supply does not
   reproduce the complete driver's input overhead; measure that separately.
5. Add actual pin/diode/boss/module/battery reliefs to a full-size guide and repeat
   brightness testing. Verify the central/spacebar/navigation regions, every key
   cap size, bottom-out travel, battery reserve and case closure at real thickness.
6. Measure the finished driver/clone at 4.2, 3.7 and 3.0 V, at idle, dim, bright
   and radio activity. Test charging with lights on. Then select the exact parts,
   route a separate PCB revision, DRC/ERC and get the real JLC assembly quote.

REFERENCES (checked 2026-10-15)
https://www.ifixit.com/Guide/Logitech+MX+Keys+disassembly+guide/148050
https://support.logi.com/hc/en-ca/articles/360034762774-Getting-Started-MX-Keys
https://www.bivar.com/Files/Content/Handbook-to-Illumination-Design-101.pdf
https://www.acrylite.co/products/brands/acrylite-led/light-guiding-edge-lit-sheet
https://en.everlight.com/visible_led/category-backlight_led/side_view_product__bl_3806/
https://led-ld.nichia.co.jp/en/product/backlighting_sideview.html
https://www.ti.com/product/TPS61162A
https://www.ti.com/lit/ds/symlink/tps61162a.pdf
https://www.ti.com/product/TPS61169
https://jlcpcb.com/capabilities/pcb-assembly-capabilities
Kailh drawing: ../render-keycaps-lighting/reference/CPG1353S01D02-01-datasheet.pdf
