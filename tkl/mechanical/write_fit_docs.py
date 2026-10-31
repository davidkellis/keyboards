#!/usr/bin/env python3
"""Write fit documentation from the checked geometry report and shared notes."""
from pathlib import Path
import argparse
import hashlib
import json

p=argparse.ArgumentParser()
p.add_argument('revision',type=Path)
a=p.parse_args()
shared=Path(__file__).resolve().parent
for root in (a.revision.resolve(),):
 v=root.name.removeprefix('tkl')
 out=root/'case'
 report=json.loads((out/'fit-report.json').read_text())
 assert report['fit_config_sha256']==hashlib.sha256((shared/'fit-config.json').read_bytes()).hexdigest(), 'Rebuild fit geometry before writing docs'
 assert not report['collisions'] and report['pcb_case_overlap_mm3']<1e-4
 bat=report['battery']
 front=report['front_lip'];rear=report['rear_lip'];tilt=report['tilt_degrees']
 pack_text=' × '.join(f'{n:g}' for n in bat['pack_max_dimensions_mm'])
 reserve_text=' × '.join(f'{n:g}' for n in bat['reserved_dimensions_mm'])
 extra_thickness=bat['reserved_dimensions_mm'][2]-bat['pack_max_dimensions_mm'][2]
 pack_gauge='battery-pack-max-gauge-'+'x'.join(f'{n:g}' for n in bat['pack_max_dimensions_mm'])+'.stl'
 reserve_gauge='battery-reserve-gauge-'+'x'.join(f'{n:g}' for n in bat['reserved_dimensions_mm'])+'.stl'
 for file in ('BATTERY.md','OWNED_PARTS.md'):
  text=(shared/file).read_text()
  (out/file).write_text(text)
 text=f'''# TKL v{v}: separate plate, low-profile caps and fixed thin case

Use these files for a physical fit test. The **XVX Skyline R2, advertised 5 mm
low-profile caps** are the design target. Your KBDiy KOA set is advertised as
9 mm and is recorded as an alternate. Both purchased stabilizer sets are
plate mount. Their latch, body/wire clearance and travel with Choc V2 remain
unverified; the plate slots are diagnostic, not approved production geometry.

## Start with the small sample

Print the matched **`stabilizer-test/2u-pcb-for-1.5mm-plate.stl`** and
**`stabilizer-test/2u-plate-1.5mm.stl`**, then try an actual Choc V2 switch,
a pair of Durock or TX AP stabilizers and an XVX 2u cap. Test each stabilizer
set separately. Follow [the sample instructions](stabilizer-test/README.md)
and repeat with the 6.25u spacebar sample. These fit a 256 mm printer.

**Discard the old sample supports:** the corrected plate TOP is 2.2 mm above
the PCB. The prior sample incorrectly used that value for the underside.
The corrected 1.5 mm plate has only **0.7 mm clear space beneath it**. If the
stabilizer hits the PCB, the diagnostic relief sample can locate the problem;
neither routed PCB contains stabilizer relief cutouts yet. Do not solder all
86 switches or release the Gerbers before this is resolved.

## How the pieces fit

From the bottom upwards: a flat case floor supports the padded battery; case
bosses/perimeter ledges support the PCB; 0.7 mm prototype feet support the
1.5 mm plate on the PCB; the cover sits 0.4 mm above the plate. Its small feet
rest on the plate above PCB/case supports. The plate has 86 switch openings,
slots at all five stabilized keys, JST-tail clearances and six LED apertures.
There is no higher case ledge obstructing vertical insertion of the PCB.

| Plane or part | Height from PCB underside, perpendicular to PCB |
| --- | --- |
| PCB | 0–1.6 mm |
| Air space / plate feet | 1.6–2.3 mm |
| Separate plate | 2.3–3.8 mm (1.5 mm material) |
| Gap below cover | 3.8–4.2 mm |
| Cover | 4.2–5.4 mm (1.2 mm material) |
| Choc V2 unpressed stem top | 10.2 mm (8.6 mm above PCB top) |

The **assembled lip heights are {front:g} mm front / {rear:g} mm rear**, with {tilt:.2f}°
tilt. These include the cover and preserve the requested thin profile. Lip
height excludes switches and keycaps. The outside footprint is 355.56 × 133.35 mm.
The wide battery bay uses the deeper space near the rear; a clearance tunnel
under the rear PCB ledge allows the bay to approach the rear wall.

The floor is 1.2 mm beneath the battery. Small internal pockets beneath front
diodes D77–D86 leave about 0.836 mm of material and 0.4 mm modeled component
clearance; the exterior bottom is still flat. Test the thin floor and the long
rear PCB span for flex. CAD collision checks do not establish stiffness.

For a fit trial, place the battery gauge within the floor's low locating
corners; place the matched PCB/plate with switches into the open case; lower
the cover over the switches; then install the keycaps. Check full travel at
every wide key and access to rear USB and power switch. The assembled plate
rests on the PCB and is located by the switches. The case, PCB and cover are
still gravity seated; transport fastening is not finalized.

## Printable and CAD files

| File | Purpose |
| --- | --- |
| `case.stl` | Wedge case with flat floor, PCB supports and battery locating corners |
| `cover.stl` | Flat-oriented drop-on cover, outside flush with case |
| `plate-supported.stl` | Full diagnostic plate, with integral 0.7 mm feet underneath |
| `plate-supported-left/right.stl` | Plate split to fit a 256 mm printer |
| `plate-flat-1.5mm.stl`, `plate-diagnostic.dxf` | Flat plate without feet; review geometry only, needs separate 0.7 mm spacers |
| `plate-supported.step` | Plate in PCB-local assembly coordinates |
| `pcb-left/right.stl` | 1.6 mm PCB gauge with actual switch/connector holes; insert real switches |
| `pcb-populated-left/right.stl` | PCB with conservative electronics and solder-pin envelopes |
| `pcb-bare.stl`, `pcb-populated.stl` | Full PCB gauges for a large printer |
| `pcb-populated.step` | PCB and fitted component envelopes |
| `fit-assembly.step` | Case, plate, PCB, cover, battery reserve, switches and cap envelopes |
| `fit.scad`, `fit-preview.png` | Exploded view of printable parts |
| `stack.svg` | Annotated stack diagram; dimensions control, not drawing scale |
| `case-left/right.stl`, `cover-left/right.stl` | Optional split shell/cover trials, tape or glue at butt seams |
| `{pack_gauge}` | Finished-pack target: {pack_text} mm, including wrapping and protection board |
| `{reserve_gauge}` | Reserved space: {reserve_text} mm, including provisional growth/assembly room |
| Battery gauge `-left/right.stl` files | Butt-join the two halves when using a 256 mm printer |
| `battery-space.svg` | Plan view of the bay and fixed case dimensions |
| `keycap-envelopes-left/right.stl` | Separate 5 mm cap boxes; no real underside/socket detail |

Import STLs at **100% in millimetres**, without automatic scaling. PCB and
plate splits follow the same stairstep seam; align their upper faces, not the
lowest component/foot surfaces. The seam stays clear of switch drills; tape
or brace it for a fit trial. Each left/right part fits a 256 × 256 mm bed.
The full one-piece case and plate give a better stiffness test.

Use 0.1 mm layers for the 1.5 mm plate and 0.7 mm feet, and measure the result.
Supported plate and cover prints need support beneath their wide undersides,
or print them upside down with the feet pointing up. Populated PCB mocks also
need supports. Bare PCB gauges are easier when using real switches. Nominal
printed drill holes may need reaming; never scale the PCB to enlarge holes.
FDM plate flex/latches do not establish a final material or production tolerance.

## What is and is not verified

`fit-report.json` checks modeled case/PCB/plate/cover/component/switch/battery
intersections. `mesh-validation.json` checks all STL meshes and split bed sizes.
Actual stabilizer solids, cap underside and full key travel are **not checked**.
The cap envelope is 5 mm tall, with an assumed 18 × 17 mm 1u footprint, 3 mm
socket insertion and 0.6 mm cover clearance per side. These are not measured
XVX dimensions and must not be read as an installed-height guarantee.

The battery reserve is **{reserve_text} mm**, for a finished pack up to
**{pack_text} mm**. It includes {extra_thickness:g} mm extra thickness plus a separate
0.5 mm padding allowance below. A retail pack has not been selected; expansion
allowance is provisional and the size gauge has no assigned capacity.
[BATTERY.md](BATTERY.md) covers sourcing references,
connector, external NTC and unresolved charging-temperature compatibility.
Real wiring, coax bends, adhesive and pack expansion still need a physical
check. Component blocks are conservative envelopes, not manufacturer CAD.

Source geometry comes from this revision's routed PCB, without XY scaling.
See [the shared generator guide](../../mechanical/README.md),
[the purchased hardware record](OWNED_PARTS.md) and `fit-config.json`.
The inherited `keyboard-plate.*` / `tklplate.stl` outside this folder remain
obsolete; the new `plate-*` files here are the current diagnostic prototype.

![Exploded fit model](fit-preview.png)
'''
 (out/'README.md').write_text(text)
 # Engineering stack diagram, perpendicular to PCB, not an optical simulation.
 svg='''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="650" viewBox="0 0 1100 650">
<rect width="1100" height="650" fill="#f7f9fc"/>
<style>text{font-family:Arial,sans-serif;fill:#203044}.title{font-size:26px;font-weight:bold}.body{font-size:18px}.small{font-size:15px}.line{stroke:#40546a;stroke-width:1.5}</style>
<text x="35" y="44" class="title">TKL — separate plate / PCB / cover fit prototype</text>
<text x="35" y="74" class="body">Dimensions perpendicular to PCB. Diagram not to scale.</text>
<rect x="80" y="110" width="180" height="58" rx="12" fill="#9aa8bc"/>
<text x="520" y="143" class="body">XVX Skyline R2: advertised 5 mm cap height</text>
<path d="M270 139H500" class="line"/><text x="520" y="168" class="small">Socket insertion and underside still unmeasured</text>
<rect x="148" y="168" width="44" height="35" fill="#3d526b"/>
<rect x="113" y="203" width="114" height="109" rx="8" fill="#c0c7ce"/>
<text x="520" y="210" class="body">Choc V2 stem top: 8.6 mm above PCB</text>
<path d="M240 195H500" class="line"/>
<path d="M65 250H110V273H65Z M230 250H430V273H230Z" fill="#dedede"/>
<text x="520" y="259" class="body">Cover: 1.2 mm, with key clearance opening</text>
<path d="M442 260H500" class="line"/>
<text x="520" y="288" class="small">0.4 mm gap between plate top and cover underside</text>
<path d="M75 303H112V331H75Z M228 303H430V331H228Z" fill="#477dc0"/>
<text x="520" y="321" class="body">Plate: 1.5 mm; TOP 2.2 mm above PCB</text>
<path d="M442 315H500" class="line"/>
<rect x="385" y="331" width="24" height="14" fill="#477dc0"/>
<text x="520" y="350" class="small">0.7 mm feet/air space underneath plate</text>
<rect x="75" y="345" width="355" height="31" fill="#34794f"/>
<text x="520" y="377" class="body">PCB: 1.6 mm; actual drill locations retained</text>
<path d="M442 363H500" class="line"/>
<rect x="385" y="376" width="24" height="124" fill="#657387"/>
<rect x="92" y="429" width="256" height="56" fill="#d7ae62"/>
<text x="520" y="445" class="body">Battery reserve: __BATTERY_RESERVE__ mm</text>
<path d="M355 449H500" class="line"/>
<text x="520" y="472" class="small">0.5 mm padding allowance below; prototype locating corners</text>
<rect x="92" y="485" width="256" height="15" fill="#eee1be"/>
<rect x="65" y="500" width="385" height="22" fill="#657387"/>
<text x="520" y="516" class="body">Case: 1.2 mm floor + PCB support bosses</text>
<path d="M462 510H500" class="line"/>
<text x="35" y="570" class="body">Assembled lip: __FRONT__ mm front / __REAR__ mm rear; tilt __TILT__°. Key tops sit higher.</text>
<text x="35" y="603" class="small">Stabilizer bodies/wire and keycap travel are unverified. Print the 2u and 6.25u samples first.</text>
<text x="35" y="628" class="small">Battery target: __PACK__ mm; expansion and charging-temperature requirements remain unverified.</text>
</svg>'''
 svg=svg.replace('__BATTERY_RESERVE__',reserve_text).replace('__PACK__',pack_text)
 svg=svg.replace('__FRONT__',f'{front:g}').replace('__REAR__',f'{rear:g}').replace('__TILT__',f'{tilt:.2f}')
 (out/'stack.svg').write_text(svg+'\n')
 # Top view uses one uniform XY scale; cover/PCB removed to expose the reserve.
 cw,cd,_=report['case_size'];bx,by,_=bat['position_xyz_case_mm']
 bw,bd,bh=bat['reserved_dimensions_mm'];pw,pd,ph=bat['pack_max_dimensions_mm']
 scale=2.2;ox=70;oy=135
 px=bx+(bw-pw)/2;py=by+(bd-pd)/2
 # World Y points rearward; display rear at the top of the plan.
 def sy(y):return oy+(cd-y)*scale
 plan=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="670" viewBox="0 0 1000 670">
