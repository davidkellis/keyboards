# V11 prototype tests

Test the unmounted prototype on an insulating surface before fitting a battery,
plate or key switches. Do not infer functional success from ERC/DRC alone.

1. Inspect LED polarity, the reverse slots, U2 pin orientation, 100 ohm R10,
   1 Mohm R9/R11, 60 V D87 and 50 V C1/C2. With power off, check that BAT_SW,
   LED_HV and GND are not shorted. Check battery connector polarity separately.
2. Before installing the clone, power BAT_SW from a current-limited 3.7 V bench
   supply, with common GND and CTRL/BL_EN low. Start with a low supply-current
   limit, then raise only as needed for startup. Verify the driver stays off.
3. Apply a 3.3 V logic, 20 kHz PWM signal to BL_EN. Begin at 10%, then 25%,
   50% and 100%. Measure R10 voltage: approximately 20, 51, 102 and 204 mV.
   I_LED = measured voltage / 100 ohm. Do not connect LED_HV to a module pin.
4. Measure LED_HV, supply current, output ripple, boost-switch ringing and
   inductor startup peaks. Repeat at 4.2, 3.7 and 3.0 V; component ratings and
   effective C2 capacitance under DC bias must hold. The inductor's normal low
   load is not a guarantee of acceptable startup current. Check actual power
   switch current including charging; SW87 is rated 300 mA.
5. Test with ten LEDs first. Then disconnect power, wait 30 seconds and verify
   LED_HV <5 V; remove LED7–LED10 and bridge each pad pair with insulated wire.
   At the same PWM duty confirm R10 voltage/current is unchanged and supply
   power drops. Record ten- and six-source results. Never bypass R10 or all LEDs.
6. Refit ten LEDs if needed. Install the clone, using the existing v10 matrix
   mapping and the new lighting PWM period of 50 us. Confirm off/boot state,
   idle-off, BLE scan with lights on, USB and charging with the actual protected
   cell. Keep the clone charger at its verified low/default rate.
7. Hold an acrylic coupon above the PCB at the existing plate height. Compare
   clear acrylic, localized optical coupling features, and sparse extraction
   patches. Keep the main sheet clear; do not begin with full-surface frosting.
   The ETCH layer marks entry trial areas, not a finished extraction pattern. Use the
   actual Whale switch and XVX shine-through cap. Compare legends, not only
   plate glow. Lock camera exposure and white balance; avoid saturation.
8. Test ten versus six at equal per-LED current, then at comparable subjective
   readability. Fewer LEDs save lighting power at equal current but may need
   increased brightness. Measure the complete keyboard's battery-side current
   to calculate runtime. Software estimates are not an optical result.
9. Verify each switch clips and bottoms out, the acrylic does not crack, and
   stabilizers travel correctly. Check added parts against the chosen case and
   battery. The new acrylic sheet still needs its own retention design if used
   with the v10 hidden-mount upper, which had the plate integrated into it.
