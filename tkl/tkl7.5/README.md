# TKL v7.5 — nRF52840 module carrier

New isolated revision derived from v7.4, using the v6 module footprint and
the user's TENSTAR ROBOT ProMicro nRF52840 clone photograph. All 86 switch
positions, switch drills, board outline and 1.6 mm thickness are preserved.
The module remains between End and Up, moved 2.7 mm rearward from v6 for clearance.

**Prototype, not yet approved for production.** Electrical CAD checks and the
specified mechanical envelopes can be validated in software; the actual clone,
cable, battery/charging, firmware, RF and stabilizer travel need physical checks.

- Two copper layers; all 102 JLC placements on the bottom, in seven BOM groups.
- Ordinary 0.30 mm drill / 0.60 mm via lands, tented; no filled/capped vias.
- OSP and lead-free assembly retained. Compare a complete Economic versus
  Standard quote; neither eligibility nor a new delivered price is claimed yet.
- User installs the module and switches. The module's integrated USB, antenna,
  regulator and charger replace the carrier's discrete controller/power block.
- USB uses a **data-capable** male-to-female extension cable, with a rear case
  receptacle and a printed cradle; no USB differential traces on the carrier.
- Case outside remains 355.56 × 133.352 mm, with 7.3 / 20.6 mm front/rear lips.

## Files

Open [KiCad PCB](kicad/keyboard.kicad_pcb) and [schematic](kicad/keyboard.kicad_sch).
See [front copper](front.svg), [bottom copper](back.svg),
[validation summary](validation/summary.json) and [independent audit](validation/revision-audit.json).

The [case guide](case/README.md) identifies printable models, cable limits and
fit assumptions; the [module/cable preview](case/module-fit.png) shows their location.
The [measurement record](case/MEASUREMENTS.md) includes your 33 × 18 mm clone and
0.84 mm socket overhang, and the cable's 25 mm flange / 17 mm screw spacing.
The cable's reported **6.6 mm male housing** fails the current floor and PCB
clearances. The main fit model retains a **4.5 mm slim-plug target**; a separate
6.6 mm housing gauge and failed-fit assessment document the supplied cable.
The [assembled STEP](case/fit-assembly.step) includes the module,
plug, cable route and rear receptacle envelopes. Start with a fit print before
fabricating the electronic PCB. The [bare PCB STEP](case/pcb-bare.step) contains
the real board outline/drills; the populated model uses approximate body envelopes.

For a quote use the matched [Gerbers](manufacturing/tkl-v7.5-gerbers.zip),
[BOM](manufacturing/jlcpcb-bom.csv), and [CPL](manufacturing/jlcpcb-cpl.csv).
Read [fabrication requirements](manufacturing/FABRICATION.md) and
[ordering notes](manufacturing/ORDERING.md) first. These files exclude U1 from
JLC assembly; the user supplies and solders the clone.

## Changes to power and lighting

J1 → SW87 → the module's battery-positive pads. SW87 OFF disconnects both
battery operation **and charging**. USB can still power the keyboard with the
switch OFF. The former BQ24072 power path and external cell-NTC connector are
absent; do not transfer their charging settings or temperature claims to this PCB.

Keep the module at its verified default low charging current. SW87 is rated
300 mA; **do not enable a genuine nice!nano's 500 mA charge boost** through this
switch. Confirm the actual clone charge IC/current and protection against
charging outside the selected cell's temperature range before using a battery.
The large pack remains unselected. See [bring-up](BRINGUP.md).

The six original white reverse LEDs and common PWM MOSFET are retained. Their
1 kohm resistors now run from the module's switched 3.3 V rail, so initial
brightness is lower than the parent board's battery-powered setting. This keeps
the load conservative until the exact clone regulator and LED current are measured.
Do not rely on software alone to correct an unsuitable charging circuit.

## Routing and assembly cost

The user selected the cheapest practical approach: one component assembly side,
with traces allowed on both copper layers. This avoids extra zero-ohm jumpers.
Compared with v7.4, JLC placements fall from 142 to 102 and BOM groups from 31
to seven. The radio/USB/charger chips and their small support parts move onto the
user-installed module. Reverse-LED fixture review remains necessary.

No new JLC quote has been submitted for this revision. The preceding
[cost study](../research/module-controller-2026-09-25/README.md) used old quote
line items, not these new manufacturing files. Exact stock, assembly fees,
shipping and any remaining fixture charges must be requoted.

## Rebuild and provenance

The primary artifact is the checked, routed PCB. Do not run `build_board.py`
on later edits unless deliberately replacing this revision's placement/routing.
It derives a fresh placement from v7.4 and v6, then discards this revision's tracks.
All scripts live in [scripts](scripts/README.md). Mechanical generators are local
copies so changes to v7.5 do not alter old case generators.

The audit checks hashes of 1,602 files in v7/v8/v7.3/v7.4 and the exact parent
switch/drill geometry. Those previous revisions are preserved. The completed
route combines Freerouting with checked A* connections and trimmed unused stubs.
