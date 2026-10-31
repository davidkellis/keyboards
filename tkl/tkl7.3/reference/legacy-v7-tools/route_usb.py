#!/usr/bin/python3
"""Add the locked USB full-speed pair after build_board.py, before autorouting.

Nominal geometry: 0.25 mm tracks, 0.15 mm gap, 0.20 mm to adjacent GND.
The fabricator must confirm the selected stackup gives 90 ohms differential.
"""
from pathlib import Path
import math, gc, sys
sys.excepthook=sys.__excepthook__;gc.disable()
import pcbnew as k
ROOT=Path(__file__).resolve().parents[1]/'kicad'
board=ROOT/'keyboard.kicad_pcb';pro=board.with_suffix('.kicad_pro')
settings=pro.read_bytes();b=k.LoadBoard(str(board))
mm=k.FromMM
def v(x,y):return k.VECTOR2I(mm(x),mm(y))
def line(net,points,layer=k.B_Cu,width=.18):
    for a,c in zip(points,points[1:]):
        if a==c:continue
        t=k.PCB_TRACK(b);t.SetStart(v(*a));t.SetEnd(v(*c));t.SetLayer(layer)
        t.SetWidth(mm(width));t.SetNet(b.FindNet(net));t.SetLocked(True);b.Add(t)
def via(net,x,y,size=.35,drill=.15):
    t=k.PCB_VIA(b);t.SetPosition(v(x,y));t.SetWidth(mm(size));t.SetDrill(mm(drill))
    t.SetViaType(k.VIATYPE_THROUGH);t.SetLayerPair(k.F_Cu,k.B_Cu)
    t.SetNet(b.FindNet(net));t.SetLocked(True);b.Add(t)
# USB-C duplicates: D+ crosses D- on the other side using two filled vias.
for x in (365.75,366.75):
    line('USB_DP',[(x,26.145),(x,26.35)],width=.15);via('USB_DP',x,26.35)
line('USB_DP',[(365.75,26.35),(366.75,26.35)],k.F_Cu,.15)
line('USB_DM',[(366.25,26.145),(366.25,27.4),(365.25,28.4),(365.25,28.8)],width=.15)
line('USB_DM',[(365.25,26.145),(365.25,28.8)],width=.15)
via('USB_DM',365.25,28.8)
# Approach the ESD inputs on F.Cu; the protected pair leaves its opposite side.
via('USB_DP',359.95,27.8625);via('USB_DM',358.05,27.8625)
line('USB_DP',[(366.75,26.35),(366.75,27.2),(365.75,28.2),(359.95,28.2),(359.95,27.8625)],k.F_Cu,.2)
line('USB_DM',[(365.25,28.8),(365.05,28.6),(358.05,28.6),(358.05,27.8625)],k.F_Cu,.2)
via('USB_DM',358.05,30.1375)
line('USB_DM',[(358.05,27.8625),(358.05,30.1375)])
line('USB_DP',[(359.95,27.8625),(359.95,30.1375)])
via('GND',359,30.1375)
line('VBUS',[(359,27.8625),(359,26.025),(358.175,25.2)],width=.25)
via('GND',359.825,25.2)
line('USB_DP',[(359.95,30.1375),(359.95,30.7375)])
via('USB_DP',359.95,30.7375)
# Offset a common 45-degree centreline, retaining constant differential gap.
center=[(357,30.3375),(341,30.3375),(339,32.3375),
        (339,79.525),(348.675,89.2),(348.675,89.3)]
def offset(points,d):
    normals=[]
    for a,c in zip(points,points[1:]):
        dx,dy=c[0]-a[0],c[1]-a[1];length=math.hypot(dx,dy)
        normals.append((-dy/length,dx/length))
    out=[]
    for i,p in enumerate(points):
        if i==0:n=normals[0]
        elif i==len(points)-1:n=normals[-1]
        else:
            a,c=normals[i-1:i+1];denom=1+a[0]*c[0]+a[1]*c[1]
            n=((a[0]+c[0])/denom,(a[1]+c[1])/denom)
        out.append((round(p[0]+d*n[0],6),round(p[1]+d*n[1],6)))
    return out
line('USB_DM',[(358.05,30.1375)]+offset(center,.2)+[(348.475,89.55)],k.F_Cu,.25)
line('USB_DP',[(359.95,30.7375),(357.4,30.7375),(357.2,30.5375)]+offset(center,-.2)+[(349.2,89.625),(349.2,90.0)],k.F_Cu,.25)
via('USB_DM',348.475,89.55);via('USB_DP',349.2,90.0)
line('USB_DM',[(348.475,89.55),(348.475,90.58),(348.495,90.6)])
line('USB_DP',[(349.2,90.0),(348.84,90.36),(348.84,90.6)])
for x,y in [(360.8,29.5),(357.3,29.0),(347.5,89.5),(349.8,90)]:via('GND',x,y,.45,.2)
b.BuildConnectivity();k.SaveBoard(str(board),b);pro.write_bytes(settings)
print('Locked USB connector escape, ESD flow-through and differential pair')
