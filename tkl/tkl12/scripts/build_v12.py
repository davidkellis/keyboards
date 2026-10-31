#!/usr/bin/env python3
"""Reset V12 from its preserved V11 source; add three-family solder patterns.

This resets routing to the clipped V11 baseline. Do not run to export a finished
board; use export_manufacturing.py for that. All original pads remain intact.
"""
from routing_geometry import *
from shapely.ops import unary_union
import copy, hashlib, sexpdata as sx, uuid

R=Path(__file__).resolve().parents[1]; P=R/'kicad/keyboard.kicad_pcb'
SOURCE=R/'reference/source-v11.kicad_pcb'
S=sx.Symbol
def tag(n): return str(n[0]) if isinstance(n,list) and n else ''
def children(n,t): return [v for v in n if tag(v)==t]
def field(n,t): return next(iter(children(n,t)),None)
def uid(name): return str(uuid.uuid5(uuid.NAMESPACE_URL,'tkl-v12/'+name))
def ref(n): return next(v[2] for v in children(n,'property') if v[1]=='Reference')

assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == json.loads((R/'reference/preserved-v11.json').read_text())['kicad/keyboard.kicad_pcb']
tree=sx.loads(SOURCE.read_text()); switches=0; templates={}
for f in children(tree,'footprint'):
    r=ref(f)
    if r=='C2':
        field(f,'at')[1:3]=[124,34.5]
    if not r.startswith('SW') or r=='SW87': continue
    assert field(f,'layer')[1]=='F.Cu' and len(field(f,'at'))==3
    original={str(p[1]):p for p in children(f,'pad') if p[1]}
    assert field(original['1'],'at')[1:3]==[0,-5.9]
    assert field(original['2'],'at')[1:3]==[5,-3.8]
    name=f[1].split(':')[1].replace('SW_Kailh_Choc_V2','SW_LP_ThreeFamily')
    f[1]='V12Switches:'+name
    field(f,'descr')[1]='Soldered Choc V2 unchanged / Choc V1 / Gateron LP 3.0; see V12 SWITCHES.md'
    # Gateron's PCB layout is a TOP view. The orientation here corresponds
    # to the standard KiCad MX contact pattern, sharing Kailh's LED-facing edge.
    # Do not mirror it by treating it as Kailh's bottom ("Pattern Side") view.
    for number,x,y in [('1',2.54,-5.08),('2',-3.81,-2.54)]:
        pad=copy.deepcopy(original[number]); field(pad,'at')[1:3]=[x,y]
        field(pad,'size')[1:]=[2.4,2.4];field(pad,'drill')[1:]=[1.5]
        field(pad,'uuid')[1]=uid(r+'/gateron-contact/'+number)
        f.append(pad)
    for side in [-1,1]:
        f.append(sx.loads(f'(pad "" np_thru_hole oval (at {side*5.29} 0) (size 2.32 1.9) (drill oval 2.32 1.9) (layers "*.Cu" "*.Mask") (uuid "{uid(r+"/locator/"+str(side))}"))'))
    if name not in templates:
        template=copy.deepcopy(f)
        template[1]=name
        template[:]=[v for v in template if tag(v) not in ('at','path','sheetname','sheetfile','uuid')]
        for p in children(template,'pad'):
            p[:]=[v for v in p if tag(v) not in ('net','pinfunction','pintype')]
        next(p for p in children(template,'property') if p[1]=='Reference')[2]='REF**'
        templates[name]=template
    switches+=1
assert switches==86
title=field(tree,'title_block');field(title,'title')[1]='TKL v12 - Choc V2 / Choc V1 / Gateron LP 3.0; soldered switches'
field(title,'rev')[1]='v12'
P.write_text(sx.dumps(tree))
lib=R/'kicad/footprints/V12Switches.pretty';lib.mkdir(exist_ok=True)
for name,f in templates.items(): (lib/(name+'.kicad_mod')).write_text(sx.dumps(f)+'\n')
table=R/'kicad/fp-lib-table';t=sx.loads(table.read_text())
if not any(field(l,'name')[1]=='V12Switches' for l in children(t,'lib')):
    t.append(sx.loads('(lib (name "V12Switches") (type "KiCad") (uri "${KIPRJMOD}/footprints/V12Switches.pretty") (options "") (descr "V12 soldered three-family low-profile switches"))'))
