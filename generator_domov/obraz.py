# -*- coding: utf-8 -*-
"""Дом по картинке (слово владельца 28.09: «переделать в тот, которому показываешь фотографию дома, а он делает дом»).

Генератор сам картинок не смотрит — он читает паспорт. Картинку смотрят «глаза» — ИИ, который видит изображения
(Claude через Claude Code или ключ API, либо любой чат вручную): он заполняет паспорт облика по схеме — семейство,
облик, композицию или часть дома, уклон и свес крыши, камень низа, высоту этажа, размеры, ставни, цвета материалов.
Дальше генератор строит ближайший дом, который знает, — с нутром и проверками. Числа вне пределов прижимаются к краю;
если дом с числами картинки не проходит проверки, числа по одному возвращаются к зерну, пока дом не пройдёт.

    python -m generator_domov.obraz foto.jpg [--glaza=vruchnuyu|ollama|claude|api] [--zerno=N] [--vyhod=папка]
    python -m generator_domov.obraz foto.jpg --pasport=pasport.json      # паспорт уже заполнен (например, в чате)

Сам генератор ИИ и подписок не требует; «глаза» нужны только картинке. Бесплатно: `vruchnuyu` — печатает подсказку,
её вместе с картинкой вставить в любой чат с ИИ (бесплатные тоже видят картинки) и вернуть ответ; `ollama` — своя
модель на своём компьютере, без интернета. Автоматически: `claude` — Claude Code без окна (`claude -p`, подписка того,
кто запускает); `api` — Anthropic API по ключу ANTHROPIC_API_KEY (модель — LIVED_IN_HOUSES_MODEL, по умолчанию
claude-sonnet-5), центы за картинку.
"""
import base64
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request

from . import dom_dvor, traktir
from .proverki import proverit

PODSKAZKA = """You are the art director for a rule-based generator of enterable village houses. Look at the picture and
describe the house as a passport the generator can build. The generator knows two families and two styles: choose the
nearest ones even if the picture shows something else, and carry over its proportions, roof, stone base and colours.

Return ONLY one valid JSON object (no comments, no prose around it) with these fields:
- "semejstvo": "traktir" (a two-storey tavern, inn or workshop house with a forge) or "dom-dvor" (a one-storey family
  house with an attic and a yard).
- "stil": "mangala" (lime plaster, red stone lower walls, terracotta tile roof) or "kolybel" (cream clay walls, dark
  half-timbering, thick thatched roof).
- "kompoz": for "traktir" only — "galereya" (a gallery or balcony along the front), "naves" (a forge under a gabled
  canopy at the front), "ugol" (a corner terrace above the forge), "pristrojka" (a side annex); otherwise null.
- "chast": for "dom-dvor" only — "krylco" (a porch with a canopy), "sad" (a garden at the side), "masterskaya"
  (a workshop under a canopy); otherwise null.
- "krysha": for "traktir" only — "valma" (hip roof: slopes on all four sides) or "dvuskat" (gable roof: two slopes
  with triangular gable walls at the ends); "dom-dvor" always has a gable roof.
- "uklon_krysy_grad": roof pitch in degrees (tiles 20–34, thatch 38–52).
- "svs_m": eave overhang in metres (0.45–0.9).
- "kamen_niza_m": height of the stone base or of the lower stone walls in metres (0.3–1.6).
- "vysota_etazha_m": storey height in metres (2.6–3.1).
- "shirina_m" and "glubina_m": for "dom-dvor" only — width along the entrance facade (7.6–9.8) and depth (5.6–7.2)
  in metres; otherwise null.
- "stavni": true if the windows have shutters.
- "cveta": material colours as they would look in soft daylight, not in shadow, as "#rrggbb":
  {"steny": walls, "kamen": stone, "brus": timber, "krysha": roof, "stavni": shutters or doors}.
- "pochemu": one short sentence — what in the picture led to these choices."""

PORYADOK_OTKATA = ('shirina_m', 'glubina_m', 'vysota_etazha_m', 'kamen_niza_m', 'svs_m', 'uklon_krysy_grad', 'stavni')


def iz_teksta(tekst):
    """Первый объект JSON в ответе ИИ."""
    a, b = tekst.find('{'), tekst.rfind('}')
    if a < 0 or b <= a:
        raise ValueError('в ответе нет JSON: ' + tekst[:300])
    return json.loads(tekst[a:b + 1])


