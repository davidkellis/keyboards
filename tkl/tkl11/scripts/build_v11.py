#!/usr/bin/env python3
"""Reset v11 from preserved v10: ten reverse LEDs, one bypassable series string."""
from routing_geometry import *
from shapely.ops import unary_union
import sexpdata as sx,copy,uuid,itertools
R=Path(__file__).resolve().parents[1];P=R/'kicad/keyboard.kicad_pcb'
S=sx.Symbol
def tag(n):return str(n[0]) if isinstance(n,list) and n else ''
def ch(n,t):return [v for v in n if tag(v)==t]
def field(n,t):return next(iter(ch(n,t)),None)
def ref(n):return next(v[2] for v in ch(n,'property') if v[1]=='Reference')
def fresh(n):
 for v in n:
  if tag(v)=='uuid':v[1]=str(uuid.uuid4())
  elif isinstance(v,list):fresh(v)
source=R.parent/'tkl10/kicad/keyboard.kicad_pcb'
tree=sx.loads(source.read_text())
oldnets={'BL','BL_EN','VCC',*[f'S{i}' for i in range(1,7)]}
remove={'Q1',*[f'R{i}' for i in range(1,7)]}
template=copy.deepcopy(next(v for v in tree if tag(v)=='footprint' and ref(v)=='LED1'))
tree=[v for v in tree if not(tag(v)=='footprint' and ref(v) in remove)
      and not(tag(v) in ['segment','via'] and field(v,'net')[-1] in oldnets)]
newleds={7:(128,51.8),8:(243,51.8),9:(350,51.8),10:(350,128.585)}
for i,pos in newleds.items():
 n=copy.deepcopy(template);fresh(n);field(n,'at')[1:3]=list(pos)
 next(v for v in ch(n,'property') if v[1]=='Reference')[2]=f'LED{i}'
 tree.append(n)
P.write_text(sx.dumps(tree))
b=k.LoadBoard(str(P));fp={f.GetReference():f for f in b.GetFootprints()}
def net(name):
 n=b.FindNet(name)
 if not n:n=k.NETINFO_ITEM(b,name);b.Add(n)
 return n
def setpins(f,mapping):
 for p in f.Pads():
  if p.GetNumber() in mapping:p.SetNet(net(mapping[p.GetNumber()]))
def props(f,mpn,lcsc,manufacturer,assembly='SMT'):
 for name,value in dict(MPN=mpn,LCSC=lcsc,Manufacturer=manufacturer,Assembly=assembly).items():
  f.SetField(name,value);f.GetField(name).SetVisible(False);f.GetField(name).SetLayer(k.B_Fab)
def add(ref,lib,name,pos,value,pins,mpn,lcsc,maker,angle=0):
 f=k.FootprintLoad('/usr/share/kicad/footprints/'+lib+'.pretty',name)
 assert f,name
 f.SetFPID(k.LIB_ID(lib,name));f.SetReference(ref);f.SetValue(value);b.Add(f)
 f.Flip(f.GetPosition(),False);f.SetOrientationDegrees(angle);f.SetPosition(vec(pos))
 f.Reference().SetVisible(False);f.Value().SetVisible(False);setpins(f,pins);props(f,mpn,lcsc,maker)
 fp[ref]=f;return f
add('U2','Package_TO_SOT_SMD','SOT-353_SC-70-5',(94.5,26.5),'TPS61169DCKR',
 {'1':'BOOST_SW','2':'GND','3':'LED_FB','4':'BL_EN','5':'BAT_SW'},'TPS61169DCKR','C71045','Texas Instruments')
add('L1','Inductor_SMD','L_Sunlord_SWPA4018S',(89.7,24),'10uH',
 {'1':'BAT_SW','2':'BOOST_SW'},'FNR4018S100MT','C167808','cjiang')
add('D87','Diode_SMD','D_SMA',(96.4,22.5),'SS16',
 {'1':'LED_HV','2':'BOOST_SW'},'SS16','C3034074','ShunYe')
