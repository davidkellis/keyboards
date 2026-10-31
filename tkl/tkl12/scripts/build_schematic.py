#!/usr/bin/python3
"""Generate the three-sheet v7 schematic and synchronize footprint UUID paths.

Pin connectivity comes from the audited placement, with standard KiCad symbols.
The independent exported netlist is checked against every numbered PCB pad.
"""
from pathlib import Path
import sys, uuid, copy, math
import sexpdata as sx

ROOT=Path(__file__).resolve().parents[1]/'kicad'
S=sx.Symbol
def f(tag,*args):return [S(tag),*args]
def uid(name):return str(uuid.uuid5(uuid.NAMESPACE_URL,'tkl-v12/'+name))
def children(node,tag):return [a for a in node if isinstance(a,list) and a and a[0]==S(tag)]
def child(node,tag):return next(iter(children(node,tag)),None)
def effects(size=1.0,hide=False,justify=None):
    e=f('effects',f('font',f('size',size,size)))
    if hide:e.append(f('hide',S('yes')))
    if justify:e.append(f('justify',S(justify)))
    return e
pcb=sx.loads((ROOT/'keyboard.kicad_pcb').read_text())
parts={}
for fp in children(pcb,'footprint'):
    props={p[1]:p[2] for p in children(fp,'property')}
    r=props['Reference'];pins={}
    for p in children(fp,'pad'):
        if p[1]:
            net=child(p,'net')[-1] if child(p,'net') else ''
            pins[str(p[1])]='' if net.startswith('unconnected-(') else net
    parts[r]={'value':props['Value'],'fp':fp[1],'pins':pins,'node':fp,
              'properties':props,'dnp':S('dnp') in (child(fp,'attr') or []),
              'in_bom':S('exclude_from_bom') not in (child(fp,'attr') or [])}

cache={}
def libsymbol(libid):
    if libid in cache:return copy.deepcopy(cache[libid])
    lib,name=libid.split(':')
    local=ROOT/'symbols'/(lib+'.kicad_sym')
    data=sx.loads((local if local.exists() else Path('/usr/share/kicad/symbols',lib+'.kicad_sym')).read_text())
    table={a[1]:a for a in children(data,'symbol')}
    def resolve(name):
        node=copy.deepcopy(table[name]);ext=child(node,'extends')
        if ext:
            base=resolve(ext[1])
            base[1]=name
            for sub in children(base,'symbol'):sub[1]=name+sub[1][sub[1].rfind('_',0,sub[1].rfind('_')):]
            overrides={p[1]:p for p in children(node,'property')}
            base=[a for a in base if not (isinstance(a,list) and a[0]==S('property') and a[1] in overrides)]
            base.extend(overrides.values());node=base
        return node
    result=resolve(name);result[1]=libid;cache[libid]=copy.deepcopy(result)
    return result

rootid=uid('root');sheetids={n:uid('sheet/'+n) for n in ['matrix','power']}
files={n:(ROOT/({'controller':'keyboard','matrix':'matrix','power':'power'}[n]+'.kicad_sch')) for n in ['controller','matrix','power']}
pages={}
labels=set()
for page in files:
    pages[page]=[S('kicad_sch'),f('version',20250114),f('generator',S('eeschema')),
                 f('uuid',rootid if page=='controller' else uid('file/'+page)),f('paper','A3'),
                 f('title_block',f('title','TKL v12 - '+page.title()),f('rev','11'),
                   f('comment',1,'Pro Micro nRF52840 carrier; two layers; bottom assembly; module by user')),
                 f('lib_symbols')]

def text(page,s,x,y,size=1.27):
    pages[page].append(f('text',s,f('at',x,y,0),effects(size,justify='left'),f('uuid',uid(f'text/{page}/{x}/{y}'))))

