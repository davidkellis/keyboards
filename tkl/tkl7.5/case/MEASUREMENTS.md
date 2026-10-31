# Clone and USB extension dimensions — 2026-09-25

| Dimension | Value | Evidence |
| --- | --- | --- |
| Clone PCB length × width | 33 × 18 mm | User measurement |
| Socket projection beyond PCB edge | 0.84 mm | User measurement; direction explicitly confirmed |
| Clone width in listing drawing | 17.8 mm | Saved TENSTAR drawing; use larger user value |
| End-to-end edge-pad centres | 30.5 mm | TENSTAR drawing; carrier uses 30.48 mm (12 × 2.54) |
| Clone overall thickness / USB axis | Unknown | 4 mm module height and 3 mm axis depth remain model assumptions |
| Male housing length × width | 17 × 11.5 mm | Saved seller drawing; excludes the undimensioned strain relief |
| Male housing thickness | **6.6 mm** | User-supplied dimension; replaces the earlier estimate |
| Female flange width | 25 mm | Seller drawing |
| Female mounting screw centres | 17 mm | Seller drawing; this is **not** the flange width |
| Female body depth | 20 mm | Seller drawing; strain relief extends farther |
| Female height, flange depth, screw thread | Unknown | 6 mm height limit and 3.2 mm clearance holes are provisional |
| Selected cable length | 300 mm | Listing option; excess cable storage remains unverified |

The clone envelope is registered to the centre of the two 13-position edge-pin
rows, assuming equal end margins as depicted. Its 33 mm PCB plus 0.84 mm socket
projection gives a 33.84 mm overall length. The model retains 19 mm width to allow
some clearance around the measured 18 mm PCB. This does not verify auxiliary-pad
registration or connector height.

The earlier estimate of 1.6 mm plastic around the male shell implied about
5.6 mm total height: 2.4 + 2 × 1.6. The 2.4 mm shell height is supported by
[Hirose's USB-C plug specification](https://www.hirose.com/product/p/CL0480-0465-0-00).
Its 8.25 mm width plus the same plastic allowance would be 11.45 mm, consistent
with the seller's 11.5 mm width. This is an inference about an unmeasured moulding,
not proof that its top/bottom plastic thickness equals its side thickness.
The user subsequently supplied **6.6 mm** as the housing thickness, so the
5.6 mm estimate is superseded.

At the current assumed socket axis, the **6.6 mm** housing extends **0.30 mm
into the carrier PCB** and would leave only **0.053 mm of floor** to retain
0.4 mm clearance. That fails the 0.8 mm minimum floor rule.
The corresponding theoretical housing limit is approximately 5.10 mm before
tolerances; the printable model retains the 4.5 mm target, with roughly 1.10 mm
floor. `fit-report.json` records the failed 6.6 mm candidate under
`reported_cable_fit`, separately from the collision-free target model.
`usb_male-reported-6.6mm-gauge.stl` is a dimension gauge for the reported housing;
it is **not a fitting component for the current case**. Do not interpret a passing
mesh/collision check on the 4.5 mm target as approval of the linked cable.

Lowering the socket axis to 3.5 mm below the PCB provides 0.2 mm PCB clearance,
but then recovering the required floor clearance needs a **12.54 mm rearward
move**. A bounding-envelope check puts the module into the solder pins of SW42
(End) and SW49. This simple relocation has not been implemented. The check
screens that one arrangement; it does not establish that every alternative
mounting design is impossible. Accommodating this housing would need a more
substantial change such as a separately supported, recessed module/PCB opening,
which would require new routing and plate/case validation. A slimmer male housing
avoids that redesign. Module/socket height remains an assumption.

The revised rear mount reserves the full 25 mm flange width through the 20 mm
depth as a conservative box. It sits against the vertical rear wall, with
17 mm screw centres. The 3.2 mm holes permit a fit trial; determine the actual
insert thread and suitable screw length before fastening. The flange height,
socket recession through the 2 mm wall, cable bends and strain relief still
need verification. The 300 mm cable's spare length is not represented in the
direct-route envelope; the supplied screenshots do not dimension strain relief.

Sources saved in `../reference/`: `tenstar-dimensions-listing.png`,
`usb-extension-dimensions-listing.png`, and `usb-extension-front-listing.png`.
The [seller listing](https://www.aliexpress.us/item/3256809522717241.html) could
not be fetched by the web tool; dimensions above were read from the supplied
screenshots, not its generated product overview.
