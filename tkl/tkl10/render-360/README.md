# V10 assembled keyboard — interactive 360° studio

Open **[index.html](index.html)** in Brave or Chrome. It is a self-contained,
offline HTML file; it needs no server or network downloads. WebGL must be
available in the browser.

Drag in any direction to orbit, scroll to zoom, and right-drag to pan. The
camera can go beneath the keyboard. Presets show the front, rear, right
profile, top, underside, rounded front corner and rear USB surround. Press
**R** or Reset view to return to the overview. Auto-rotate provides a turntable.

The controls compare Graphite, Chalk and Slate finishes, custom case colours,
light/dark/two-tone keycaps, satin/matte roughness and raking light. They change
the visualization only. Save this view exports the current canvas at twice
its displayed pixel resolution.

## Geometry and appearance

The enclosure is the latest `../case-hidden-mounts/` design: actual upper,
removable bottom, USB insert, eight M2 screws/nuts and internal nut carriers.
The 355.56 × 133.352 mm footprint, 2.5 mm top round-over, 3 mm vertical corner
radii, openings and small rear insert/bottom joints are retained. The PCB
comes from its existing assembly mesh. All 86 switch centres use the v10
geometry and its 5.696° tilt.

The 5 mm low-profile keycaps, ANSI legends, switch bodies, stabilizer appearance,
controller/component bodies and USB-C socket details are illustrative. They
are not supplier-exact 3D models. The cap height and mounting position follow
the existing fit configuration. The nominal 147 × 44 × 5 mm battery body is
inside the existing reserve. No cable or optional feet are fitted.

Smooth materials represent a finished enclosure. Split printed parts require
bonding and finishing to match this appearance. This visualization does not
establish physical fit, strength, RF performance, electronics function or the
appearance of an unfinished print.

`provenance.json` records the source hashes and preserved inputs. No PCB,
printable case, manufacturing handoff or JLCPCB order has been changed.

## Outputs

- `index.html`: offline, freely rotatable studio.
- `v10-assembled.glb`: completed visual model for other 3D viewers.
- `v10-hero-high-resolution.png`: high-resolution overview without controls.
- `studio-preview.png`: viewer and controls.
- `hero.png`, `front.png`, `rear.png`, `side.png`, `top.png`, `bottom.png`,
  `edge.png`, `usb.png`: captured camera presets.
- `browser-validation.json`: actual offline browser interaction and export checks.

## Rebuild

Run `npm ci` in `source/`, then run `python source/build.py` from this directory.
Python uses only its standard library; the JavaScript dependencies are pinned.
An existing installation can be selected with `V10_RENDER_NODE_MODULES`.

Run `node source/capture.cjs` for the browser checks and image/GLB exports.
It uses `/usr/bin/brave-browser` by default; `V10_RENDER_BROWSER` can select
another Chromium executable. HTTP(S) requests are blocked during verification
to confirm that the HTML works offline. The renderer uses Three.js under the
included MIT license.
