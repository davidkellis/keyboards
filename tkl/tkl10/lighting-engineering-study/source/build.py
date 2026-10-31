#!/usr/bin/env python3
"""Build a source-preserving lighting proposal and optical bench coupons."""
from pathlib import Path
import csv,hashlib,json,math,shutil,zipfile
from html import escape

OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parent
for d in ['coupons','diagrams','reference']: (OUT/d).mkdir(parents=True,exist_ok=True)
sources={}
def read(rel):
    b=(ROOT/rel).read_bytes();sources[rel]=hashlib.sha256(b).hexdigest();return b
g=json.loads(read('case/board-geometry.json'))
for rel in ['case/fit-config.json','case/fit-report.json','manufacturing/jlcpcb-bom.csv','manufacturing/assembly-notes.csv','kicad/keyboard.kicad_pcb','kicad/power.kicad_sch']:read(rel)
shutil.copy2(ROOT/'render-keycaps-lighting/reference/CPG1353S01D02-01-datasheet.pdf',OUT/'reference/Kailh-MINI-drawing.pdf')

def budget(n=86,current=.2,hours=12,rail=3.6,efficiency=.85,capacity=5000,usable=.8,active=.7,sleep=.1,self_pct=3,driver_iq=0):
    assert 0<=hours<=24 and 0<efficiency<=1 and 0<usable<=1
    light_mw=n*current*rail/efficiency
    light_ma=light_mw/3.7+driver_iq
    self_day=capacity*self_pct/100/30
    daily=hours*(light_ma+active)+(24-hours)*sleep+self_day
    return dict(led_count=n,average_led_current_ma=current,lit_hours_per_day=hours,lighting_battery_mw=light_mw+driver_iq*3.7,
      lighting_battery_ma=light_ma,daily_mah=daily,days=capacity*usable/daily,
      continuous_hours=capacity*usable/(light_ma+active+self_day/24))

