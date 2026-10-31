#!/usr/bin/env python3
"""Validate design counts, optical artwork, energy arithmetic and source preservation."""
from pathlib import Path
import hashlib, json, math, xml.etree.ElementTree as ET, zipfile

out=Path(__file__).resolve().parents[1]
d=json.loads((out/'study.json').read_text())
assert d['maximum_backlight_leds']==12 and d['baseline_backlight_leds']==10
for name,positions in d['source_layouts'].items():
    assert len(positions)==int(name)<=12
    for edge in ['front','rear']: assert sum(p['edge']==edge for p in positions)==int(name)//2
assert len(d['switches'])==86
assert all(hashlib.sha256((out.parent/f).read_bytes()).hexdigest()==sha for f,sha in d['source_sha256'].items())
c=d['coupon']; assert len(c['outputs'])==18 and len(c['pin_reliefs'])==72 and len(c['source_positions'])==2
assert math.isclose(c['width_mm']*5,d['board']['width'])
assert math.isclose(c['depth_mm'],d['board']['depth'])
for pattern in c['patterns']:
    assert len(pattern['dots'])>300
    for x,y,r in pattern['dots']:
        assert any(abs(x-wx)+r<=1.01+1e-8 and abs(y-wy)+r<=1.36+1e-8 for wx,wy in c['outputs'])
        assert all(math.hypot(x-hx,y-hy)>=hr+r+.12 for hx,hy,hr in c['pin_reliefs'])
for p in (out/'coupons').glob('*.svg'):
    svg=ET.fromstring(p.read_text())
    assert svg.attrib['width']==str(c['width_mm'])+'mm' and svg.attrib['height']==str(c['depth_mm'])+'mm'
for p in (out/'coupons').glob('*.dxf'):
    text=p.read_text(); assert '$INSUNITS\n70\n4\n' in text and text.endswith('0\nEOF\n')
for row in d['runtime_scenarios']:
    expected=row['battery_lighting_mw']/3.7
    assert math.isclose(row['lighting_battery_ma'],expected)
    daily=row['lit_hours_day']*(expected+.7)+(24-row['lit_hours_day'])*.1+5
    assert math.isclose(row['daily_mah'],daily)
    assert math.isclose(row['days']*daily,4000)
    match=next(r for r in d['runtime_scenarios'] if r['led_count']!=row['led_count'] and r['battery_lighting_mw']==row['battery_lighting_mw'] and r['lit_hours_day']==row['lit_hours_day'])
    assert row['days']==match['days']
    assert math.isclose(row['illustrative_led_ma']*row['led_count']*3/.85+1.2*3.7,row['battery_lighting_mw'])
with zipfile.ZipFile(out/'full-depth-optical-test-kit.zip') as z:
    assert z.testzip() is None
    assert z.read('README.txt')==(out/'README.txt').read_bytes()
report=dict(passed=True,source_hashes_unchanged=True,maximum_led_count=12,
    actual_keyboard_keys=len(d['switches']),coupon_outputs=18,coupon_reliefs=72,
    extraction_patterns=[dict(name=p['name'],dots=len(p['dots'])) for p in c['patterns']],
    physical_optics_validated=False,case_fit_validated=False,production_pcb_modified=False)
(out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
