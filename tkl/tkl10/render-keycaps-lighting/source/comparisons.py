#!/usr/bin/env python3
"""Arrange browser-rendered views without changing their shapes or lighting."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parents[1]
FONT = '/usr/share/fonts/google-noto-vf/NotoSans[wght].ttf'


def font(size):
    return ImageFont.truetype(FONT, size)


def grid(filename, title, subtitle, items, dark=False):
    background = '#161e23' if dark else '#eeefea'
    foreground = '#e4e8e0' if dark else '#26332d'
    secondary = '#a6b2aa' if dark else '#637166'
    w, margin, gap, tile_w, tile_h = 1480, 40, 24, 688, 370
    image = Image.new('RGB', (w, 1330), background)
    draw = ImageDraw.Draw(image)
    draw.text((margin, 28), title, font=font(32), fill=foreground)
    draw.text((margin, 76), subtitle, font=font(17), fill=secondary)
    for i, (source, label, note) in enumerate(items):
        x = margin + (i % 2) * (tile_w + gap)
        y = 125 + (i // 2) * (tile_h + 8)
        if source:
            photo = Image.open(OUT / 'views' / source).convert('RGB')
            photo = photo.crop((135, 230, 1180, 665))
            photo.thumbnail((tile_w, 287), Image.Resampling.LANCZOS)
            image.paste(photo, (x + (tile_w-photo.width)//2, y))
        draw.text((x+12, y+285), label, font=font(23), fill=foreground)
        for j, line in enumerate(note.split('\n')):
            draw.text((x+12, y+322+j*23), line, font=font(16), fill=secondary)
    draw.text((margin, 1294), 'V10 appearance study · real case envelope · illustrative mounting / light output · Joe Scotto cap meshes: CC BY-NC-SA 4.0', font=font(14), fill=secondary)
    image.save(OUT / filename)


grid('keycap-comparison.png', 'V10 / Keycap silhouettes',
     'Same case and switches. Nominal socket engagement 3.0 mm; extra-flat concept 2.3 mm. Installed fit remains unverified.', [
    ('caps-xvx-bow-hero.png', 'XVX Skyline R2 · BOW', 'Approximate 5 mm uniform profile · shine-through legends'),
    ('caps-xvx-wob-hero.png', 'XVX Skyline R2 · WOB', 'Same shape in black · shine-through legends'),
    ('caps-flat-hero.png', 'ScottoCaps Flat MX · FDM', 'Actual source meshes · 6.7 mm overall · blank caps'),
    ('caps-glass-hero.png', 'ScottoCaps Glass MX · resin', 'Actual source meshes · 5.7 mm socket-to-top · blank caps'),
    ('caps-slim-hero.png', 'Extra-flat MX · experimental', '3.5 mm appearance concept · not a verified printable keycap'),
    (None, 'Compare the Profile view in the studio', 'Flat cap tops do not necessarily lower the keyboard.\nSocket depth, dust-collar clearance and travel matter.\nThe existing 5000 mAh battery reserve stays in place.'),
])

grid('lighting-comparison.png', 'V10 / Making the light visible',
     'Same XVX WOB caps, graphite case and dim studio. Light brightness is illustrative; PCB changes are identified below.', [
    ('lighting-original.png', 'Current v10 · six small windows', 'Existing PCB / case · several windows hide behind key skirts'),
    ('lighting-pills.png', 'Flush diffuser slots', 'Existing six LEDs · case / optical prototype'),
    ('lighting-nav.png', 'Navigation light bar', 'Existing LED2 + guide trial, or relocate that LED on a new PCB'),
    ('lighting-deck.png', 'Frosted key deck', 'Existing six LEDs · localized pools, not uniform illumination'),
    ('lighting-halo.png', 'Lower edge halo', 'Added / redirected light sources · enclosure and PCB work'),
    ('lighting-perkey.png', 'Illuminated legends', '86 proposed LED positions · substantial PCB / power revision'),
], dark=True)
print('Saved keycap-comparison.png and lighting-comparison.png')
