#!/usr/bin/python3
"""Build the v7 placement and reference routing using KiCad 10's pcbnew API.

The Nordic circuitry is copied from the manufacturer's configuration 7 PCB,
including its local tracks, vias and RF keepouts. Run before autorouting only.
"""
from pathlib import Path
import json
import tempfile
import gc, sys, traceback
gc.disable()  # KiCad 10 SWIG ownership conflicts with Python 3.14 cyclic GC.
sys.excepthook = sys.__excepthook__
import pcbnew as k
import sexpdata as sx

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'reference/matrix-source.kicad_pcb'
OUT = ROOT / 'kicad/keyboard.kicad_pcb'
mm = k.FromMM
def v(x, y): return k.VECTOR2I(mm(x), mm(y))
def xy(p): return (k.ToMM(p.x), k.ToMM(p.y))

original = k.LoadBoard(str(SOURCE))
old = {f.GetReference(): f for f in original.GetFootprints()}
oldpins = {p.GetNumber(): p.GetNetname() for p in old['U1'].Pads()}
old_leds = {r: xy(f.GetPosition()) for r, f in old.items() if r.startswith('LED')}
tree=sx.loads(SOURCE.read_text())
keep=[]
for item in tree:
    if not isinstance(item,list): keep.append(item);continue
    tag=str(item[0])
    if tag in ('segment','arc','via','zone','group'): continue
    if tag.startswith('gr_') and not any(isinstance(q,list) and q[:2]==[sx.Symbol('layer'),'Edge.Cuts'] for q in item): continue
    if tag=='footprint':
        r=next(q[2] for q in item if isinstance(q,list) and q[:2]==[sx.Symbol('property'),'Reference'])
        if not ((r.startswith('SW') and r!='SW87') or r in {'R1','R2','R3','R4','R5','R6','R9','Q1'}):continue
    keep.append(item)
scratch=tempfile.TemporaryDirectory(prefix='tkl-v7-')
clean=Path(scratch.name)/'stripped.kicad_pcb'
clean.write_text(sx.dumps(keep))
b=k.LoadBoard(str(clean))
b.SetCopperLayerCount(4)
layers=b.GetEnabledLayers()
layers.AddLayer(k.In1_Cu);layers.AddLayer(k.In2_Cu)
b.SetEnabledLayers(layers)

def net(name):
    if not name: return b.FindNet(0)
    n = b.FindNet(name)
    if not n:
        n = k.NETINFO_ITEM(b, name); b.Add(n)
    return n

def assign(fp, pins):
    for p in fp.Pads():
        p.SetNet(net(pins.get(p.GetNumber(), '')))

def part(ref, val, lib, x, y, pins, angle=0, bottom=True):
    library, name = lib.split(':')
    f = k.FootprintLoad('/usr/share/kicad/footprints/' + library + '.pretty', name)
    if not f: raise ValueError(lib)
    f.SetReference(ref); f.SetValue(val)
    f.SetFPID(k.LIB_ID(library, name))
    b.Add(f)
    if bottom: f.Flip(v(0,0), k.FLIP_DIRECTION_TOP_BOTTOM)
    f.SetOrientationDegrees(angle)
    f.SetPosition(v(x,y)); assign(f,pins)
    return f

# Preserve the key layout and diode polarity. All assembled parts are underside.
for f in b.GetFootprints():
    r = f.GetReference()
    if r.startswith('SW'): continue
    if f.GetLayer() != k.B_Cu: f.Flip(f.GetPosition(), k.FLIP_DIRECTION_TOP_BOTTOM)
    if r in {'R1','R2','R3','R4','R5','R6'}:
        i=int(r[1:]); x,y=old_leds['LED'+str(i)]
        f.SetPosition(v(x+4.3,y))
        f.SetOrientationDegrees(0)
        f.SetValue('1k')
    if r=='Q1': f.SetValue('DMN2056U-7')
    for p in f.Pads():
        if p.GetNetname() == 'VDD': p.SetNet(net('VDDH'))

