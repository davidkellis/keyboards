V10 lighting engineering study — 2026-10-15

Open index.html for the design brief, power calculator and source-position
diagrams. This directory preserves the current V10 design and all earlier
case/rendering revisions. It contains a proposed architecture and bench
artwork, not a production PCB, a ray-traced guide, or verified photometry.

DESIGN DECISION

Treat "backlight the keys well" as useful, readable XVX legends across the
keyboard, with controlled spill. Decorative deck brightness is secondary.
For the user's 6–12 lit hours per day, aim first at approximately 10 mA
incremental battery current for the entire lighting system. More light is
available by accepting shorter runtime; neither source count nor a render
establishes brightness.

Recommended prototype: 86 plain white LEDs at the native switch LED windows,
individual ballast resistors, a dedicated regulated lighting rail and a common
MOSFET/PWM command. Native-window placement avoids sending most of the light
around opaque switch bases. Check the actual Whale switch and XVX caps before
choosing footprint orientation. The Kailh drawing is a pattern-side view;
handedness must not be inferred casually from the viewer's appearance meshes.

Candidate parts, subject to sample and procurement qualification:

- Lite-On LTW-C230DS / existing JLC C575513: reverse-mount white, 1206, already
  used by V10. Test at 0.1–0.5 mA average, not only its 20 mA data-sheet test
  condition. One per native window may preserve bottom-only factory assembly.
  This does not imply that 86 reverse placements have an acceptable quote.
- Kingbright APT1608LQWF/D: low-current top-emitting white comparison part,
  1.6 x 0.8 x 0.75 mm; 20 mcd minimum / 35 typical at 2 mA, typical Vf 2.65 V
  and maximum 3.1 V at that test current. It requires the correct top mount,
  cavity fit and potentially two-sided factory assembly. Test its efficiency
  at the proposed operating point before selecting it over the reverse LED.
- TI TPS63900: candidate low-Iq buck-boost for a separate provisional 3.6 V
  LED rail. Feed it from the protected, switched battery rail, not clone VCC.
  Evaluate TI's reference circuit/layout, 2.2 uH inductor and effective output
  capacitance under load, component derating and converter/LED-bank transients.
  Configure a 100 mA input limit for prototype evaluation and verify it. This
  is a candidate architecture, not a completed regulator schematic/BOM.
- Retain a logic-level low-side MOSFET such as V10's DMN2056U-7, gate pull-down
  and one PWM output (P0.31 / module pad 20 in the current netlist). The GPIO
  drives only the gate. Check gate timing, leakage and ground bounce.
- Each LED needs its OWN resistor. Prepare 1.0/1.5/2.2/3.3 kohm sample values
  and select from measured Vf for roughly 0.5 mA peak. Do not approve these
  as interchangeable production values. Formula: R=(Vrail-Vf-Vswitch)/Ipeak.
  With a verified 0.5 mA peak, PWM at 20%, 40%, 100% gives 0.1, 0.2, 0.5 mA
  average. Light output need not scale perfectly with these averages.

This is regulated-voltage, ballasted LED drive. It is not individual precision
constant-current regulation. Measure branch-current and luminance spread;
choose a consistent LED bin and adjust resistor groups if needed. If it cannot
meet the uniformity target, reconsider current sinks, accounting for their
quiescent current, cost and interface requirements. The current controller
already uses 20 matrix GPIO plus one PWM. An I2C implementation would need a
pin/matrix redesign; for example a new 9x10 matrix has 19 lines but is not the
present PCB's matrix. Avoid adding an I2C driver without accounting for this.

Keep the PWM off the converter EN pin. Maintain the lighting rail with low
standby loss and switch/dim the LED bank. Final shutdown control, startup,
low-battery behavior and any USB supply selection require a real schematic
and measurements. Do not assume the clone charger supplies the new LED rail
through USB or has a power-path function. The existing 300 mA battery switch
and its charging/discharge path must be audited for combined loads/inrush.

WHAT THE USER'S ZMK SCREENSHOT MEANS

The source code uses I=N*(Vout-Vf)/R*duty, then applies the sleep percentage.
For genuine nice!nano v2, white=3.2 V, six LEDs, R=100 ohms, 100% brightness:
Iawake=6*(3.3-3.2)/100 = 6 mA. At 50% sleep that becomes 3 mA average for LEDs.
Including its other assumptions reproduces 52.04 days. That does not prove
the current V10's 1 kohm drive, the clone, or a future guide will behave that
way. Real Vf varies with current/temperature; a 20 mA Vf value is not a fixed
low-current diode voltage. The profiler does not calculate optical flux.

