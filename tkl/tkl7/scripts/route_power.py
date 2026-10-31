#!/usr/bin/python3
"""Route the charger locally and provide through-via access to its power rails."""
from pathlib import Path
import pcbnew as k,sys,gc
sys.excepthook=sys.__excepthook__;gc.disable()
P=Path(__file__).resolve().parents[1]/'kicad/keyboard.kicad_pcb'
pro=P.with_suffix('.kicad_pro');settings=pro.read_bytes();b=k.LoadBoard(str(P));mm=k.FromMM
v=lambda p:k.VECTOR2I(mm(p[0]),mm(p[1]))
def line(net,pts,width=.25,layer=k.B_Cu):
 for a,c in zip(pts,pts[1:]):
  t=k.PCB_TRACK(b);t.SetStart(v(a));t.SetEnd(v(c));t.SetWidth(mm(width));t.SetLayer(layer);t.SetNet(b.FindNet(net));t.SetLocked(True);b.Add(t)
def via(net,p,size=.45,drill=.2):
 t=k.PCB_VIA(b);t.SetPosition(v(p));t.SetWidth(mm(size));t.SetDrill(mm(drill));t.SetViaType(k.VIATYPE_THROUGH);t.SetLayerPair(k.F_Cu,k.B_Cu);t.SetNet(b.FindNet(net));t.SetLocked(True);b.Add(t)
line('TS',[(324.5625,25.75),(324,26.3125),(324,26.6)],.18);via('TS',(324,26.6),.35,.15)
via('TS',(321.175,23));line('TS',[(324,26.6),(321.175,26.6),(321.175,23),(321.175,22.5),(311,22.5),(311,24)],.18,k.B_Cu)
line('VBAT',[(324.5625,25.25),(324.5625,24.75),(323.5,24.75)]);via('VBAT',(323.5,24.75))
via('VBAT',(318.225,26));line('VBAT',[(318.225,26),(318.225,24.75),(323.5,24.75),(323.5,21.5),(335.5,21.5),(338,24)],.4,k.F_Cu)
line('VSYS',[(325.75,23.5625),(325.75,22.8)]);via('VSYS',(325.75,22.8),.35,.15)
line('VSYS',[(327.4375,24.75),(327.4375,25.25),(328.2,25.25),(328.45,25),(332.225,25),(332.225,26)])
via('VSYS',(332.225,26));via('VSYS',(345.75,23.93))
line('VSYS',[(325.75,22.8),(325.75,22.2),(331,22.2),(332.225,23.425),(332.225,26),(342,26),(344.07,23.93),(345.75,23.93)],.4,k.F_Cu)
line('ILIM',[(327.4375,25.75),(328.2,26.5125),(329.175,27.4875),(329.175,27.5)],.18)
line('ISET',[(325.25,26.4375),(325.25,27.4),(322.175,27.4),(322.175,28.5)],.18)
line('VBUS',[(326.75,26.4375),(326.75,27.3)]);via('VBUS',(326.75,27.3),.35,.15);via('VBUS',(329.225,23))
line('VBUS',[(326.75,27.3),(330,27.3),(330,23.775),(329.225,23)],.4,k.In2_Cu)
via('VDDH',(348.75,23.93))
for p in [(325.6,24.6),(325.6,25.4),(326.4,24.6),(326.4,25.4),(324.5625,24.25),(325.25,23.5625),(326.75,23.5625),(326.25,26.4375),(325.75,26.4375)]:via('GND',p,.35,.15)
b.BuildConnectivity();k.SaveBoard(str(P),b);pro.write_bytes(settings)
print('Routed charger, thermal vias, NTC and load switch')
