# v9.3 — finished plate surface with concealed pin clearances

This mechanical revision closes v9.2's exposed controller slots and battery
connector opening. Blind underside pockets leave a continuous, flat top with
a 0.9 mm roof. Six flush translucent inserts turn the LED openings into small
round light windows. Installed M2 screw heads remain visible and recessed.
There is no separate top cover or raised frame on the plate.

The v9.1 PCB, circuitry, switch positions, twelve mounting holes and M2 × 5 mm
screw/DIN 934 nut stack are unchanged. The footprint remains 355.56 × 133.352 mm
and the outside height remains 7.3 mm at the front / 20.6 mm at the rear.
The **v9.2 base is reusable**: all three base STL files are byte-identical.
v9.2 and earlier revisions are preserved.

The controller must be installed **before** the plate/switch assembly. Trim the
two J1 battery-connector tails and controller pins so the complete pin/solder
envelope projects no more than **1.0 mm above the PCB**. Blind pockets provide
another 0.3 mm clearance. Later top-side controller-pad service requires
removing the plate, which may require desoldering switches.

- [Print and assembly guide](case/README.md)
- [Complete print kit](case/tkl-v9.3-print-kit.zip)
- [Small fit coupons](case/tkl-v9.3-fit-coupons.zip)
- [Electrical bring-up](BRINGUP.md)
- [Manufacturing compatibility](manufacturing/README.md)

Print the rear-corner plate sample and one light-window coupon before the full
plate. Use clear/translucent material for the six inserts and attach their
flanges underneath with compatible adhesive. Actual brightness, surface finish,
pin clearance and flex/rattle still need physical trials. The modeled geometry
does not establish optical or electrical performance.
