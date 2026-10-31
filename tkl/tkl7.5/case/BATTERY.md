# v7.5 battery fit and electrical limits

The inherited bay reserves 270 × 52 × 6.3 mm, for a finished protected 1S pack
no larger than **264 × 50 × 5.5 mm**, with 0.5 mm padding below. It starts at
case X=6 / Y=78.5 mm and is clear of the modelled module/cable. No retail pack,
capacity or 10,000 mAh claim is approved. The 9858102 does not fit this exterior.

v7.5 uses the clone charger. The old BQ24072 settings and J5 temperature sensor
do not exist on this carrier. A pack protection PCB is not automatically
protection against charging hot/cold cells. Verify the actual module charger
and suitable cell-temperature protection for the selected pack.

Use a suitable protected **1S, 4.2 V maximum-charge** lithium pack. J1 pin 1 is
positive and pin 2 ground; verify cable polarity rather than infer it from the
JST housing. SW87 disconnects both battery operation and charging. Its rating
is 300 mA: do not enable a 500 mA charging boost. Begin with a verified low-current
setting. At 100 mA a hypothetical 10 Ah pack needs at least 100 hours before
charge taper and keyboard consumption; this is not a charge-time guarantee.

See [BRINGUP.md](../BRINGUP.md). The STEP battery box is a reserved-volume gauge,
not an actual selected cell or a complete validated charging system.
