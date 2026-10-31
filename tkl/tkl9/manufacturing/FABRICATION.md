# v9 fabrication and assembly requirements

Prototype quote files; physical/charging/firmware validation remains pending.
Use only this revision's Gerbers, BOM and CPL together.

| Setting | Requirement |
| --- | --- |
| Construction | Two-layer FR-4, 350.76 × 129.19 mm finished outline |
| Thickness | 1.6 mm |
| Copper | 1 oz outer copper |
| Finish / solder | OSP; lead-free SMT and any through-hole soldering |
| Mask / silkscreen | Green / white |
| Minimum design track / copper clearance | 0.18 mm; routed tracks nominally 0.20 mm |
| Vias | Through, minimum 0.30 mm drill / 0.60 mm land; tent both sides |
| Filled, copper-capped or via-in-pad processing | Not requested; no SMT paste land contains a via drill |
| Impedance / stackup | No controlled impedance required on the carrier; USB and RF are on module |
| Electrical test | Ordinary open/short flying-probe test |
| Assembly | Bottom only: 98 SMT components plus J1 through-hole connector |
| User-installed | U1 module and 83 key switches; battery is off-board; direct rear module USB |

All copper keepouts beneath/beyond U1's antenna must remain clear. The footprint
uses a historical nice!nano/ProMicro pin geometry, with three auxiliary GPIO pads.
The exact clone is supplied by the user and is not a JLC substitute part.

LED1–LED6 are reverse-mount LTW-C230DS, emitting through their optical slots.
Confirm the insertion/support-fixture process and polarity with the factory.
Any required reverse-LED tooling is not included in an assumed price.
J1's body is installed from the bottom; pin 1 is battery positive. SW87's actuator
faces the rear edge. Confirm diode cathode orientation and component rotations
against the assembly drawing; CPL angle conventions need factory review.

If assembly rails/tooling holes are needed, let JLC add them outside the finished
outline and remove them before shipment. Do not move or enlarge the finished PCB.
No module, battery, keycaps, stabilizers or case is in the JLC BOM.
This package does not program or function-test the keyboard.
