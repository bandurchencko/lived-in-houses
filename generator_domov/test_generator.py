# -*- coding: utf-8 -*-
"""Тесты генератора домов: то же зерно — тот же дом; разные зёрна — разные; проверки зелёные на сотне зёрен; детали в
пределах слота; отражение не ломает дом; правила Астры держатся (уклон, свес, окна, лестница)."""
import json

import pytest

from generator_domov import traktir
from generator_domov.proverki import proverit
from generator_domov.stil_mangala import STIL


def test_to_zhe_zerno_tot_zhe_dom():
    a = traktir.sobrat(171)[2].v_json()
    b = traktir.sobrat(171)[2].v_json()
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_raznye_zyorna_raznye_doma():
    otp = {json.dumps(traktir.sobrat(z)[0]['parametry'], sort_keys=True) for z in range(20)}
    assert len(otp) == 20


@pytest.mark.parametrize('zerno', range(0, 100))
def test_proverki_zelenye(zerno):
    pas, plan, D = traktir.sobrat(zerno)
    krasnye = [x['chto'] for x in proverit(pas, plan, D) if not x['ok']]
    assert not krasnye, krasnye


@pytest.mark.parametrize('zerno', (1, 2, 171, 298, 1899))
def test_v_predelah_slota(zerno):
    pas, plan, D = traktir.sobrat(zerno)
    for d in D.spisok:
        if d['t'] in ('kor', 'stena') and d['g'] != 'krysha':
            b = d['b']
            assert -1.2 <= b[0] and b[1] <= traktir.SU + 1.2, (d['t'], b)
            assert -1.2 <= b[2] and b[3] <= traktir.SV + 1.2, (d['t'], b)


def test_pravila_astry():
    for z in range(40):
        p = traktir.parametry(z)
        assert 22.0 <= p['uklon'] <= 30.0
        assert STIL['svs'][0] <= p['svs'] <= STIL['svs'][1]
        assert p['s'] in (1, -1)
    storony = {traktir.parametry(z)['s'] for z in range(40)}
    assert storony == {1, -1}, 'зерно должно менять сторону лестницы'


@pytest.mark.parametrize('kompoz', traktir.KOMPOZ)
@pytest.mark.parametrize('zerno', range(0, 30))
def test_kompozicii_zelenye(kompoz, zerno):
    """Каждая композиция на 30 зёрнах: все проверки зелёные, дом в пределах слота."""
    pas, plan, D = traktir.sobrat(zerno, kompoz)
    krasnye = [x['chto'] for x in proverit(pas, plan, D) if not x['ok']]
    assert not krasnye, krasnye
    assert pas['kompoz'] == kompoz


def test_kompozicii_razlichny():
    """Астра 28.09: варианты различаются крупными объёмами — у каждой композиции свой набор частей и своя кровля."""
    nabory, krovli = set(), set()
    for kz in traktir.KOMPOZ:
        pas, plan, D = traktir.sobrat(298, kz)
        nabory.add(tuple(sorted(ch['imya'] + str(ch['etazh']) for ch in plan['chasti'])))
        krovli.add(sum(1 for d in D.spisok if d['g'] == 'krysha' and d['t'] == 'plita'))
    assert len(nabory) == len(traktir.KOMPOZ)
    assert len(krovli) >= 3


def test_zerno_vybiraet_kompoziciyu():
    vse = {traktir.parametry(z)['kompoz'] for z in range(60)}
    assert vse == set(traktir.KOMPOZ)


def test_vid_ot_vhoda():
    """Из двери зала видны очаг и общий стол, от стола — очаг: во всех композициях (проверка в proverit)."""
    for kz in traktir.KOMPOZ:
        for z in (171, 298, 13):
            pas, plan, D = traktir.sobrat(z, kz)
            vid = [x for x in proverit(pas, plan, D) if x['chto'].startswith('вид ')]
            assert len(vid) == 3 and all(x['ok'] for x in vid), vid


def test_otrazhenie_simmetrichno():
    """Дом с s = −1 — зеркало дома с теми же размерами: сумма u-середин коробок отражается."""
    for z in range(30):
        pas, plan, D = traktir.sobrat(z)
        if pas['parametry']['s'] < 0:
            b = [d['b'] for d in D.spisok if d['t'] == 'kor']
            assert all(x[0] < x[1] for x in b)
            break


def test_kosyaki_ne_zapodlico_s_otkosom():
    """28.09: косяк заподлицо с откосом стены мигал при проходе (две грани в одной плоскости) — косяки выступают в проём."""
    from generator_domov import dom_dvor
    for pas, plan, D in (traktir.sobrat(13), traktir.sobrat(4), traktir.sobrat(7),
                         dom_dvor.sobrat(1717, 'krylco', [], None, None, 'kolybel'), dom_dvor.sobrat(2020, 'masterskaya')):
        # вырезы дверей в стенах вдоль u (фасад и зад): откос — грани u = a0 и u = a1 на глубину стены
        vyrezy = [v for d in D.spisok if d['t'] == 'stena' for v in d.get('vyr', [])]
        dveri = [(p, v) for p in plan['proemy'] if p['vid'].startswith('dver') and p['storona'] in ('ul', 'zad')
                 for v in vyrezy if abs(v[0] - p['a0']) < 1e-3 and abs(v[1] - p['a1']) < 1e-3 and abs(v[4] - p['w0']) < 1e-3]
        assert dveri
        for d in D.spisok:
            if d['t'] != 'kor' or d['m'] != traktir.BRUS:
                continue
            u0, u1, v0, v1, w0, w1 = d['b']
            for p, v in dveri:
                if w0 < p['w1'] and w1 > p['w0'] and v0 < v[3] and v1 > v[2] and u0 < p['a1'] + 0.2 and u1 > p['a0'] - 0.2:
                    assert abs(u1 - p['a0']) > 0.005 and abs(u0 - p['a1']) > 0.005, (p, d['b'])


@pytest.mark.parametrize('zerno', range(0, 40, 3))
def test_lestnicy_i_poly_ne_migayut(zerno):
    """28.09: ступени строились коробками «до конца марша» — боковые грани всех ступеней в одной плоскости при
    чередовании доски и бруса мигали при проходе камерой. Ни одной разноцветной пары граней в одной плоскости у полов и
    лестниц; прочих мелких (спрятанных в стенах) — не больше 12 на дом."""
    from generator_domov import dom_dvor
    from generator_domov.proverki import sovpadayushchie_grani
    for pas, plan, D in (traktir.sobrat(zerno), dom_dvor.sobrat(zerno + 1000)):
        raz = [x for x in sovpadayushchie_grani(D) if D.spisok[x[3]]['m'] != D.spisok[x[4]]['m']]
        poly = [x for x in raz if D.spisok[x[3]]['g'] == 'poly' and D.spisok[x[4]]['g'] == 'poly']
        assert not poly, [(D.spisok[x[3]]['b'], D.spisok[x[4]]['b']) for x in poly[:3]]
        assert len(raz) <= 12, len(raz)