# Low-drop Schottky diodes preserve input-low margin with 1.8 V matrix GPIOs.
for refname in ['D'+str(i) for i in range(1,87)]:
    src=old[refname]
    pins={p.GetNumber():p.GetNetname() for p in src.Pads()}
    x,y=xy(src.GetPosition());angle=src.GetOrientationDegrees()
    part(refname,'BAT46W','Diode_SMD:D_SOD-123',x,y,pins,angle)

# Nordic reference block: reflected as a complete assembly onto the underside.
ref = k.LoadBoard(str(ROOT / 'reference/nordic-config7.kicad_pcb'))
origin = next(f.GetPosition() for f in ref.GetFootprints() if f.GetReference()=='U1')
target = v(350,100)
delta = target-origin
gpio = {}
ru = next(f for f in ref.GetFootprints() if f.GetReference()=='U1')
for p in ru.Pads():
    n=oldpins.get(p.GetNumber(),'')
    if n.startswith(('ROW','COL')) or n=='BL_EN': gpio[p.GetNetname()] = n
# Avoid consuming NFC pins for matrix scanning; ordinary spare GPIOs suffice.
gpio.pop('P0.09/NFC1',None); gpio.pop('P0.10/NFC2',None)
gpio.update({'P0.13':'ROW1', 'P0.15':'ROW2'})
names={'VDD_HV':'VDDH','D+':'USB_DP','D-':'USB_DM','P0.18/RESET':'RESET',
       'SWDCLK':'SWCLK', 'NetL2_1':'DCDC_FILTER','NetL2_2':'DCC',
       'NetL4_2':'DCCH','NetC20_1':'DECUSB','NetC13_1':'DEC2',
       'NetC9_1':'DEC5','NetC3_2':'ANT','NetC4_2':'RF_MATCH',
       'P0.00/XL1':'XL1','P0.01/XL2':'XL2', **gpio}
unused={n.GetNetname() for n in ref.GetNetsByNetcode().values()
        if n.GetNetname().startswith(('P0.','P1.')) and n.GetNetname() not in names}
def newname(n): return '' if n in unused else names.get(n,n)
def transform(item):
    item.Flip(origin,k.FLIP_DIRECTION_TOP_BOTTOM)
    item.Move(delta)
    return item
for src in ref.GetFootprints():
    if not src.GetReference(): continue
    f=k.FOOTPRINT(src)
    pinmap={p.GetNumber():newname(p.GetNetname()) for p in src.Pads()}
    transform(f); b.Add(f); assign(f,pinmap)
    if f.GetReference()=='U1':
        for p in f.Pads():
            if p.GetNumber()=='74': p.SetNumber('EP')
    if f.GetReference() in ('C10','C13'): f.SetDNP(True)
for src in ref.GetTracks():
    n=src.GetNetname()
    if n in unused: continue
    t=src.Duplicate()
    t=k.Cast_to_PCB_VIA(t) if isinstance(src,k.PCB_VIA) else k.Cast_to_PCB_TRACK(t)
    transform(t); b.Add(t); t.SetNet(net(newname(n)))
    if isinstance(t,k.PCB_VIA):
        t.SetViaType(k.VIATYPE_THROUGH);t.SetLayerPair(k.F_Cu,k.B_Cu)
    t.SetLocked(True)
for src in ref.Zones():
    # Preserve manufacturer keepouts and the local RF ground copper.
    box=src.GetBoundingBox()
    if src.GetIsRuleArea() and min(box.GetWidth(),box.GetHeight()) < mm(.2):
        continue  # Reference coupon's perimeter, not an RF exclusion.
    z=k.ZONE(src); transform(z); b.Add(z)
    if src.GetNetname():
        z.SetNet(net(newname(src.GetNetname())))
        z.SetPadConnection(k.ZONE_CONNECTION_FULL)
        z.SetAssignedPriority(z.GetAssignedPriority()+10)

# Coax connector at the reference's 50-ohm endpoint, facing its RF pad toward L5.
rf_end = v(350+(159.0581-147.5011),100-(104.2416-105.0036))
j4=part('J4','U.FL-R-SMT-1(10)','Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical',
        k.ToMM(rf_end.x)+1.525,k.ToMM(rf_end.y),{'1':'RF','2':'GND'})

