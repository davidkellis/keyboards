#!/usr/bin/env python3
"""Bundle the validated small fit samples and their dimensions for printing."""
from pathlib import Path
import hashlib,json,zipfile
root=Path(__file__).resolve().parents[1];case=root/'case'
fit=json.loads((case/'fit-report.json').read_text())
assert not fit['collisions'] and fit['pcb_case_overlap_mm3']<1e-4
assert fit['source_sha256']==hashlib.sha256((root/'kicad/keyboard.kicad_pcb').read_bytes()).hexdigest()
assert fit['fit_config_sha256']==hashlib.sha256((root/'scripts/fit-config.json').read_bytes()).hexdigest()
mesh={row['file']:row for row in json.loads((case/'mesh-validation.json').read_text())}
usb=json.loads((case/'usb-opening-validation.json').read_text())
assert usb['fit_config_sha256']==fit['fit_config_sha256']
for name,sha in usb['mesh_sha256'].items():
 assert hashlib.sha256((case/name).read_bytes()).hexdigest()==sha
files=['fit-coupon-case.stl','fit-coupon-pcb.stl','fit-coupon-plate.stl','fit-coupon-cover.stl',
       'single-switch-fit.stl','print-fit-files.json',
       'module-gap-gauge.stl','u1-envelope.stl','usb_socket-envelope.stl','usb_plug_external-envelope.stl',
       'README.md','fit-report.json','module-fit.png','layout-preview.svg',
       'usb-surround.png','usb-opening-validation.json']
for f in files:
 if f.endswith('.stl'):assert mesh[f]['watertight'] and mesh[f]['positive_volume'] and mesh[f]['solid_shells']==1
manifest={f:hashlib.sha256((case/f).read_bytes()).hexdigest() for f in files}
with zipfile.ZipFile(case/'tkl-v9-fit-coupons.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(case/f,f)
 z.writestr('SHA256.json',json.dumps(manifest,indent=2)+'\n')
print('Packaged',len(files),'coupon files with hashes')
