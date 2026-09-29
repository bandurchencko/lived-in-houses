# -*- coding: utf-8 -*-
"""Тесты семейства «дом с двором»: то же зерно — тот же дом; проверки зелёные на зёрнах и всех выразительных частях;
сторона просвета свободна (Астра 28.09: «сохраняя просвет к воде между №12 и №17»); сад — к соседу."""
import json

import pytest

from generator_domov import dom_dvor
from generator_domov.proverki import proverit


def test_to_zhe_zerno():
    a = dom_dvor.sobrat(1717, 'krylco', ['zad'])[2].v_json()
    b = dom_dvor.sobrat(1717, 'krylco', ['zad'])[2].v_json()
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


@pytest.mark.parametrize('chast', dom_dvor.CHASTI)
@pytest.mark.parametrize('zerno', range(0, 25))
def test_proverki(chast, zerno):
    pas, plan, D = dom_dvor.sobrat(zerno, chast, ['zad', 'jug'], None, 'sev')
    krasnye = [x['chto'] for x in proverit(pas, plan, D) if not x['ok']]
    assert not krasnye, krasnye


@pytest.mark.parametrize('zerno', range(0, 20))
def test_prosvet_svoboden(zerno):
    """Ни сарая, ни заднего двора с плетнём на стороне просвета: при просвете сзади двор не огораживается."""
    pas, plan, D = dom_dvor.sobrat(zerno, 'krylco', ['zad', 'jug'], None, 'sev')
    imena = [ch['imya'] for ch in plan['chasti']]
    assert 'задний двор' not in imena
    p = pas['parametry']
    u0, u1, v0, v1 = plan['razmery']['korpus']
    saraj = [ch['b'] for ch in plan['chasti'] if ch['imya'] == 'сарай'][0]
    # в осях генератора (до отражения) сторона «jug» мира — это u1 при s = +1 и u0 при s = −1
    if p['s'] > 0:
        assert saraj[0] < u1, 'сарай не на стороне просвета (jug = u1)'
    else:
        assert saraj[1] > u0, 'сарай не на стороне просвета (jug мира = u0 генератора)'


def test_sad_k_sosedu():
    for z in range(10):
        pas, plan, D = dom_dvor.sobrat(z, 'sad', [], None, 'jug')
        sad = [ch['b'] for ch in plan['chasti'] if ch['imya'] == 'сад'][0]
        u0, u1 = plan['razmery']['korpus'][:2]
        s = pas['parametry']['s']
        # сад мира — сторона jug: в осях генератора у s = +1 это правее u1, у s = −1 — левее u0
        assert (sad[0] >= u1 - 0.01) if s > 0 else (sad[1] <= u0 + 0.01)


def test_saraj_ne_v_proseve():
    """Сарай — только на свободной стороне; если в просвете все стороны, сарая нет (пара №20–21: зад и бок №20 — к №19)."""
    for z in range(10):
        pas, plan, D = dom_dvor.sobrat(z, 'masterskaya', ['jug', 'zad'], None, 'sev')
        assert [ch for ch in plan['chasti'] if ch['imya'] == 'сарай'], 'сарай на свободном боку есть'
        pas, plan, D = dom_dvor.sobrat(z, 'masterskaya', ['jug', 'zad', 'sev'], None, 'sev')
        assert not [ch for ch in plan['chasti'] if ch['imya'] == 'сарай'], 'все стороны в просвете — сарая нет'


@pytest.mark.parametrize('chast', dom_dvor.CHASTI)
def test_krovlya_nad_stenoj(chast):
    """Камыш у лица стены выше её верха (28.09: нижняя грань была положе среднего уклона — кремовая стена прорезала кровлю
    светлой полосой-«поясом»); переломы мягкие — соседние грани различаются не больше чем на 6°; щипец внутри толщи."""
    for z in range(15):
        pas, plan, D = dom_dvor.sobrat(z, chast, [], None, 'jug')
        p = pas['parametry']
        u0, u1, v0, v1 = plan['razmery']['korpus']
        EV = plan['razmery']['EV']
        prof = dom_dvor._profil_krovli(p, v0, v1, EV)
        for v in (v0, v1):
            assert dom_dvor.w_krovli(prof, v0, v1, v) >= EV + 0.1
        ug = prof['ugly']
        assert all(0 < b - a <= 6.0 for a, b in zip(ug, ug[1:]))
        plity = [d for d in D.spisok if d['t'] == 'plita' and d['g'] == 'krysha' and 'uv_v' in d]
        assert len(plity) == 8, 'по четыре грани на скат, со сплошной развёрткой'


@pytest.mark.parametrize('chast, osoboe, chast_imya', [('masterskaya', {'konyushnya': True}, 'конюшня'),
                                                       ('sad', {'ulya': 3}, 'ульи'),
                                                       ('krylco', {'kuryatnik': True}, 'птичник')])
def test_osobye_detali_dvora(chast, osoboe, chast_imya):
    """Особые детали по месту (улица Колыбели, 28.09): конюшня на навесе мастерской, ульи в саду, птичник в заднем
    дворе — встают, дом проходит проверки; без них дом прежний."""
    pas, plan, D = dom_dvor.sobrat(1414, chast, [], None, 'jug' if chast != 'krylco' else None, 'kolybel', None, osoboe)
    assert any(ch['imya'] == chast_imya for ch in plan['chasti'])
    assert all(x['ok'] for x in proverit(pas, plan, D))
    pas0, plan0, D0 = dom_dvor.sobrat(1414, chast, [], None, 'jug' if chast != 'krylco' else None, 'kolybel')
    assert not any(ch['imya'] == chast_imya for ch in plan0['chasti'])


def test_lezhen_ne_peregorazhivaet_dver():
    """Лежень фахверка (и лежень облика Мангалы) идёт по стене, но не поперёк двери: в дом можно войти с улицы
    (29.09, проход по улице: брус на высоте колена стоял поперёк входа у домов без крыльца)."""
    for stil in ('kolybel', 'mangala'):
        for zerno in range(1, 25):
            for chast in ('krylco', 'sad', 'masterskaya'):
                pas, plan, D = dom_dvor.sobrat(zerno, chast, [], None, None, stil)
                p = pas['parametry']
                v0 = plan['razmery']['korpus'][2]
                dveri = [(pr['a0'], pr['a1']) for pr in plan['proemy'] if pr['storona'] == 'ul' and pr['vid'].startswith('dver')]
                if p['s'] < 0:
                    dveri = [(dom_dvor.SU_D - a1, dom_dvor.SU_D - a0) for a0, a1 in dveri]
                for d in D.spisok:
                    if d['t'] != 'brus' or d['g'] != 'obolochka':
                        continue
                    (u1, v1_, w1), (u2, v2_, w2) = d['p1'], d['p2']
                    if abs(w1 - w2) > 1e-6 or not (p['P'] + 0.05 < w1 < p['P'] + 2.0) or abs(v1_ - v2_) > 1e-6:
                        continue
                    if abs(v1_ - (v0 - 0.04)) > 0.02:
                        continue
                    lo, hi = sorted((u1, u2))
                    for a0, a1 in dveri:
                        assert hi <= a0 + 0.02 or lo >= a1 - 0.02, (stil, zerno, chast, (lo, hi), (a0, a1), w1)
