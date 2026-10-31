# Print the small sample first

Both purchased stabilizer sets are **plate mount**. These diagnostic samples
use generic Cherry-style slots; Durock V3 and TX AP latch fit, body depth,
stem height and travel with Choc V2 still need a physical test. Low-profile
keycaps are the intended choice. A cross-shaped stem alone does not establish
compatibility.

**Height correction:** the old sample incorrectly put the plate UNDERSIDE
2.2 mm above the PCB. Kailh's drawing places the switch seating flange, hence
the plate TOP, 2.2 mm above the PCB. Discard earlier printed sample supports.
For a 1.5 mm plate the air gap is **0.7 mm**; for 1.2 / 1.6 mm plates it is
1.0 / 0.6 mm respectively. Each new PCB sample is paired with its thickness.

1. Print `2u-pcb-for-1.5mm-plate.stl` and `2u-plate-1.5mm.stl` at 100% in mm.
   Use 0.1 mm layers to obtain a measured 1.5 mm plate. Ream undersized drills;
   do not scale the entire model. The older generic filenames now contain
   this corrected 1.5 mm arrangement.
2. Clip in one purchased stabilizer pair. Try the matched 1.2 / 1.6 mm files
   if latch fit requires it. Test Durock and TX AP separately.
3. Assemble the plate on its four supports and insert a real Choc V2 switch.
   Its base must seat fully on the PCB while its flange rests on the plate.
4. Attach the actual low-profile 2u keycap. Press at centre and both ends;
   check full travel/return, skirt clearance and that the cap sits level.
5. If the housings or wire hit the solid PCB, try `2u-pcb-diagnostic-relief.stl`.
   Its 8 × 16 mm diagnostic openings are NOT production PCB cutouts. Tell us
   where contact occurs and how far the stabilizer protrudes beneath the PCB.
6. Repeat with the `spacebar-6.25u-*` sample and your actual 6.25u spacebar.
   Its stem span is provisionally 100 mm; 2u samples use 23.8 mm. The 7u wire
   does not match this keyboard's 6.25u spacebar layout.

A passing sample does not certify the full plate: check every wide key, cover,
wire path and all underside electronics before soldering all switches. The
full PCBs still have no stabilizer housing relief, and exact stabilizer solids
are not included in the CAD collision test. Mechanical release remains on hold.

`pcb-as-mounting-plate-1.6mm.stl` remains an optional lower-plane diagnostic:
it clips PLATE-MOUNT stabilizers into PCB-thickness material. It is not a
PCB-clip-in footprint and is not the full assembly's chosen mounting plane.

[Kailh PG1353 drawing](https://www.kailhswitch.com/Content/upload/pdf/202015927/PG135301D03.pdf)
shows the 2.2 mm flange offset and 6.4 mm flange-to-stem height (8.6 mm total).
[Cherry mounting drawing, page 4](https://www.smcelectronics.com/DOWNLOADS/CHERRYMX.PDF)
is the reference for the generic slots, with small diagnostic print allowances.
