# -*- coding: utf-8 -*-
"""Дом по картинке без сети: ответ ИИ разбирается, перечни и пределы держатся, дом с крайними числами проходит проверки,
цвета картинки ложатся в палитру."""
import pytest

from generator_domov import obraz
from generator_domov.eksport_glb import palitra


def test_json_iz_otveta():
    t = 'Here is the passport:\n```json\n{"semejstvo": "traktir", "stil": "mangala", "cveta": {"steny": "#ffffff"}}\n```\nDone.'
    assert obraz.iz_teksta(t)['semejstvo'] == 'traktir'
    with pytest.raises(ValueError):
        obraz.iz_teksta('no json here')


def test_normalizovat():
    p = obraz.normalizovat({'semejstvo': 'castle', 'stil': 'gothic', 'kompoz': 'galereya', 'chast': 'tower'})
    assert p['semejstvo'] == 'dom-dvor' and p['stil'] == 'mangala' and p['chast'] is None and p['kompoz'] is None
    p = obraz.normalizovat({'semejstvo': 'traktir', 'stil': 'kolybel', 'kompoz': 'ugol', 'chast': 'sad'})
    assert p['stil'] == 'mangala' and p['kompoz'] == 'ugol' and p['chast'] is None


@pytest.mark.parametrize('pas', [
    {'semejstvo': 'dom-dvor', 'stil': 'kolybel', 'chast': 'sad', 'uklon_krysy_grad': 70, 'svs_m': 2.0, 'kamen_niza_m': 0.0,
     'vysota_etazha_m': 5.0, 'shirina_m': 20.0, 'glubina_m': 2.0, 'stavni': False},
    {'semejstvo': 'dom-dvor', 'stil': 'mangala', 'chast': 'masterskaya', 'uklon_krysy_grad': 5, 'shirina_m': 7.6,
     'glubina_m': 7.2, 'stavni': True},
    {'semejstvo': 'traktir', 'kompoz': 'naves', 'uklon_krysy_grad': 40, 'svs_m': 0.3, 'kamen_niza_m': 3.0,
     'vysota_etazha_m': 2.0},
    {'semejstvo': 'traktir', 'kompoz': 'galereya'},
])
def test_kraynie_chisla_dom_prohodit(pas):
    pasport, plan, D, otchet = obraz.postroit(pas, 7)
    assert all(x['ok'] for x in otchet['proverki'])
    assert len(D.spisok) > 200


def test_prizhato_k_predelam():
    pasport, plan, D, otchet = obraz.postroit({'semejstvo': 'dom-dvor', 'stil': 'kolybel', 'chast': 'krylco',
                                              'uklon_krysy_grad': 80, 'shirina_m': 30}, 3)
    assert 'uklon_krysy_grad' in otchet['prizhato'] or 'uklon_krysy_grad' in otchet['otkat']


def test_cveta_kartinki_v_palitre():
    pal = palitra('kolybel', {'steny': '#ff0000', 'krysha': '#00ff00', 'nevedomoe': '#0000ff', 'brus': 'plohoj'})
    assert pal[1][0][:3] == (1.0, 0.0, 0.0) and pal[3][0][:3] == (0.0, 1.0, 0.0)
    assert pal[2] == palitra('kolybel')[2]


@pytest.mark.parametrize('kompoz', ['naves', 'galereya', 'ugol', 'pristrojka'])
def test_dvuskatnaya_krysha_traktira(kompoz):
    """Двускатная кровля трактира по картинке: щипцы и конёк вдоль фасада, проверки — все."""
    pasport, plan, D, otchet = obraz.postroit({'semejstvo': 'traktir', 'kompoz': kompoz, 'krysha': 'dvuskat'}, 11)
    assert pasport['parametry']['krysha'] == 'dvuskat'
    assert all(x['ok'] for x in otchet['proverki'])
    assert sum(1 for d in D.spisok if d['t'] == 'plita' and d['g'] == 'krysha') >= 2


def test_valma_po_umolchaniyu():
    from generator_domov import traktir
    pas, plan, D = traktir.sobrat(13, 'galereya')
    assert pas['parametry']['krysha'] == 'valma'
