# Battery size and capacity within the fixed thin case

The fixed outside footprint is **355.56 × 133.35 mm**. The assembled case
**including its cover** is **7.3 mm high at the front and 20.6 mm at the rear**.
Switches and keycaps project above those heights. Keep these dimensions;
do not extend the case behind the keys or raise its front/rear lips.

## Current shopping envelope

To use more of the available space, the battery bay now runs across the rear
of the keyboard. Dimensions are **across keyboard × front-to-back × thickness**:

| Item | Dimensions |
| --- | --- |
| Finished protected-pack body target, including wrapping/PCM/tolerances | **up to 264 × 50 × 5.5 mm** |
| Larger volume kept clear in the CAD model | **270 × 52 × 6.3 mm** |
| Padding below that volume | **0.5 mm** |
| Case floor beneath the battery | **1.2 mm** |

A pack can be shorter than 264 mm. For example, a **100 × 50 × 5 mm** pack
fits within this envelope. Do not combine the length/depth limits of another
bay with this thickness: the PCB slopes downward toward the front, and switch
pins and electronics reduce the available height. A pack that is 65–70 mm
deep reaches much farther forward and must be thinner.

The reserve starts at case coordinates **x=6, y=78.5, z=1.7 mm** and ends at
x=276, y=130.5, z=8 mm. Its origin is the front-left outside case corner on the
bottom surface. PCB support locations and battery locators are regenerated
around the new bay. The long rear span requires a physical flex/typing test;
collision-free CAD does not establish stiffness or final fastening.

The reserve provides **0.8 mm additional thickness**, 6 mm additional length
and 2 mm additional depth beyond the body target. This is provisional space,
not a pack manufacturer's approved expansion specification. The free lead
and connector must route outside the pack body towards J1 on the right.
Check the lead length, insulation, adhesive, expansion specification and
actual fully charged maximum dimensions before purchasing a final pack.

The earlier central 135 × 68 mm bay could only reserve 4.8 mm height in this
thin case, giving a 127 × 65.5 × 4 mm provisional body target. The new narrow,
longer bay uses the deeper space near the rear. It is not a claim that
264 × 50 × 5.5 mm is the mathematically largest possible battery of every shape.
It is a practical rectangular envelope checked with the modeled electronics.

## Capacity and actual purchase candidates

**No final battery has been selected. Capacity cannot be calculated from the
case dimensions alone.** These seller listings were checked on 2026-09-24;
their capacity claims have not been independently measured.

| Candidate | Advertised body and capacity | Purchase/fit status |
| --- | --- | --- |
| [EHAO12 on eBay, item 112417470757](https://www.ebay.com/itm/112417470757) | 100 × 50 × 5 mm; 3.7 V, **4,000 mAh** | Single-unit retail listing, more than 10 shown available, US delivery offered. PCM and 4.2 V charging stated. **Description also says ±2 mm**, so a guaranteed fit is not established; confirm actual maximum body dimensions. Charge limit 0–45 °C. |
| [Polar Tech 5050100 with PH2.0](https://www.polartech.com.au/products/ph2-0-jst-connector-5050100-universal-5000mah-3-7v-rechargeable-li-ion-lithium-polymer-battery-1) | 100 × 50 × 5 mm; 3.7 V, **5,000 mAh** | Highest-capacity single-pack retail candidate found within the envelope; **preorder**, advertised 1–2 weeks, US battery delivery unconfirmed. Capacity/protection/maximum-size specifications need confirmation. |

The wide bay has room in principle for two approximately 100 × 50 × 5 mm
cells arranged end-to-end across the keyboard. A **supplier-assembled,
protected 1S2P pack** could therefore target **8,000 mAh** from two 4 Ah cells,
or **10,000 mAh** from two genuine 5 Ah cells. These are packing concepts and
capacity arithmetic, not verified products. The complete assembly, PCM,
interconnects, wrapping and manufacturing tolerances must fit the stated body
envelope. Do not treat two independently protected retail packs and a Y cable
as an approved assembly. A matched, protected pack needs its own supplier
specification and electrical/thermal review.

**A stocked, ready-to-connect 8–10 Ah pack within this envelope has not been
verified.** For single-pack sourcing, 4 Ah is a stocked lead but its stated tolerance
needs clarification; 5 Ah is a preorder candidate. Neither is a proven global
maximum or an approved purchase.

## Rejected or unconfirmed larger packs

- [DNK9858102 10 Ah drawing](https://www.dnkpower.com/wp-content/uploads/2023/11/DNK9858102-3.7V-10000mAh-Lipo-Battery-Specification.pdf):
  nominal finished body **104 × 58 × 9.8 mm**. Even pushed to the rear wall,
  ignoring all underside parts/supports, its front edge has only **7.49 mm**
  below the bare PCB above the padded floor. Its 9.8 mm thickness fails that
  optimistic bound by **2.31 mm**. Moving it sideways cannot fix this.
- [Meshnology 10 Ah](https://meshnology.com/products/3-7v-10000mah-lipo-battery-with-usb-charger-protection-for-arduino-esp32-drone):
  115 × 63 × 11 mm; too thick.
- [Mkfrobotics eBay 10 Ah](https://www.ebay.com/itm/175680781212):
  112 × 65 × 8.8 mm with stated ±2 mm tolerance; too thick.
- [AKZYTUE Amazon B0FBRGNCJF](https://www.amazon.com/dp/B0FBRGNCJF):
  100 × 60 × 11 mm; too thick.
- [Olimex 7 Ah](https://www.olimex.com/Products/Power-Supply/Lipo-battery/BATTERY-LIPO7000mAh/):
  product page says 185 × 70 × 4 mm, but its
  [linked pack drawing, page 8](https://www.olimex.com/Products/Power-Supply/Lipo-battery/BATTERY-LIPO7000mAh/resources/JA426992P2P-Spec-Data-Sheet-3.7V-7000mAh--161201.pdf)
  gives up to 190 × 69.5 × 4.7 mm. Too deep for the current bay; a wider-depth
  bay needs a new clearance assessment with expansion room. US sourcing is
  also unconfirmed. The nominal 4 mm web listing alone does not prove a fit.

## Electrical requirements and remaining hold

- **Protected 1S Li-ion/LiPo, 3.7 V nominal, 4.2 V full charge.** A 7.4 V pack,
  high-voltage phone cell or 5 V power-bank output is not a drop-in substitute.
- JST **PHR-2, 2.0 mm pitch**, with **J1 pin 1 positive, pin 2 negative**.
  Verify actual polarity; the connector shell alone does not identify it.
- Separate **10 kohm 103AT-2-type NTC on J5**, thermally attached to the pack.
  Charging is disabled without the sensor.
- The existing nominal charge current is about **445 mA**. Capacity/current
  alone gives roughly 9 h for 4 Ah, 11.2 h for 5 Ah and 22.5 h for 10 Ah;
  the charging taper, load and thermal/input limiting add time.
- **Charging-temperature compatibility remains unresolved.** The existing
  [BQ24072 / 103AT-2 circuit](https://www.ti.com/lit/ds/symlink/bq24072.pdf)
  has a nominal 0–50 °C window. Match the selected pack's specified charging
  limits before production. Simple passive NTC bias resistors cannot narrow
  this charger's temperature window. A mechanically fitting pack does not
  resolve this issue.

Print the matching `battery-pack-max-gauge-264x50x5.5.stl` and
`battery-reserve-gauge-270x52x6.3.stl`, or their left/right halves. These are
size gauges, not battery models with an assigned capacity. Earlier battery
gauges and the taller 11.5/24.7 mm case files are superseded. Nothing has been
ordered or sent to a supplier.
