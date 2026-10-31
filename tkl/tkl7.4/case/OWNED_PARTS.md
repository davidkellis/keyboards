# Purchased hardware and unresolved fit details

Updated 2026-09-24 from the user's parts information.

| Item | User information | Design status |
| --- | --- | --- |
| Switches | Kailh Choc V2 | Existing PCB switch hole pattern and 15 mm body envelope |
| Durock stabilizers | Plate Mount V3; four 2u and one 6.25u | Plate-mount type identified; Choc V2 height/travel fit unverified |
| TX AP stabilizers | User explicitly confirmed **plate mount**; five stabilizers; 7u, 6.25u and four 2u wires | Plate-mount type confirmed; Choc V2 height/travel fit unverified |
| Intended keycaps | XVX Skyline R2, advertised 5 mm, uniform low profile, MX-style socket | Model and advertised height confirmed by user screenshots; underside and travel unmeasured |
| Alternate keycaps | KBDiy KOA, advertised 9 mm; Botanical-KR option shown | Recorded as alternate; not the low-profile design target |
| Battery | Maximum capacity within the fixed thin case; 10,000 mAh preferred, thinner pack takes priority | Wide rear body envelope 264 × 50 × 5.5 mm; reserve 270 × 52 × 6.3 mm; no final pack selected |

The user identified the TX AP set as the **“2003 version”** of
[Divinikey's TX AP Stabilizers Rev 4 listing](https://divinikey.com/products/tx-ap-stabilizers-rev-4).
No option named “2003” appears on that current listing; the version/year wording
is recorded as supplied and has not been silently corrected.

The linked listing describes PCB clip-in variants, but the user subsequently
confirmed that their own TX AP set is **plate mount**. Use that confirmation
as the design input. The listing's 1.6T/1.2T PCB-clip-in options and SKUs do not
identify the purchased set. Do not request the mounting type again.

Both purchased sets therefore need plate-mount attachment features. Matching
clip retention alone does not prove the stabilizer stem height, travel or
wire clearance matches Choc V2.

The new full diagnostic plate and rectangular-slot coupons are generic **plate-mount** diagnostics
for both the Durock and TX AP sets. Their exact latch fit and height remain
unverified; test each set separately with the actual switches and keycaps.
`pcb-as-mounting-plate-1.6mm.stl` means a plate-mount stabilizer clipped into
PCB-thickness material. It is **not** a PCB-clip-in stabilizer footprint.
Do not judge a PCB-clip-in TX AP set against those rectangular slots.

Neither full PCB has been altered for any stabilizer attachment or housing
relief. Production remains on hold pending a physical test with the actual
switches and keycaps, plus final battery approval. See [battery specification](BATTERY.md).

## Keycap identification supplied by the user

The first two order links are the same product:
[XVX Skyline R2](https://www.aliexpress.us/item/3256808009058126.html).
The user supplied screenshots showing **5 mm low-profile caps and MX-style
cross sockets**, and explicitly wants low-profile caps. This is the design
target. The [manufacturer page](https://www.xvxchannel.com/products/xvx-skyline-r2)
identifies a uniform low profile; it does not supply an underside/socket drawing.
Do not infer installed height by simply adding 5 mm to the switch stem height.

The other link is [KBDiy KOA](https://www.aliexpress.us/item/3256806823423428.html).
The supplied screenshot shows the Botanical-KR option and a **9 mm KOA**
profile. The listing title also says NightSakura; it is a multi-option listing,
not proof the user bought the NightSakura color. This is an alternate set.

The fit assembly now draws 5 mm cap envelopes, with explicitly assumed
18 × 17 mm 1u footprint and 3 mm socket insertion. It does not represent the
actual underside or certify full travel. Try the XVX 2u and 6.25u caps on the
corrected samples first. Both stabilizer sets remain unverified with Choc V2.
