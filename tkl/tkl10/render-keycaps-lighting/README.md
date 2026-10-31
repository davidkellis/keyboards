# V10 keycaps and lighting studio

Open [index.html](index.html) in Brave. It is a standalone offline 360° viewer:
drag to orbit above or below, scroll to zoom, and use the eight view presets.
Choose a keycap profile and lighting concept independently. “Save this view”
downloads a PNG; “Download this 3D model” exports the selected visible assembly.
The profile and lighting comparison PNGs provide a quick overview.

This study preserves the original [V10 viewer](../render-360/index.html),
rounded case, PCB and manufacturing files. Alternative lighting geometry is
embedded for visualization only; it is not a new printable case release.
No quote, BOM, cart or order has been changed.

## Keycap comparison

| Selection | Geometry used | Height assumption and fit limits |
| --- | --- | --- |
| XVX Skyline R2 BOW | Approximate uniform, scooped MX shape; white caps with translucent legends | 5 mm nominal overall is the existing fit assumption, not a verified manufacturer CAD dimension. |
| XVX Skyline R2 WOB | Same approximation in black | Same height; the dark caps make lighting easier to compare. |
| ScottoCaps Flat MX | Joe Scotto's actual blank meshes in eight unit sizes | 6.7 mm overall. FDM design. Not automatically lower than the nominal XVX profile. |
| ScottoCaps Glass MX | Joe Scotto's actual blank MX meshes in eight unit sizes | 5.7 mm from central switch socket opening to key top. Wide-key stabilizer bosses extend another 0.9 mm. Resin design; not the Choc variant. |
| Extra-flat MX concept | Procedural 3.5 mm appearance shape | Experimental silhouette only. Default 2.3 mm engagement; not a finished printable or verified product. |

The Scotto meshes are rotated from their face-down printing orientation into
the assembly and simplified with a 0.025 mm surface tolerance. Their central
socket openings share the same mounting reference, including the wide Glass
caps with longer stabilizer bosses. Source dimensions and hashes are recorded
in [geometry-study.json](geometry-study.json).

The socket engagement slider is a fit-study assumption. Installed height is
switch stem-tip height + cap height − engagement, not cap height alone. The
appearance model uses a nominal 8.6 mm switch height above the PCB top,
derived from Kailh's drawing. Neither changing this slider nor rendering a
cap proves that its socket fits the Whale's round dust collar. Check stem
fit, return, full 2.8 mm travel, plate clips and stabilizers with actual
parts before choosing a printable cap. Printed blank caps default to no
legends. Optional labels are an illustration, not an engraving operation.

