#!/usr/bin/python3
"""Export/import local Specctra routing while preserving project constraints."""
from pathlib import Path
import sys, gc, re
sys.excepthook=sys.__excepthook__;gc.disable()
import pcbnew as k
board=Path(__file__).resolve().parents[1]/'kicad/keyboard.kicad_pcb'
mode,path=sys.argv[1:]
b=k.LoadBoard(str(board))
if mode=='export':
    if not k.ExportSpecctraDSN(b,path):raise SystemExit('DSN export failed')
    p=Path(path);data=p.read_text()
    # KiCad exports copper-pour-only exclusions as all-routing barriers.
    # Remove only those on the assembly side in this exchange copy. The
    # source PCB retains all exclusions; internal RF exclusions remain here.
    data,n=re.subn(r'    \(keepout "" \(polygon B.Cu.*?\)\)', '',data,flags=re.S)
    data=data.replace('(width 200)','(width 127)')
    p.write_text(data)
    print('Exported DSN; corrected',n,'copper-only exclusions')
elif mode=='import':
    pro=board.with_suffix('.kicad_pro');saved=pro.read_bytes()
    if not k.ImportSpecctraSES(b,path):raise SystemExit('SES import failed')
    b.BuildConnectivity();k.SaveBoard(str(board),b);pro.write_bytes(saved)
    print('Imported routing session')
else:raise SystemExit('usage: routing_exchange.py export|import FILE')
