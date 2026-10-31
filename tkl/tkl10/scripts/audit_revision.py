#!/usr/bin/python3
"""Independent isolation, layout, assembly and no-via-in-pad checks."""
import hashlib,json
from routing_geometry import *
ROOT=Path(__file__).resolve().parents[1]
preserved=json.loads((ROOT/'reference/preserved-revisions.json').read_text())
assert all(hashlib.sha256((ROOT.parent/name).read_bytes()).hexdigest()==sha for name,sha in preserved.items()),'Prior revision changed'
old=k.LoadBoard(str(ROOT.parent/'tkl7.5/kicad/keyboard.kicad_pcb'))
b=k.LoadBoard(str(ROOT/'kicad/keyboard.kicad_pcb'))
assert b.GetCopperLayerCount()==2 and b.GetDesignSettings().GetBoardThickness()==mm(1.6)
project=json.loads((ROOT/'kicad/keyboard.kicad_pro').read_text())['board']['design_settings']
assert not project['drc_exclusions']
assert project['rule_severities']['hole_to_hole']=='error'
ds=b.GetDesignSettings()
assert not ds.m_CapVias and not ds.m_FillVias
assert not any(getattr(ds,n) for n in ('m_CoverViasBack','m_CoverViasFront','m_PlugViasBack','m_PlugViasFront'))
assert ds.m_TentViasBack and ds.m_TentViasFront
fp={f.GetReference():f for f in b.GetFootprints()};before={f.GetReference():f for f in old.GetFootprints()}
for i in range(1,87):
 f=fp['SW'+str(i)];o=before[f.GetReference()]
 assert xy(f.GetPosition())==xy(o.GetPosition()) and f.GetOrientationDegrees()==o.GetOrientationDegrees()
 def drills(f):return sorted((p.GetNumber(),xy(p.GetPosition()),xy(p.GetDrillSize())) for p in f.Pads())
 assert drills(f)==drills(o)
assert b.GetBoardEdgesBoundingBox()==old.GetBoardEdgesBoundingBox()
assert all(f'{prefix}{i}' in fp for prefix in ('SW','D') for i in (9,15,16))
assert not (set(before)-set(fp))
mounts=json.loads((ROOT/'scripts/fit-config.json').read_text())['mounting']
assert set(fp)-set(before)=={p['ref'] for p in mounts['points']}
for p in mounts['points']:
 f=fp[p['ref']];assert f.IsBoardOnly()
 assert math.dist(xy(f.GetPosition()),(27.03+p['xy'][0],149.19-p['xy'][1]))<1e-5
 assert len(list(f.Pads()))==1
 pad=next(iter(f.Pads()));assert pad.GetAttribute()==k.PAD_ATTRIB_NPTH
 assert k.ToMM(pad.GetDrillSize().x)==mounts['pcb_drill_mm']
# Electrical pads must also stay outside each hardware exclusion. The rule
# areas allow pads because KiCad models each mounting NPTH as a pad itself.
mount_pad_clearance=1000.
for point in mounts['points']:
 center=Point(27.03+point['xy'][0],149.19-point['xy'][1])
 for f in fp.values():
  for pad in f.Pads():
   if pad.GetAttribute()==k.PAD_ATTRIB_NPTH:continue
   mount_pad_clearance=min(mount_pad_clearance,center.distance(shape(pad))-mounts['copper_keepout_radius_mm'])
assert mount_pad_clearance>=-1e-5,('Electrical pad in screw support area',mount_pad_clearance)
assert fp['U1'].GetOrientationDegrees()==0
assert xy(fp['U1'].GetPosition())==(57.15,37.49)
assert xy(fp['SW87'].GetPosition())[0]==327.03
catalog=json.loads((ROOT/'manufacturing/parts.json').read_text())
parts={r:g for g in catalog['groups'] for r in g['refs']}
assert set(parts)==set(fp)
fitted=[r for r,g in parts.items() if g['assembly'] in ('SMT','THT-bottom')]
assert len(fitted)==102
assert all(fp[r].GetLayer()==k.B_Cu for r in fitted)
assert fp['U1'].GetLayer()==k.B_Cu and parts['U1']['assembly']=='User-installed'
vias=[v for v in b.GetTracks() if isinstance(v,k.PCB_VIA)]
assert all(v.GetWidth(k.F_Cu)>=mm(.6) and v.GetDrillValue()>=mm(.3) for v in vias)
assert all(t.GetLayer() in LAYERS for t in b.GetTracks() if not isinstance(t,k.PCB_VIA))
minimum=1000
for v in vias:
 for f in fp.values():
  for p in f.Pads():
   if p.GetAttribute()!=k.PAD_ATTRIB_SMD:continue
   clearance=Point(*xy(v.GetPosition())).distance(shape(p))-k.ToMM(v.GetDrillValue())/2
   minimum=min(minimum,clearance)
assert minimum>=.1-1e-5,'Via drill too close to a paste/solder land'
assert sum(z.GetIsRuleArea() for z in b.Zones())==1+len(mounts['points'])
result=dict(parent='v9.3 / v9.1 electrical',revision='v10',preserved_files_checked=len(preserved),mounting_holes=len(mounts['points']),
    unchanged_switch_positions_and_drills_from_v7_5=86,restored_switches=['SW9','SW15','SW16'],direct_rear_usb=True,copper_layers=2,thickness_mm=1.6,
    jlc_placements=len(fitted),jlc_bom_groups=sum(g['assembly'] in ('SMT','THT-bottom') for g in catalog['groups']),
    assembly_side='Bottom',user_installed_module=True,via_count=len(vias),
    filled_or_capped_vias=False,min_via_drill_to_smt_land_mm=minimum,
    min_mount_keepout_to_electrical_pad_mm=mount_pad_clearance,hardware_tested=False,production_ready=False,
    holds=['Actual clone/socket dimensions, pin registration and direct USB insertion','Module charge current and cell-temperature protection',
           'Custom firmware and prototype electrical/RF tests','Keycap and plate-mount stabilizer travel'])
(ROOT/'validation/revision-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