[XVX's product page](https://www.xvxchannel.com/products/xvx-skyline-r2)
identifies the Skyline R2 uniform MX profile, double-shot PBT and BOW/WOB
shine-through options. The rendered legend placement and cap shape follow
its photographs approximately; this is not licensed vendor CAD. The
[ScottoCaps Flat README](https://github.com/joe-scotto/scottokeebs/blob/main/Extras/ScottoCaps/Flat/Readme.md)
specifies 18.05 × 18.05 × 6.7 mm and the FDM process. The
[Glass README](https://github.com/joe-scotto/scottokeebs/blob/main/Extras/ScottoCaps/Glass/README.md)
specifies MSLA/resin printing and biocompatible resin. Files are pinned to
commit `066112d0d31848695b32c05eb8aa6362257929dc`;
[download-sources.json](reference/download-sources.json) lists exact URLs.

## Lighting comparison

V10 currently has **six white reverse-mount LTW-C230DS LEDs between key rows**,
not an LED beneath each switch. R1–R6 are 1 kΩ and are deliberately conservative
at 3.3 V; see [BRINGUP.md](../BRINGUP.md). Shine-through caps alone will not
give uniformly illuminated legends with these positions.

| Concept | What is shown | Work needed to make it real |
| --- | --- | --- |
| Current V10 | Six small round flush diffuser windows | Existing design. Cap skirts obscure some windows at typing angles. |
| Flush diffuser slots | Six 11 × 0.65 mm outlets fed at the existing LEDs | Case/optical trial; right Shift outlet shifts 2.25 mm. Still partly hidden from low angles. |
| Navigation light bar | 28 × 1.2 mm flush bar in the open area above the arrows | The displayed guide routes LED2 about 38 mm. Test optical loss at the actual LED current. A future PCB could instead move that existing LED directly beneath the bar. |
| Frosted key deck | Six localized pools visible in the gaps | Different plate material/insert and structural/optical trials. Six low-current sources should not be assumed to light a full deck uniformly. |
| Lower edge halo | Recessed luminous band around the base | Revised enclosure and added/redirected sources. Upward reverse LEDs behind an opaque PCB do not directly provide underside light. |
| Illuminated legends | 86 proposed emitters aligned with switch LED openings | PCB, drive/current and routing revision; verify optical orientation, firmware, heat and battery load. XVX caps have translucent legends; printed blanks stay blank. |

The Mini Tactile Whale's clear upper housing and LED opening allow a lighting
path. The main constraints here are LED placement, the cap skirts and optical
loss. The switch body in the viewer is a dimensioned appearance model, not
vendor CAD. Sources: [Kailh MINI tactile product](https://kailhswitch.net/products/kailh-deep-sea-silent-min-low-profile-keyboard-switch),
[manufacturer drawing](https://www.kailhswitch.com/uploads/15927/files/CPG1353S01D02-01-data-sheet.pdf)
and [manufacturer specification](https://www.kailhswitch.com/mechanical-keyboard-switches/low-profile-key-switches/choc-v2-low-profile-silent-tactile-switch.html).

The navigation bar is the most promising visual direction for retaining a
clean flush top and making a modest accent visible from the typing position.
If another PCB revision is acceptable, relocating one existing LED directly
under that bar is likely simpler optically than a long passive guide, with
the same LED part count. That is a proposed next design step, not a change
made to V10 in this study. Choose the per-key direction only if illuminated
letters are the goal; it is substantially more work than a visible accent.

Lighting brightness, spill and diffusion are **illustrative**. The dim-room
control helps compare visibility; it is not a lumen measurement, ray trace
or battery-life prediction. The frosted-deck shader deliberately shows six
pools rather than a fictitious uniformly lit plate. The selected GLB includes
geometry, colors and emissive materials; the viewer's custom spatial shader,
studio lights and floor glow do not transfer exactly to other GLB viewers.

## What stays fixed

The case envelope is 355.56 × 133.352 mm, with the existing rounded perimeter,
5.696° tilt and underside fasteners. Key centers, controller position and the
5000 mAh pouch reserve remain those of V10. No thinner battery or switch is
assumed. Alternative optical inserts have not passed a mechanical assembly
or print-strength review. The historical split-print seams still require
bonding and finishing; render materials do not remove those physical seams.

## Rebuild and verification

Viewing needs no packages or server. To rebuild, install the pinned JS
dependencies under `source/` with `npm ci`, and the Python mesh dependencies
from `source/requirements.txt` in a virtual environment. Run:

```sh
python source/prepare_assets.py
python source/build.py
NODE_PATH="$PWD/source/node_modules" node source/capture.cjs
python source/comparisons.py
```

`V10_RENDER_NODE_MODULES` can point to a separate installed node_modules.
`V10_RENDER_BROWSER` can override the Brave executable. The capture script
blocks HTTP requests, checks all 30 profile/concept combinations, mounted
cap-top alignment, legends and lighting, all eight views, mouse orbit,
zoom, spin, controls, PNG/GLB exports and mobile layout. It also checks the
source CAD/reference hashes. Results are in
[browser-validation.json](browser-validation.json) and
[provenance.json](provenance.json).

ScottoCaps attribution and license conditions accompany the embedded meshes
and exported models; see [ATTRIBUTIONS.md](ATTRIBUTIONS.md).
