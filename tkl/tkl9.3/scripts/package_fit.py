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
surface=json.loads((case/'surface-validation.json').read_text())
for name,sha in surface['mesh_sha256'].items():
 assert hashlib.sha256((case/name).read_bytes()).hexdigest()==sha
assert usb['fit_config_sha256']==fit['fit_config_sha256']
for name,sha in usb['mesh_sha256'].items():
 assert hashlib.sha256((case/name).read_bytes()).hexdigest()==sha
files=['fit-coupon-case.stl','fit-coupon-pcb.stl','fit-coupon-upper.stl',
       'led-diffuser.stl','led-fit-coupon.stl','led-diffuser-assembly.step',
       'rim-coupon-case.stl','rim-coupon-plate.stl','rim-coupon-pcb.stl',
       'rim-coupon-assembly.step',
       'mount-coupon-case.stl','mount-coupon-pcb.stl','mount-coupon-upper.stl',
       'mount-coupon-assembly.step',
       'single-switch-fit.stl','print-fit-files.json',
       'module-gap-gauge.stl','u1-envelope.stl','usb_socket-envelope.stl','usb_plug_external-envelope.stl',
       'README.md','fit-report.json','module-fit.png','layout-preview.svg','mounting-plan.svg',
       'usb-surround.png','usb-opening-validation.json','surface-validation.json','rear-detail.png']
for f in files:
 if f.endswith('.stl'):assert mesh[f]['watertight'] and mesh[f]['positive_volume'] and mesh[f]['solid_shells']==1
manifest={f:hashlib.sha256((case/f).read_bytes()).hexdigest() for f in files}
with zipfile.ZipFile(case/'tkl-v9.3-fit-coupons.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(case/f,f)
 z.writestr('SHA256.json',json.dumps(manifest,indent=2)+'\n')
print('Packaged',len(files),'coupon files with hashes')

# Full, matched print set: keep mechanical parts and compensated PCB gauges together.
full_files=['case.stl','case-left.stl','case-right.stl','plate.stl',
            'plate-left.stl','plate-right.stl','pcb-bare.stl','pcb-left.stl','pcb-right.stl',
            'base-split.step','plate-split.step','plate.step',
            'fit-assembly.step','pcb-bare.step','mesh-validation.json',
            'plate-preview.png','base-preview.png','assembled-exploded.png','assembled-preview.png']
full_files=sorted(set(files+full_files+[p.name for p in case.glob('battery-*-gauge-*.stl')]))
for name in full_files:
 if name.endswith('.stl'):
  assert mesh[name]['watertight'] and mesh[name]['positive_volume'] and mesh[name]['solid_shells']==1,name
with zipfile.ZipFile(case/'tkl-v9.3-print-kit.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name in full_files:z.write(case/name,name)
 z.writestr('SHA256.json',json.dumps({name:hashlib.sha256((case/name).read_bytes()).hexdigest() for name in full_files},indent=2)+'\n')
print('Packaged',len(full_files),'full print/fit files')
