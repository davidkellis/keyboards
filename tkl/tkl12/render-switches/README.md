# V12 switch and keycap studio

Open [index.html](index.html) in Brave or Chrome. It is a self-contained offline
page; no web server, external JavaScript, font or image download is required.
Select the switch family first, then a matching keycap style. Drag to orbit in
360°, scroll to zoom and right-drag to pan. **Inspect stems** removes caps and the
top frame; **Show completed** restores them.

The previous V11 viewer and all electrical/manufacturing sources are preserved.
This directory contains a visualization, not revised case manufacturing files.

## Choices

| Switch | Matching cap styles shown |
| --- | --- |
| Kailh Choc V2 Mini Whale | XVX Skyline R2 BOW/WOB, NuPhy nSA COAST-inspired, Keychron LSA V2-inspired, ScottoCaps Flat and Glass MX |
| Kailh Choc V1 PG1350 | MBK Colors Chili blanks, MBK Legend Glow-style white, Chocfox CFX white blanks |
| Gateron LP 3.0 Grey Heron / Silver | The same MX-cross profile candidates as Choc V2 |

The filter follows the stem interface. It does **not** assert that every cap
clears a switch’s dust collar, case or stabilizers. Those need samples and a
physical fit check. Switch selection changes housing dimensions and appearance,
contact/locator positions, moving stem shape, stem-tip height, plate seating and
maximum travel. It is not a colour-only change.

Commercial cap shapes, colours, legends and socket engagement are appearance
approximations. NuPhy accents and the LSA row shape are illustrative. ScottoCaps
Flat and Glass use the designer’s actual adapted meshes, with attribution and
license in [ATTRIBUTIONS.md](ATTRIBUTIONS.md). Commercial caps are not printable
production models. The GLB export is for viewing, not cap manufacture.

The actual V12 drilled PCB is used, including all three contact/locator patterns
and the relocated C2 component. Copper traces and package details are not fully
modeled. All 86 switch centres and ten LED locations come from V12 exports. The
PCB substrate STL is scaled in Z from its native 1.53 mm to the nominal finished
1.6 mm thickness used by the assembly study.

## Fit and height assumptions

Heights below are measured from the PCB **top**; the board itself is 1.6 mm.

| Switch reference | Plate top | Stem tip at rest | Travel preview |
| --- | --- | --- | --- |
| Choc V2 CPG1353S01D02-01 Whale | 2.2 mm | 8.6 mm | 2.8 mm |
| Choc V1 CPG135001D01-16 | 2.2 mm | approx. 8.0 mm | 3.0 mm |
| Gateron 3.0 KS-33BHB10B050NW-G13 Heron | 2.5 mm | drawing-derived 9.4 mm | up to 3.4 mm |
| Gateron 3.0 KS-33BS10B043NW-Y92B Silver | 2.5 mm | drawing-derived 9.4 mm | up to 3.5 mm |

The Gateron selection lifts the plate/backing/coupler preview 0.3 mm along the
board normal. It retains the existing case geometry to expose the difference.
A matching Gateron-height case, clip apertures, retention and optical coupling
have not been released or validated. Silent Red and other retail variants can
have different travel and installed height; they are not silently substituted.

The existing rounded V10/V11 case editions remain available: floating keys and
the raised surround designed around nominal XVX skirts. Alternative caps may
sit below or above that surround or collide with it when pressed. The travel
slider helps inspect the concept but does not perform a solid collision check.
Stabilizers are illustrative reference envelopes, not family-specific releases.

Nominal appearance assumptions, explicitly editable through socket engagement:

| Cap style | Overall height used | 1U width × depth used |
| --- | --- | --- |
| XVX Skyline R2 | assumed 5.0 mm | assumed 18 × 17 mm |
| NuPhy nSA | assumed 4.6 mm | assumed 18 × 18 mm |
| Keychron LSA V2 | assumed 4.8–5.7 mm by row | assumed 18 × 17.8 mm |
| MBK-style | assumed 3.6 mm | assumed 17.5 × 16.5 mm |
| Chocfox CFX 1U | published 3.7 mm | published 16.5 × 16.5 mm |
| ScottoCaps Flat MX | mesh 6.7 mm | designer mesh |
| ScottoCaps Glass MX | mesh 5.7 mm at central socket | designer mesh |

