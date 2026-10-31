"""Verify v9.2 preservation and unchanged PCB manufacturing for v9.3."""
from pathlib import Path
import hashlib,json

root=Path(__file__).resolve().parents[1]
old=root.parent/'tkl9.2'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
preserved=json.loads((root/'reference/preserved-v9.2.json').read_text())
for name,digest in preserved.items():
    assert sha(old/name)==digest, f'Preserved v9.2 changed: {name}'
identical={}
for p in (root/'kicad').rglob('*'):
    if p.is_file():
        name=p.relative_to(root)
        assert p.read_bytes()==(old/name).read_bytes(),f'Electrical source changed: {name}'
        identical[str(name)]=sha(p)
for name in ['parts.json','matrix-map.csv','jlcpcb-bom.csv','jlcpcb-cpl.csv']:
    rel='manufacturing/'+name
    assert (root/rel).read_bytes()==(old/rel).read_bytes(),rel
    identical[rel]=sha(root/rel)
cfg=json.loads((root/'scripts/fit-config.json').read_text())
old_cfg=json.loads((old/'scripts/fit-config.json').read_text())
assert cfg['mounting']==old_cfg['mounting']
assert cfg['battery']==old_cfg['battery']
for key in ['fixed_footprint_mm','fixed_lips_mm','plate_thickness_mm','plate_top_above_pcb_mm']:
    assert cfg[key]==old_cfg[key],key
fit=json.loads((root/'case/fit-report.json').read_text())
assert not fit['collisions'] and fit['pcb_case_overlap_mm3']<1e-4
assert not fit['recessed_plate']['has_top_cover']
assert min(fit['recessed_plate']['minimum_horizontal_clearances_mm'].values())>=.3
assert len(fit['mounts'])==12
for name in ['case.stl','case-left.stl','case-right.stl']:
    assert (root/'case'/name).read_bytes()==(old/'case'/name).read_bytes(),name
assert fit['surface_finish']['actual_roof_thickness_mm']>=.9-1e-8
assert fit['surface_finish']['actual_pin_clearance_mm']>=.3-1e-8
report=dict(preserved_v9_2_files=len(preserved),unchanged_electrical_files=identical,
            same_mounting_hardware=True,same_battery_reserve=True,
            v9_2_base_stls_identical=True,
            case_dimensions_mm=fit['case_size'],rim=fit['recessed_plate'],
            physical_fit_verified=False)
(root/'validation/mechanical-revision.json').write_text(json.dumps(report,indent=2)+'\n')
print('Preserved',len(preserved),'v9.2 files;',len(identical),'electrical files identical; revised mechanics pass.')