table=[budget(current=i,hours=h) for i in [.1,.2,.5] for h in [6,12]]
with (OUT/'runtime-scenarios.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=table[0].keys());w.writeheader();w.writerows(table)
# Reproduce the user's screenshot using the current ZMK source formula.
zmk_led=6*(3.3-3.2)/100*1000
zmk_avg=5000*.05/30/24+.018+.5*(3*.023+315*.02/1000)+.5*zmk_led
zmk=dict(led_ma_awake=zmk_led,average_battery_ma=zmk_avg,days=5000*.85/zmk_avg/24,
  notes='Fixed 3.2 V LED drop; 100 ohm branches; 50% sleep; genuine nice!nano v2 profile. No optical model.')

def svg(w,h,body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}">{body}</svg>'
def rect(x,y,w,h,**attrs):
    return f'<rect x="{x:.4f}" y="{y:.4f}" width="{w:.4f}" height="{h:.4f}" '+ ' '.join(f'{k.replace("_","-")}="{v}"' for k,v in attrs.items())+'/>'
def circle(x,y,r,**attrs):
    return f'<circle cx="{x:.4f}" cy="{y:.4f}" r="{r:.4f}" '+ ' '.join(f'{k.replace("_","-")}="{v}"' for k,v in attrs.items())+'/>'
W,H=83.15,45.05
centers=[(13+19.05*c,13+19.05*r) for r in range(2) for c in range(4)]
windows=[(x,y+4.93) for x,y in centers]
# Suggested *rotated* switch footprint clearances, not a V10 drop-in part.
# Actual side/handedness of the switch LED channel must be confirmed on a coupon.
pin_holes=[(x+dx,y+dy,r) for x,y in centers for dx,dy,r in [(0,0,2.775),(5,5.15,1.05),(0,-5.9,1.2),(-5,-3.8,1.2)]]
def inside_hole(x,y,margin=0):return any((x-hx)**2+(y-hy)**2<(r+margin)**2 for hx,hy,r in pin_holes)
def dxf(lines,holes,dots):
    a=['0','SECTION','2','HEADER','9','$ACADVER','1','AC1015','9','$INSUNITS','70','4','0','ENDSEC','0','SECTION','2','ENTITIES']
    for layer,points in lines:
        a+=['0','LWPOLYLINE','8',layer,'90',str(len(points)),'70','1']
        for x,y in points:a+=['10',str(x),'20',str(H-y)]
    for layer,items in [('CUT',holes),('ETCH',dots)]:
        for x,y,r in items:a+=['0','CIRCLE','8',layer,'10',str(x),'20',str(H-y),'30','0','40',str(r)]
    return '\n'.join(a+['0','ENDSEC','0','EOF'])+'\n'

outer=[(.5,.5),(W-.5,.5),(W-.5,H-.5),(.5,H-.5)]
cut=rect(.5,.5,W-1,H-1,fill='none',stroke='#ff0000',stroke_width='.01')
cuts=cut+''.join(circle(x,y,r,fill='none',stroke='#ff0000',stroke_width='.01') for x,y,r in pin_holes)
(OUT/'coupons/guide-solid-CUT.svg').write_text(svg(W,H,cut))
(OUT/'coupons/guide-perforated-CUT.svg').write_text(svg(W,H,cuts))
assert len(windows)==8 and len(pin_holes)==32
dot_reports=[]
for name,rmin,rmax,pitch in [('sparse',.055,.105,.42),('medium',.08,.14,.42),('dense',.10,.18,.42)]:
    dots=[]
    for x,y in windows:
        assert not inside_hole(x,y)
        # Extract only at the eight proposed PCB windows, not across the deck.
        distance=min(math.hypot(x-.5,y-H/2),math.hypot(x-(W-.5),y-H/2))
        radius=rmin+(rmax-rmin)*min(1,distance/(W/2))
        for a in range(-3,4):
            for b in range(-4,5):
                dx=x+a*pitch;dy=y+b*pitch
                if abs(dx-x)+radius>1.01 or abs(dy-y)+radius>1.36:continue
                if not inside_hole(dx,dy,radius+.12):dots.append((dx,dy,radius))
    etch=''.join(circle(x,y,r,fill='#000000') for x,y,r in dots)
    (OUT/f'coupons/guide-{name}-ETCH.svg').write_text(svg(W,H,etch))
    (OUT/f'coupons/guide-{name}-perforated.dxf').write_text(dxf([('CUT',outer)],pin_holes,dots))
    (OUT/f'coupons/guide-{name}-solid.dxf').write_text(dxf([('CUT',outer)],[],dots))
    dot_reports.append(dict(pattern=name,dots=len(dots),min_diameter_mm=min(2*r for x,y,r in dots),max_diameter_mm=max(2*r for x,y,r in dots)))

# Opaque upper mask admits light only where a proposed native LED window sits.
mask=rect(.5,.5,W-1,H-1,fill='none',stroke='#ff0000',stroke_width='.01')
masklines=[('CUT',outer)]
for x,y in windows:
    mask+=rect(x-1.05,y-1.4,2.1,2.8,fill='none',stroke='#ff0000',stroke_width='.01')
    masklines.append(('CUT',[(x-1.05,y-1.4),(x+1.05,y-1.4),(x+1.05,y+1.4),(x-1.05,y+1.4)]))
(OUT/'coupons/opaque-output-mask-CUT.svg').write_text(svg(W,H,mask))
(OUT/'coupons/opaque-output-mask.dxf').write_text(dxf(masklines,[],[]))
reflector=cut+''.join(circle(x,y,r+.15,fill='none',stroke='#ff0000',stroke_width='.01') for x,y,r in pin_holes)
(OUT/'coupons/white-backing-CUT.svg').write_text(svg(W,H,reflector))

# Engineering diagram rather than an uncalibrated glowing product render.
body='<rect width="1000" height="440" fill="#f5f4ed"/><g font-family="sans-serif" fill="#243b37">'
body+='<text x="28" y="38" font-size="25">V10 lighting: illuminate the legend through the switch LED channel</text>'
body+='<text x="28" y="65" font-size="14">Conceptual section; dimensions and optical efficiency need a bench sample.</text>'
for x,title,detail in [(40,'Recommended: one white LED per key','A short light path; one shared PWM control'),(535,'Alternative: side-lit guide below PCB','24 sources / 86 extraction windows')]:
    body+=f'<text x="{x}" y="105" font-size="19">{escape(title)}</text><text x="{x}" y="129" font-size="13">{escape(detail)}</text>'
    body+=f'<rect x="{x+80}" y="153" width="230" height="38" rx="12" fill="#c8cec2"/><text x="{x+140}" y="178" font-size="14">XVX keycap</text>'
    body+=f'<rect x="{x+112}" y="198" width="166" height="56" rx="5" fill="#6383aa"/><text x="{x+145}" y="231" fill="white" font-size="14">Whale switch</text>'
    body+=f'<rect x="{x+30}" y="270" width="340" height="17" fill="#466b54"/><text x="{x+45}" y="264" font-size="12">PCB</text>'
    body+=f'<rect x="{x+242}" y="197" width="16" height="74" fill="#cedcda"/><rect x="{x+238}" y="267" width="24" height="23" fill="#faf7d4"/>'
    body+=f'<path d="M{x+250},267V190" stroke="#d3a546" stroke-width="5"/><path d="M{x+242},200l8,-13l8,13" fill="none" stroke="#d3a546" stroke-width="3"/>'
    if x==40:
        body+=f'<rect x="{x+235}" y="287" width="30" height="16" rx="3" fill="#e8b14b"/><text x="{x+130}" y="331" font-size="13">Reverse-mount LED + its own resistor</text>'
        body+=f'<text x="{x+35}" y="363" font-size="13">Local diffuser only if the sample benefits.</text><text x="{x+35}" y="386" font-size="13">Keep factory components on the bottom where feasible.</text>'
    else:
        body+=f'<rect x="{x+20}" y="304" width="360" height="17" fill="#b9dfe6"/><rect x="{x+20}" y="327" width="360" height="6" fill="#e5e7db"/><rect x="{x+2}" y="306" width="16" height="13" fill="#e8b14b"/>'
        body+=f'<path d="M{x+24},313H{x+250}V291" fill="none" stroke="#d3a546" stroke-width="4"/><text x="{x+45}" y="365" font-size="13">Guide + reflector + clearance around pins/components.</text><text x="{x+45}" y="388" font-size="13">Full case fit is unresolved; prototype before routing.</text>'
body+='</g>'
(OUT/'diagrams/lighting-section.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="440" viewBox="0 0 1000 440">'+body+'</svg>')

data=dict(checked_date='2026-10-15',status='Engineering proposal and bench optical coupons; not production PCB or validated optics',
  source_sha256=sources,source_files_unchanged=True,pcb_modified=False,board=g['board'],switches=g['switches'],
  previous_leds=[p for p in g['components'] if p['ref'].startswith('LED')],runtime_scenarios=table,zmk_screenshot=zmk,
  assumptions=dict(capacity_mah=5000,usable_fraction=.8,average_battery_voltage=3.7,lighting_rail_voltage=3.6,conversion_efficiency=.85,
                   active_base_ma=.7,sleep_base_ma=.1,self_discharge_pct_month=3,brightness_or_uniformity_measured=False),
  coupon=dict(size_mm=[W,H],outside_cut_mm=[W-1,H-1],key_pitch_mm=19.05,outputs=8,output_window_mm=[2.1,2.8],
              proposed_north_led_offset_mm=4.93,pin_reliefs=32,guide_thickness_trials_mm=[.8,1,1.5],patterns=dot_reports,
              status='Loose bench guide, not a load-bearing switch plate or V10 drop-in. Native-window orientation must be checked. No machine kerf/tool compensation applied.'))
assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==sha for p,sha in sources.items())
(OUT/'study.json').write_text(json.dumps(data,indent=2)+'\n')
with zipfile.ZipFile(OUT/'optical-bench-kit.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted((OUT/'coupons').iterdir()):z.write(p,str(p.relative_to(OUT)))
    for name in ['README.txt','study.json','diagrams/coupon-preview.svg']:
        if (OUT/name).exists():z.write(OUT/name,name)
html=(OUT/'source/template.html').read_text().replace('__DATA__',json.dumps(data,separators=(',',':')))
(OUT/'index.html').write_text(html)
print(json.dumps(dict(source_files_unchanged=True,keys=len(g['switches']),zmk_screenshot=zmk,coupon_patterns=dot_reports,runtime_scenarios=table),indent=2))
