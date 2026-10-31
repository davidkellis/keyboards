#!/usr/bin/python3
"""Create an unrouted v9 placement from v7.5. Replaces v9 only."""
import gc,json
import sexpdata as sx
from pathlib import Path
gc.disable()
import pcbnew as k
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'kicad/keyboard.kicad_pcb'
config=json.loads((ROOT/'scripts/fit-config.json').read_text())
removed={f'{prefix}{i}' for prefix in ('SW','D') for i in (9,15,16)}
tree=sx.loads((ROOT.parent/'tkl7.5/kicad/keyboard.kicad_pcb').read_text())
def keep(node):
    if not isinstance(node,list):return True
    if str(node[0]) in ('segment','arc','via','zone'):return False
    if str(node[0])=='footprint':
        ref=next(x[2] for x in node if isinstance(x,list) and str(x[0])=='property' and x[1]=='Reference')
        return ref not in removed
    return True
P.write_text(sx.dumps([n for n in tree if keep(n)]))
b=k.LoadBoard(str(P))
fp={f.GetReference():f for f in b.GetFootprints()}
vec=lambda x,y:k.VECTOR2I(k.FromMM(x),k.FromMM(y))
u=fp['U1'];u.SetOrientationDegrees(0)
u.SetPosition(vec(*config['module']['placement_kicad_mm']))
power=fp['SW87'];power.SetPosition(vec(327.03,k.ToMM(power.GetPosition().y)))
for layer in (k.F_Cu,k.B_Cu):
    z=k.ZONE(b);z.SetLayer(layer);z.SetIsRuleArea(True)
    z.SetDoNotAllowZoneFills(True);z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True)
    z.SetDoNotAllowPads(True);z.SetDoNotAllowFootprints(False)
    x,y,xx,yy=config['module']['antenna_keepout_kicad_bounds_mm']
    p=z.Outline();p.NewOutline()
    for a,c in [(x,y),(xx,y),(xx,yy),(x,yy)]:p.Append(k.FromMM(a),k.FromMM(c))
    b.Add(z)
b.GetTitleBlock().SetTitle('TKL v9 - 83 keys; direct rear USB module')
b.GetTitleBlock().SetRevision('v9')
k.SaveBoard(str(P),b)
cat=json.loads((ROOT.parent/'tkl7.5/manufacturing/parts.json').read_text())
for group in cat['groups']:
    group['refs']=[r for r in group['refs'] if r not in removed]
    if group['refs']==['U1']:group['notes']='User-installed underside clone; USB faces rear; 1 mm mounting gap; no tall sockets. Actual height and auxiliary pad registration require a fit trial.'
cat['notes']='v9 derives from v7.5: three rear navigation-cluster keys removed, direct rear USB-C module, no extension cable, 83 remaining matrix positions unchanged.'
(ROOT/'manufacturing/parts.json').write_text(json.dumps(cat,indent=2)+'\n')
print('v9 placement:',len(fp),'footprints; removed',sorted(removed))
