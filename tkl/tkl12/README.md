# TKL V12 — three soldered low-profile switch families

V12 is a separate revision derived from the final routed V11 board. **V11 and
earlier revisions are preserved.** Open [the KiCad project](kicad/keyboard.kicad_pro)
or [the PCB](kicad/keyboard.kicad_pcb).

Explore the assembled keyboard in the new [V12 switch and keycap studio](render-switches/index.html):
switch families, matching keycap styles, both case editions, free 360° viewing,
exploded layers and lighting previews. Appearance and alternate-family mechanical
fit assumptions are explained in the [viewer notes](render-switches/README.md).

The board retains every original Kailh Choc V2 drill, copper land and switch
position. Each of the 86 keys gains two shared nonplated locating slots and two
Gateron electrical contacts. Choose one switch family for the build:

| Family | PCB mounting | Other parts needed |
| --- | --- | --- |
| Kailh Choc V2, including our Deep Sea Mini Whale | Original holes and contacts, unchanged | Existing Kailh plate height and MX-stem keycaps |
| Kailh Choc V1 | Original electrical contacts plus shared side slots | Choc two-slot keycaps; verify stabilizers and cap/case travel |
| Selected Gateron Low Profile 3.0 | Alternate contacts plus shared side slots | Plate top 2.5 mm above PCB instead of Kailh's 2.2 mm; verify keycap skirts, travel and optics |

These are **soldered footprints**, without hot-swap sockets. The exact Gateron
references and mounting drawing are in [SWITCHES.md](SWITCHES.md). This does not
claim compatibility with older Gateron generations, Cherry Low Profile or every
retail switch sold under a similar name.

The three-family pattern uses the same LED-facing direction. The earlier
feasibility study mixed top and bottom drawing views for Gateron; V12 corrects
that chirality and checks it against the official PCB drawing and KiCad's
standard MX footprint. One output capacitor, **C2**, moves from (117.8, 31) to
(124, 34.5) mm to clear the added contacts. All other component positions,
the boost switching loop, LED positions, matrix, controller pinout, board outline
and twelve M2 mounting holes remain unchanged.

## Assembly and cost

The target stays **two layers, 1.6 mm FR-4, lead-free HASL and lead-free Economic
bottom-side assembly**. The factory BOM is unchanged: ten purchasing groups and
106 placements, all on the bottom. Switches and the controller clone are fitted
by the user. The new holes do not add SMT placements or feeder types; extra
drilling/routing can still affect the fabrication quote. The current live quote is linked below; it retains the previous $29.05 fabrication price for five.

The ten reverse LEDs, TPS61169 driver, ZMK PWM interface and optional four-LED
wire bypass retain V11's circuit. See [bring-up instructions](BRINGUP.md).
Changing switch family does not require a different electrical matrix or pinmap.

## Files and checks

- [Front copper preview](front.svg) and [back copper preview](back.svg).
- [Switch mounting diagram](reference/switch-pattern.svg).
- [Manufacturing package](manufacturing/tkl-v12-prototype-handoff.zip), including
  Gerbers/drills, schematic PDF, assembly drawings, BOM and CPL.
- [Ordering settings](manufacturing/ORDERING.md) and [fabrication notes](manufacturing/FABRICATION.md).
- [Exact PCB STL](case/pcb-bare.stl) and [enlarged-hole print gauge](case/pcb-fit-check.stl).
- [Small three-position print-fit coupon](case/switch-fit-coupon.stl).
- [Electrical checks](validation/summary.json), [preservation and pattern audit](validation/revision-audit.json)
  and [export checks](validation/handoff-check.json).
- [Repeatable checking/export commands](scripts/README.md).

The existing V11/V10 case and plate remain the reference for our Kailh build;
V12 does not silently change their switch seating height. There is no completed
Gateron-height case/plate in this PCB revision. The print coupon checks pin and
peg alignment, not metal PCB tolerances, switch clip retention or optical performance.
Test real switches, plate, stabilizers and keycap travel before buying a complete
alternate-family build. Hardware, charging, RF and lighting still need prototype
bench tests; software checks do not establish physical performance.

Final software checks (KiCad 10, 2026-10-16): **0 ERC errors/warnings,
0 DRC errors/warnings, 0 unrouted connections and 0 schematic parity issues**.
All 86 keys and all 344 new holes are checked. The original V11's 470 saved
files are unchanged. Exported drill coordinates, archive hashes and 106 bottom
placements also pass; all three STL models are watertight.

The [live JLCPCB quote saved on 2026-10-16](manufacturing/quote-v12-2026-10-16/README.md)
is **$180.26 delivered for five assembled boards** using lead-free HASL,
lead-free Economic bottom-side assembly and UPS DDP, before any unpriced
reverse-LED handling/fixture charge after review. Nothing has been ordered or
paid. The displayed PCB fabrication price remains $29.05 for five.
