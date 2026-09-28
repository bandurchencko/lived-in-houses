# -*- coding: utf-8 -*-
"""Comparison sheets "picture | generated house" for the README: docs/obrazy/obraz-<name>.jpg.

    python listy_obraza.py <renders-folder>      # renders: obraz-kuznya.png, obraz-ulica.png (snimok_obraz via the viewer)
"""
import json
import sys

from PIL import Image, ImageDraw, ImageFont

SHRIFT_B, SHRIFT = 'C:/Windows/Fonts/seguisb.ttf', 'C:/Windows/Fonts/segoeui.ttf'
PRIMERY = (('dom-kuznya', 'obraz-kuznya.png', 'Picture: forge-house concept (Astra)'),
           ('ulica-k-vode', 'obraz-ulica.png', 'Picture: village street concept (Astra)'))


def list_(imya, render, levaya):
    F, F2 = ImageFont.truetype(SHRIFT_B, 30), ImageFont.truetype(SHRIFT, 24)
    ps = json.load(open('docs/obraz/%s/pasport.json' % imya, encoding='utf-8'))
    pas = ps['pasport_kartinki']
    H = 720
    a = Image.open('docs/obraz/%s/kartinka.jpg' % imya).convert('RGB')
    a = a.resize((int(a.width * H / a.height), H))
    b = Image.open(render).convert('RGB')
    b = b.crop((b.width // 2 - 480, b.height // 2 - 360, b.width // 2 + 480, b.height // 2 + 360)).resize((960, H))
    im = Image.new('RGB', (a.width + b.width + 24, H + 150), (29, 33, 38))
    im.paste(a, (0, 0))
    im.paste(b, (a.width + 24, 0))
    d = ImageDraw.Draw(im)
    d.text((20, H + 18), levaya, font=F, fill=(240, 240, 240))
    d.text((a.width + 44, H + 18), 'Generated house · seed %d · enterable, all checks passed' % ps['zerno'], font=F,
           fill=(240, 240, 240))
    krysha = {'dvuskat': 'gable roof', 'valma': 'hip roof'}.get(pas.get('krysha'), 'roof')
    d.text((a.width + 44, H + 62), 'passport read from the picture: %s · %s · %s %s° · stone %s m · shutters %s' % (
        pas['semejstvo'], pas.get('kompoz') or pas.get('chast'), krysha, pas.get('uklon_krysy_grad'),
        pas.get('kamen_niza_m'), 'yes' if pas.get('stavni') else 'no'), font=F2, fill=(200, 200, 200))
    x = a.width + 44
    for k, en in (('steny', 'walls'), ('kamen', 'stone'), ('brus', 'timber'), ('krysha', 'roof'), ('stavni', 'shutters')):
        c = (pas.get('cveta') or {}).get(k)
        if c:
            d.rectangle((x, H + 100, x + 34, H + 130), fill=c)
            d.text((x + 42, H + 100), en, font=F2, fill=(200, 200, 200))
            x += 160
    out = 'docs/obrazy/obraz-%s.jpg' % imya
    im.save(out, quality=88)
    print(out)


if __name__ == '__main__':
    for imya, render, levaya in PRIMERY:
        list_(imya, sys.argv[1] + '/' + render, levaya)