def glaza_claude(put, model=None):
    """Claude Code без окна: картинка копируется в пустую папку (без чужих CLAUDE.md), Claude читает её и отвечает."""
    papka = tempfile.mkdtemp(prefix='obraz-')
    imya = 'kartinka' + os.path.splitext(put)[1].lower()
    shutil.copy(put, os.path.join(papka, imya))
    zapros = PODSKAZKA + '\n\nThe picture is the file ./%s in the current folder — read it with the Read tool.' % imya
    exe = shutil.which('claude')                       # в Windows — claude.cmd; подсказка — через ввод (в ней переносы строк)
    if not exe:
        raise RuntimeError('не найден claude (Claude Code): https://claude.com/claude-code')
    cmd = [exe, '-p', '--output-format', 'text', '--allowedTools', 'Read']
    if model:
        cmd += ['--model', model]
    r = subprocess.run(cmd, cwd=papka, input=zapros, capture_output=True, text=True, encoding='utf-8', timeout=600)
    shutil.rmtree(papka, ignore_errors=True)
    if r.returncode != 0:
        raise RuntimeError('claude -p: %s' % (r.stderr or r.stdout)[:500])
    return iz_teksta(r.stdout)


def glaza_api(put, model=None):
    """Anthropic API по ключу ANTHROPIC_API_KEY."""
    kl = os.environ.get('ANTHROPIC_API_KEY')
    if not kl:
        raise RuntimeError('нет ANTHROPIC_API_KEY')
    ext = os.path.splitext(put)[1].lower().lstrip('.')
    media = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png', 'webp': 'image/webp', 'gif': 'image/gif'}[ext]
    telo = {'model': model or os.environ.get('LIVED_IN_HOUSES_MODEL', 'claude-sonnet-5'), 'max_tokens': 1500,
            'messages': [{'role': 'user', 'content': [
                {'type': 'image', 'source': {'type': 'base64', 'media_type': media,
                                             'data': base64.b64encode(open(put, 'rb').read()).decode()}},
                {'type': 'text', 'text': PODSKAZKA}]}]}
    z = urllib.request.Request('https://api.anthropic.com/v1/messages', data=json.dumps(telo).encode(),
                               headers={'x-api-key': kl, 'anthropic-version': '2023-06-01', 'content-type': 'application/json'})
    otvet = json.loads(urllib.request.urlopen(z, timeout=300).read())
    return iz_teksta(''.join(c.get('text', '') for c in otvet['content']))


def glaza_ollama(put, model=None):
    """Бесплатно и без интернета: своя модель, видящая картинки, через Ollama (http://localhost:11434). Модель —
    LIVED_IN_HOUSES_OLLAMA (по умолчанию qwen2.5vl:7b; поставить: `ollama pull qwen2.5vl:7b`)."""
    telo = {'model': model or os.environ.get('LIVED_IN_HOUSES_OLLAMA', 'qwen2.5vl:7b'), 'stream': False, 'format': 'json',
            'options': {'temperature': 0.2},
            'messages': [{'role': 'user', 'content': PODSKAZKA,
                          'images': [base64.b64encode(open(put, 'rb').read()).decode()]}]}
    z = urllib.request.Request(os.environ.get('OLLAMA_HOST', 'http://localhost:11434').rstrip('/') + '/api/chat',
                               data=json.dumps(telo).encode(), headers={'content-type': 'application/json'})
    otvet = json.loads(urllib.request.urlopen(z, timeout=600).read())
    return iz_teksta(otvet['message']['content'])


def glaza_vruchnuyu(put):
    print('Вставьте в любой чат с ИИ картинку %s и эту подсказку, ответ (JSON) вставьте сюда и закройте ввод '
          '(Ctrl+Z, Enter в Windows; Ctrl+D в Linux и macOS):\n\n%s\n' % (put, PODSKAZKA), file=sys.stderr)
    return iz_teksta(sys.stdin.read())


def normalizovat(pas):
    """Паспорт с картинки → проверенные значения (перечни — из известных генератору)."""
    p = dict(pas)
    if p.get('semejstvo') not in ('traktir', 'dom-dvor'):
        p['semejstvo'] = 'dom-dvor'
    if p.get('stil') not in dom_dvor.STILI:
        p['stil'] = 'mangala'
    if p['semejstvo'] == 'traktir':
        p['stil'] = 'mangala'                                   # трактир-кузня пока только в облике красного камня
        if p.get('kompoz') not in traktir.KOMPOZ:
            p['kompoz'] = None
        if p.get('krysha') not in traktir.KRYSHI:
            p['krysha'] = None
        p['chast'] = None
    else:
        if p.get('chast') not in dom_dvor.CHASTI:
            p['chast'] = None
        p['kompoz'] = None
        p['krysha'] = None
    return p


