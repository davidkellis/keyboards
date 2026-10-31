# V8 design references

The controller, regulator, USB and RF circuits are inherited from the audited
[v7 reference work](../../tkl7/reference/README.md). The imported Nordic coupon
and matrix source live there; they are not duplicated in this revision.

`mcu-pinmap.json` and `firmware-pins.json` preserve the physical package and
GPIO maps. Logical ROW8 is absent; compact it out of the eleven-row matrix.

V8 changes only the lighting placement/footprints/routing and adds top assembly
fiducials. [lighting-audit.json](../validation/lighting-audit.json) confirms
that every non-lighting copper track/via is unchanged from v7 and that all
six top LED courtyards clear the 15 mm switch body envelopes. Uniformity has
not been measured.

- [Lite-On LTW-C191TS5 manufacturer data sheet](https://optoelectronics.liteon.com/upload/download/DS22-2004-201/LTW-C191TS5.PDF)
- [JLCPCB C125123 assembly listing](https://jlcpcb.com/partdetail/LiteOn-LTWC191TS5/C125123)
- [Shared mechanical generation and dimension references](../../mechanical/README.md)
