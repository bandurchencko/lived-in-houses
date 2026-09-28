# -*- coding: utf-8 -*-
"""Лист дома для Астры до стройки: планы этажей сверху (комнаты с подписями и площадями, проёмы наружных стен, двери
между комнатами с направлением входа, лестницы, очаг и горн, крыльцо, кузня, галереи и пристройки) — как листы фабрики
сёл. Рисуется из плана генератора; при s = −1 отражён, как сам дом."""
import math

from PIL import Image, ImageDraw, ImageFont

M = 58          # пикселей на метр
POLE = 40


def list_(pasport, plan, put, SU=11.7, SV=10.25):
    p = pasport['parametry']
    s = p.get('s', 1)
    ft = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 15)
    fm = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 13)
    fz = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 20)
    shir = int((SU + 1.5) * M) + 2 * POLE
    vys = int((SV + 1.0) * M) + 2 * POLE + 30
    im = Image.new('RGB', (shir * 2 + 20, vys + 96), (245, 240, 230))
    d = ImageDraw.Draw(im)
    d.text((10, 8), 'Генератор домов · %s · зерно %s · %s · корпус %.2f × %.2f м · вальма %.0f° · %s' % (
        pasport['semejstvo'], pasport['zerno'], pasport.get('kompoz_imya') or pasport.get('chast_imya', ''), p['Wb'], p['Db'], p['uklon'],
        'вид сверху, улица внизу — как в мире'), fill=(20, 20, 20), font=fz)

    def xy(ox, u, v):
        uu = SU - u if s > 0 else u          # 28.09: оси Unreal левые — сверху, улица внизу, +u лежит слева
        return ox + POLE + (uu + 0.75) * M, 50 + POLE + (SV + 0.5 - v) * M          # улица (v = 0) — внизу листа

    def pr(ox, b, **kw):
        a, c = xy(ox, b[0], b[3]), xy(ox, b[1], b[2])
        d.rectangle([min(a[0], c[0]), min(a[1], c[1]), max(a[0], c[0]), max(a[1], c[1])], **kw)

    def punktir(ox, b, cvet):
        a, c = xy(ox, b[0], b[3]), xy(ox, b[1], b[2])
        x0, x1 = sorted((a[0], c[0]))
        y0, y1 = sorted((a[1], c[1]))
        for (p0, p1) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
            dl = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
            n = max(1, int(dl / 12))
            for k in range(0, n, 2):
                t0, t1 = k / n, min(1.0, (k + 1) / n)
                d.line([p0[0] + (p1[0] - p0[0]) * t0, p0[1] + (p1[1] - p0[1]) * t0,
                        p0[0] + (p1[0] - p0[0]) * t1, p0[1] + (p1[1] - p0[1]) * t1], fill=cvet, width=3)

    cveta = {'zal': (250, 214, 170), 'povarnya': (238, 196, 150), 'kladovaya': (215, 200, 170), 'koridor': (225, 225, 210),
             'gornica': (250, 214, 170), 'spalnya': (215, 205, 240),
             'gostevaya': (205, 225, 240), 'nochlezhka': (200, 215, 235), 'hozyajskaya': (215, 205, 240)}
    cveta_chastej = {'крыльцо': (150, 110, 60), 'кузня': (200, 70, 20), 'галерея': (60, 120, 60), 'терраса': (60, 120, 60),
                     'лестница': (120, 60, 20)}
    for i, et in enumerate(plan['etazhi']):
        ox = i * (shir + 20)
        pr(ox, [0, SU, 0, SV], outline=(150, 150, 150))
        d.text((ox + POLE, 50 + 8), ('Низ — пол %.2f м' if i == 0 else 'Верх — пол %.2f м') % et['w_pola'], fill=(40, 40, 40), font=fz)
        u0, u1, v0, v1 = plan['razmery']['korpus']
        # крыльцо, кузня, галереи, пристройки — пунктиром с подписью
        for ch in plan.get('chasti', []):
            if ch['etazh'] != i and not (i == 1 and ch['imya'] == 'лестница'):
                continue
            cv = cveta_chastej.get(ch['imya'], (90, 90, 90))
            punktir(ox, ch['b'], cv)
            a = xy(ox, (ch['b'][0] + ch['b'][1]) / 2.0, (ch['b'][2] + ch['b'][3]) / 2.0)
            d.text((a[0] - 24, a[1] - 8), ch['imya'], fill=cv, font=ft)
        pr(ox, [u0, u1, v0, v1], outline=(90, 40, 30), width=6)
        for k in et['komnaty']:
            ku0, ku1, kv0, kv1 = k['b']
            pr(ox, k['b'], fill=cveta.get(k['id'], (230, 230, 230)), outline=(60, 60, 60), width=2)
            pl = (ku1 - ku0) * (kv1 - kv0)
            for z in k.get('bez', []):
                pl -= max(0, min(ku1, z[1]) - max(ku0, z[0])) * max(0, min(kv1, z[3]) - max(kv0, z[2]))
            c = xy(ox, (ku0 + ku1) / 2, (kv0 + kv1) / 2)
            d.text((c[0] - 40, c[1] - 10), '%s\n%.1f м²' % (k['imya'], pl), fill=(20, 20, 20), font=ft)
            for z in k.get('bez', []):
                pr(ox, z, outline=(60, 60, 60), width=2)
        # проёмы наружных стен этого этажа
        for pr_ in plan['proemy']:
            niz = pr_['w0'] < plan['razmery']['F1']
            if (i == 0) != niz:
                continue
            cvet = (200, 40, 30) if pr_['vid'].startswith(('dver', 'proem')) else (40, 110, 220)
            st, a0, a1 = pr_['storona'], pr_['a0'], pr_['a1']
            if st == 'ul':
                A, B = xy(ox, a0, v0), xy(ox, a1, v0)
            elif st == 'zad':
                A, B = xy(ox, a0, v1), xy(ox, a1, v1)
            elif st == 'sev':
                A, B = xy(ox, u0, a0), xy(ox, u0, a1)
            else:
                A, B = xy(ox, u1, a0), xy(ox, u1, a1)
            d.line([A, B], fill=cvet, width=9)
        # двери между комнатами: разрыв в перегородке и четверть круга — куда открывается (в какую комнату входят)
        for dv in plan.get('vnutr_dveri', []):
            if dv['etazh'] != i:
                continue
            b = dv['b']
            pr(ox, b, fill=(245, 240, 230))
            dlina = (b[1] - b[0]) if (b[1] - b[0]) >= (b[3] - b[2]) else (b[3] - b[2])
            if (b[1] - b[0]) >= (b[3] - b[2]):
                vc = b[2] if dv['v_komnatu'] < 0 else b[3]
                pet, kon = xy(ox, b[0], vc), xy(ox, b[0], vc + dv['v_komnatu'] * dlina)
                A = xy(ox, b[1], vc)
            else:
                uc = b[0] if dv['v_komnatu'] < 0 else b[1]
                pet, kon = xy(ox, uc, b[2]), xy(ox, uc + dv['v_komnatu'] * dlina, b[2])
                A = xy(ox, uc, b[3])
            d.line([pet, kon], fill=(200, 110, 20), width=4)
            r_ = math.hypot(kon[0] - pet[0], kon[1] - pet[1])
            g1 = math.degrees(math.atan2(kon[1] - pet[1], kon[0] - pet[0]))
            g2 = math.degrees(math.atan2(A[1] - pet[1], A[0] - pet[0]))
            if (g2 - g1) % 360 > 180:
                g1, g2 = g2, g1
            d.arc([pet[0] - r_, pet[1] - r_, pet[0] + r_, pet[1] + r_], g1, g2, fill=(200, 110, 20), width=2)
        for l in plan['lestnicy']:
            if l.get('vid') != 'vnutr':
                continue
            lu0, lu1, lv0, lv1 = l['b']
            a, b = xy(ox, lu0, lv1), xy(ox, lu1, lv0)
            d.rectangle([min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])], outline=(120, 60, 20), width=3)
            n = 12
            for k in range(n + 1):
                yy = min(a[1], b[1]) + (abs(b[1] - a[1])) * k / n
                d.line([min(a[0], b[0]), yy, max(a[0], b[0]), yy], fill=(120, 60, 20), width=1)
            d.text((min(a[0], b[0]) + 3, min(a[1], b[1]) + 3), 'лестница %.0f°' % l['ugol'], fill=(120, 60, 20), font=fm)
        # очаг (внутри) и горн (снаружи) — на одной трубе
        if i == 0:
            for o in plan.get('ochagi', []):
                if 'rama' not in o:                       # печь дома с двором — прямо коробкой
                    b = o['b']
                else:
                    os_, lico, zn = o['rama']
                    a = o['a']
                    if os_ == 'u':
                        b = [a - 0.95, a + 0.95, min(lico, lico + zn * 0.8), max(lico, lico + zn * 0.8)]
                    else:
                        b = [min(lico, lico + zn * 0.8), max(lico, lico + zn * 0.8), a - 0.95, a + 0.95]
                pr(ox, b, fill=(210, 80, 30) if o['vid'] == 'gorn' else (170, 60, 40), outline=(60, 20, 10))
                c = xy(ox, (b[0] + b[1]) / 2, (b[2] + b[3]) / 2)
                d.text((c[0] - 16, c[1] - 7), {'gorn': 'горн', 'pech': 'печь'}.get(o['vid'], 'очаг'), fill=(255, 255, 255), font=fm)
            for v_ in plan.get('vidy', []):
                d.line([xy(ox, *v_['ot']), xy(ox, *v_['na'])], fill=(80, 150, 60), width=2)
        d.text((ox + POLE, vys + 20), 'улица ↓', fill=(40, 40, 40), font=fz)
    d.text((10, vys + 46), 'красное — двери и проём в кузню, синее — окна, оранжевое — двери между комнатами (дуга — куда '
                           'открывается), зелёные линии — вид от входа на очаг и общий стол; пунктир — крыльцо, кузня, '
                           'галерея, терраса, наружная лестница', fill=(60, 60, 60), font=ft)
    im.save(put, quality=90)
    return put
