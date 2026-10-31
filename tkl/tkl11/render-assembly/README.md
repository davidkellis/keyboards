# V11 assembly studio

Open [index.html](index.html) in Brave or Chrome. The interactive 360° model is
self-contained and works offline. V10 viewers, mechanical source files, and V11
PCB/manufacturing files remain unchanged.

Choose **Exploded** to separate the lower case, battery, PCB/electronics,
acrylic plate, top frame, switches and keycaps. The camera switches to a lower
stack angle so the battery can be seen beneath the PCB. Drag **Layer separation**
to inspect intermediate positions, and choose **Assembled** to seat the parts
again. All original assembly transforms are restored at zero separation.

Use **Visible parts** to hide individual layers, **Transparent case** to look
inside the assembled shell, and **Exploded layer labels** to identify the parts.
Screws follow the lower case; nuts and carriers follow the top frame. The battery
is a nominal 147 × 44 × 5 mm pouch in the existing battery reserve.

The earlier controls remain: both case editions, five keycap profiles, four plate
treatments, reflective backing, light brightness and day/dim studio lighting,
case/keycap colours, surface finish, key travel and socket engagement. Orbit
freely, auto-rotate, or use the ten camera presets. Under Inspect, hide the caps
to expose the plate. Turn off automatic fitting if you want to keep the camera
fixed while changing separation.

**Save this view** exports a PNG at twice the viewport resolution, including
the exploded labels when they are shown. **Download
this 3D model** exports the selected visible parts as GLB in their current
assembled or exploded positions. Hidden parts and the unused case edition are
excluded. Layer labels are screen annotations; they are not included in the GLB.
These are appearance models; use the separate millimetre manufacturing and print
files for fabrication.

## Geometry and limits

The PCB mesh comes from the current routed **V11** board, including its real pin
holes and ten optical slots. The KiCad 1.53 mm native substrate export is displayed
at the board's nominal 1.6 mm finished thickness. LED models and light-field
sources use the current two-row V11 coordinates, not V10's six-source layout.
The reference meshes and all 86 switch centers use their established assembly
positions; `provenance.json` records the source hashes.

The separate plate and top frame are a **fit concept**. The original printed
upper integrates the switch plate into one solid. This rendering partitions that
upper and shows a separate 1.5 mm acrylic sheet following the V11 trial drawing,
including its module/pin reliefs. Plate retention, switch clips, structural support
and assembly access still need a mechanical prototype. The viewer does not release
a new case or a finished light-guide manufacturing design.
Isolated spacers formerly attached to the integrated plate are omitted from the
separate-frame concept so they are not shown floating without support.

The exploded stack explains how the layers sit relative to one another. It is
not a service sequence: soldered switches cannot be lifted out of the PCB without
desoldering, and the module/connector cannot pass through arbitrary case openings.

Lighting is illustrative. Ten equal source kernels show possible concentrated,
scattered and patterned appearances; lateral coupling, losses at switch holes,
actual LED flux and calibrated brightness are not solved. Uniformity and useful
legend brightness require physical testing. Detached plates stop receiving the
illustrative PCB light in exploded mode. The brightness slider is a visual
comparison, not a new current setting or battery-runtime estimate.

XVX profiles, switch details, battery appearance, components and surface finish
are approximate. ScottoCaps Flat and Glass MX use Joe Scotto's adapted source
meshes; retain [attribution](ATTRIBUTIONS.md) and their CC BY-NC-SA 4.0 license
when sharing these assets or exports containing them.

## Rebuild and verify

Use the repository's KiCad/Python environment with numpy, trimesh, shapely and
manifold3d. The current workspace environment is `/tmp/tkl-v11-env/bin/python`.
Install the pinned Node packages with `npm ci --prefix source`, or set
`V11_RENDER_NODE_MODULES` to an existing installation. The build also reads the
preserved V10 case and keycap assets in the same repository.

```sh
/tmp/tkl-v11-env/bin/python source/build.py
node source/capture.cjs validate
node source/capture.cjs capture
node source/capture.cjs exports
/tmp/tkl-v11-env/bin/python source/package_release.py
```

Browser checks exercise 120 case/profile/treatment/separation combinations,
assembly round trips, layer visibility, the real ten source locations, travel,
materials, animation, mobile layout and actual PNG/GLB downloads. Rendering is
captured from the offline viewer with Brave/Playwright; network requests are
blocked. Results are saved in the three `*-validation.json` files.
