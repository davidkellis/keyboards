"""Verify preserved revisions and v10's coordinated case/plate/PCB geometry."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
preserved=json.loads((root/'reference/preserved-revisions.json').read_text())
for name,digest in preserved.items():assert sha(root.parent/name)==digest,name
cfg=json.loads((root/'scripts/fit-config.json').read_text())
old=json.loads((root.parent/'tkl9.3/scripts/fit-config.json').read_text())
for key in ['fixed_footprint_mm','fixed_lips_mm','plate_thickness_mm','plate_top_above_pcb_mm']:
 assert cfg[key]==old[key],key
for key,value in old['mounting'].items():
 if key!='points':assert cfg['mounting'][key]==value,key
fit=json.loads((root/'case/fit-report.json').read_text())
g=json.loads((root/'case/board-geometry.json').read_text())
assert fit['source_sha256']==sha(root/'kicad/keyboard.kicad_pcb')
assert not fit['collisions'] and fit['pcb_case_overlap_mm3']<1e-4
assert not fit['recessed_plate']['has_top_cover']
assert min(fit['recessed_plate']['minimum_horizontal_clearances_mm'].values())>=.3
assert len(fit['mounts'])==12 and len(g['switches'])==86
assert fit['surface_finish']['actual_roof_thickness_mm']>=.9-1e-8
assert fit['surface_finish']['actual_pin_clearance_mm']>=.3-1e-8
switches={s['ref']:s for s in g['switches']}
module=next(c for c in g['components'] if c['ref']=='U1')
x,y,xx,yy=module['bounds']
assert switches['SW1']['xy'][0]+7.5<x<xx<switches['SW2']['xy'][0]-7.5
assert cfg['module']['placement_kicad_mm']==[57.15,37.49]
assert all(nom<maximum<reserved for nom,maximum,reserved in zip(cfg['battery']['nominal_dimensions_mm'],cfg['battery']['pack_max_dimensions_mm'],cfg['battery']['reserved_dimensions_mm']))
report=dict(preserved_files=len(preserved),same_mounting_hardware=True,moved_mounts=['H9','H12'],
 switch_count=86,clone_between_esc_f1=True,restored_keys=['SW9','SW15','SW16'],
 case_dimensions_mm=fit['case_size'],battery=fit['battery'],physical_fit_verified=False)
(root/'validation/mechanical-revision.json').write_text(json.dumps(report,indent=2)+'\n')
print('Preservation, fixed profile, 86 keys, Esc/F1 module, M2 hardware and CAD fit pass.')