Source snapshots are linked and hashed in reference/source-snapshots.json.
ZMK's source is MIT licensed; its original headers remain in the snapshots.
Its model currently also assumes 5% monthly self-discharge, 85% usable energy,
genuine-board quiescent loads, 2% time holding a key and a fixed 3.8 V battery.
Our separate calculator intentionally exposes different conservative design
assumptions rather than presenting the screenshot as a measurement.

OUR BATTERY MODEL

5000 mAh advertised capacity, 80% usable/reserved => 4000 mAh design allowance.
Average cell voltage 3.7 V; LED rail 3.6 V; converter efficiency assumed 85%.
Other active battery current 0.7 mA (allowance for clone, BLE, PWM and control);
unlit/sleep current 0.1 mA; self-discharge 3% of nominal capacity per month.
These are assumptions, not measured clone or battery specifications.

Lighting input power mW = N * Iaverage(mA) * Vrail / efficiency.
Lighting battery current mA = lighting power / Vbattery.
Daily use mAh = lit_hours*(lighting current + active other current)
             + (24-lit_hours)*unlit current + nominal_mAh*self_pct/100/30.
Days = usable_mAh / daily_use.
Continuous hours includes the same active and self-discharge assumptions.

At 86 LEDs, targets of 0.1, 0.2 and 0.5 mA average per LED respectively use
approximately 9.8, 19.7 and 49.2 mA from the battery for lighting. Runtime:
roughly 57/30, 31/16 and 13/7 days for 6/12 lit hours per day. None of those
current settings has been demonstrated to provide acceptable legend light.
The purchased battery's true capacity and the clone's actual drain must be
measured. Actual backlight ON time is used; idle-off is not counted twice.

GUIDE COMPARISON DESIGN

Use 24 side-view white emitters as a starting architecture: four sources in
each of six physical row regions. The goal is shorter transport paths and
adjustable extraction. This source count is provisional, not optimized by
simulation or experiment. Compare at equal measured battery input watts.

Candidate family: Everlight BL-3806 (catalogue BL-3806NN1P example 3.8x1x0.6 mm).
The manufacturer describes it for light-guide use. Obtain an exact current
suffix-specific drawing/data sheet, low-current flux curves, and sourcing
before committing. Catalogue flux at a different test current is not proof
of efficiency in this keyboard. JLC availability has not been established.

A full guide for legends belongs beneath the PCB, with extraction patches
and optical apertures aligned to the 86 native LED passages. It needs pin,
solder, diode, component and mount reliefs. The current six source holes are
not sufficient. Merely making the switch plate translucent mostly exposes
the gaps; it cannot be assumed to bypass opaque switch bases into legends.

Keep transport surfaces polished. Use small output patches under the optical
windows, not a uniformly sanded sheet. Use a nonconductive white lower
reflector with controlled air spacing and a black/opaque upper mask outside
the outputs. Match side-source optical axis to guide midplane, near the input
edge without mechanical contact. Bivar recommends close, matched coupling;
our exact gaps and extraction pattern require sample tuning.

Target guide thickness 0.8–1.0 mm only IF all clearances allow it. Current
underside components and pins make a full-case solution uncertain. A 1.5 mm
sample is allowed for the bench, not a statement that the case can accept it.
Never raise the keyboard height or delete battery clearance silently.

An electrical option for 24 side LEDs is four SERIES strings of six with
two dual-channel boost/current-sink drivers, e.g. TI TPS61162A. It supports
single-cell input and PWM, but its DSBGA assembly cost, current programming,
low-load efficiency and true shutdown behavior still need qualification.
Both drivers can share one PWM command if timing/interface is validated.
Do not parallel bare LED strings on a single current regulator and assume
equal current. Do not estimate this series design with the parallel-rail
calculator without converting to measured battery input power.

OPTICAL BENCH COUPONS

All artwork has the same 83.15 x 45.05 mm page origin; actual outer cut is
82.15 x 44.05 mm, inset 0.5 mm. The eight proposed native-window locations
use a 2x4 key grid at 19.05 mm pitch with a provisional north offset 4.93 mm.
These must be checked against the actual switch's LED passage. The pin-relief
pattern is a 180-degree rotation of the current footprint clearances and is
NOT a drop-in alignment to the current V10 PCB. This is loose optical stock,
not a structural switch plate. The source drawing references 1.2 mm aluminum
for switch clip retention; no acrylic clip thickness is approved here.

Files:
  guide-solid-CUT.svg           solid reference light guide outline
  guide-perforated-CUT.svg      same outline, 32 pin/body clearance holes
  guide-*-ETCH.svg              sparse/medium/dense eight-patch extraction
  guide-*-solid.dxf             nominal CUT + ETCH, solid reference
  guide-*-perforated.dxf        nominal CUT + ETCH, pin-relief comparison
  opaque-output-mask-CUT.svg    upper mask; eight 2.1 x 2.8 mm windows
  opaque-output-mask.dxf        same nominal cut paths
  white-backing-CUT.svg         insulating reflector with larger pin clearances