for ref,pos,positive in [('C1',(88.7,28.8),'BAT_SW'),('C2',(101.8,26),'LED_HV')]:
 add(ref,'Capacitor_SMD','C_1206_3216Metric',pos,'4.7uF 50V',
  {'1':positive,'2':'GND'},'CL31B475KBHNNNE','C51205','Samsung Electro-Mechanics')
add('R10','Resistor_SMD','R_0603_1608Metric',(97.4,29),'100',
 {'1':'LED_FB','2':'GND'},'0603WAF1000T5E','C22775','UNI-ROYAL')
# Exact shortest Euclidean source tour with both ends at the driver. This is
# wiring-length guidance, not an optical optimization or final routed length.
ids=list(range(1,11));loc={i:xy(fp[f'LED{i}'].GetPosition()) for i in ids};start=(97,26)
dp={}
for j,i in enumerate(ids):dp[(1<<j,j)]=(math.dist(start,loc[i]),[i])
for mask in range(1,1<<10):
 for j in range(10):
  if (mask,j) not in dp:continue
  cost,path=dp[(mask,j)]
  for q in range(10):
   if mask&(1<<q):continue
   key=(mask|1<<q,q);cand=(cost+math.dist(loc[ids[j]],loc[ids[q]]),path+[ids[q]])
   if key not in dp or cand[0]<dp[key][0]:dp[key]=cand
order=min((v[0]+math.dist(loc[ids[j]],start),v[1]) for (mask,j),v in dp.items() if mask==1023)[1]
for idx,i in enumerate(order):
 anode='LED_HV' if idx==0 else f'LED_LINK_{idx}'
 cathode='LED_FB' if idx==9 else f'LED_LINK_{idx+1}'
 setpins(fp[f'LED{i}'],{'1':cathode,'2':anode})
 # The existing 1206 lands are the wire-bypass attachment points after removal.
 f=fp[f'LED{i}'];f.Reference().SetVisible(True);f.Reference().SetTextSize(vec((.8,.8)));f.Reference().SetTextThickness(mm(.12))
 f.Reference().SetPosition(vec((loc[i][0],loc[i][1]+2.2)))
 f.Reference().SetTextAngle(k.EDA_ANGLE(180,k.DEGREES_T))
f=fp['R9'];f.SetValue('100k');setpins(f,{'1':'BL_EN','2':'GND'})
b.GetTitleBlock().SetTitle('TKL v11 - ten reverse LEDs; removable to six; acrylic plate trial')
b.GetTitleBlock().SetRevision('v11')
# Clear space for the four new optical slots and rear driver cluster. Existing
# matrix components never move. Only nearby copper is clipped and rerouted.
regions=[box(86.8,20.8,104,30.3)]
for i in newleds:
 x,y=loc[i];regions.append(box(x-3.2,y-2.1,x+3.2,y+2.8))
region=unary_union(regions)
front_region=unary_union([shape(p) for i in newleds for p in fp[f'LED{i}'].Pads() if p.GetAttribute()==k.PAD_ATTRIB_NPTH])
b.BuildConnectivity();k.SaveBoard(str(P),b)
tree=sx.loads(P.read_text());result=[];clipped=0
for n in tree:
 if tag(n) not in ('segment','via'):result.append(n);continue
 if tag(n)=='via':
  if Point(*field(n,'at')[1:3]).distance(region)<field(n,'size')[1]/2+.2:clipped+=1
  else:result.append(n)
  continue
 line=LineString([field(n,'start')[1:3],field(n,'end')[1:3]])
 selected=front_region if field(n,'layer')[1]=='F.Cu' else region
 safe=selected.buffer(field(n,'width')[1]/2+.27)
 if line.disjoint(safe):result.append(n);continue
 clipped+=1;remain=line.difference(safe)
 for seg in list(remain.geoms) if hasattr(remain,'geoms') else [remain]:
  if seg.is_empty or seg.length<.08:continue
  part=copy.deepcopy(n);field(part,'start')[1:]=[round(v,6) for v in seg.coords[0]]
  field(part,'end')[1:]=[round(v,6) for v in seg.coords[-1]];field(part,'uuid')[1]=str(uuid.uuid4());result.append(part)
