#!/usr/bin/env python3
"""Compose unaltered WebGL captures; no painted or amplified lighting."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

OUT=Path(__file__).resolve().parents[1]
FONT='/usr/share/fonts/google-noto-vf/NotoSans[wght].ttf'
def font(n):return ImageFont.truetype(FONT,n)
BG='#161e23';INK='#e8ede7';MUTED='#a6b2ab'

image=Image.new('RGB',(1520,1320),BG);draw=ImageDraw.Draw(image)
draw.text((40,24),'V10 / Acrylic plate comparisons',font=font(34),fill=INK)
draw.text((40,78),'Same six LED locations, exposure, XVX BOW keycaps and raised case. White backing on.',font=font(19),fill=MUTED)
options=[('original','Current opaque plate','Small light windows; most of the deck stays dark.'),
         ('clear','Clear acrylic','Concentrated pools with darker areas between them.'),
         ('frosted','Lightly frosted acrylic','Softer pools, lower peaks and less distinct hot spots.'),
         ('etched','Selectively engraved acrylic','Patterned extraction; wider spread depends on coupling.')]
for i,(kind,title,note) in enumerate(options):
    x=40+(i%2)*750;y=132+(i//2)*570
    draw.text((x,y),title,font=font(25),fill=INK)
    draw.text((x,y+39),note,font=font(16),fill=MUTED)
    for suffix,crop,dy,size in [('top',(90,190,1200,655),75,(700,293)),('detail',(120,220,1170,480),367,(700,173))]:
        p=Image.open(OUT/'views'/f'raised-{kind}-{suffix}.png').convert('RGB').crop(crop)
        p.thumbnail(size,Image.Resampling.LANCZOS);image.paste(p,(x+(700-p.width)//2,y+dy))
draw.rectangle((0,1280,1520,1320),fill=BG)
draw.text((40,1289),'Illustrative light spread, not a measured brightness forecast. Lower strip: close-up between keycaps.',font=font(16),fill=MUTED)
image.save(OUT/'acrylic-comparison.png')

image=Image.new('RGB',(1520,985),BG);draw=ImageDraw.Draw(image)
draw.text((40,24),'V10 / What the keycaps conceal',font=font(34),fill=INK)
draw.text((40,78),'Same raised case and lighting settings. Keycaps hidden only; switches remain in place.',font=font(19),fill=MUTED)
for i,(kind,title,note) in enumerate(options):
    x=40+(i%2)*750;y=128+(i//2)*390
    draw.text((x,y),title,font=font(25),fill=INK)
    p=Image.open(OUT/'views'/f'raised-{kind}-plate.png').convert('RGB').crop((90,190,1200,655))
    p.thumbnail((700,293),Image.Resampling.LANCZOS);image.paste(p,(x,y+50))
draw.text((40,938),'Appearance study. Clear input collectors and engraving need a physical optical prototype.',font=font(17),fill=MUTED)
image.save(OUT/'acrylic-plate-revealed.png')
print('Saved acrylic-comparison.png and acrylic-plate-revealed.png')
