# v9.1 fabrication and assembly requirements

Prototype files. Use this revision's Gerbers, BOM and CPL together.

| Setting | Requirement |
| --- | --- |
| Construction | Two-layer FR-4, 350.76 × 129.19 mm finished outline |
| Thickness / copper | 1.6 mm / 1 oz outer copper |
| Finish / solder | Lead-free HASL; lead-free assembly solder, including any through-hole work |
| Mask / silkscreen | Green / white |
| Minimum design track / copper clearance | 0.18 mm |
| Vias | Through, minimum 0.30 mm drill / 0.60 mm land; tent both sides |
| Mounts | H1–H12: 2.5 mm non-plated through holes; do not plate or omit |
| Filled, copper-capped or via-in-pad processing | Not requested; no SMT paste land contains a via drill |
| Impedance / stackup | No controlled impedance required on carrier; USB and RF are on module |
| Electrical test | Ordinary open/short flying-probe test |
| Assembly | Bottom only: 98 SMT components plus J1 through-hole connector |
| User-installed | U1 clone module, 83 key switches, 12 M2 screws/nuts, case, keycaps and stabilizers |

Keep the mounting-hole copper exclusions and antenna exclusion clear. Mounting
holes and their hardware are excluded from the assembly BOM/CPL. The exact clone
is supplied and installed by the user, with its USB socket facing the rear.
No battery, controller module or mechanical hardware is supplied by JLC.

LED1–LED6 are reverse-mount LTW-C230DS, emitting through their optical slots.
Confirm polarity and the reverse-LED process/fixture with the factory. Any
required reverse-LED tooling must be quoted; it is not included in an assumed
price. J1's body is on the bottom; pin 1 is battery positive. SW87 faces the rear.
Review all CPL rotations against the assembly drawings before production.

Request Economic bottom-side assembly if JLC accepts the reverse LEDs and J1.
Do not add paid rail removal by default. If the factory requires assembly rails,
retain the specified finished outline and obtain the proposed breakaway/rail
arrangement for review. The case requires rails to be detached before fitting.

This package does not program or function-test the keyboard. Physical module,
switch, stabilizer, keycap and mounting tests remain necessary. The PCB is a
prototype, not hardware validated by the CAD or electrical rules checks.
