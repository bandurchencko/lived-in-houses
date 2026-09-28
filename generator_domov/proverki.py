# -*- coding: utf-8 -*-
"""Проверки дома до стройки: связность комнат дверями, окна у жилых комнат, лестница (уклон, ступень, проступь,
ширина), двери, толщина стен, труба у очага, целость деталей, вид от входа на очаг и общий стол. Числа — Астра 28.09 и
разведка генераторов 28.09 (навигация UE 5.8: радиус агента 0,34 м, шаг 0,35 м; ступень ≤ 0,19, проступь ≥ 0,27,
двери ≥ 1,0 × 2,35)."""
import math

ZHILYE = ('zal', 'povarnya', 'gostevaya', 'nochlezhka', 'hozyajskaya', 'gornica', 'spalnya', 'masterskaya')


def proverit(pasport, plan, D):
    out = []

    def p(ok, chto):
        out.append({'ok': bool(ok), 'chto': chto})

    # связность: улица → все комнаты (двери этажей + связи плана: лестницы, открытая кузня)
    rebra = {}

    def rebro(a, b):
        rebra.setdefault(a, set()).add(b)
        rebra.setdefault(b, set()).add(a)
    for et in plan['etazhi']:
        for dv in et['dveri']:
            rebro(dv['iz'], dv['v'])
    for a, b in plan.get('svyazi', [['zal', 'lestnica'], ['lestnica', 'koridor'], ['galereya', 'ulica']]):
        rebro(a, b)
    vidno, fr = {'ulica'}, ['ulica']
    while fr:
        x = fr.pop()
        for y in rebra.get(x, ()):
            if y not in vidno:
                vidno.add(y)
                fr.append(y)
    komnaty = [k['id'] for et in plan['etazhi'] for k in et['komnaty']]
    nedost = [k for k in komnaty if k not in vidno]
    p(not nedost, 'все комнаты достижимы с улицы' + ('' if not nedost else ' — нет входа в: ' + ', '.join(nedost)))
    p('dvor' in vidno, 'есть дверь во двор')
    if 'kuznya' in rebra:
        p('kuznya' in vidno, 'кузня доступна (с улицы или из зала)')
    if 'galereya' in rebra:
        p('galereya' in vidno, 'галерея (терраса) доступна')

    # окна у жилых комнат (фасадные и боковые)
    u0, u1, v0, v1 = plan['razmery']['korpus']
    F1 = plan['razmery']['F1']
    bez_okna = []
    for i, et in enumerate(plan['etazhi']):
        for k in et['komnaty']:
            if k['id'] not in ZHILYE:
                continue
            ku0, ku1, kv0, kv1 = k['b']
            est = False
            for pr in plan['proemy']:
                if not pr['vid'].startswith('okno') or ((pr['w0'] < F1) != (i == 0)):
                    continue
                st, a0, a1 = pr['storona'], pr['a0'], pr['a1']
                if st == 'ul' and kv0 < v0 + 0.8 and a1 > ku0 and a0 < ku1:
                    est = True
                elif st == 'zad' and kv1 > v1 - 0.8 and a1 > ku0 and a0 < ku1:
                    est = True
                elif st == 'sev' and ku0 < u0 + 0.8 and a1 > kv0 and a0 < kv1:
                    est = True
                elif st == 'jug' and ku1 > u1 - 0.8 and a1 > kv0 and a0 < kv1:
                    est = True
            if not est:
                bez_okna.append(k['imya'])
    p(not bez_okna, 'у жилых комнат есть окна' + ('' if not bez_okna else ' — без окна: ' + ', '.join(bez_okna)))

    # лестница
    for l in plan['lestnicy']:
        if l['vid'] != 'vnutr':
            continue
        n = max(10, int(round(l['podem'] / 0.19)))
        st, pr_ = l['podem'] / n, l['dlina'] / n
        p(l['ugol'] <= 38.0, 'лестница не круче 38° (%.1f°)' % l['ugol'])
        p(st <= 0.19 + 1e-6, 'ступень ≤ 0,19 м (%.3f)' % st)
        p(pr_ >= 0.27 - 1e-6, 'проступь ≥ 0,27 м (%.3f)' % pr_)
        p(l['shir'] >= 1.2, 'ширина марша ≥ 1,2 м (%.2f)' % l['shir'])

    # двери
    uzkie = [dv for et in plan['etazhi'] for dv in et['dveri'] if dv['shir'] < 0.95]
    p(not uzkie, 'двери не уже 0,95 м' + ('' if not uzkie else ' — узкие: %d' % len(uzkie)))
    vhod = [dv for dv in plan['etazhi'][0]['dveri'] if dv['iz'] == 'ulica']
    p(vhod and vhod[0]['shir'] >= 1.2 - 1e-6, 'входная дверь ≥ 1,2 м')

    # очаг и труба
    p(all(o.get('truba') for o in plan['ochagi']), 'у очага и горна есть труба')

    # виды зала: от входа на очаг и общий стол, от стола на очаг — перегородки низа не заслоняют (Астра 28.09)
    vidy = plan.get('vidy')
    if vidy:
        P = plan['etazhi'][0]['w_pola']
        pregrady = [d['b'] for d in D.spisok if d['t'] in ('stena', 'kor') and d['g'] in ('peregorodki',)
                    and d['b'][4] < P + 1.5 and d['b'][5] > P + 1.2]
        s = pasport['parametry'].get('s', 1)
        SU = pasport.get('sled', [11.7])[0]

        def m_(pt):
            return pt if s > 0 else [SU - pt[0], pt[1]]
        for v_ in vidy:
            zaslon = [b for b in pregrady if _otrezok_v_korobke(m_(v_['ot']), m_(v_['na']), b)]
            p(not zaslon, 'вид %s открыт' % v_['imya'] + ('' if not zaslon else ' — заслоняет перегородка'))
    vid = plan.get('vid_ot_vhoda') if not vidy else None
    if vid:
        P = plan['etazhi'][0]['w_pola']
        pregrady = [d['b'] for d in D.spisok if d['t'] in ('stena', 'kor') and d['g'] in ('peregorodki',)
                    and d['b'][4] < P + 1.5 and d['b'][5] > P + 1.2]
        s = pasport['parametry'].get('s', 1)
        SU = pasport.get('sled', [11.7])[0]

        def m(pt):                      # план — в осях до отражения, детали — уже отражены
            return pt if s > 0 else [SU - pt[0], pt[1]]
        for cel, imya in ((vid['ochag'], 'очаг'), (vid['stol'], 'общий стол')):
            zaslon = [b for b in pregrady if _otrezok_v_korobke(m(vid['ot']), m(cel), b)]
            p(not zaslon, 'от входа виден %s' % imya + ('' if not zaslon else ' — заслоняет перегородка'))

    # детали целы
    plohie = 0
    for d in D.spisok:
        if d['t'] in ('kor', 'stena'):
            b = d['b']
            if not all(math.isfinite(x) for x in b) or b[1] <= b[0] or b[3] <= b[2] or b[5] <= b[4]:
                plohie += 1
    p(plohie == 0, 'коробки деталей невырожденные' + ('' if not plohie else ' — плохих %d' % plohie))
    return out


def _otrezok_v_korobke(a, b, box):
    """Пересекает ли отрезок a→b (на плане) прямоугольник box (u0, u1, v0, v1, …) — метод отсечения."""
    t0, t1 = 0.0, 1.0
    for os_, lo, hi in ((0, box[0], box[1]), (1, box[2], box[3])):
        d = b[os_] - a[os_]
        if abs(d) < 1e-9:
            if a[os_] < lo or a[os_] > hi:
                return False
            continue
        ta, tb = (lo - a[os_]) / d, (hi - a[os_]) / d
        if ta > tb:
            ta, tb = tb, ta
        t0, t1 = max(t0, ta), min(t1, tb)
        if t0 > t1:
            return False
    return True