<rect width="1000" height="670" fill="#f7f9fc"/>
<style>text{{font-family:Arial,sans-serif;fill:#203044}}.title{{font-size:26px;font-weight:bold}}.body{{font-size:18px}}.small{{font-size:15px}}.dim{{stroke:#53657a;fill:none;stroke-width:1.3}}</style>
<text x="35" y="42" class="title">TKL v{v} — battery space within the thin case</text>
<text x="35" y="74" class="body">Plan view with cover and PCB removed. All dimensions in millimetres.</text>
<text x="360" y="111" class="body">{cw:.2f} across keyboard</text>
<path d="M{ox} 119H{ox+cw*scale}" class="dim"/>
<rect x="{ox}" y="{oy}" width="{cw*scale}" height="{cd*scale}" fill="#dde4ec" stroke="#53657a" stroke-width="3"/>
<rect x="{ox+bx*scale}" y="{sy(by+bd)}" width="{bw*scale}" height="{bd*scale}" fill="#eedebd" stroke="#bc8b3c" stroke-width="2"/>
<rect x="{ox+px*scale}" y="{sy(py+pd)}" width="{pw*scale}" height="{pd*scale}" fill="#d9ac5c" stroke="#805616" stroke-dasharray="6 4"/>
<text x="115" y="174" class="body">Finished body: {pack_text} mm</text>
<text x="115" y="204" class="small">Reserve: {reserve_text} mm + 0.5 mm padding below</text>
<text x="690" y="185" class="small">Rear electronics</text>
<text x="690" y="209" class="small">and connectors</text>
<text x="345" y="350" class="body">Front of keyboard</text>
<text x="895" y="275" class="body" transform="rotate(90 895 275)">{cd:.2f} front to back</text>
<text x="35" y="475" class="body">Case + cover: {front:g} mm front / {rear:g} mm rear. Switches and keycaps sit higher.</text>
<text x="35" y="513" class="body">Thickness target: {ph:g} mm finished pack + {extra_thickness:g} mm provisional expansion space.</text>
<text x="35" y="547" class="body">1.2 mm floor under battery; 0.5 mm padding; modeled electronics clearance:</text>
<text x="35" y="579" class="body">{bat['minimum_reserved_volume_clearance_mm']:.3f} mm beyond the reserve ({bat['nearest_reference']}).</text>
<text x="35" y="620" class="small">This is a size envelope, not a selected battery or a guarantee of capacity. Check BATTERY.md.</text>
<text x="35" y="646" class="small">Wiring, expansion requirements, retention and the long PCB span still need physical validation.</text>
</svg>'''
 (out/'battery-space.svg').write_text(plan+'\n')
 print('Wrote fit documentation for',root.name)
