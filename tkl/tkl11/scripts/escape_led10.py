#!/usr/bin/env python3
"""Add an ordinary via outside LED10's anode land for front-layer link routing."""
from routing_geometry import *
R=Path(__file__).resolve().parents[1];P=R/'kicad/keyboard.kicad_pcb'
b=k.LoadBoard(str(P));net=b.FindNet('LED_LINK_5');start=(275.1,107.04);end=(275.1,105.4)
assert not any(isinstance(t,k.PCB_VIA) and xy(t.GetPosition())==end for t in b.GetTracks()),'Escape already present'
t=k.PCB_TRACK(b);t.SetStart(vec(start));t.SetEnd(vec(end));t.SetWidth(mm(.2));t.SetLayer(k.B_Cu);t.SetNet(net);b.Add(t)
v=k.PCB_VIA(b);v.SetPosition(vec(end));v.SetWidth(mm(.6));v.SetDrill(mm(.3));v.SetViaType(k.VIATYPE_THROUGH);v.SetLayerPair(k.F_Cu,k.B_Cu);v.SetNet(net);b.Add(v)
b.BuildConnectivity();k.SaveBoard(str(P),b)
print('LED10 anode has an external via; connect LED_LINK_5 on the front layer')