Use the solid guide as an optical control with an opaque mask. Use the
perforated version to measure how the clearances reduce useful output.
Mount actual switches/caps above a suitable independent fixture and align
their native LED windows; the coupon is not intended to carry pressing loads.
The optical bench fixture must allow source height and window alignment to
be adjusted. It is not an electrical PCB or ready-made test keyboard.

Use two opposed side inputs, centered at the guide's short edges. Match the
emitter axis to the material midplane. Preserve polished transport areas.
The eight extraction patches have graded dot diameter increasing with source
distance. The patterns are starting samples, not ray-trace results. Compare
the three patterns and several shallow laser settings using the same input.
Suggested trial etch depth is a few hundredths of a millimetre; establish it
on scrap rather than treating laser power/speed as portable across machines.
SVG is in millimetres. DXF includes millimetre units and CUT/ETCH layers.
No laser kerf, CNC cutter radius/dogbones, toolpath or feeds/speeds are applied.
For CNC, adapt the mask's square corners/tool clearance in CAM. The DXF/SVG
may be used for nominal geometry, not directly as machine G-code.

MEASUREMENT AND ACCEPTANCE

1. Verify the actual Whale optical channel, window orientation and XVX legend
   transmissivity. Use real keycaps including wide keys, not appearance meshes.
2. Sample reverse LTW-C230DS and low-current top LED at several currents, e.g.
   0.1, 0.2, 0.5, 1 and 2 mA with a controlled source. Measure Vf/current/colour.
3. Compare eight direct emitters and the two-input/eight-output guide at equal
   measured battery power. Record converter loss separately from LED power.
4. Use an opaque output mask; glowing unused acrylic does not count. Record
   brightness of the dimmest comparable legend and glare at normal view angles.
5. Initial chosen goals: comfortable readability in a dim room; min/max legend
   luminance >=0.5 across comparable caps; no full-travel interference; no bare
   source glare. A provisional 5–15 cd/m2 night legend target is not a standard
   or a measured specification. Adjust to the user's comfort using a sample.
6. Try to meet those goals at <=10 mA incremental battery draw, to approach a
   month at 12 h/day. If insufficient, record the required power honestly and
   use the shorter runtime. Do not brighten the rendering to imply compliance.
7. Measure clone active/idle/sleep current and battery capacity. A target of
   <=5 uA additional lighting-off leakage is for prototype verification.
8. Use a calibrated luminance instrument, or a fixed-exposure linear RAW camera
   for relative comparisons. Disable auto exposure and avoid clipped pixels;
   a camera comparison does not independently establish absolute cd/m2.
9. Only after selecting the optical winner, make the next full board/case
   revision in a distinct directory. Preserve old V10. Re-run routing/DRC,
   case/PCB/plate/pin fit, RF keepout, power path, thermal and firmware checks.

Firmware reference files illustrate one 20 kHz PWM output and 30 s idle-off.
They are not a complete or compiled firmware package. Automatic USB/battery
brightness policy needs extra behavior, and saved settings can override START.

SOURCES

https://github.com/zmkfirmware/zmk/blob/main/docs/src/components/power-estimate.js
https://github.com/zmkfirmware/zmk/blob/main/docs/src/data/power.js
https://zmk.dev/docs/config/lighting
https://zmk.dev/docs/hardware-integration/lighting/backlight
https://www.ti.com/product/TPS63900
https://www.ti.com/lit/ug/slvubu9a/slvubu9a.pdf
https://www.ti.com/product/TPS61162A
https://optoelectronics.liteon.com/upload/download/DS22-2007-0232/LTW-C230DS.pdf
https://jlcpcb.com/partdetail/liteon-LTWC230DS/C575513
https://www.kingbrightusa.com/images/catalog/spec/APT1608LQWF-D.pdf
https://en.everlight.com/visible_led/category-backlight_led/side_view_product__bl_3806/
https://www.everlight.com/wp-content/uploads/2024/08/2024-2025_Catalogue_0806.pdf
https://www.bivar.com/Files/Content/Handbook-to-Illumination-Design-101.pdf
https://www.kailhswitch.com/uploads/15927/files/CPG1353S01D02-01-data-sheet.pdf

Manufacturer documents retain original ownership/attribution. Source input
hashes in study.json prove that the V10 PCB/manufacturing inputs were not edited.
Rebuild with Python source/build.py; no third-party Python modules required.
