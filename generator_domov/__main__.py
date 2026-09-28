# -*- coding: utf-8 -*-
"""python -m generator_domov dom <семейство> <зерно> [--kompoz=naves|galereya|ugol|pristrojka] [--vyhod=папка] —
паспорт, план, детали и лист дома (без --kompoz композицию выбирает зерно)."""
import json
import os
import sys

from . import traktir
from .list_doma import list_
from .proverki import proverit

SEMEJSTVA = {'m-traktir-masterskaya': traktir.sobrat}


def dom(semejstvo, zerno, vyhod, kompoz=None):
    os.makedirs(vyhod, exist_ok=True)
    pasport, plan, D = SEMEJSTVA[semejstvo](int(zerno), kompoz)
    pr = proverit(pasport, plan, D)
    imya = '%s-%s' % (semejstvo, zerno) + ('-' + kompoz if kompoz else '')
    json.dump(pasport, open(os.path.join(vyhod, imya + '.pasport.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(plan, open(os.path.join(vyhod, imya + '.plan.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(D.v_json(), open(os.path.join(vyhod, imya + '.detali.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(pr, open(os.path.join(vyhod, imya + '.proverki.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    list_(pasport, plan, os.path.join(vyhod, imya + '.list.jpg'))
    ok = all(x['ok'] for x in pr)
    print('%s: деталей %d, %s, проверки %s' % (imya, len(D.spisok), D.po_gruppam(),
                                               'все зелёные' if ok else 'КРАСНЫЕ: ' + '; '.join(x['chto'] for x in pr if not x['ok'])))
    return ok


if __name__ == '__main__':
    a = sys.argv[1:]
    vyhod = next((x[len('--vyhod='):] for x in a if x.startswith('--vyhod=')), 'rab/generator')
    kompoz = next((x[len('--kompoz='):] for x in a if x.startswith('--kompoz=')), None)
    a = [x for x in a if not x.startswith('--')]
    if a and a[0] == 'dom':
        sys.exit(0 if dom(a[1], a[2], vyhod, kompoz) else 1)
    print(__doc__)
