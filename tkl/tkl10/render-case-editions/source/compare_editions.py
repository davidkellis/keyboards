#!/usr/bin/env python3
"""Compose unaltered browser captures for the current and raised case."""
from pathlib import Path
from PIL import Image, ImageFont, ImageDraw

OUT=Path(__file__).resolve().parents[1]
FONT='/usr/share/fonts/google-noto-vf/NotoSans[wght].ttf'
def font(n):return ImageFont.truetype(FONT,n)
image=Image.new('RGB',(1500,1000),'#eeefea');draw=ImageDraw.Draw(image)
draw.text((40,26),'V10 / Two case editions',font=font(34),fill='#28362f')
draw.text((40,78),'Same keys, PCB, battery, footprint and typing angle. Only the upper enclosure changes.',font=font(19),fill='#627164')
for i,(edition,title,note) in enumerate([
    ('current','Edition 1 · current floating keys','Switch housings remain exposed along the outer rows.'),
    ('raised','Edition 2 · raised key wells','Outer deck +3.25 mm · nominal XVX skirt gap 0.15 mm.')]):
    x=40+i*730
    for view,y,crop,size in [('hero',135,(135,230,1180,665),(690,288)),('side',560,(245,310,1050,535),(690,193))]:
        p=Image.open(OUT/'views'/f'{edition}-{view}.png').convert('RGB').crop(crop)
        p.thumbnail(size,Image.Resampling.LANCZOS);image.paste(p,(x+(690-p.width)//2,y))
    draw.text((x,435),title,font=font(25),fill='#28362f')
    draw.text((x,480),note,font=font(17),fill='#627164')
    draw.text((x,790),'Profile at rest',font=font(23),fill='#28362f')
    draw.text((x,830),'The keycap tops remain at the same height.',font=font(17),fill='#627164')
draw.text((40,915),'Switch editions in the 360° studio. Use Key travel preview to inspect the full 2.8 mm downward movement.',font=font(18),fill='#4e6154')
draw.text((40,959),'Mechanical prototype · nominal XVX shape / seating · actual cap and switch fit require the front coupon',font=font(15),fill='#718071')
image.save(OUT/'case-editions-comparison.png')
print('Saved case-editions-comparison.png')
