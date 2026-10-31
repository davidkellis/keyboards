# v9.2 PCB fit prints with larger holes

Print at 100% in millimetres, flat on the bed. These gauges add **0.4 mm
to hole diameters** (0.2 mm per side); all pin centers, the 1.6 mm board
thickness and the board outline remain unchanged. This allowance compensates
for plastic printing and permits insertion trials; it does not establish the
clearance of manufactured PCB holes. Do not also apply a slicer hole expansion
for the first trial. Printer results still depend on material and calibration.

Start with `single-switch-easy-fit.stl` for one actual Choc V2 switch. Then use
`fit-coupon-pcb-easy-fit.stl` in place of the old rear-corner PCB coupon to test
the actual clone and several switches. Use the matching base, plain plate and
1 mm module gap gauge; those mating parts are included in this ZIP. The clone
goes underneath, components toward the case floor and USB toward the rear.

The case corner includes the recessed USB bezel: a 10.1 x 3.8 mm socket slot
behind a wider, blind cable-housing recess. Its 0.6 mm web and the provisional
socket dimensions need a physical fit trial. Check thin-wall paths in the
slicer, seat the socket through the bezel, and confirm full cable insertion
without pushing on the module. There is no separate bezel part to attach.

`pcb-left-easy-fit.stl` and `pcb-right-easy-fit.stl` are full PCB halves for a
256 mm bed. `pcb-bare-easy-fit.stl` is the unsplit PCB for a larger printer.
Use the bare gauges to insert real parts. The old populated models contain
printed pin envelopes and are not insertion-test fixtures.

The main case directory also receives these models as `pcb-bare.stl`,
`pcb-left.stl`, `pcb-right.stl`, `fit-coupon-pcb.stl`, `rim-coupon-pcb.stl`
and `single-switch-fit.stl`.
Only switch pin/locating holes and the 29 module holes are enlarged. Other
holes, nominal STEP references, populated envelope models, KiCad sources and
JLC Gerber/BOM/CPL files are unchanged. Check that every module pin enters vertically without bending;
larger holes can mask small registration errors. Physical confirmation of the
three auxiliary pad positions is especially important before ordering.

Rebuild: `python tkl/tkl9.2/scripts/build_print_fit.py` in the CadQuery environment.
`validation.json` records dimensions, mesh checks, sizes and source hashes.
