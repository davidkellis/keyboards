#!/usr/bin/env python3
"""Board-coordinate mounting map; no inferred component dimensions."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle,Polygon
from plate_geometry import stabilizer_apertures
R=Path(__file__).resolve().parents[1];C=R/'case'
g=json.loads((C/'board-geometry.json').read_text());cfg=json.loads((R/'scripts/fit-config.json').read_text())
W,D=g['board']['width'],g['board']['depth']
fig,ax=plt.subplots(figsize=(15,6.5));fig.patch.set_facecolor('#f6f8fb');ax.set_facecolor('#f6f8fb')
ax.add_patch(Rectangle((0,0),W,D,facecolor='#bfcddd',edgecolor='#314459',linewidth=1.2))
for key in g['switches']:
 x,y=key['xy'];ax.add_patch(Rectangle((x-7.075,y-7.075),14.15,14.15,facecolor='white',edgecolor='#789',linewidth=.4))
 if key['units']>=2:
  geo=stabilizer_apertures(x,y,100 if key['units']==6.25 else 23.8)
  for p in (list(geo.geoms) if hasattr(geo,'geoms') else [geo]):ax.add_patch(Polygon(list(p.exterior.coords),facecolor='white',edgecolor='#789',linewidth=.4))
for p in cfg['mounting']['points']:
 x,y=p['xy'];color='#b75b25' if p['support']=='rear-wall bracket' else '#155a8a'
 ax.add_patch(Circle((x,y),3.5,facecolor='#f6f8fb',edgecolor=color,linewidth=1))
 ax.add_patch(Circle((x,y),1.25,facecolor=color))
 ax.annotate(p['ref'],(x,y),xytext=(0,12 if y<120 else 15),textcoords='offset points',ha='center',va='bottom',color=color,fontsize=10,weight='bold',bbox=dict(boxstyle='round,pad=.15',facecolor='#f6f8fb',edgecolor='none'))
x,y,xx,yy=next(c['bounds'] for c in g['components'] if c['ref']=='U1')
ax.add_patch(Rectangle((x,y),xx-x,yy-y,fill=False,edgecolor='#6b4fa1',linestyle='--',linewidth=1.4));ax.text((x+xx)/2,(y+yy)/2,'Clone\nbelow',ha='center',va='center',fontsize=9,color='#6b4fa1')
ax.set_xlim(-3,W+3);ax.set_ylim(-6,D+10);ax.set_aspect('equal');ax.axis('off')
fig.suptitle('v9.1 mounting map • top view',x=.06,ha='left',fontsize=18,color='#24384a')
fig.text(.06,.905,'12 × M2 × 5 button-head screws · heads recessed below the switch-plate surface',fontsize=11,color='#3c5165')
fig.text(.06,.055,'Blue: floor posts    Brown: rear-wall brackets above the battery    Rear at top · front at bottom',fontsize=11,color='#3c5165')
fig.subplots_adjust(left=.04,right=.98,bottom=.09,top=.87)
fig.savefig(C/'mounting-plan.svg');fig.savefig(C/'mounting-plan.png',dpi=140);plt.close(fig)
