#!/usr/bin/env python3
"""Build an offline V11 assembly/explosion viewer without changing source CAD."""
from pathlib import Path
import base64,hashlib,json,os,subprocess,sys
import numpy as np,trimesh,manifold3d as m
from shapely.geometry import box,LineString
from shapely.ops import unary_union

SRC=Path(__file__).resolve().parent;OUT=SRC.parent;ROOT=OUT.parent
V10=ROOT.parent/'tkl10';REPO=ROOT.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from plate_geometry import switch_aperture,stabilizer_apertures
hashes={}
def read(p):
 b=p.read_bytes();hashes[str(p.relative_to(REPO))]=hashlib.sha256(b).hexdigest();return b
def loadjson(p):return json.loads(read(p))
g=loadjson(ROOT/'case/board-geometry.json');cfg=loadjson(ROOT/'scripts/fit-config.json')
lighting=loadjson(ROOT/'reference/lighting-design.json')
fit=loadjson(V10/'case/fit-report.json');case=loadjson(V10/'case-hidden-mounts/validation.json')
read(ROOT/'kicad/keyboard.kicad_pcb');read(ROOT/'case/acrylic-plate-trial.dxf')
assert g['source_sha256']==hashes['tkl/tkl11/kicad/keyboard.kicad_pcb']
W,D,T=[g['board'][k] for k in ['width','depth','thickness']]
angle=case['tilt_degrees'];z0=case['pcb_origin_z']
PT=T+cfg['plate_top_above_pcb_mm'];PB=PT-cfg['plate_thickness_mm']
def solid(p):
 read(p);t=trimesh.load(p,force='mesh',process=True)
 assert t.is_watertight,p
 s=m.Manifold(m.Mesh(np.asarray(t.vertices,np.float32),np.asarray(t.faces,np.uint32)))
 assert s.status()==m.Error.NoError,p
 return s
def unpack(a):
 s=m.Manifold(m.Mesh(np.frombuffer(base64.b64decode(a['positions']),dtype='<f4').reshape(-1,3).copy(),np.frombuffer(base64.b64decode(a['indices']),dtype='<u4').reshape(-1,3).copy()))
 assert s.status()==m.Error.NoError;return s
def pack(s,name,material):
 assert s.status()==m.Error.NoError and s.volume()>0,name
 mesh=s.to_mesh()
 return dict(name=name,material=material,triangles=len(mesh.tri_verts),
 positions=base64.b64encode(np.asarray(mesh.vert_properties[:,:3],dtype='<f4').tobytes()).decode(),
 indices=base64.b64encode(np.asarray(mesh.tri_verts,dtype='<u4').tobytes()).decode())
def place(s):return s.rotate((angle,0,0)).translate((2.4,2.4,z0))
def section(p):
 return m.CrossSection([np.array(p.exterior.coords[:-1]),*[np.array(r.coords[:-1]) for r in p.interiors]],m.FillRule.EvenOdd)
parts=[pack(solid(V10/f'case-hidden-mounts/reference/{n}-assembly.stl'),n,mat) for n,mat in [('bottom','base'),('bezel','shell')]]
board=solid(ROOT/'case/pcb-bare.stl');native=board.bounding_box();board=board.scale((1,1,T/(native[5]-native[2])))
for led in lighting['leds']:
 x,y=led['board_xy'];assert (board.slice(.8)^m.CrossSection.circle(.03).translate((x,y))).area()<1e-6,led['ref']
parts.append(pack(place(board),'board','pcb'))
for i in range(1,9):
 for part,mat in [('carrier','carrier'),('screw','metal'),('nut','metal')]:
  parts.append(pack(solid(V10/f'case-hidden-mounts/reference/M{i}-{part}-assembly.stl'),f'M{i}-{part}',mat))

# Follow the V11 trial DXF: continuous sheet over all ten entries, actual 86
# switch/stabilizer openings and blind reliefs under module/connector tails.
cutouts=[switch_aperture(*s['xy']) for s in g['switches']]
for s in g['switches']:
 if s['units']>=2:cutouts.append(stabilizer_apertures(*s['xy'],100 if s['units']==6.25 else 23.8))
profile=box(0,.3,W,D).difference(unary_union(cutouts));assert profile.geom_type=='Polygon'
plate=section(profile).extrude(PT-PB).translate((0,0,PB))
module={h['pad']:h['xy'] for h in g['holes'] if h['ref']=='U1'}
pockets=[LineString([module[n] for n in nums]).buffer(1.3) for nums in [('28','12'),('29','13'),('25','26','27')]]
pockets.append(LineString([h['xy'] for h in g['holes'] if h['ref']=='J1']).buffer(1.1))
for p in pockets:plate-=section(p).extrude(.6).translate((0,0,PB-.001))
ref_profile=profile
for led in lighting['leds']:
 x,y=led['board_xy'];assert profile.covers(box(x-1.05,y-1.4,x+1.05,y+1.4)),led['ref']
 ref_profile=ref_profile.difference(box(x-1.3,y-1.65,x+1.3,y+1.65))
