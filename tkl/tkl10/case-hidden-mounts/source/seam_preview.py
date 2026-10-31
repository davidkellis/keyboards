#!/usr/bin/env python3
"""Show the actual front cross-section; this does not modify the enclosure."""
import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/keyboards-matplotlib')
from pathlib import Path
import json
import hashlib
import cadquery as cq
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Patch

out = Path(__file__).resolve().parents[1]
upper = cq.Shape.importBrep(str(out / 'reference/upper.brep'))
assert upper.isValid() and len(upper.Solids()) == 1

fig, ax = plt.subplots(figsize=(11, 7), facecolor='#f5f7fa')
ax.set_facecolor('#f5f7fa')
colors = {'upper': '#53697b', 'bottom': '#d09852'}
sections = {}
for name, color in colors.items():
    source = out / 'reference' / (name + '-assembly.stl')
    mesh = trimesh.load_mesh(source, process=True)
    section = mesh.section(plane_origin=[100, 0, 0], plane_normal=[1, 0, 0])
    assert section is not None
    paths = [entity.discrete(section.vertices) for entity in section.entities]
    assert all(entity.closed for entity in section.entities)
    for loop in paths:
        ax.add_patch(Polygon(loop[:, 1:3], closed=True, facecolor=color,
                             edgecolor=color, linewidth=.6))
    sections[name] = {'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                      'closed_section_loops': len(paths)}

ax.set_xlim(-3.8, 14)
ax.set_ylim(-2.1, 11.5)
ax.set_aspect('equal')
ax.axis('off')
def label(text, point, target):
    ax.annotate(text, xy=target, xytext=point, fontsize=11, color='#20364b',
                va='center', arrowprops={'arrowstyle': '->', 'color': '#20364b',
                                       'linewidth': 1.25})

label('Plate and wall:\none continuous printed part', (3.7, 9), (1.6, 4.9))
label('Flush top\n2.5 mm round', (-3.5, 7.5), (.65, 5.0))
label('Continuous\nouter wall', (-3.5, 4.4), (.2, 3.5))
label('Inset removable bottom', (6.1, 2.7), (5, .7))
label('Opening joint is underneath', (3.5, -1.35), (1.6, .15))
ax.text(7.8, 7.6, 'Inside the keyboard', color='#526a7b', fontsize=11)
ax.legend(handles=[Patch(color=colors['upper'], label='Upper shell'),
                   Patch(color=colors['bottom'], label='Bottom panel')],
          loc='lower right', frameon=False, fontsize=10)
fig.suptitle('Flush top, rounded edge, no upper seam', x=.08, ha='left', y=.96,
             color='#20364b', fontsize=23, fontweight='bold')
fig.text(.08, .885, 'Actual CAD mesh cross-section through the front edge (x = 100 mm)',
         color='#526a7b', fontsize=11)
fig.text(.08, .04, 'Full-size upper shell shown. Split prints still need bonding and surface finishing.\n'
         'Rear USB and switch inserts have separate local joints.', color='#526a7b', fontsize=10)
fig.subplots_adjust(top=.87, bottom=.13, left=.06, right=.98)
fig.savefig(out / 'shell-section.png', dpi=150)
fig.savefig(out / 'shell-section.svg')
plt.close(fig)
(out / 'shell-continuity.json').write_text(json.dumps({
    'upper_valid': True, 'upper_solid_count': len(upper.Solids()),
    'upper_brep_sha256': hashlib.sha256((out/'reference/upper.brep').read_bytes()).hexdigest(),
    'section_plane_x_mm': 100, 'section_sources': sections,
    'surface': json.loads((out/'validation.json').read_text())['surface'],
    'notes': ['Plate and perimeter walls are fused into the upper solid.',
              'Raised lip removed; 2.5 mm outer top roll-over and 3 mm vertical corners.',
              'Bottom panel is removable; its perimeter is inset behind the outer skirt.',
              'Split-print bond and rear port inserts remain separate joints.']
}, indent=2) + '\n')
print('Verified one valid upper solid; wrote front section preview.')
