V10 / Acrylic plate appearance study

Open index.html in Brave or Chrome. The viewer is self-contained and works
offline. Earlier cases, viewers, PCB, Gerbers and print files are preserved.

WHAT TO COMPARE

Four treatments are available: the current opaque plate, clear acrylic,
lightly frosted acrylic, and selectively engraved acrylic. The three acrylic
options have a switchable white backing. Both existing case editions and all
five previous keycap profiles remain available.

Start with XVX Skyline R2 BOW, Edition 2, Dim studio and Top or Light detail.
Change only Plate treatment to compare the appearances. Show keycaps can be
turned off under Inspect to reveal the sheet beneath them. The raised frame
and cap skirts conceal much of the plate from a low viewing angle; this study
does not add a glowing perimeter or new openings in the outside case walls.

Drag to orbit, scroll to zoom, and use Auto-rotate for a full 360 degree view.
Save this view exports a PNG; Download this 3D model exports the selected
assembly, acrylic material, emission textures and backing as GLB. The existing
2.8 mm key-travel slider is an appearance/clearance aid, not a fit guarantee.

HOW TO READ THE LIGHTING

The PCB is unchanged. The model uses the same six LTW-C230DS locations, the
existing 1 kohm LED branch resistors, and six visual clear input collectors.
It does not add per-key LEDs or make every keycap legend emit light.

Clear acrylic emphasizes local hot spots; frosted acrylic illustrates wider,
softer pools; engraving illustrates small extraction dots and a broader
distribution if input coupling works. These are intended appearances to
compare, not predictions of a purchased acrylic product's performance.

The emission textures use six radial kernels with equal INITIAL integrated
weight for each treatment. The wider distributions have lower peaks, and
light outside the sheet or removed by holes is lost. There is a common display
gain, not a measured lux or luminance calibration. The backing toggle applies
an illustrative return-light factor; the displayed 30 percent change is not
a measured efficiency. Neither propagation around all switch holes nor
coupler losses, actual LED flux, material scattering, ray paths or battery
life are solved. The engraved option is the most optimistic coupling study.
The shared brightness slider changes the illustrative display strength, not
the electrical design.

Ordinary clear sheet alone is not a uniform light panel. Specialized light
guiding acrylic, effective input coupling and controlled surface extraction
may help, but a small optical sample using the actual LED/PCB drive is needed
to establish whether useful light spreads far enough between these keys.

MECHANICAL STATUS

This is a new rendering study, not a print or laser-cut manufacturing release.
The nominal 1.5 mm plate envelope matches the old CAD stack. Kailh's MINI
drawing references a 1.2 mm aluminum plate; that does not establish an acrylic
thickness or confirm its clips will retain. Test switch retention and full
travel on a coupon before committing to a material or thickness.

The integrated printed upper has been partitioned visually into an opaque
support/frame and an acrylic plate. The original solids are retained as the
baseline. A production acrylic plate needs support, captured edges or another
retention scheme, screw/nut and switch-pin relief, assembly access and an
appropriate tolerance plan. The thin backing needs clearance and an opaque,
electrically insulating material. No mounting release is implied here.

The PCB, controller, key positions, footprint, battery reserve and typing
angle are unchanged. Source hashes are recorded in provenance.json and
acrylic-study.json. browser-validation.json records the viewer checks.

REFERENCE MATERIAL

Kailh MINI switch drawing (including aluminum plate and travel references):
https://www.kailhswitch.com/uploads/15927/files/CPG1353S01D02-01-data-sheet.pdf
Local manufacturer copy: reference/CPG1353S01D02-01-datasheet.pdf

ACRYLITE LED light guiding sheet:
https://www.acrylite.co/products/brands/acrylite-led/light-guiding-edge-lit-sheet

PLEXIGLAS LED product families / light guiding versus diffusing grades:
https://www.plexiglas.de/en/products/plexiglas/plexiglas-led

Bivar illumination/light-pipe design handbook:
https://www.bivar.com/Files/Content/Handbook-to-Illumination-Design-101.pdf

ScottoCaps mesh sources, adaptations and licensing: ATTRIBUTIONS.md.
The ScottoCaps-derived meshes remain CC BY-NC-SA 4.0, including in exports.

REBUILD

Use source/package-lock.json with npm ci in source/, or point
V10_RENDER_NODE_MODULES at the existing render-case-editions/source/node_modules.
Install Python dependencies from source/requirements.txt in an isolated venv.
Run source/prepare_acrylic.py, then source/build.py.
Run source/capture.cjs with Node and the following stage arguments:
  validate                       (all 40 selectable combinations)
  features                       (controls, lighting, exports, mobile, hashes)
  capture raised clear           (one edition / treatment's WebGL views)
  capture raised frosted
  capture raised etched
  capture raised original
  capture current clear          (likewise for other current treatments)
  caps                           (five keycap comparison views)
The short capture batches avoid long-running software-renderer sessions.
Run source/comparisons.py with Pillow to compose the captured comparisons.

No external HTTP resources are fetched by index.html during normal use.
