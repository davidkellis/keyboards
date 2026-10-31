#!/usr/bin/python3
"""Independent isolation, layout, assembly and no-via-in-pad checks."""
import hashlib,json
from routing_geometry import *
ROOT=Path(__file__).resolve().parents[1]
preserved=json.loads((ROOT/'reference/preserved-revisions.json').read_text())
assert all(hashlib.sha256((ROOT.parent/name).read_bytes()).hexdigest()==sha for name,sha in preserved.items()),'Prior revision changed'
old=k.LoadBoard(str(ROOT.parent/'tkl7.4/kicad/keyboard.kicad_pcb'))
b=k.LoadBoard(str(ROOT/'kicad/keyboard.kicad_pcb'))
assert b.GetCopperLayerCount()==2 and b.GetDesignSettings().GetBoardThickness()==mm(1.6)
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
assert sum(z.GetIsRuleArea() for z in b.Zones())==2
result=dict(parent='v7.4',revision='v7.5',preserved_files_checked=len(preserved),
    unchanged_switch_positions_and_drills=86,copper_layers=2,thickness_mm=1.6,
    jlc_placements=len(fitted),jlc_bom_groups=sum(g['assembly'] in ('SMT','THT-bottom') for g in catalog['groups']),
    assembly_side='Bottom',user_installed_module=True,via_count=len(vias),
    filled_or_capped_vias=False,min_via_drill_to_smt_land_mm=minimum,
    hardware_tested=False,production_ready=False,
    holds=['Actual clone/cable dimensions and polarity','Module charge current and cell-temperature protection',
           'Custom firmware and prototype electrical/RF tests','Keycap and plate-mount stabilizer travel'])
(ROOT/'validation/revision-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
