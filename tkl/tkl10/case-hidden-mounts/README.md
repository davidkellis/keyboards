# v10 alternate enclosure — flush rounded top, concealed underside mounting

This is a separate **mechanical prototype** for the unchanged v10 PCB. It does
not modify the original `case/`, PCB, Gerbers, BOM, CPL or JLCPCB order.

The switch plate and full-height exterior walls form one continuous
upper shell: **there is no top-cover-to-body assembly seam or raised perimeter
lip**. The perimeter is flush with the sloping plate surface. The outside top
edge has a **2.5 mm roll-over radius**, and the four vertical corners have
**3 mm radii** (previously 0.8 mm for both). Its top has no screw
openings, including at the twelve previous mounting points. Eight screws are
accessible from underneath. The bottom edge fits inside the upper skirt, moving
the opening seam to the underside. Switch and stabilizer apertures and the six
flush LED windows retain the v10 layout.

The external footprint remains **355.56 × 133.352 mm**. Removing the old 1.6 mm
raised lip lowers the perimeter without moving the switch seating plane, PCB,
or bottom. The flat plate plane extrapolates to **5.692 mm at the front and
18.992 mm at the rear**; the rounded exterior edge sits below that
plane. These replace the former 7.3/20.6 mm raised-rim heights. The measured
edge and overall heights are recorded in `validation.json` under `surface`.
The switch seating regions retain their 1.5 mm plate thickness; the outer
border rolls down into the side walls. The existing **155 × 50 × 6.3
mm battery reserve** is retained; it is an allowance, not a new approved battery
specification. The original module thickness, socket position, keycap and
stabilizer assumptions still need physical verification.

## Look at the design

- `preview.html`: local preview gallery with view buttons and downloads.
- `with-keycaps-preview.png`: assembled appearance with illustrative keycaps.
- `assembled-preview.png`: smooth upper surface with keys omitted.
- `top-preview.png`: top view of the actual exported enclosure.
- `underside-preview.png`: recessed screw heads and removable bottom.
- `exploded-preview.png`: upper, PCB, nut carriers, bottom and USB insert.
- `mount-detail.png`: cutaway of one concealed mount.
- `rounded-edge-detail.png`: close view of the flush front corner and rounds.
- `edge-coupon-upper.stl`: a small front-left corner print to judge the larger
  rounds, appearance and wall stiffness before printing the whole shell.
- `shell-section.png` / `shell-section.svg`: actual front cross-section showing
  the continuous plate-to-wall connection and inset underside opening.
- `assembly.step`: CAD assembly in common coordinates; battery shape is the
  reserved space, and electronics are fit envelopes rather than detailed parts.

The complete-shell renders show the full-size model. A two-half print will
have a bonded seam across the upper that requires finishing if it is to look
like the full-size render. Moving the enclosure fasteners underneath does not
erase the seam between separately printed halves.

The earlier raised rim has been removed, leaving a flat surface out to the
rounded perimeter. The local rear USB insert and power-switch surround
still have small joints around their lower portions; those are separate from
the eliminated top/body perimeter joint. `shell-continuity.json` records the
single-solid check and the source meshes used for the section preview.

The previous 0.8 mm version is preserved in
`../case-hidden-mounts-history/flush-radius-0p8-2026-09-29.tar.gz`, and the
earlier raised-rim version in `../case-hidden-mounts-history/raised-rim-2026-09-29.tar.gz`.
This directory and its printable ZIP now contain the larger rounds.

## What holds it together

Each printed nut carrier slides into an internal wall pocket **after the PCB
is installed**. Its broad tongue bears on the wall. Two locating pins on the
bottom prevent the carrier withdrawing inward when assembled. An underside
screw passes through the bottom into the nut in that carrier.

The carriers are necessary because a fixed nut boss beneath the PCB would
obstruct inserting the PCB into this narrow, one-piece upper shell. They are
removable mounting pieces, not exposed fasteners or holes in the plate.

The bottom retains distributed PCB supports, reinforced areas and component
reliefs. Two small locating pins use existing PCB mounting holes. The upper's
spacers and the bottom supports locate the plate/PCB stack; the case screws
fasten the enclosure around it.

The U-shaped USB insert slides downward and slightly rearward after the bottom is removed, admitting
the pre-soldered controller from below. Its small upper lip stays on the shell.
It retains the small original USB aperture and plug recess. Its two lower
locating pins are captured by the installed bottom. The power-switch surround
is split between the upper and bottom, leaving a closed rear actuator opening
when assembled and a continuous upper edge.

## Hardware for one enclosure

- **8 × M2 × 4 mm button-head machine screws**, 0.4 mm pitch, head no larger
  than 3.8 mm diameter and 1.3 mm high. Length is measured under the head.
- **8 × DIN 934 M2 hex nuts**, 4 mm across flats and 1.6 mm thick.
- **8 × printed `nut-carrier.stl`**.
- **1 × printed `usb-bezel.stl`**.
- **6 × translucent `led-diffuser.stl`**, as in the original v10.

The original M2 × 5 screws are too long for this alternate stack. Do not use
them without rechecking clearance. The existing standard M2 nuts are reused.
The modeled screw tip extends 0.1 mm beyond the nominal nut; the head is
recessed 0.2 mm above the bottom surface. Confirm this stack with the coupon.

## Print the mounting trial first