P.write_text(sx.dumps(result))
# New purchasing groups; retain matrix, module, mounting and connector details.
cat=json.loads((R.parent/'tkl10/manufacturing/parts.json').read_text())
cat['groups']=[v for v in cat['groups'] if not set(v['refs'])&remove]
for v in cat['groups']:
 if v['refs'][0]=='LED1':
  v['refs']=[f'LED{i}' for i in ids];v['spec']='White reverse-mount LED; regulated series string, 2.04 mA nominal maximum'
  v['notes']='Bottom only; shines through existing-style PCB slot into acrylic plate. To disable an LED remove it and wire across pads 1/2; start with LED7..LED10 to retain the original six positions. Never bridge the current-sense resistor. Fixture/handling quote required.'
def group(refs,package,maker,mpn,lcsc,spec,notes=''):
 cat['groups'].append(dict(refs=refs,package=package,manufacturer=maker,mpn=mpn,lcsc=lcsc,spec=spec,assembly='SMT',notes=notes,source='https://jlcpcb.com/partdetail/'+mpn+'/'+lcsc))
group(['U2'],'SC-70-5','Texas Instruments','TPS61169DCKR','C71045','Series white LED boost/current driver; 2.7-5.5 V input; 5-100 kHz PWM','20 kHz BL_EN from module P0.31. Direct protected switched battery input; not module VCC.')
group(['L1'],'4x4x1.8mm shielded','cjiang','FNR4018S100MT','C167808','10 uH +/-20%; 1.3 A rated / 1.6 A saturation','FNR4018 land drawing must match selected footprint; validate startup and pulse current on prototype.')
group(['D87'],'SMA','ShunYe','SS16','C3034074','1 A / 60 V Schottky boost rectifier','Cathode pad 1 to LED_HV. Not a matrix diode.')
group(['C1','C2'],'1206','Samsung Electro-Mechanics','CL31B475KBHNNNE','C51205','4.7 uF / 50 V / X7R','Input and output use one SKU. Confirm output effective capacitance >=1 uF under actual DC bias.')
group(['R10'],'0603','UNI-ROYAL','0603WAF1000T5E','C22775','100 ohm +/-1%; 0.1 W','Current sense: 204 mV / 100 ohm = 2.04 mA nominal maximum; NEVER bridge.')
cat['reviewed_date']='2026-10-15';cat['notes']='v11: bottom-only; ten reverse LEDs; one constant-current series string; acrylic plate diffusion experiment; no side-emitting guide.'
(R/'manufacturing/parts.json').write_text(json.dumps(cat,indent=2)+'\n')
study=dict(revision='v11',parent='v10',series_order=[f'LED{i}' for i in order],
 optional_to_retain_v10_six=['LED7','LED8','LED9','LED10'],nominal_max_led_current_ma=2.04,
 current_sense_ref='R10',current_sense_ohm=100,pwm_frequency_hz=20000,
 leds=[dict(ref=f'LED{i}',kicad_xy=loc[i],board_xy=[loc[i][0]-27.03,149.19-loc[i][1]],added=i>=7) for i in ids],
 optical_plate='User trial: acrylic switch plate above PCB; reverse LEDs illuminate plate underside through ten local PCB slots',
 input_supply='BAT_SW',all_factory_parts_on_bottom=True,brightness_validated=False,hardware_tested=False)
(R/'reference/lighting-design.json').write_text(json.dumps(study,indent=2)+'\n')
print('Ten-LED series order:',order,'clipped tracks:',clipped)