table.write_text(sx.dumps(t)+'\n')

# Clip only copper conflicting with the added pads/slots. Preserve all other
# routing, especially the boost switching loop, controller and LED positions.
b=k.LoadBoard(str(P));regions=[];newholes=[]
for f in b.GetFootprints():
    if f.GetReference().startswith('SW') and f.GetReference()!='SW87':
        for p in f.Pads():
            if p.m_Uuid.AsString() in {uid(f.GetReference()+'/gateron-contact/'+i) for i in ['1','2']}:
                regions.append((shape(p),p.GetNetname(),.23))
                newholes.append((shape(p,p.GetDrillSize()),p.GetNetname(),False))
            elif p.GetAttribute()==k.PAD_ATTRIB_NPTH and p.GetDrillShape()==k.PAD_DRILL_SHAPE_OBLONG:
                regions.append((shape(p),'!hole',.30))
                newholes.append((shape(p),'!hole',True))
assert len(regions)==344
for f in b.GetFootprints():
    if f.GetReference()=='C2':
        regions.extend((shape(p),p.GetNetname(),.23) for p in f.Pads())
geoms=[v[0] for v in regions];index=STRtree(geoms)
removed=clipped=0;new=[]
for n in tree:
    if tag(n) not in ('segment','via'):new.append(n);continue
    net=field(n,'net')[-1]
    if tag(n)=='via':
        pos=Point(field(n,'at')[1:3]);rad=field(n,'size')[1]/2
        drill=field(n,'drill')[1]/2
        hit=any(pos.distance(g)<rad+clearance and expected!=net for g,expected,clearance in regions)
        hit |= any(pos.distance(g)<drill+.26 for g,_,_ in newholes)
        if hit:removed+=1
        else:new.append(n)
        continue
    line=LineString([field(n,'start')[1:3],field(n,'end')[1:3]]);rad=field(n,'width')[1]/2
    obstacles=[regions[int(j)][0].buffer(rad+regions[int(j)][2]) for j in index.query(line.buffer(rad+.31)) if regions[int(j)][1]!=net]
    if not obstacles:new.append(n);continue
    safe=unary_union(obstacles)
    if line.disjoint(safe):new.append(n);continue
    clipped+=1;remain=line.difference(safe)
    for seg in list(remain.geoms) if hasattr(remain,'geoms') else [remain]:
        if seg.is_empty or seg.length<.15:continue
        part=copy.deepcopy(n);field(part,'start')[1:]=[round(v,6) for v in seg.coords[0]]
        field(part,'end')[1:]=[round(v,6) for v in seg.coords[-1]]
        field(part,'uuid')[1]=uid(field(n,'uuid')[1]+'/'+str(list(seg.coords)))
        new.append(part)
P.write_text(sx.dumps(new))
b=k.LoadBoard(str(P)); b.BuildConnectivity();k.SaveBoard(str(P),b)
(R/'reference/pattern.json').write_text(json.dumps(dict(
 revision='v12',parent='v11',key_count=86,soldered_switches=True,original_holes_unchanged=True,
 gateron_orientation_vs_kailh_deg=0,
 added_contacts=[dict(pad='1',xy_mm=[2.54,-5.08],drill_mm=1.5,copper_mm=2.4),dict(pad='2',xy_mm=[-3.81,-2.54],drill_mm=1.5,copper_mm=2.4)],
 capacitor_relocation=dict(ref='C2',from_mm=[117.8,31],to_mm=[124,34.5]),
 shared_locator_slots=dict(centers_xy_mm=[[-5.29,0],[5.29,0]],size_mm=[2.32,1.9]),
 new_electrical_holes=172,new_locator_slots=172,clipped_source_segments=clipped,removed_source_vias=removed,
 physical_fit_verified=False),indent=2)+'\n')
print('Added',switches*4,'holes; clipped',clipped,'segments; removed',removed,'vias',flush=True)
