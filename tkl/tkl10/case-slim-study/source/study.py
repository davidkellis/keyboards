#!/usr/bin/env python3
"""Screen v10 thickness options using the existing component/pin envelopes.

This generates a dimensional study only. It does not rebuild or validate a case.
Dependencies for plots: numpy, matplotlib. All dimensions are millimetres.
"""
from pathlib import Path
import hashlib
import json
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parents[1]
ROOT = OUT.parent
paths = [ROOT/'case'/n for n in ('board-geometry.json', 'fit-config.json', 'fit-report.json')]
hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
geo, cfg, fit = [json.loads(p.read_text()) for p in paths]
M, PT = 2.4, 3.8
A0 = math.radians(fit['tilt_degrees'])
Z0 = fit['pcb_underside_front_origin_z']
H0 = Z0 - M*math.tan(A0) + PT/math.cos(A0)
BX, BY = cfg['battery']['origin_xy_case_mm']
BW, BD, BH = cfg['battery']['reserved_dimensions_mm']
BZ = 1.2 + cfg['battery']['padding_below_mm']

def clipped_min(poly, ylo, yhi):
    """Lowest z on a convex YZ polygon within the battery's Y projection."""
    v = [z for y,z in poly if ylo <= y <= yhi]
    for p,q in zip(poly, poly[1:] + poly[:1]):
        y,z = p
        yy,zz = q
        if abs(yy-y) > 1e-10:
            for lim in (ylo,yhi):
                t = (lim-y)/(yy-y)
                if 0 <= t <= 1:
                    v.append(z+t*(zz-z))
    return min(v) if v else None

def required_origin(a, reserve, connector=8., module=6.):
    """Find PCB elevation clearing the floor and fixed-position pouch reserve.

    Floor reliefs are permitted for the front diodes and front pins. The new
    positions of supports, ribs, fasteners and walls are deliberately not assumed
    to be collision-free: they must be rebuilt after selecting a concept.
    """
    c,s = math.cos(a),math.sin(a)
    constraints = []
    def battery_constraint(x0,x1,poly,label):
        if x0+M < BX+BW and x1+M > BX:
            v = clipped_min(poly,BY,BY+BD)
            if v is not None:
                constraints.append((BZ+reserve+.4-v,label+' / battery'))
    for q in geo['components']:
        if q['side'] != 'bottom' or q['ref'] == 'USB_PLUG_EXTERNAL':
            continue
        x,y,xx,yy = q['bounds']
        zt = q.get('z_top',0.)
        zb = zt-q['height']
        if q['ref'] == 'J1':
            zb = -connector
        if q['ref'] == 'U1':
            zb = -module
        floor = .8 if q['ref'].startswith('D') and y < 10 else 1.2
        constraints.append((floor+.4-y*s-zb*c,q['ref']+' / floor'))
        poly = [(M+yl*c-zl*s, yl*s+zl*c) for yl,zl in ((y,zb),(yy,zb),(yy,zt),(y,zt))]
        battery_constraint(x,xx,poly,q['ref'])
    for q in geo['pins']:
        if q.get('top'):
            continue
        x,y = q['xy']
        rad = max(q['diameter'],q['collar_diameter'])/2
        d = q['depth']
        floor = .8 if y < 12 else 1.2
        constraints.append((floor+.4-(y-rad)*s+d*c,q['ref']+' pin / floor'))
        poly = [(M+yl*c-zl*s, yl*s+zl*c) for yl,zl in ((y-rad,-d),(y+rad,-d),(y+rad,0),(y-rad,0))]
        battery_constraint(x-rad,x+rad,poly,q['ref']+' pin')
    board_line = [(M+yl*c,yl*s) for yl in (0,geo['board']['depth'])]
    battery_constraint(0,geo['board']['width'],board_line,'PCB')
    return max(constraints)

def case(a, reserve, connector=8., module=6., margin=.2):
    req,lim = required_origin(a,reserve,connector,module)
    z = req+margin
    depth = geo['board']['depth']*math.cos(a)+2*M
    front = z-M*math.tan(a)+PT/math.cos(a)
    rear = front+depth*math.tan(a)
    return {'angle_deg':math.degrees(a),'front_plate_plane_mm':front,'rear_plate_plane_mm':rear,
            'depth_mm':depth,'constraint':lim,'extra_vertical_study_margin_mm':margin}

