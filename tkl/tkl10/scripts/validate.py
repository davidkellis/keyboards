#!/usr/bin/env python3
"""Run ERC/DRC, compare independent netlist, and check circuit invariants."""
from pathlib import Path
import argparse, collections, json, subprocess, sys, xml.etree.ElementTree as ET
import sexpdata as sx
ROOT=Path(__file__).resolve().parents[1];K=ROOT/'kicad'
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'validation');args=p.parse_args();O=args.output;O.mkdir(parents=True,exist_ok=True)
def run(*cmd):subprocess.run(cmd,check=True)
run('kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(O/'netlist.xml'),str(K/'keyboard.kicad_sch'))
run('kicad-cli','sch','erc','--format','json','-o',str(O/'erc.json'),str(K/'keyboard.kicad_sch'))
# Refill in memory; verification must not rewrite a PCB already uploaded for quotation.
run('kicad-cli','pcb','drc','--refill-zones','--schematic-parity','--format','json','-o',str(O/'drc.json'),str(K/'keyboard.kicad_pcb'))
def ch(n,tag):return [x for x in n if isinstance(x,list) and str(x[0])==tag]
board=sx.loads((K/'keyboard.kicad_pcb').read_text());parts={};pads={};issues=[]
for f in ch(board,'footprint'):
    props={x[1]:x[2] for x in ch(f,'property')};ref=props['Reference']
    parts[ref]={'value':props['Value'],'manufacturer':props.get('Manufacturer'),'lcsc':props.get('LCSC'),'pins':{}}
    for p in ch(f,'pad'):
        if not p[1]:continue
        n=ch(p,'net');net=n[0][-1] if n else ''
        if net.startswith('unconnected-('):net=''
        pads[(ref,str(p[1]))]=net;parts[ref]['pins'][str(p[1])]=net
nets={}
for net in ET.parse(O/'netlist.xml').findall('./nets/net'):
    name=net.attrib['name']
    if name.startswith('unconnected-('):name=''
    for p in net.findall('node'):
        if not p.attrib['ref'].startswith('#'):nets[(p.attrib['ref'],p.attrib['pin'])]=name
for pin in set(pads)|set(nets):
    if pads.get(pin,'')!=nets.get(pin,''):issues.append(f'{pin}: PCB {pads.get(pin)} != schematic {nets.get(pin)}')
def expect(ref,pin,net):
    if pads.get((ref,str(pin)))!=net:issues.append(f'{ref}.{pin} must be {net}')
# Module pin numbering follows the historical footprint and official nice!nano v2 pinout.
expected={'1':'COL0','2':'COL1','3':'GND','4':'GND','5':'COL2','6':'COL3',
 '7':'COL4','8':'COL5','9':'COL6','10':'COL7','11':'COL8','12':'ROW0',
 '13':'ROW1','14':'ROW2','15':'ROW3','16':'ROW4','17':'ROW5','18':'ROW6',
 '19':'ROW7','20':'BL_EN','21':'VCC','23':'GND','24':'BAT_SW',
 '25':'ROW9','26':'ROW10','27':'ROW11','28':'GND','29':'BAT_SW'}
for pin,net in expected.items():expect('U1',pin,net)
expect('J1',1,'VBAT');expect('J1',2,'GND')
expect('SW87',1,'VBAT');expect('SW87',2,'BAT_SW')
expect('Q1',1,'BL_EN');expect('Q1',2,'GND');expect('Q1',3,'BL')
for i in range(1,7):
 expect('R'+str(i),2,'VCC');expect('LED'+str(i),1,'BL')
 if parts['R'+str(i)]['value']!='1k':issues.append('Initial LED resistor must be 1k')
if any(ref in parts for ref in ('U2','U3','J3','J4','J5')):issues.append('Legacy power/RF component unexpectedly retained')
keys=set()
for i in range(1,87):
    if (parts['D'+str(i)]['value'],parts['D'+str(i)]['manufacturer'],parts['D'+str(i)]['lcsc'])!=('BAT46W','Jiangsu Changjing Electronics Technology Co., Ltd.','C54110'):issues.append(f'D{i}: requires reviewed JSCJ BAT46W / C54110')
    d=parts['D'+str(i)]['pins'];sw=parts['SW'+str(i)]['pins']
    if not d['1'].startswith('ROW') or not sw['1'].startswith('COL') or d['2']!=sw['2']:issues.append(f'Incorrect matrix pair {i}')
    pair=(d['1'],sw['1'])
    if pair in keys:issues.append(f'Duplicate matrix address {pair}')
    keys.add(pair)
erc=json.loads((O/'erc.json').read_text());drc=json.loads((O/'drc.json').read_text())
ev=[v for s in erc['sheets'] for v in s['violations']]
result={'numbered_pads':len(pads),'unique_keys':len(keys),'circuit_issues':issues,
        'erc_errors':sum(v['severity']=='error' for v in ev),'erc_warnings':sum(v['severity']=='warning' for v in ev),
        'drc_errors':sum(v['severity']=='error' for v in drc['violations']),
        'drc_warnings':sum(v['severity']=='warning' for v in drc['violations']),
        'unconnected_items':len(drc.get('unconnected_items',[])),
        'schematic_parity_issues':len(drc.get('schematic_parity',[]))}
(O/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
sys.exit(any(value for key,value in result.items() if key not in ('numbered_pads','unique_keys')))
