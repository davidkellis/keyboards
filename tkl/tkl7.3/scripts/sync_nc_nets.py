#!/usr/bin/python3
"""Synchronize KiCad's generated names for deliberately unconnected pads."""
from pathlib import Path
import tempfile, subprocess, xml.etree.ElementTree as E, gc, sys
sys.excepthook=sys.__excepthook__;gc.disable()
import pcbnew as k
R=Path(__file__).resolve().parents[1]/'kicad';board=R/'keyboard.kicad_pcb';pro=board.with_suffix('.kicad_pro');saved=pro.read_bytes()
with tempfile.TemporaryDirectory() as d:
    xml=Path(d)/'nets.xml'
    subprocess.run(['kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(xml),str(R/'keyboard.kicad_sch')],check=True)
    nets={(p.attrib['ref'],p.attrib['pin']):n.attrib['name'] for n in E.parse(xml).findall('./nets/net') for p in n.findall('node')}
b=k.LoadBoard(str(board));count=0
for f in b.GetFootprints():
    for p in f.Pads():
        n=nets.get((f.GetReference(),p.GetNumber()),'')
        if n.startswith('unconnected-('):
            n=n.replace('/', '{slash}')
            assert not p.GetNetname() or p.GetNetname().startswith('unconnected-('),(f.GetReference(),p.GetNumber())
            net=b.FindNet(n)
            if not net:net=k.NETINFO_ITEM(b,n);b.Add(net)
            p.SetNet(net);count+=1
b.BuildConnectivity();k.SaveBoard(str(board),b);pro.write_bytes(saved)
print('Synchronized',count,'intentionally unconnected pads')