Print one each of:

1. `mount-coupon-upper.stl`
2. `mount-coupon-bottom.stl`
3. `mount-coupon-pcb.stl` (optional plastic spacing gauge)
4. `nut-carrier.stl`

Use one actual M2 nut and M2 × 4 screw. `mount-coupon-assembly.step` shows how
they fit. Check that the nut slides fully into its side pocket, the carrier
slides into the wall pocket, the bottom pins enter freely and the screw draws
the joint closed without the carrier pulling out or the wall cracking. Tighten
gently by hand. The wall behind the carrier recess is 0.8 mm thick, making this
a particularly useful physical strength test before a large print.

Use the same material and slicer settings intended for the enclosure. A
small `edge-coupon-upper.stl` print lets you assess the new rounded corner.
The lower outer skirt is approximately 0.88 mm thick at the corner diagonal;
check it for flex and bonding between layers before committing to a full print.
A 0.16 mm layer height helps resolve the small nut-pocket roof and clearances.
The upper now prints with its broad, flat top surface facing the bed; it no
longer rests on a raised rim with an elevated plate. Review supports around
the internal mounting pockets and rear port features in the slicer.
The nut carriers print on their broad lower faces; keep the side nut-entry
slots open and remove any bridge sag before fitting hardware.

## Full enclosure print files

For a 256 mm bed:

- `plate-upper-left.stl` + `plate-upper-right.stl`
- `case-bottom-left.stl` + `case-bottom-right.stl`
- The small parts listed above.

The halves have bonded stepped lap joints with a 0.2 mm glue allowance. Dry-fit,
align on a flat fixture, and bond with adhesive appropriate to the print
material. Finish the upper joint before installing switches. The joints are
not snap joints, and must be bonded for structural use.

For a sufficiently large printer, use `plate-upper.stl` and `case-bottom.stl`
instead. All of these printing STLs are in millimetres, individually oriented
and placed on z=0. Do not scale them. Assembly-coordinate meshes in `reference/`
are diagnostic files and are not substitutes for these print files.

`v10-hidden-mount-print-files.zip` contains the printable parts, coupons and
these instructions. The mount coupon tests only the new fastening system. Also print the three
`usb-coupon-*.stl` pieces and `usb-bezel.stl` to test the new sliding surround
with your actual controller and cable. That coupon’s plastic PCB gauge has
0.4 mm added to switch/module hole diameters; the real PCB remains nominal.
`usb-coupon-assembly.step` shows the corner trial assembled.

## Assembly and servicing

1. Dry-fit the bare printed parts, carriers and hardware. Bond split halves
   before installing electronics. Fit the LED diffusers from underneath.
2. Solder/test the controller on the PCB and trim the protruding pins according
   to the original v10 instructions. Leave the USB insert and nut carriers out.
3. Fit switches into the upper from above. Bring the PCB into place from below,
   align the switch pins and solder from underneath. The plate is part of the
   upper shell, so this shell stays with the soldered switch/PCB assembly.
4. Slide the rear USB insert upward and slightly forward around the socket
   from underneath, normal to the tilted PCB. Fit one M2 nut in each carrier,
   then slide all eight carriers into the wall pockets from inside.
5. Secure the battery to the bottom using suitable padding/retention, route its
   lead clear of supports and screws, and connect it with correct polarity.
   The battery travels with the bottom during opening; leave disconnect slack.
6. Seat the bottom, engaging its carrier and USB-insert locating pins. Install
   the eight M2 × 4 screws from underneath and tighten lightly and evenly.

To service it, remove the eight underside screws, lower the bottom carefully
and disconnect the battery. The plate, switches and PCB remain together. The
carriers can then slide inward from their wall pockets, and the USB insert
slides down normal to the PCB (about 5.7° rearward from vertical) if removal
is necessary. Do not pull the insert straight out through the back wall.

## Checks and limitations

`validation.json` records solid clearances, enclosure hardware and modeled
insertion checks. `assembly-paths.json` checks carrier and USB-insert withdrawal.
`print-validation.json` records closed former screw holes,
watertight connected print meshes, split-bed dimensions and hashes verifying
that original files were preserved. These are geometry checks, not proof of
print strength, long-term creep, absence of rattle, electrical function or real
switch/keycap/stabilizer fit. Print and inspect the coupon before the enclosure.

The intended benefit is a clean, flush top with a continuous connection between
the plate and perimeter. The structural behavior of this printed prototype has not been
load tested. No PCB manufacturing changes or additional JLCPCB charges are
introduced by this alternate enclosure.

## Rebuild

Use the CadQuery environment already used by v10:

```sh
/tmp/keyboards-fit-work/venv/bin/python tkl/tkl10/case-hidden-mounts/source/build.py
/tmp/keyboards-fit-work/venv/bin/python tkl/tkl10/case-hidden-mounts/source/preview.py
/tmp/keyboards-fit-work/venv/bin/python tkl/tkl10/case-hidden-mounts/source/seam_preview.py
/tmp/keyboards-fit-work/venv/bin/python tkl/tkl10/case-hidden-mounts/source/check_paths.py
/tmp/keyboards-fit-work/venv/bin/python tkl/tkl10/case-hidden-mounts/source/finish.py
```

Sources read the original v10 case geometry and write only inside this new
directory. `preserved-inputs.json` captures the original file hashes.
