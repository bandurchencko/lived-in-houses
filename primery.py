# -*- coding: utf-8 -*-
"""Build the example houses for the browser viewer: docs/glb/*.glb + docs/glb/manifest.json.

    python primery.py

Examples (seeds chosen with our art-direction assistant): the tavern with forge — seed 13 (gallery) is the cover, then
7 (annex) and 4 (corner); thatched houses with a yard — porch, garden, workshop; one red-stone house with a garden.
"""
import json
import os

from generator_domov import dom_dvor, traktir
from generator_domov.eksport_glb import dom_v_glb
from generator_domov.proverki import proverit

PAPKA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs', 'glb')

PRIMERY = [
    # (file, title EN, title RU, builder)
    ('tavern-13-gallery', 'Tavern with forge · seed 13 · gallery', 'Трактир с кузницей · зерно 13 · галерея',
     lambda: (traktir.sobrat(13, 'galereya'), 'mangala')),
    ('tavern-7-annex', 'Tavern with forge · seed 7 · annex', 'Трактир с кузницей · зерно 7 · пристройка',
     lambda: (traktir.sobrat(7, None), 'mangala')),
    ('tavern-4-corner', 'Tavern with forge · seed 4 · corner', 'Трактир с кузницей · зерно 4 · угол',
     lambda: (traktir.sobrat(4, None), 'mangala')),
    ('garden-house-1818', 'Thatched garden house · seed 1818', 'Садовый дом под камышом · зерно 1818',
     lambda: (dom_dvor.sobrat(1818, 'sad', [], None, 'jug', 'kolybel'), 'kolybel')),
    ('porch-house-1717', 'Thatched house with porch · seed 1717', 'Дом с крыльцом под камышом · зерно 1717',
     lambda: (dom_dvor.sobrat(1717, 'krylco', [], None, None, 'kolybel'), 'kolybel')),
    ('workshop-house-2020', 'Thatched house with workshop · seed 2020', 'Дом с мастерской под камышом · зерно 2020',
     lambda: (dom_dvor.sobrat(2020, 'masterskaya', [], None, 'sev', 'kolybel'), 'kolybel')),
    ('red-stone-garden-house-7', 'Red-stone house with garden · seed 7', 'Дом красного камня с садом · зерно 7',
     lambda: (dom_dvor.sobrat(7, 'sad', [], None, 'jug', 'mangala'), 'mangala')),
]


def main():
    os.makedirs(PAPKA, exist_ok=True)
    spisok = []
    for imya, en, ru, sobrat in PRIMERY:
        (pas, plan, D), stil = sobrat()
        pr = proverit(pas, plan, D)
        svodka = dom_v_glb(D, os.path.join(PAPKA, imya + '.glb'), stil, True, plan=plan)
        ok = all(x['ok'] for x in pr)
        spisok.append({'file': imya + '.glb', 'title': en, 'title_ru': ru, 'style': stil, 'details': len(D.spisok),
                       'triangles': sum(svodka.values()), 'checks_passed': ok,
                       'checks': [{'what': x['chto'], 'ok': x['ok']} for x in pr]})
        print('%-26s деталей %4d, треугольников %6d, проверки %s' % (imya, len(D.spisok), sum(svodka.values()),
                                                                    'зелёные' if ok else 'КРАСНЫЕ'))
    spisok += po_kartinkam()
    json.dump({'houses': spisok}, open(os.path.join(PAPKA, 'manifest.json'), 'w', encoding='utf-8'), ensure_ascii=False,
              indent=1)


def po_kartinkam():
    """Дома по картинкам (docs/obraz/<имя>/: картинка, паспорт, который прочёл ИИ) — пересобрать по паспорту."""
    from generator_domov import obraz
    koren = os.path.join(os.path.dirname(PAPKA), 'obraz')
    out = []
    podpisi = {'dom-kuznya': ('From a picture · forge-house concept', 'По картинке · рисунок дома-кузни'),
               'ulica-k-vode': ('From a picture · village street concept', 'По картинке · рисунок улицы села')}
    for imya in sorted(os.listdir(koren)) if os.path.isdir(koren) else []:
        ps = json.load(open(os.path.join(koren, imya, 'pasport.json'), encoding='utf-8'))
        pas = ps['pasport_kartinki']
        pasport, plan, D, otchet = obraz.postroit(pas, ps['zerno'])
        stil = obraz.normalizovat(pas)['stil']
        svodka = dom_v_glb(D, os.path.join(koren, imya, 'dom.glb'), stil, True, plan=plan, cveta=pas.get('cveta'))
        en, ru = podpisi.get(imya, ('From a picture · ' + imya, 'По картинке · ' + imya))
        out.append({'file': 'obraz/%s/dom.glb' % imya, 'title': en, 'title_ru': ru, 'style': stil, 'colors': pas.get('cveta'),
                    'picture': 'obraz/%s/kartinka.jpg' % imya, 'details': len(D.spisok), 'triangles': sum(svodka.values()),
                    'checks_passed': all(x['ok'] for x in otchet['proverki']),
                    'checks': [{'what': x['chto'], 'ok': x['ok']} for x in otchet['proverki']]})
        print('%-26s по картинке, зерно %d, проверки %s' % (imya, otchet['zerno'],
                                                           'зелёные' if out[-1]['checks_passed'] else 'КРАСНЫЕ'))
    return out


if __name__ == '__main__':
    main()
