# v7 firmware and prototype bring-up

No firmware image has been built or flashed for this revision. Use the
[schematic](manufacturing/schematic.pdf) and
[GPIO map](reference/firmware-pins.json) when creating a custom ZMK board.

## Electrical configuration

The MCU is powered at VDDH through SW87. VDD_NRF is the nRF's regulator output
and must remain **1.8 V**, the factory REGOUT0 default. Both internal DC/DC
stages are populated. Do not install firmware/bootloaders that program REGOUT0
to 3.3 V: Nordic's high-voltage regulator needs VDDH at least 0.3 V above its
selected output, which would prematurely exclude much of the battery range.
Use a programmer that supports **1.8 V target reference and I/O**.

J2 is the six-pad TC2030-IDC-NL programming interface:

| Pin | Signal |
| --- | --- |
| 1 | VDD_NRF / target reference, 1.8 V |
| 2 | SWDIO |
| 3 | RESET / P0.18 |
| 4 | SWCLK |
| 5 | GND |
| 6 | Unconnected |

Power the target through its normal input; J2 pin 1 is a reference, not a
3.3 V power input. An unprogrammed nRF does not provide a USB bootloader.

| Matrix signal | GPIO |
| --- | --- |
| COL0, COL1, COL2 | P0.06, P0.08, P0.17 |
| COL3, COL4, COL5 | P0.20, P0.22, P0.24 |
| COL6, COL7, COL8 | P1.00, P0.11, P1.04 |
| ROW0, ROW1, ROW2 | P1.06, P0.13, P0.15 |
| ROW3, ROW4, ROW5 | P1.11, P1.13, P1.15 |
| ROW6, ROW7 | P0.02, P0.29 |
| ROW9, ROW10, ROW11 | P1.01, P1.02, P1.07 |
| Backlight enable/PWM | P0.31, active high |

There is no logical ROW8. Compact the eleven used rows into firmware's row
array and map each switch accordingly. The diode anode goes to the switch and
column; the cathode goes to ROW. A straightforward scan drives one row low
and reads columns with pull-ups; inactive rows should not drive high into a
pressed-key path. Confirm the chosen scanner's diode-direction setting rather
than copying it from a different keyboard. Check simultaneous key presses as
well as individual keys. Schottky reverse leakage increases with temperature;
the prototype should be checked across its intended indoor operating range.
The [matrix CSV](manufacturing/matrix-map.csv) gives every switch's row,
column, compact row index and position on the PCB.

Enable the 32 MHz and 32.768 kHz crystals with the listed load capacitances.
The HF crystal budget is 10 ppm initial + 20 ppm temperature + 3 ppm/year
aging, before board/load errors. Keep BLE packet payloads at or below 200
bytes for Nordic's 40 ppm clock budget; larger packets require a tighter
30 ppm budget. Measure clock error on the prototype and adjust load capacitors
if needed. The LF crystal uses the 9 pF variant; use a conservative sleep-clock
accuracy declaration that accounts for its parabolic temperature drift.

Backlight LEDs run from VDDH through individual 1 kohm resistors. They are
switched together by Q1. Drive P0.31 low before System OFF and initialize it
low at boot. There is no battery ADC divider/fuel gauge in this revision, so
accurate battery percentage reporting is not provided by the hardware.

## Battery candidate and temperature hold

The mechanical prototype targets a protected LP7065125 10 Ah pouch. See
[the battery specification](case/BATTERY.md). Its current drawing permits
charging at +10–45 °C, while the fitted BQ24072 with a direct 103AT-2 NTC
has a nominal 0–50 °C window. This candidate is **not electrically approved**
until the pack specification and charge-temperature protection match. The
plain series/parallel bias network in TI's data sheet only widens the window;
a narrower window needs another validated solution. Do not bypass the NTC.

## Initial checks

1. Inspect component orientation, LED slots and the USB/slide-switch overhang.
   Obtain X-ray inspection for the controller/charger exposed pads. Check for
   supply shorts before attaching a battery.
2. With the battery disconnected, attach a known 5 V source and current-limit
   the first power-up. Verify VBUS, approximately 4.4 V VSYS, and 1.8 V VDD_NRF
   with SW87 on. Check the rail with SW87 off as well. Start with backlights off.
3. Read the chip over 1.8 V SWD, verify REGOUT0, then load a minimal diagnostic
   image. Verify both crystals, reset and USB enumeration in both plug
   orientations before loading full keyboard firmware.
4. Use the exact protected 1S pack, with a cell-mounted 103AT-2-compatible NTC
   on J5. Verify charge current, TS cold/hot/open inhibition, 4.2 V termination,
   switch-off charging and battery-only operation. Measure charger and cell
   temperatures during a long charge inside the intended enclosure.
5. Exercise all 86 keys and multi-key chords. Check LED polarity, brightness
   and PWM, BLE range with the selected 2.4 GHz 50-ohm U.FL antenna, reconnect,
   USB/wireless transitions, sleep/wake and battery current in System OFF.
6. Check USB signal integrity and RF output/matching on the fabricated stack.
   Confirm the battery, coax and connectors fit without contacting exposed
   underside parts. Update the inherited case before committing to a batch.

The fixed 500 mA charger setting does not follow USB enumeration/suspend power
states; see [fabrication operating conditions](manufacturing/FABRICATION.md).

Sources: [Nordic power specification](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/power.html),
[Nordic crystal requirements](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/clock.html),
[TI charger specification](https://www.ti.com/lit/ds/symlink/bq24072.pdf),
[HCI LF crystal specification](https://datasheet.lcsc.com/datasheet/pdf/41c9d4b73ec774d5e861f34b007ace22.pdf?productCode=C2848222).
