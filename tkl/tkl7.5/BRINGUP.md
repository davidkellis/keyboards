# v7.5 prototype bring-up

No firmware has been built or flashed and no physical electronics have been tested.
The clone photograph establishes the apparent pin labels, not its hidden circuit,
charging current, connector polarity, dimensions or reliability.

1. Print the case/PCB/module/plug gauges. Measure the actual module and cable.
   Match the orientation in the assembly drawing: USB points left; components
   face the floor; the antenna is on the right. Use a 0.5 mm insulating spacer
   and short soldered pins/wires, not tall sockets. Trim protruding pins above
   the keyboard PCB flush enough to retain the plate's 0.7 mm under-plate gap.
2. Check all module pads against its labels and continuity before installation.
   The three auxiliary connections are 101, 102 and 107. P0.09/P0.10 are edge
   pins, and must be enabled as GPIO rather than NFC in firmware. Consult the
   [candidate GPIO map](reference/firmware-pins.csv), schematic and matrix CSV.
3. Before fitting the module, check carrier supply resistance/polarity. J1 pin 1
   is positive; pin 2 is ground. SW87 connects VBAT to BAT_SW. Module pads 24
   and 29 are battery positive; 3, 4, 23 and 28 are ground; 21 is switched VCC.
   Never put 5 V USB power onto BAT_SW. There is no second charger to parallel.
4. Power the module from USB without a battery, initially with lighting off.
   Confirm approximately 3.3 V VCC, USB data/bootloader operation through both
   extension-plug orientations and the carrier's supply current. Charge-only
   extensions are unsuitable. Firmware must match the exact clone/bootloader.
5. Verify actual charging current with the intended protected 1S 4.2 V pack.
   Keep the default low setting until characterized. SW87's 300 mA rating means
   a 500 mA boost setting is not permitted. OFF disconnects the battery from
   the charger too; USB can still run the module. The carrier has no cell NTC
   input: establish suitable cell-temperature protection before battery use.
   Verify charge termination, hot/cold inhibition where implemented, and
   temperatures during a complete charge in the closed enclosure.
6. Load a custom ZMK shield/keymap for all 86 keys. Eleven row lines and nine
   columns consume 20 GPIO; BL_EN uses the final pin. ROW8 is absent. Diode
   cathodes face ROW, so check scanner polarity and multi-key chords explicitly.
   A UF2 bootloader alone is not keyboard firmware. Test sleep/wake, reconnect
   and battery reporting; clone circuit variants may need a custom board definition.
7. Enable the module's switched VCC and test PWM on P0.31. The six 1k resistors
   give a deliberately low initial load at 3.3 V. Measure brightness/current
   before changing them. Set BL_EN low before sleep. Test BLE range in the case
   with the actual battery and USB cable; keep metal away from the antenna.

The source includes copper keepouts under/beyond the module antenna. A metal
plate or foil-lined case would need a separate RF review. The fit case/plate
are intended as nonconductive printed prototypes.

The module charger replaces the former BQ24072/NTC implementation. This revision
does not inherit the parent's charge current, timers or cell-temperature safety
validation. It also does not establish that a 10,000 mAh pack fits the case.