scenarios = [
    {'name':'Existing battery reserve and electronics','reserve':6.3,'connector':8.,'module':6.,'color':'#647590'},
    {'name':'Thinner pouch reserve, current electronics','reserve':4.3,'connector':8.,'module':6.,'color':'#337caf'},
    {'name':'Thinner pouch + low connector envelope','reserve':4.3,'connector':3.,'module':6.,'color':'#218376'},
    {'name':'Thinner pouch + low connector + recessed module','reserve':4.3,'connector':3.,'module':4.5,'color':'#b4751e'},
]
rows=[]
for sc in scenarios:
    rows.append({'scenario':sc['name'],'battery_reserve_mm':sc['reserve'],
                 'connector_below_pcb_mm':sc['connector'],'module_below_pcb_mm':sc['module'],
                 'examples':[case(math.radians(a),sc['reserve'],sc['connector'],sc['module']) for a in (4.,3.,2.,0.)]})

# Quantify the available reduction with the current front height, floor minimum
# and existing battery. There is no additional study margin in this bound.
lo,hi=0.,A0
for _ in range(70):
    a=(lo+hi)/2
    allowed_z=H0+M*math.tan(a)-PT/math.cos(a)
    if allowed_z < required_origin(a,BH)[0]: lo=a
    else: hi=a
bound=case(hi,BH,margin=0.)
report={'status':'analytic envelope screening; not fitted printable CAD',
        'source_sha256':hashes,
        'current':{'front_plate_plane_mm':H0,'rear_plate_plane_mm':H0+cfg['fixed_footprint_mm'][1]*math.tan(A0),
                   'rounded_case_max_height_mm':18.730319010740356,'width_depth_mm':cfg['fixed_footprint_mm'],
                   'tilt_deg':math.degrees(A0),'front_relief_floor_mm':.8359322746002019,
                   'front_diode_clearance_mm':.4,'key_pitch_mm':19.05},
        'constant_front_existing_electronics_bound':bound,
        'scenarios':rows,
        'assumptions':['Fixed battery plan reserve 155 x 50 at x=83,y=80.5; battery bottom z=1.7.',
                       'Thinner battery reserve 4.3 mm is a design target, not a sourced pack or a capacity guarantee.',
                       'A 3 mm connector envelope and 4.5 mm module depth are hypothetical redesigned targets.',
                       'Minimum floor 0.8 mm at front reliefs and 1.2 mm elsewhere; vertical gap 0.4 mm.',
                       'Table examples add 0.2 mm to the required PCB elevation as a study margin.',
                       'Case depth follows the PCB projection with the same 2.4 mm end margins.',
                       'Switches/keycaps/feet are excluded from quoted plate heights.',
                       'Supports, hidden nut carriers, ports, structure, battery leads and physical dimensions require a new CAD fit audit.']}
(OUT/'measurements.json').write_text(json.dumps(report,indent=2)+'\n')

fig,axs=plt.subplots(1,2,figsize=(13,5.7),facecolor='#f6f8fc')
angles=np.linspace(0,math.degrees(A0),500)
for sc in scenarios:
    vals=[case(math.radians(a),sc['reserve'],sc['connector'],sc['module']) for a in angles]
    for ax,key in zip(axs,('rear_plate_plane_mm','front_plate_plane_mm')):
        ax.plot(angles,[v[key] for v in vals],label=sc['name'],color=sc['color'],lw=2)
for ax,title,ylabel in zip(axs,('Rear height','Front height'),('Rear plate plane above desk (mm)','Front plate plane above desk (mm)')):
    ax.set_title(title,loc='left',fontweight='bold')
    ax.set_xlabel('Typing angle (degrees)')
    ax.set_ylabel(ylabel)
    ax.set_xlim(0,6)
    ax.grid(alpha=.15)
    ax.set_facecolor('#ffffff')
    ax.spines[['top','right']].set_visible(False)
axs[0].scatter([math.degrees(A0)],[report['current']['rear_plate_plane_mm']],color='#263549',zorder=5)
axs[1].scatter([math.degrees(A0)],[H0],color='#263549',zorder=5)
axs[1].axhline(H0,color='#263549',lw=.8,ls='--')
fig.suptitle('v10 thickness options • flattening the case changes both ends',x=.065,ha='left',fontsize=15,fontweight='bold')
handles,labels=axs[0].get_legend_handles_labels()
fig.legend(handles,labels,loc='lower center',bbox_to_anchor=(.5,.06),ncol=2,frameon=False,fontsize=9)
fig.text(.065,.025,'Calculated envelopes, not validated new cases. 0.2 mm study margin; keycaps excluded. Dark dots show the current plate plane.',fontsize=9,color='#596b80')
fig.tight_layout(rect=(0,.18,1,.94))
fig.savefig(OUT/'height-options.png',dpi=160,facecolor=fig.get_facecolor())
fig.savefig(OUT/'height-options.svg',facecolor=fig.get_facecolor())
assert hashes == {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
print(json.dumps({'current_front_mm':H0,'same_front_existing_battery_bound':bound,'scenarios':rows},indent=2))
