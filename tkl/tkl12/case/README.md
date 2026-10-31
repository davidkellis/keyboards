# V12 PCB fit models

The case outline, mounting locations and existing Kailh switch stack are inherited
unchanged from V11. This folder contains updated **PCB** models, not a new case.
The Gateron plate-height variant has not been designed here.

- `pcb-bare.stl`: exact fabrication holes; KiCad exports the FR-4 substrate at
  about 1.53 mm, excluding outer copper from the nominal finished 1.6 mm stack.
- `pcb-fit-check.stl`: print gauge at 1.6 mm finished thickness. Plated holes
  gain 0.4 mm diameter and plastic/mounting holes gain 0.3 mm for print shrinkage.
- `switch-fit-coupon.stl`: three repetitions of the same V12 pattern in a small
  print gauge. Try Choc V2, Choc V1 and Gateron 3.0 independently. Its oversize
  holes check alignment only; plastic shrinkage cannot validate PCB drill fits.
  Insert switches from the face with the small blind corner groove. Keep that
  groove at the front-left when comparing the mounting diagram; testing from
  the other face would mirror the pin pattern.

Never fabricate from a fit-gauge STL. Use the Gerber/drill package. A shared PCB
pattern does not settle plate clip retention, keycap/stabilizer fit, travel or
the acrylic lighting result. See `../SWITCHES.md` before changing switch family.