def add(ref,libid,page,x,y,override=None,angle=0,skip=()):
    part=parts.get(ref,{'value':'PWR_FLAG','fp':'','pins':override or {},'dnp':False})
    lib=libsymbol(libid)
    libs=child(pages[page],'lib_symbols')
    if not any(isinstance(a,list) and len(a)>1 and a[1]==libid for a in libs):libs.append(lib)
    instid=uid('component/'+ref)
    path='/'+rootid+('' if page=='controller' else '/'+sheetids[page])
    inst=f('symbol',f('lib_id',libid),f('at',x,y,angle),f('unit',1),
           f('in_bom',S('yes') if not ref.startswith('#') and part.get('in_bom',True) else S('no')),f('on_board',S('yes') if not ref.startswith('#') else S('no')),
           f('dnp',S('yes') if part['dnp'] else S('no')),f('uuid',instid))
    for name,value in [('Reference',ref),('Value',part['value'])]:
        template=next(p for p in children(lib,'property') if p[1]==name)
        px,py=child(template,'at')[1:3]
        eff=copy.deepcopy(child(template,'effects'))
        child(child(eff,'font'),'size')[1:]=[1.0,1.0]
        if page=='matrix' and name=='Value':eff.append(f('hide',S('yes')))
        inst.append(f('property',name,value,f('at',x+px,y-py,0),eff))
    inst.append(f('property','Footprint',part['fp'],f('at',x,y,0),effects(hide=True)))
    for name in ('Manufacturer','MPN','LCSC','Assembly','Datasheet','Description'):
        if name in part.get('properties',{}):
            inst.append(f('property',name,part['properties'][name],f('at',x,y,0),effects(hide=True)))
    inst.append(f('instances',f('project','keyboard',f('path',path,f('reference',ref),f('unit',1)))))
    pins=[p for sub in children(lib,'symbol') for p in children(sub,'pin')]
    wired=set()
    for p in pins:
        num=str(child(p,'number')[1]);at=child(p,'at');dx,dy,ang=at[1:]
        if angle==180:dx,dy,ang=-dx,-dy,(ang+180)%360
        pos=(round(x+dx,5),round(y-dy,5));n=part['pins'].get(num,'')
        inst.append(f('pin',num,f('uuid',uid('pin/'+ref+'/'+num))))
        if num in skip:continue
        if pos in wired:continue
        wired.add(pos)
        if not n:
            pages[page].append(f('no_connect',f('at',*pos),f('uuid',uid('nc/'+ref+'/'+num))))
            continue
        # Extend outward from each pin. Stacked power pins share one wire.
        length=2.54 if page=='matrix' else 5.08
        ox={0:-length,180:length}.get(ang,0);oy={90:length,270:-length}.get(ang,0)
        end=(round(pos[0]+ox,5),round(pos[1]+oy,5))
        pages[page].append(f('wire',f('pts',f('xy',*pos),f('xy',*end)),f('stroke',f('width',0),f('type',S('default'))),f('uuid',uid('wire/'+ref+'/'+num))))
        pages[page].append(f('global_label',n,f('shape',S('passive')),f('at',*end,ang),effects(1.0),f('uuid',uid('label/'+ref+'/'+num)),
                            f('property','Intersheetrefs','${INTERSHEET_REFS}',f('at',*end,ang),effects(hide=True))))
    pages[page].append(inst)
    if 'node' in part:
        fp=part['node']
        fp[:]=[a for a in fp if not (isinstance(a,list) and a[0] in (S('path'),S('sheetname'),S('sheetfile')))]
        fp.extend([f('path',path+'/'+instid),f('sheetname',page.title()),f('sheetfile',files[page].name)])

# Historical module footprint with corrected battery connections.
add('U1','MCU_nice_nano:Nice_Nano_V2','controller',139.7,119.38)
text('controller','U1: user-installed TENSTAR / compatible nRF52840 module.\nModule USB-C faces the rear case opening directly; no extension cable.\n21 GPIO: 20 matrix + BL_EN. P0.09/P0.10 configured as GPIO.\nNo tall sockets; mechanical model defines mounting envelope.\nBattery/charger and exact clone remain subject to bench validation.',30.48,210.82)
for i,page in enumerate(['matrix','power']):
    x=241.3+i*81.28;y=236.22
    pages['controller'].append(f('sheet',f('at',x,y),f('size',66.04,15.24),f('stroke',f('width',.1524),f('type',S('default'))),
        f('fill',f('color',0,0,0,0)),f('uuid',sheetids[page]),
        f('property','Sheetname',page.title(),f('at',x,y-1.27,0),effects(1.27,justify='left')),
        f('property','Sheetfile',files[page].name,f('at',x,y+16.51,0),effects(1.27,justify='left')),
        f('instances',f('project','keyboard',f('path','/'+rootid,f('page',str(i+2)))))))