reflector=place(section(ref_profile).extrude(.06).translate((0,0,PB-.08)))
tool=place(m.Manifold.cube((W-.8,D-1.2,PT-PB+.004)).translate((.4,.8,PB-.002)))
raised=loadjson(V10/'case-raised-deck/viewer-assets.json')
editions={};frame_notes=[]
for name,upper in [('current',solid(V10/'case-hidden-mounts/reference/upper-assembly.stl')),('raised',unpack(raised['variants']['original'][0]))]:
 frame=upper-tool
 # Old spacers were joined to the integrated plate. Removing that plate must
 # not leave unsupported spacer islands floating inside the rendered frame.
 pieces=frame.decompose();frame=max(pieces,key=lambda s:s.volume())
 frame_notes.append(dict(edition=name,omitted_isolated_integrated_plate_spacers=len(pieces)-1))
 collectors=[]
 for led in lighting['leds']:
  x,y=led['board_xy'];collector=place(m.Manifold.cylinder(.45,1.03,circular_segments=24).translate((x,y,PB-.22)))
  collectors.append(pack(collector,led['ref']+' acrylic input trial','acrylic'))
 editions[name]=dict(frame=pack(frame,name+' top case frame — separate plate concept','shell'),
 plate=pack(place(plate),name+' V11 acrylic switch plate — fit trial','acrylic'),
 reflector=pack(reflector,name+' reflective backing — optical concept','reflector'),collectors=collectors)

rows=[['Esc']+[f'F{i}' for i in range(1,13)]+['PrtSc','ScrLk','Pause'],
 ['`','1','2','3','4','5','6','7','8','9','0','-','=','Backspace','Ins','Home','PgUp'],
 ['Tab','Q','W','E','R','T','Y','U','I','O','P','[',']','\\','Del','End','PgDn'],
 ['Caps','A','S','D','F','G','H','J','K','L',';',"'",'Enter'],
 ['Shift','Z','X','C','V','B','N','M',',','.','/','Shift','↑'],
 ['Ctrl','Win','Alt','','Alt','Fn','Ctrl','←','↓','→']]
switches=[]
for y,labels in zip(sorted({s['xy'][1] for s in g['switches']},reverse=True),rows):
 keys=sorted([s for s in g['switches'] if s['xy'][1]==y],key=lambda s:s['xy'][0]);assert len(keys)==len(labels)
 switches.extend(dict(s,label=label,modifier=s['units']>1 or y==111.09 or s['xy'][0]>290) for s,label in zip(keys,labels))
caps=loadjson(V10/'render-case-editions/assets.json')['caps']
data=dict(parts=parts,switches=switches,components=g['components'],pins=g['pins'],holes=g['holes'],
 board=g['board'],config=cfg,tilt=angle,originZ=z0,surface=case['surface'],lighting=lighting,
 study=dict(caps=caps,variants={}),raisedEdition=dict(variants={}),acrylicStudy=dict(editions=editions),
 assemblyNote='Separate acrylic plate and upper frame are a fit concept; original printed upper combines them. Explode separates illustrative layers, not a service procedure.')
modules=Path(os.environ.get('V11_RENDER_NODE_MODULES',SRC/'node_modules' if (SRC/'node_modules').exists() else V10/'render-case-editions/source/node_modules'))
bundle=subprocess.run([str(modules/'.bin/esbuild'),str(SRC/'viewer.js'),'--bundle','--format=iife','--minify','--legal-comments=inline','--target=es2022'],env=dict(os.environ,NODE_PATH=str(modules)),check=True,capture_output=True,text=True).stdout
html=(SRC/'template.html').read_text().replace('__MODEL_DATA__',json.dumps(data,separators=(',',':'))).replace('__VIEWER_SCRIPT__',bundle.replace('</script','<\\/script'))
(OUT/'index.html').write_text(html);(OUT/'THREE-LICENSE.txt').write_bytes((modules/'three/LICENSE').read_bytes())
assert all(hashlib.sha256((REPO/p).read_bytes()).hexdigest()==sha for p,sha in hashes.items())
manifest=dict(revision='v11',source_sha256=hashes,source_files_unchanged=True,key_count=len(switches),led_count=len(lighting['leds']),
 led_positions_board_xy_mm={l['ref']:l['board_xy'] for l in lighting['leds']},actual_v11_pcb_holes=True,
 finished_pcb_thickness_mm=T,native_substrate_thickness_mm=native[5]-native[2],
 plate_thickness_mm=PT-PB,plate_underside_relief_mm=.6,standalone_html_bytes=len(html.encode()),
 case_status=data['assemblyNote'],frame_concept_details=frame_notes,physical_fit_verified=False,optics_calibrated=False,
 illustrative=['Case/plate separation and retention','Keycaps and switch bodies','Battery pouch, controller and component appearance','Lighting spread and couplers'])
(OUT/'provenance.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Built V11 assembly viewer:',len(switches),'keys,',len(lighting['leds']),'real LED positions;',len(html.encode()),'bytes')
