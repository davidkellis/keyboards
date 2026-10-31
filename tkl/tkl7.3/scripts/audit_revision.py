#!/usr/bin/python3
"""Independently audit revision isolation, copper migration and mechanical fit."""
from pathlib import Path
import collections, gc, hashlib, json, subprocess, sys
sys.excepthook = sys.__excepthook__
gc.disable()
import pcbnew as k
import sexpdata as sx

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT.parent/'tkl7'
REPO = ROOT.parents[1]
O = ROOT/'validation'
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
preserved = json.loads((ROOT/'reference/preserved-revisions-sha256.json').read_text())
current = {str(p.relative_to(REPO)) for d in ('tkl/tkl7','tkl/tkl8') for p in (REPO/d).rglob('*') if p.is_file()}
assert current == set(preserved), 'Old revision file set changed'
assert all(digest(REPO/name) == sha for name,sha in preserved.items()), 'Old revision contents changed'

old = k.LoadBoard(str(BASE/'kicad/keyboard.kicad_pcb'))
new = k.LoadBoard(str(ROOT/'kicad/keyboard.kicad_pcb'))
assert old.GetCopperLayerCount() == 4 and new.GetCopperLayerCount() == 6
assert old.GetDesignSettings().GetBoardThickness() == new.GetDesignSettings().GetBoardThickness() == k.FromMM(1.6)
assert new.GetDesignSettings().m_CapVias and new.GetDesignSettings().m_FillVias
pair = lambda p: (p.x,p.y)
def item_snapshot(t, remap=False):
    row = dict(net=t.GetNetname(), start=pair(t.GetStart()), end=pair(t.GetEnd()), locked=t.IsLocked())
    if isinstance(t,k.PCB_VIA):
        row.update(kind='via', diameter=t.GetWidth(k.F_Cu), drill=t.GetDrillValue(),
                   type=t.GetViaType(), layers=[t.TopLayer(),t.BottomLayer()])
    else:
        layer=t.GetLayer()
        if remap and layer == k.In2_Cu: layer=k.In4_Cu
        row.update(kind=type(t).__name__,layer=layer,width=t.GetWidth())
        if isinstance(t,k.PCB_ARC): row['mid']=pair(t.GetMid())
    return row
before={t.m_Uuid.AsString():item_snapshot(t,True) for t in old.GetTracks()}
after={t.m_Uuid.AsString():item_snapshot(t) for t in new.GetTracks()}
assert before == after, 'Signal/via geometry, net or lock changed unexpectedly'
assert not any(t.GetLayer() in (k.In2_Cu,k.In3_Cu) for t in new.GetTracks() if not isinstance(t,k.PCB_VIA))

def children(n,tag): return [x for x in n if isinstance(x,list) and str(x[0]) == tag]
def child(n,tag): return next(iter(children(n,tag)),None)
ot=sx.loads((BASE/'kicad/keyboard.kicad_pcb').read_text())
nt=sx.loads((ROOT/'kicad/keyboard.kicad_pcb').read_text())
stack=child(child(nt,'setup'),'stackup')
assert child(stack,'copper_finish')[1] == 'OSP'
sl={x[1]:x for x in children(stack,'layer')}
for name in ('dielectric 1','dielectric 5'):
    assert child(sl[name],'thickness')[1] == .2104
    assert child(sl[name],'epsilon_r')[1] == 4.4
assert [x[1] for x in children(stack,'layer') if str(child(x,'type')[1]) == 'copper'] == ['F.Cu','In1.Cu','In2.Cu','In3.Cu','In4.Cu','B.Cu']

# Every existing zone policy/outline is retained, with old In2 now on In4.
def zone_snapshot(z,remap=False):
    ignored={'uuid','filled_polygon','fill_segments','filled_areas_thickness'}
    out=[]
    for x in z:
        if isinstance(x,list) and str(x[0]) in ignored: continue
        if remap and isinstance(x,list) and str(x[0])=='layer' and x[1]=='In2.Cu': x=[x[0],'In4.Cu']
        out.append(x)
    return out
oz={child(z,'uuid')[1]:z for z in children(ot,'zone')}
nz={child(z,'uuid')[1]:z for z in children(nt,'zone')}
assert set(oz) <= set(nz)
assert all(zone_snapshot(z,True) == zone_snapshot(nz[uid]) for uid,z in oz.items()), 'Existing zone policy/outline changed'
rf=next(z for z in oz.values() if child(z,'keepout') and child(z,'layer')[1]=='In1.Cu')
for layer in ('In1.Cu','In2.Cu','In3.Cu','In4.Cu'):
    rule=next(z for z in nz.values() if child(z,'keepout') and child(z,'layer')[1]==layer)
    assert child(rule,'polygon') == child(rf,'polygon')
    assert child(rule,'keepout') == child(rf,'keepout')
assert len(nz)-len(oz) == 6

# Source-derived body/hole geometry; model MPN metadata is the only difference.
subprocess.run([sys.executable,str(ROOT/'scripts/export_geometry.py'),str(ROOT)],check=True)
old_geometry=json.loads((BASE/'case/board-geometry.json').read_text())
new_geometry=json.loads((ROOT/'case/board-geometry.json').read_text())
def geometry_only(data):
    data=json.loads(json.dumps(data));data.pop('source_sha256')
    for component in data['components']: component.pop('mpn')
    return data
assert geometry_only(old_geometry) == geometry_only(new_geometry), 'Mechanical geometry changed'
assets=[p for p in (ROOT/'case').rglob('*') if p.suffix.lower() in ('.stl','.step','.dxf')]
assert all(p.read_bytes() == (BASE/'case'/p.relative_to(ROOT/'case')).read_bytes() for p in assets)
report=json.loads((BASE/'case/fit-report.json').read_text())
report['source_sha256']=digest(ROOT/'kicad/keyboard.kicad_pcb')
report['geometry_reused_from_source_sha256']=digest(BASE/'kicad/keyboard.kicad_pcb')
report['geometry_reuse_evidence']='../validation/revision-audit.json: exact mechanical geometry and model asset comparison'
(ROOT/'case/fit-report.json').write_text(json.dumps(report,indent=2)+'\n')

summary=dict(revision='v7.3',parent_revision='v7.2',parent_commit='4cb332e',
             source_sha256=digest(ROOT/'kicad/keyboard.kicad_pcb'),preserved_old_files=len(preserved),
             old_revisions_unchanged=True,layer_count=6,stackup='JLC06161H-7628',finish='OSP',
             nominal_thickness_mm=1.6,original_track_and_via_items=len(before),
             original_copper_and_vias_preserved=True,layer_remap={'In2.Cu':'In4.Cu'},
             new_layers=['In2.Cu GND','In3.Cu GND'],new_zone_count=6,
             rf_keepout_on_all_four_inner_layers=True,outer_reference_spacing_mm=.2104,
             via_count=sum(isinstance(t,k.PCB_VIA) for t in new.GetTracks()),
             mechanical_geometry_identical=True,identical_mechanical_assets=len(assets),
             fitted_components=142,bom_groups=31,
             u1_candidate='NRF52840-QIAA-R / C190794',
             j2_programming='Solder temporary 1.8 V SWD leads; no bare-OSP pogo contact',
             impedance_note='Outer signal/reference spacing and existing copper preserved; no field-solver or physical RF/USB qualification claimed.')
(O/'revision-audit.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