# Power and USB occupy the rear strip. Jack mouth and switch face the rear wall.
j3=part('J3','HC-TYPE-C-16P-01A','Connector_USB:USB_C_Receptacle_HCTL_HC-TYPE-C-16P-01A',
        366,22.4,{'A1':'GND','A12':'GND','B1':'GND','B12':'GND','SH':'GND',
                    'A4':'VBUS','A9':'VBUS','B4':'VBUS','B9':'VBUS',
                    'A5':'USB_CC1','B5':'USB_CC2','A6':'USB_DP','B6':'USB_DP',
                    'A7':'USB_DM','B7':'USB_DM'},angle=0)
part('U3','USBLC6-2SC6','Package_TO_SOT_SMD:SOT-23-6',359,29,
     {'1':'USB_DP','2':'GND','3':'USB_DM','4':'USB_DM','5':'VBUS','6':'USB_DP'},90)
for i,x,n in [(13,356.5,'USB_CC1'),(14,374.5,'USB_CC2')]:
    part('R'+str(i),'5.1k','Resistor_SMD:R_0603_1608Metric',x,25.8,{'1':n,'2':'GND'},90)
part('U2','BQ24072RGT','Package_DFN_QFN:VQFN-16-1EP_3x3mm_P0.5mm_EP1.6x1.6mm',326,25,
     {'1':'TS','2':'VBAT','3':'VBAT','4':'GND','5':'GND','6':'VSYS','8':'GND',
      '10':'VSYS','11':'VSYS','12':'ILIM','13':'VBUS','14':'GND','15':'GND','16':'ISET','17':'GND'})
# USB500 input; about 445 mA charge. A protected 10 Ah cell takes ~25-30 h.
# The fixed 5-hour timer cannot accommodate this capacity. TMR=GND disables
# timers; termination and an external 10k NTC remain active. R10 is DNP.
for r,val,x,y,n in [('R10','10k',322,23,'TS'),('R11','2k',323,28.5,'ISET'),
                     ('R12','3.48k',330,27.5,'ILIM')]:
    fp=part(r,val,'Resistor_SMD:R_0603_1608Metric',x,y,{'1':n,'2':'GND'})
    if r=='R10':fp.SetDNP(True)
for r,val,x,y,n in [('C22','1uF',330,23,'VBUS'),('C23','4.7uF',333,26,'VSYS'),
                     ('C24','4.7uF',319,26,'VBAT'),('C25','100nF',359,25.2,'VBUS')]:
    part(r,val,'Capacitor_SMD:C_0603_1608Metric',x,y,{'1':n,'2':'GND'})
part('SW87','PCM12SMTR','Button_Switch_SMD:SW_SPDT_PCM12',348,22.5,
     {'1':'VSYS','2':'VDDH'},angle=0)
part('J1','B2B-PH-K-S','Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical',
     338,24,{'1':'VBAT','2':'GND'})
part('J5','B2B-PH-K-S','Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical',
     311,24,{'1':'TS','2':'GND'})
part('J2','TC2030-IDC-NL','Connector:Tag-Connect_TC2030-IDC-NL_2x03_P1.27mm_Vertical',
     330,99,{'1':'VDD_NRF','2':'SWDIO','3':'RESET','4':'SWCLK','5':'GND'})
