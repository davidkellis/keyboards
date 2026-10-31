# PCB-derived plate, case and fit models

The routed `.kicad_pcb` controls drills, switch sizes/positions, connector
locations and component envelopes. The shared generator serves v7 and v8;
it does not modify PCB copper or cut stabilizer relief into the production PCB.
`fit-config.json` controls the mechanical stack, provisional battery reserve
and advertised keycap height. The target is now XVX Skyline R2 **5 mm** caps.
See [the hardware record](OWNED_PARTS.md) and [battery specification](BATTERY.md).

```sh
/usr/bin/python3 tkl/mechanical/export_geometry.py tkl/tkl7
python -m venv /tmp/keyboard-cad
/tmp/keyboard-cad/bin/pip install -r tkl/mechanical/requirements.txt
/tmp/keyboard-cad/bin/python tkl/mechanical/build_fit.py tkl/tkl7
/tmp/keyboard-cad/bin/python tkl/mechanical/build_stabilizer_coupon.py tkl/tkl7
/tmp/keyboard-cad/bin/python tkl/mechanical/check_fit.py tkl/tkl7
python tkl/mechanical/write_fit_docs.py tkl/tkl7
python tkl/package_handoff.py tkl/tkl7
```

Use `tkl/tkl8` for v8. The geometry export needs KiCad's `pcbnew`; CAD commands
use CadQuery in a separate environment. `write_fit_docs.py` generates each
case's README/stack diagram and copies BATTERY/OWNED_PARTS from this directory.
Update shared documentation and render the preview before packaging. The CAD and
mesh checks validate both PCB and fit-configuration hashes. Dimensions are mm.
STLs are normalized individually to the bed; STEP retains assembly coordinates.
PCB geometry uses rigid transforms only, without XY scaling or outline shrink.

The new plate is 1.5 mm thick, with its **top 2.2 mm above the PCB top** and
0.7 mm feet underneath. Case bosses support the PCB; aligned plate feet bear
on it; the cover has a 0.4 mm gap above the plate and its own small support
feet. No upper case ledge blocks vertical PCB insertion. The case has low
battery locating corners, a flat floor and open-topped rear connector notches.
The assembled case/cover lips are fixed at **7.3 / 20.6 mm**, with 5.696°
tilt and a **355.56 × 133.35 mm** outside footprint. The wide rear battery
reserve is **270 × 52 × 6.3 mm**, for a finished-pack envelope up to
**264 × 50 × 5.5 mm**, with 0.5 mm padding below. This uses more of the case
width without increasing its outside size. No battery capacity is assigned
to the gauge; see the sourcing/fit assessment in BATTERY.md.

The floor stays 1.2 mm beneath the battery. Local internal reliefs beneath
front-row diodes D77–D86 leave about 0.836 mm floor thickness and 0.4 mm
modeled component clearance. The outside bottom remains flat. These thin
areas and the long rear support span require a physical stiffness test.


`plate_geometry.py` shares the generic Cherry-style diagnostic apertures
between full plates and the 2u / 6.25u test coupons. **Print the coupons first.**
Both purchased stabilizer sets are plate mount. Their actual body depth, latch,
wire path, stem height and travel with Choc V2 are not established by a generic
slot. Neither PCB has stabilizer body cutouts. The generated DXF is review
geometry, not permission to manufacture a plate or route the PCB.

`fit-report.json` records component/PCB/plate/cover/switch/case/battery volume
checks, battery reserve distance, support positions and explicit limitations.
Component envelopes use courtyards and conservative height allowances, not
exact vendor solids. JST includes an 8 mm mated-housing allowance; USB has
3.4 mm and U.FL has 3.5 mm. Plate cutouts clear protruding JST tails and both
revisions' six optical paths. Real cable bends still require physical checks.

The 5 mm keycap envelopes have an assumed 18 × 17 mm 1u footprint and 3 mm
socket insertion. These are not measured XVX underside dimensions. Actual
stabilizer geometry and cap full-travel checks are not part of the collision
pass. The intended low-profile cap model and height are known; mounting depth
and moving clearances remain the missing information.

[Kailh's PG1353 drawing](https://www.kailhswitch.com/Content/upload/pdf/202015927/PG135301D03.pdf)
places the flange 2.2 mm above the PCB and the stem 6.4 mm above the flange,
so the rest stem height is **8.6 mm above the PCB**. The former model mistook
6.4 mm for PCB-to-stem height and its coupon put the plate underside at 2.2 mm.
Both errors are corrected; discard old coupon supports and use matched files.
The [JST PH drawing](https://www.jst-mfg.com/product/pdf/eng/ePH.pdf) gives
connector dimensions. The generic stabilizer slots refer to
[Cherry's mounting drawing, page 4](https://www.smcelectronics.com/DOWNLOADS/CHERRYMX.PDF).
Neither reference proves the purchased stabilizers' low-profile compatibility.

All printable meshes must be watertight with positive volume; split files must
fit a 256 mm bed. Negative-oriented internal shells may represent sealed
cavities, but disconnected positive solids are forbidden except the explicitly
separate keycap visualization boxes. PCB/plate splits follow the same stair
seam clear of switch drills. The full case and plate are preferred for stiffness
checks; split shells/covers are taped or glued fit trials. Gravity seating is
modeled, but final transport fastening and pack retention are not complete.
