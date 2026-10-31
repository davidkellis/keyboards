# v7 source material

`nordic-config7.kicad_pcb` is a KiCad 10 import of Nordic Semiconductor's
nRF52840-QIAA reference layout 1.3, configuration 7 (four-component RF match).
The original Altium file was imported with `kicad-cli pcb import --format altium`.
The controller, crystals, decoupling, both DC/DC stages and matching network
are transformed together onto the keyboard underside.

- [Nordic reference layout downloads](https://www.nordicsemi.com/Products/nRF52840/Compatible-downloads)
- [Original reference archive](https://nsscprodmedia.blob.core.windows.net/prod/software-and-other-downloads/reference-layouts/nrf52840/nrf52840-qiaa-reference-layout-1_3.zip)
- [nRF52840 pin assignments](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/pin.html)
- [nRF52840 power/regulator limits](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/power.html)
- [TI BQ24072 datasheet](https://www.ti.com/lit/ds/symlink/bq24072.pdf)
- [Lite-On reverse LED dimensions and polarity](https://docs.rs-online.com/6872/0900766b80e28fac.pdf)
- [BAT46W low-drop matrix diode](https://www.diodes.com/datasheet/download/BAT46W.pdf)
- [Diodes DMN2056U MOSFET datasheet](https://www.diodes.com/datasheet/download/DMN2056U.pdf)
- [C&K PCM12 switch](https://www.ckswitches.com/media/1424/pcm.pdf)

`matrix-source.kicad_pcb` preserves the checkpoint layout, with routing and
zones removed, as the deterministic input for the placement builder. Its old
controller circuitry is discarded by that builder. It is not a fabrication file.

`mcu-pinmap.json` records physical nRF package pad assignments.
`firmware-pins.json` maps matrix/backlight signals to MCU GPIOs. Logical ROW8
is absent; compact it out when defining an eleven-row ZMK matrix.

Reference modifications: mirror the complete block onto B.Cu, convert local
blind vias to through vias, remove unused GPIO stubs, rename selected GPIO nets,
replace the reference coupon boundary with the keyboard perimeter, and connect
a U.FL receptacle directly at the RF feed endpoint. Keep the imported RF copper
exclusions. Via-in-pad holes require filling, planarization and copper capping;
tenting alone is not suitable under the package lands.

The RF/crystal/regulator copper was also compared geometrically with a fresh
transformed reference placement after routing cleanup. No original copper
was lost on RF, ANT, RF_MATCH, DCC, DCDC_FILTER, DCCH, DEC1, DEC2, DEC3,
DEC4_6, DEC5, DECUSB, XC1 or XC2. The manual USB pair was preserved as well.
This is a geometry check, not an RF simulation or a substitute for prototype
measurements on the actual stackup.
