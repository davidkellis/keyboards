#!/usr/bin/env python3
"""Build a <=12-source engineering study; never modify production source files."""
from pathlib import Path
import csv, hashlib, json, math, zipfile

OUT = Path(__file__).resolve().parents[1]
ROOT = OUT.parent
for folder in ['coupons', 'diagrams', 'reference']:
    (OUT / folder).mkdir(parents=True, exist_ok=True)
inputs = ['case/board-geometry.json', 'case/fit-config.json', 'case/fit-report.json',
          'kicad/keyboard.kicad_pcb', 'kicad/power.kicad_sch',
          'manufacturing/jlcpcb-bom.csv', 'manufacturing/assembly-notes.csv']
hashes = {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in inputs}
g = json.loads((ROOT / inputs[0]).read_text())

def budget(power=40, hours=12, count=10, capacity=5000, usable=.8,
           voltage=3.7, active=.7, sleep=.1, self_pct=3):
    assert count in [6, 8, 10, 12] and 0 <= hours <= 24 and power >= 0
    lighting_ma = power / voltage
    self_day = capacity * self_pct / 100 / 30
    daily = hours * (lighting_ma + active) + (24-hours) * sleep + self_day
    return dict(led_count=count, battery_lighting_mw=power, lit_hours_day=hours,
                lighting_battery_ma=lighting_ma, days=capacity*usable/daily,
                continuous_hours=capacity*usable/(lighting_ma+active+self_day/24),
                daily_mah=daily,
                illustrative_led_ma=max(0, power-1.2*voltage)*.85/(count*3))

