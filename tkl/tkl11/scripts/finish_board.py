#!/usr/bin/env python3
"""Shorten the boost switch loop and add a low-loss output discharge resistor."""
from routing_geometry import *
import sexpdata as sx
R=Path(__file__).resolve().parents[1];P=R/'kicad/keyboard.kicad_pcb';S=sx.Symbol
def tag(n):return str(n[0]) if isinstance(n,list) and n else ''
def field(n,t):return next((a for a in n if tag(a)==t),None)
tree=sx.loads(P.read_text())
filtered=[]
for n in tree:
 if tag(n) in ['segment','via']:
  name=field(n,'net')[-1]
  if name in ['BOOST_SW','LED_HV']:continue
  if name=='GND':
   geo=Point(*field(n,'at')[1:3]) if tag(n)=='via' else LineString([field(n,'start')[1:3],field(n,'end')[1:3]])
   if geo.intersects(box(85,20.5,107,31.5)):continue
 filtered.append(n)
tree=filtered
P.write_text(sx.dumps(tree));b=k.LoadBoard(str(P));fp={f.GetReference():f for f in b.GetFootprints()}
fp['D87'].SetOrientationDegrees(180)
fp['R9'].SetValue('1M');fp['R9'].SetField('MPN','0603WAF1004T5E');fp['R9'].SetField('LCSC','C22935')
f=k.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty','R_0603_1608Metric');b.Add(f)
f.SetReference('R11');f.SetValue('1M');f.SetFPID(k.LIB_ID('Resistor_SMD','R_0603_1608Metric'))
f.Flip(f.GetPosition(),False);f.SetOrientationDegrees(0);f.SetPosition(vec((104.9,29)));f.Reference().SetVisible(False);f.Value().SetVisible(False)
for p in f.Pads():p.SetNet(b.FindNet('LED_HV' if p.GetNumber()=='1' else 'GND'))
for key,value in dict(MPN='0603WAF1004T5E',LCSC='C22935',Manufacturer='UNI-ROYAL',Assembly='SMT').items():
 f.SetField(key,value);f.GetField(key).SetVisible(False);f.GetField(key).SetLayer(k.B_Fab)
def route(net,pts,width=.35):
 for a,c in zip(pts,pts[1:]):
  t=k.PCB_TRACK(b);t.SetStart(vec(a));t.SetEnd(vec(c));t.SetLayer(k.B_Cu);t.SetWidth(mm(width));t.SetNet(b.FindNet(net));b.Add(t)
route('BOOST_SW',[(91.2,24),(92.4,24),(94.4,22.5)])
route('BOOST_SW',[(92.4,24),(92.4,27.15),(93.6625,27.15)])
route('LED_HV',[(98.4,22.5),(100.325,24.425),(100.325,26)],.4)
route('LED_HV',[(100.325,26),(100.325,27.2),(104.075,29)],.25)
# Labels sit outside the original silk rectangles; avoid neighbouring switch pads.
for i in range(1,11):
 f=fp[f'LED{i}'];x,y=xy(f.GetPosition());f.Reference().SetPosition(vec((x,y-2.65)))
 f.Reference().SetTextSize(vec((.8,.8)))
b.BuildConnectivity();k.SaveBoard(str(P),b)
cat=json.loads((R/'manufacturing/parts.json').read_text())
for g in cat['groups']:
 if g['refs']==['R9']:
  g.update(refs=['R9','R11'],mpn='0603WAF1004T5E',lcsc='C22935',spec='1 Mohm +/-1%; 0.1 W',
           notes='R9 PWM pull-down; R11 output bleeder. Approx 0.9 mW bleeder loss at 30 V. With power removed allow 30 s, verify LED_HV <5 V before rework.',
           source='https://jlcpcb.com/partdetail/0603WAF1004T5E/C22935')
(R/'manufacturing/parts.json').write_text(json.dumps(cat,indent=2)+'\n')
print('Added R11 bleeder; switch node now bottom-only short branches.')
