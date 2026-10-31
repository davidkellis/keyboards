# Slim USB-C male sourcing — 2026-09-25

The user's previously selected extension has a reported 6.6 mm male housing.
It fails the current mounting geometry; see `../case/MEASUREMENTS.md` and
`../case/fit-report.json`. The slim fit model still targets 4.5 mm. No cable
selection or production geometry was changed by this sourcing review.

## User requirement: complete cable, panel-mounted USB-C female

The user clarified that they do **not** want to assemble a cable. Both ends
must already be connected to the ribbon, with a panel-mounted USB-C female.
The separate Adafruit parts below are therefore not the proposed solution.

### Closest complete retail candidate: Atlavox / CAZN

[Atlavox USB-C Waterproof Bulkhead Extension Ribbon Cable, 20 cm](https://atlavox.com/products/usb-c-waterproof-bulkhead-extension-ribbon-cable?variant=52456432009490)
is a complete male-to-female ribbon extension with a threaded panel socket,
nut, seal and cap. Select **20CM**, SKU **CA-USBW2**. The live Shopify product
endpoint reported this variant available at **$10.25**; the 10 cm version
was $9.89. The text-only page also contains a generic sold-out notification
template, so variant data was checked directly:
`https://atlavox.com/products/usb-c-waterproof-bulkhead-extension-ribbon-cable.js`.
The retailer is in Rhode Island; its current banner notes a 2–3 day
fulfillment delay. Shipping and tax have not been quoted.

The seller describes USB 3.1 data, including firmware flashing. Its photos
show the male plug without a bulky molded housing, but neither its drawing
nor the matching CAZN E10 threaded FPC catalogue drawing dimensions the
male plug thickness. Do not assign the Adafruit part's 3 mm dimension to it.

[Seller mechanical drawing](https://cdn.shopify.com/s/files/1/0872/0957/4674/files/CAZNDRAWING.png?v=1771260240)
shows a 15.8 mm D-shaped panel opening, 15 mm across its flat, a **20.5 mm
flange**, and a nut **20 mm across flats / 22.5 mm across corners**. This is
not a replacement for the existing 25 mm-wide, 17 mm screw-spacing flange.
At 20.6 mm case height, the round flange leaves essentially no vertical
margin; internal nut/PCB clearance also needs redesign and checking.
**Available as a finished cable, but not established to fit this case.**

### Other assembled options investigated

- [Elecbee EB-504-4027-H, 20 cm](https://www.elecbee.com/en/product-detail/usb-type-c-female-panel-mount-receptacle-to-male-with-20cm-fpc-cable-ip67-ip68-waterproof_47145):
  listed in stock at $5.14 on the opened product page, with claimed dispatch
  in 1–3 business days. Other category pages show $5.47. Shipping is extra.
  This is another round bulkhead FPC assembly; no complete dimensioned fit
  was established. Price/dispatch claims are seller claims, not a quote.
- [Premier PCM-S-0659, 20 cm](https://www.premier-cable.store/products/panel-mount-usb-3-1-type-c-fpc-cable):
  $20 before tax/shipping, live product variant marked available. Its
  drawing does not dimension the male housing; it also has round panel
  hardware. Not a verified mechanical substitute.
- [Eternalstar rectangular-flange flat cable](https://www.eternalstarcable.com/products/fpc_ribbon_cable_264157/Short_USB_C_Cable_Right_Angle_Type_C_Fast_Charging_Cord_Flat_Type_USB_C_Male_to_USB_a_Male_Cable_90degree_USB_C_Extension_Short_Cable_1.html):
  the manufacturer's dimension photos show the straight CMST male housing
  **6 mm thick**, above the target. Its 4.3 mm figure belongs to an angled
  configuration with another 13 mm dimension, not a 4.3 mm straight plug.

A complete compact male-to-female ribbon extension could alternatively be
panel-mounted using a printed retaining bracket integrated into the case.
That would require only mechanical installation of an already assembled
cable, but a specific cable's connector dimensions and fit remain to be
verified. No bracket or revised rear opening has been generated here.

## Earlier thin male adapter research — excluded by user requirement

[Adafruit 4108, DIY USB Cable Parts — Straight Type C Plug](https://www.adafruit.com/product/4108)
was listed at **$4.95 and in stock** when checked. The published overall
dimensions are **23 × 17 × 3 mm**. This is a male connector on a small ribbon
adapter PCB, not a replacement plastic shell and not a complete extension.
Adafruit explicitly excludes the ribbon and other endpoint. Its description
reports USB use with a Circuit Playground and computer, but provides no
connector-axis mechanical drawing or full pinout.

[Adafruit 3561, 20 cm ribbon](https://www.adafruit.com/product/3561) was listed
at $1.95, in stock, and 10 mm wide. A compatible USB-C female endpoint has not
been established. Do not assume an off-brand ribbon adapter has the same
pinout or contact orientation. The CC path and USB data operation need
verification for the complete assembly, including both external plug orientations.

### Preliminary mechanical screen

Using the existing board geometry and assumed socket axis 3 mm below the
carrier, a conservative **23 × 17 × 3 mm rectangular envelope**, with all
23 mm placed outside the socket (no mating insertion deducted), gives:

- Board-frame bounds: X 279.19–302.19, Y 43.69–60.69, Z −4.5–−1.5 mm.
- Lowest corner: approximately 0.771 mm above the nominal 1.2 mm case floor.
- Carrier PCB clearance: 1.5 mm.
- No intersection with the exported underside solder-pin cylinders or JLC
  component bounding boxes in this simple screen.

This is conditional on centering the 3 mm thickness on the assumed socket
axis. It does not validate the actual connector offset, mounting hardware,
insulation, ribbon folds/routing, rear receptacle, or the full CAD assembly.
The clone's socket-axis height remains unmeasured. A 10 mm flat ribbon needs
a new route; the current route models a round cable no larger than 3 mm.

## Complete extension candidate, housing dimensions unverified

[Permanent Industry / FPV Solution straight USB-C male-to-female ribbon cable](https://fpv-solution.com/product/soft-slim-usbc-cable-fpv-thin-ribbon-fpc-cable-usb-type-c-male-to-usb-type-c-female-receptacle-straight-for-sync-and-charging-fpv-usb-type-c-2-0/)
is offered for $12–18 with multiple lengths including 20 cm. The seller
describes USB 2.0 data and 5 V power. Its **0.5 mm thickness is the ribbon,
not the male housing**. No male housing thickness or variant-specific stock
confirmation was obtained. This is a candidate for measurement, not a
verified-fit purchase recommendation. The female end would need a printed
retainer instead of the current 17 mm screw-spacing flange mount.

## Rejected dimensioned alternative

[ROLINE 11.02.9079 manufacturer drawing](https://www.secomp-international.com/media/pdf/s11/11029079_en_data_scmp.pdf)
shows a **5.81 mm male housing**, although the flat cable is only 2.5 mm and
the mating metal shell is 2.4 mm thick. It exceeds the current 4.5 mm target;
the slim cable description alone does not establish a suitable plug.

Prices exclude shipping and tax. No purchases or seller messages were made.
