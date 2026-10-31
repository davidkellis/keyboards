# V11 backlight integration reference

The matrix pin assignment is unchanged from v10. BL_EN is still module pad 20 /
nRF52840 P0.31, active high. V11 connects that signal to TPS61169 CTRL directly.

Merge the supplied reference overlay/config into the actual board/shield files;
they are not a complete compiled firmware. Set the PWM period to **50 us**
(20 kHz), within TI's 5–100 kHz dimming range. At 100% the 100 ohm R10 sets about
2.04 mA; at 25% the ideal target is about 0.51 mA. Verify actual low-brightness
linearity. TPS61169 averages PWM internally into a DC current reference.

Keep CTRL low at boot and while idle/sleeping. Check the actual sleep pin state;
do not assume that low-power pin configuration alone guarantees it. R9 and the
driver's internal pull-down provide a defined off state when the GPIO floats.
Existing saved ZMK brightness settings can override the suggested 25% startup.

The documented six-LED wire-bypass conversion needs no firmware change. Reducing
count does not automatically increase current in the remaining LEDs. The driver
adjusts voltage to the shorter string instead.