table = [budget(p,h,n) for n in [10,12] for p in [40,80,160] for h in [6,12]]
with (OUT / 'power-targets.csv').open('w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=table[0].keys()); w.writeheader(); w.writerows(table)

W, H = g['board']['width']/5, g['board']['depth']
row_y = sorted(set(round(k['xy'][1],4) for k in g['switches']))
assert len(row_y) == 6
centers = [(W/2+(col-1)*19.05, H-y) for y in row_y for col in range(3)]
windows = [(x,y-4.93) for x,y in centers]
# Generic, rotated test-switch footprint. Verify native LED handedness on hardware.
reliefs = [(x+dx,y-dy,r) for x,y in centers
           for dx,dy,r in [(0,0,2.775),(5,5.15,1.05),(0,-5.9,1.2),(-5,-3.8,1.2)]]
sources = [(W/2,0),(W/2,H)]

def rect(x,y,w,h,**attrs):
    return f'<rect x="{x:.5f}" y="{y:.5f}" width="{w:.5f}" height="{h:.5f}" '+ ' '.join(f'{k.replace("_","-")}="{v}"' for k,v in attrs.items())+'/>'
def circ(x,y,r,**attrs):
    return f'<circle cx="{x:.5f}" cy="{y:.5f}" r="{r:.5f}" '+ ' '.join(f'{k.replace("_","-")}="{v}"' for k,v in attrs.items())+'/>'
def svg(body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">{body}</svg>'
def path_rect(x,y,w,h): return [(x,y),(x+w,y),(x+w,y+h),(x,y+h)]
outer = path_rect(0,0,W,H)
cut_style = dict(fill='none',stroke='#ff0000',stroke_width='.01')
perimeter = rect(0,0,W,H,**cut_style)
hole_svg = ''.join(circ(x,y,r,**cut_style) for x,y,r in reliefs)
for variant in ['solid','perforated']:
    holes = hole_svg if variant == 'perforated' else ''
    (OUT/f'coupons/guide-{variant}-CUT.svg').write_text(svg(perimeter+holes))
    outputs = ''.join(rect(x-1.05,y-1.4,2.1,2.8,**cut_style) for x,y in windows)
    (OUT/f'coupons/upper-mask-{variant}-CUT.svg').write_text(svg(perimeter+outputs+holes))
    (OUT/f'coupons/white-reflector-{variant}-CUT.svg').write_text(svg(perimeter+holes))

def dxf(lines, holes, dots):
    result = ['0','SECTION','2','HEADER','9','$INSUNITS','70','4','0','ENDSEC','0','SECTION','2','ENTITIES']
    for layer,pts in lines:
        result += ['0','LWPOLYLINE','8',layer,'90',str(len(pts)),'70','1']
        for x,y in pts: result += ['10',str(x),'20',str(H-y)]
    for layer,pts in [('CUT',holes),('ETCH',dots)]:
        for x,y,r in pts:
            result += ['0','CIRCLE','8',layer,'10',str(x),'20',str(H-y),'30','0','40',str(r)]
    return '\n'.join(result+['0','ENDSEC','0','EOF'])+'\n'

patterns=[]
for name,rmin,rmax in [('sparse',.055,.105),('medium',.08,.14),('dense',.10,.18)]:
    dots=[]
    for x,y in windows:
        distance=min(math.hypot(x-sx,y-sy) for sx,sy in sources)
        grading=min(1,distance/math.hypot(H/2,W/2))
        radius=rmin+(rmax-rmin)*grading
        for i in range(-3,4):
            for j in range(-4,5):
                px=x+i*.42; py=y+j*.42
                if abs(px-x)+radius>1.01 or abs(py-y)+radius>1.36: continue
                if any(math.hypot(px-hx,py-hy)<hr+radius+.12 for hx,hy,hr in reliefs): continue
                dots.append((px,py,radius))
    (OUT/f'coupons/guide-{name}-ETCH.svg').write_text(svg(''.join(circ(x,y,r,fill='#000000') for x,y,r in dots)))
    for variant in ['solid','perforated']:
        (OUT/f'coupons/guide-{name}-{variant}.dxf').write_text(dxf([('CUT',outer)],reliefs if variant=='perforated' else [],dots))
    patterns.append(dict(name=name,dots=dots))
for variant in ['solid','perforated']:
    lines=[('CUT',outer)]+[('CUT',path_rect(x-1.05,y-1.4,2.1,2.8)) for x,y in windows]
    (OUT/f'coupons/upper-mask-{variant}.dxf').write_text(dxf(lines,reliefs if variant=='perforated' else [],[]))

# A legible annotated preview; no source-intensity field is simulated.
body = '<rect width="700" height="610" fill="#f5f2e9"/><g font-family="sans-serif" fill="#203c40">'
body += '<text x="25" y="35" font-size="23">Full-depth, two-source optical test</text><text x="25" y="59" font-size="13">18 output windows · actual V10 row spacing · test artwork, not a PCB</text>'
body += f'<g transform="translate(33,90) scale(3.65)">{rect(0,0,W,H,fill="#d1e7e5",stroke="#42787a",stroke_width=".3")}'
body += ''.join(circ(x,y,r,fill='#f5f2e9',stroke='#8aa6a5',stroke_width='.15') for x,y,r in reliefs)
body += ''.join(rect(x-1.05,y-1.4,2.1,2.8,fill='#a87520') for x,y in windows)
body += rect(W/2-1.8,-1.5,3.6,1.2,fill='#b96936')+rect(W/2-1.8,H+.3,3.6,1.2,fill='#b96936')+'</g>'
notes=[('Two side-emitting white LEDs','One at each end; nine outputs per source.'),
       ('Local extraction dots','Polished transport area between windows.'),
       ('Compare solid and perforated','Pin holes can change both loss and uniformity.'),
       ('Test real switch + shine-through cap','Move one assembly between windows if needed.'),
       ('Match the full keyboard power density','About 1/5 of ten-source LED output power.'),
       ('Keep the same stock and exposure','Three etch densities; add a separate reflector.')]
for i,(a,b) in enumerate(notes):
    yy=119+i*70
    body+=f'<text x="322" y="{yy}" font-size="17">{a}</text><text x="322" y="{yy+23}" font-size="12">{b}</text>'
body+='<text x="322" y="558" font-size="12">Guide size: 70.152 × 129.19 mm. Etch underside.</text><text x="322" y="581" font-size="12">Native LED-channel handedness must be checked.</text></g>'
(OUT/'diagrams/coupon-preview.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="700" height="610" viewBox="0 0 700 610">'+body+'</svg>')

source_layouts = {str(n): [{'x':g['board']['width']*(i+.5)/(n//2),'y':y,'edge':edge}
                            for edge,y in [('front',0),('rear',g['board']['depth'])] for i in range(n//2)]
                  for n in [6,8,10,12]}
data=dict(date='2026-10-15',status='Optical prototype proposal; not a PCB or fabrication release',
          maximum_backlight_leds=12,baseline_backlight_leds=10,source_sha256=hashes,
          board=g['board'],switches=g['switches'],source_layouts=source_layouts,
          runtime_scenarios=table,assumptions=dict(capacity_mah=5000,usable_fraction=.8,average_cell_v=3.7,
             base_lit_ma=.7,base_unlit_ma=.1,self_discharge_pct_month=3,driver_fixed_ma=1.2,
             stage_efficiency_after_fixed_load=.85,illustrative_led_v=3,brightness_measured=False),
          coupon=dict(width_mm=W,depth_mm=H,source_positions=sources,outputs=windows,
             switch_centers=centers,pin_reliefs=reliefs,patterns=patterns,
             window_size_mm=[2.1,2.8],thickness_trials_mm=[.8,1,1.5],
             status='Bench only; channel handedness, real component reliefs and case fit unresolved'))
(OUT/'study.json').write_text(json.dumps(data,indent=2)+'\n')
(OUT/'index.html').write_text((OUT/'source/template.html').read_text().replace('__DATA__',json.dumps(data,separators=(',',':'))))
assert all(hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==sha for f,sha in hashes.items())
with zipfile.ZipFile(OUT/'full-depth-optical-test-kit.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted((OUT/'coupons').iterdir()): z.write(p,str(p.relative_to(OUT)))
    for f in ['README.txt','study.json','diagrams/coupon-preview.svg']: z.write(OUT/f,f)
print(json.dumps(dict(keys=len(g['switches']),max_leds=12,bench_outputs=len(windows),pin_reliefs=len(reliefs),
                     unchanged_source_files=len(hashes),scenarios=table[:6]),indent=2))