Published CFX envelope dimensions do not establish its socket engagement or our
wide-cap geometry. Socket depth is assumed for every profile. For Glass MX,
wide-key stabilizer bosses extend a further 0.9 mm below the central socket.

The kit must contain the widths, quantities, stabilizer locations and legends
needed for this 19.05 mm-pitch ANSI TKL. MBK Colors is advertised as a full-size
blank kit. MBK Glow is shown with custom/unconfirmed widths beyond 1U, 1.5U and
2U; those amber keys are not a promise of kit contents. The CFX listing offers
sizes up to 2.25U, so the 2.75U right Shift and 6.25U spacebar are amber custom
placeholders. Printed standard legends are optional overlays, not an assertion
that blank sets include legends.

## Assembly, lighting and exports

All previous controls remain: assembled/exploded views with a separation slider,
seven visible layers, hardware toggle, transparent case, both case editions,
opaque/clear/frosted/engraved plates, reflective backing, daylight/dim lighting,
case and cap colours, travel/seating, auto-rotation, camera presets, PNG and GLB.

Explosion separates illustrative layers; it is not a service procedure for
soldered switches. Returning to zero restores the exact assembly transforms.
The battery remains a nominal 147 × 44 × 5 mm, 5000 mAh pouch envelope.

Lighting reuses ten normalized source fields at V12’s real LED positions. It
does not simulate calibrated PMMA optics, lumen output or battery life. Detached
plates do not glow from PCB sources in exploded views, and cap legends are not
given artificial emissive brightness. The page cannot demonstrate measured
backlight uniformity or validate a light guide.

## Sources and reproduction

Reference products checked 2026-10-16:

- [Kailh and Gateron drawings, exact part numbers and V12 pattern](../SWITCHES.md).
- [XVX Skyline R2](https://www.xvxchannel.com/products/xvx-skyline-r2).
- [NuPhy COAST Twilight](https://pay.nuphy.com/products/coast-twilight-nsa).
- [Keychron LSA Version 2](https://www.keychron.com/products/low-profile-double-shot-pbt-lsa-keycap-set-version-2).
- [MBK Colors Chili](https://fkcaps.com/products/mbk-colors-chili),
  [Colors kit description](https://custom.fkcaps.com/keycaps/mbk/colors) and
  [other MBK ranges](https://fkcaps.com/collections/mbk).
- [Chocfox CFX](https://chosfox.com/products/chocfox-cfx-choc-keycaps).
- [Joe Scotto’s ScottoCaps](https://github.com/joe-scotto/scottokeebs/tree/main/Extras/ScottoCaps).

Catalog parameters and source URLs are in [source/catalog.json](source/catalog.json).
[provenance.json](provenance.json) records CAD hashes and checks every rendered
family’s contacts and locating posts against all 86 real PCB patterns.
[preserved-sources.json](preserved-sources.json) records the unchanged PCB,
geometry, manufacturing outputs and previous V11 viewer. Brave interaction
checks and captures are saved in [validation.json](validation.json) and `views/`.
The [final artifact check](final-check.json) also records the HTML hash, reference
palette checks, filtered keycap choices and mobile/offline verification.

Build using the existing CAD environment and pinned Three.js/esbuild packages:

```sh
/tmp/tkl-v11-env/bin/python tkl/tkl12/render-switches/source/build.py
node tkl/tkl12/render-switches/source/capture.cjs
```

The builder uses the installed V10 render packages by default, or the directory
specified by `V12_RENDER_NODE_MODULES`. Dependencies are also pinned in
`source/package.json` and its lock file for a separate installation.