for r,(x,y) in old_leds.items():
    fp=part(r,'LTW-C230DS','LED_SMD:LED_1206_3216Metric_ReverseMount_Hole1.8x2.4mm',
         x,y,{'1':'BL_GND','2':'Net-('+r+'-A)'})
    # Lite-On's lens needs more room than the generic 1.8 mm slot.
    # The oval clears the maximum lens envelope, with 0.2 mm copper
    # clearance. Pads overlap the terminal lands by 0.35 mm.
    for p in fp.Pads():
        if not p.GetNumber():p.SetSize(v(2.1,2.8));p.SetDrillSize(v(2.1,2.8))
        else:
            p.SetPosition(v(x+(-1.9 if p.GetNumber()=='1' else 1.9),y))
            p.SetSize(v(1.3,1.6))
    for g in fp.GraphicalItems():
        if g.GetLayer() in (k.B_CrtYd,k.B_SilkS):
            fp.Remove(g)
    for layer in (k.B_CrtYd,k.B_SilkS):
        shape=k.PCB_SHAPE(fp);shape.SetShape(k.SHAPE_T_RECT);shape.SetLayer(layer)
        shape.SetStart(v(x-2.85,y-1.7));shape.SetEnd(v(x+2.85,y+1.7))
        shape.SetWidth(mm(.05 if layer==k.B_CrtYd else .12));fp.Add(shape)
    fp.SetFPID(k.LIB_ID('V7','LTW-C230DS_ReverseMount_Hole2.1x2.8'))
    # Keep the existing series-resistor nets, using the original LED pad names.
    assign(fp,{p.GetNumber():('VDD_NRF' if p.GetNetname()=='VDD' else p.GetNetname())
               for p in old[r].Pads()})

# One continuous internal ground layer, plus outer pours. Nordic's small local
# pours have higher priority; retain their precise RF clearance geometry.
for layer in (k.F_Cu,k.In1_Cu,k.In2_Cu,k.B_Cu):
    z=k.ZONE(b);z.SetLayer(layer);z.SetNet(net('GND'));z.SetLocalClearance(mm(.15))
    z.SetPadConnection(k.ZONE_CONNECTION_FULL);z.SetMinThickness(mm(.2))
    z.SetIslandRemovalMode(0);z.SetMinIslandArea(mm(1)*mm(1))
    z.Outline().NewOutline()
    for x,y in [(27.53,20.5),(377.29,20.5),(377.29,148.69),(27.53,148.69)]: z.Outline().Append(mm(x),mm(y))
    b.Add(z)

# Usable, local footprints: no dependency on the original Altium libraries.
libdir=ROOT/'kicad/footprints/V7.pretty';libdir.mkdir(exist_ok=True)
for f in b.GetFootprints():
    if f.GetReference().startswith(('SW','D')) and f.GetReference()!='SW87':continue
    local=k.FOOTPRINT(f)
    if local.GetLayer()==k.B_Cu: local.Flip(local.GetPosition(),k.FLIP_DIRECTION_TOP_BOTTOM)
    local.SetOrientationDegrees(0);local.SetPosition(v(0,0))
    name=f.GetReference()+'_'+str(f.GetFPID().GetLibItemName()).replace('/','_')
    local.SetFPID(k.LIB_ID('V7',name));k.PCB_IO_KICAD_SEXPR().FootprintSave(str(libdir),local)
    f.SetFPID(k.LIB_ID('V7',name))
    f.Reference().SetVisible(False)
    f.Value().SetVisible(False)
b.BuildConnectivity()
k.SaveBoard(str(OUT),b)
# SaveBoard also writes project defaults when the base was loaded from a temp
# file. Restore the fabrication constraints explicitly after saving.
pro=OUT.with_suffix('.kicad_pro'); settings=json.loads(pro.read_text())
settings['board']['design_settings']['rules'].update(
    min_clearance=.127,min_track_width=.127,min_via_diameter=.35,
    min_through_hole_diameter=.15,min_via_annular_width=.1,
    min_hole_clearance=.15,min_hole_to_hole=.15,min_copper_edge_clearance=.2)
settings['net_settings']['classes'][0].update(clearance=.127,track_width=.2,
                                           via_diameter=.45,via_drill=.2)
pro.write_text(json.dumps(settings,indent=2)+'\n')
pinmap={p.GetNumber():p.GetNetname() for f in b.GetFootprints() if f.GetReference()=='U1' for p in f.Pads()}
(ROOT/'reference/mcu-pinmap.json').write_text(json.dumps(pinmap,indent=2)+'\n')
print('Built',len(list(b.GetFootprints())),'footprints;',len(list(b.GetTracks())),'reference tracks/vias')
