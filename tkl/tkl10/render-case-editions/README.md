# V10 case editions studio

Open [index.html](index.html) in Brave. Everything needed to view the model
is embedded, so it works offline without a server.

The **Case edition** control switches between the current floating-key
case and the new **Edition 2 raised key wells**. It preserves the camera,
keycap selection, lighting concept and key positions, making direct
comparisons easier. Edition 2 is selected initially.

The **Key travel preview** slider moves the caps and stems through 2.8 mm
while the enclosure remains fixed. This is a visual clearance inspection;
it does not simulate the switch's springs, clipping or force.

Edition 2 raises the outer deck by 3.25 mm to meet the nominal XVX skirts
with a 0.15 mm shadow gap. The switch seating plate, PCB, battery, controller
and keycap tops stay in their existing V10 positions. Its broad wells avoid
thin bars between typing rows. The case has the same footprint, rounded
edge treatment and concealed underside fastening approach.

The raised deck targets the XVX profile. ScottoCaps and the experimental
extra-flat profile remain available; their skirts will not all be flush
with this one fixed-height enclosure. Keycap shapes, engagement and light
output have the same limitations documented in the
[earlier cap / light studio](../render-keycaps-lighting/README.md).
The Scotto-derived meshes remain under CC BY-NC-SA 4.0;
[attribution](ATTRIBUTIONS.md) accompanies the viewer and GLB exports.

Use the eight view presets, orbit freely, change finishes, and save a PNG
or download the selected visible 3D assembly. Case and lighting selections
are included in the filename. GLB exports are appearance models; print the
millimetre STL files in [case-raised-deck/prints](../case-raised-deck/prints/).

The [Edition 2 design and print notes](../case-raised-deck/README.md) describe
the changed shell, unchanged hardware, full-size and split prints, and the
small front fit coupon. Original case and PCB files remain intact.

To rebuild in the keyboard repository:

```sh
python ../case-raised-deck/source/build.py
npm ci --prefix source
python source/build.py
node source/capture.cjs
python source/compare_editions.py
```

Use a Python environment with the dependencies listed in the case and
viewer `source/requirements.txt` files. The build reads the unchanged V10
assembly meshes and the new Edition 2 assets. Browser validation blocks
HTTP requests and checks both editions, all five caps and six lighting
concepts, key travel, views, controls, exports and mobile layout.
Results are recorded in `browser-validation.json`.