# Matrix grouped by electrical row and column. Each switch/diode pair preserves
# its original net; the logical matrix has ROW0..7 and ROW9..11 (no ROW8).
rows=['ROW'+str(i) for i in list(range(8))+[9,10,11]]
for i in range(1,87):
    sw=parts['SW'+str(i)];di=parts['D'+str(i)]
    rn=next(n for n in di['pins'].values() if n.startswith('ROW'))
    cn=next(n for n in sw['pins'].values() if n.startswith('COL'))
    row=rows.index(rn);col=int(cn[3:]);x=27.94+col*40.64;y=30.48+row*20.32
    add('SW'+str(i),'Switch:SW_Push','matrix',x,y,skip=('2',))
    add('D'+str(i),'Device:D_Schottky','matrix',x+20.32,y,angle=180,skip=('2',))
    pages['matrix'].append(f('wire',f('pts',f('xy',x+5.08,y),f('xy',x+16.51,y)),
        f('stroke',f('width',0),f('type',S('default'))),f('uuid',uid('matrix-link/'+str(i)))))
text('matrix','86 switches; SW9/SW15/SW16 restored; ROW8 unused. BAT46W diodes; module GPIO is 3.3 V.\nV12: Choc V2 / Choc V1 / selected Gateron LP 3.0 solder patterns; alternate contacts share pins 1/2. See SWITCHES.md for mechanics.',20.32,15.24)

# Carrier uses only module charging; the user fits the protected 1S pack.
add('J1','Connector_Generic:Conn_01x02','power',50.8,50.8)
add('SW87','Switch:SW_SPDT','power',110.49,50.8)
for i in range(1,11):
    add('LED'+str(i),'Device:LED','power',40.64+((i-1)%5)*48.26,152.4+((i-1)//5)*38.1)
add('U2','V11Power:TPS61169DCKR','power',325.12,86.36)
add('L1','Device:L','power',215.9,81.28)
add('D87','Device:D_Schottky','power',261.62,81.28)
add('C1','Device:C','power',215.9,114.3)
add('C2','Device:C','power',261.62,114.3)
add('R10','Device:R','power',325.12,134.62)
add('R9','Device:R','power',381,101.6)
add('R11','Device:R','power',381,139.7)
for i,n in enumerate(['GND','VBAT','BAT_SW','VCC']):
    add('#FLG0'+str(i+1),'power:PWR_FLAG','power',180.34+i*25.4,50.8,{'1':n})
text('power','V12: ten bottom-mounted reverse LEDs shine through PCB into an acrylic plate.\nU2 boost supply uses BAT_SW; one regulated SERIES string, not ten parallel branches.\nR10 = 100 ohm: 204 mV / R10 = 2.04 mA nominal maximum at 100% PWM.\nBL_EN is active-high 20 kHz PWM from existing module P0.31; low shuts down U2.\nRemove LED7..LED10 and bridge EACH removed LED pads 1/2 for six-source mode.\nLED1..LED6 remain distributed across both interior rows; see placement drawing.\nNever bridge R10; do not bypass all LEDs. Power off before rework.\nProtected 1S cell / module charging / RF and optical performance need bench tests.',20.32,231.14)

for page,filename in files.items():
    if page=='controller':pages[page].append(f('sheet_instances',f('path','/',f('page','1'))))
    pages[page].append(f('embedded_fonts',S('no')))
    filename.write_text(sx.dumps(pages[page]).replace(') (',')\n(')+'\n')
(ROOT/'keyboard.kicad_pcb').write_text(sx.dumps(pcb).replace(') (',')\n(')+'\n')
print('Wrote controller, matrix and power sheets;',len(parts),'board components')