def zerno_kartinki(put):
    """Одна и та же картинка — одно и то же зерно (дом повторяется)."""
    return int(hashlib.sha1(open(put, 'rb').read()).hexdigest()[:6], 16) % 100000


def postroit(pas, zerno):
    """Дом по паспорту картинки. Не прошёл проверки — числа по одному обратно к зерну; не помогло — соседние зёрна.
    → (паспорт дома, план, детали, отчёт)."""
    pas = normalizovat(pas)
    obraz = {k: pas.get(k) for k in PORYADOK_OTKATA if pas.get(k) is not None}

    def sobrat(z, ob):
        if pas['semejstvo'] == 'traktir':
            return traktir.sobrat(z, pas.get('kompoz'), ob, pas.get('krysha'))
        chast = pas.get('chast')
        return dom_dvor.sobrat(z, chast, [], None, 'jug' if chast == 'sad' else None, pas['stil'], ob)

    otkat = []
    for z in [zerno] + [zerno + k for k in range(1, 12)]:
        ob = dict(obraz)
        otkat = []
        while True:
            pasport, plan, D = sobrat(z, ob)
            pr = proverit(pasport, plan, D)
            if all(x['ok'] for x in pr):
                return pasport, plan, D, {'zerno': z, 'otkat': otkat, 'proverki': pr,
                                          'prizhato': pasport['parametry'].get('obraz_prizhato', [])
                                          if 'parametry' in pasport else []}
            ostalos = [k for k in PORYADOK_OTKATA if k in ob]
            if not ostalos:
                break
            otkat.append(ostalos[0])
            del ob[ostalos[0]]
    raise RuntimeError('дом с этим паспортом не проходит проверки ни на одном из 12 зёрен')


def main(a):
    from .eksport_glb import dom_v_glb
    opc = dict(x[2:].split('=', 1) for x in a if x.startswith('--') and '=' in x)
    poz = [x for x in a if not x.startswith('--')]
    put = poz[0]
    imya = os.path.splitext(os.path.basename(put))[0]
    vyhod = opc.get('vyhod', os.path.join('rab', 'obraz', imya))
    os.makedirs(vyhod, exist_ok=True)
    if opc.get('pasport'):
        pas = json.load(open(opc['pasport'], encoding='utf-8'))
    else:
        glaza = opc.get('glaza', 'claude')
        pas = {'claude': glaza_claude, 'api': glaza_api, 'ollama': glaza_ollama}.get(glaza, glaza_vruchnuyu)(put)
    json.dump(pas, open(os.path.join(vyhod, 'pasport-kartinki.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    zerno = int(opc['zerno']) if opc.get('zerno') else zerno_kartinki(put)
    pasport, plan, D, otchet = postroit(pas, zerno)
    stil = normalizovat(pas)['stil']
    glb = os.path.join(vyhod, imya + '-dom.glb')
    svodka = dom_v_glb(D, glb, stil, True, plan=plan, cveta=pas.get('cveta'))
    json.dump({'kartinka': os.path.abspath(put), 'pasport_kartinki': pas, 'zerno': otchet['zerno'],
               'otkat_k_zernu': otchet['otkat'], 'prizhato_k_predelam': otchet['prizhato'],
               'proverki': [{'chto': x['chto'], 'ok': x['ok']} for x in otchet['proverki']],
               'treugolnikov': sum(svodka.values()), 'glb': glb},
              open(os.path.join(vyhod, 'otchet.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('%s → %s: %s %s, зерно %d, проверки %d/%d%s%s' % (
        put, glb, pas.get('semejstvo'), pas.get('kompoz') or pas.get('chast') or '', otchet['zerno'],
        sum(x['ok'] for x in otchet['proverki']), len(otchet['proverki']),
        ('; к зерну вернулись: ' + ', '.join(otchet['otkat'])) if otchet['otkat'] else '',
        ('; прижаты к пределам: ' + ', '.join(otchet['prizhato'])) if otchet['prizhato'] else ''))
    if pas.get('pochemu'):
        print('почему:', pas['pochemu'])
    return glb


if __name__ == '__main__':
    main(sys.argv[1:])
