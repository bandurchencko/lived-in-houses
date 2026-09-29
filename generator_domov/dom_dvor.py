# -*- coding: utf-8 -*-
"""Семейство «дом с двором» — второе семейство генератора (Астра 28.09, разбор трёх композиций трактира: «дальше — дом с
двором. Проверять на паре №17–18, общий двор (−2375, −2690). Три правила: входы обращены к общему месту; у каждого дома
своя выразительная часть — крыльцо, сад или мастерская; хозяйственные постройки и зелень связывают двор, сохраняя просвет
к воде между №12 и №17. Для Колыбели брать её кремовую штукатурку, тёмное дерево и толстые крыши: переносить устройство
генератора, а облик задавать местный»).

Устройство то же, что у трактира: паспорт → план этажа → детали без движка по группам → проверки. Облик Колыбели —
места материалов те же (0 камень цоколя, 1 штукатурка, 2 тёмный брус, 3 кровля…), в движке им дают материалы Колыбели
(кремовая глина, тёмное дерево, камыш). Дом — одна изба с чердаком: горница с печью и «красным углом» (стол, лавки по
стенам), спальня, кладовая; фахверк тёмным брусом по всем стенам и щипцам; толстая камышовая кровля; вход — к общему
двору (сторона v0). Двор: сарай, поленница, грядки, плетень за домом; выразительная часть — крыльцо, сад или мастерская;
сторона просвета (к воде) остаётся свободной.

Оси — как у трактира: u вдоль фасада входа, v от входа вглубь, w вверх; слот SU_D × SV_D, дом — посередине.

Облик задаётся отдельно от устройства (Астра 28.09, генератор поселений: «значения стиля отделить от композиционного
алгоритма»): stil='kolybel' — камыш с мягким переломом, фахверк, кремовая глина; stil='mangala' — двускатная черепица
положе (жильё — не вальма трактира: «все дома не превращать в уменьшенный трактир»), красное каменное основание выше,
перемычки над проёмами и выпуски стропил вместо фахверка, навесы крылец под черепицей. Материалы — по местам SLOTY земли.
"""
STILI = ('kolybel', 'mangala')
import math
import random

from .detali import Detali, zerkalo_detalej
from .stil_mangala import (BRUS, CHER, CVET, DOSKI, KAM, KRAS, MOSH, SHT, STEK, STIL, TKAN, TRAV, UGLI, ZHEL)
from .traktir import (Rama, _dveri, _kamen_zhivoj, _krovat, _kryuchki, _peresek2, _podokonnik, _stol, _sunduk, _svobodno,
                      sn)

SU_D, SV_D = 16.0, 14.0
T, TV = 0.45, 0.16
CHASTI = ('krylco', 'sad', 'masterskaya')
IMENA_CHASTEJ = {'krylco': 'крыльцо с навесом к общему двору', 'sad': 'сад сбоку', 'masterskaya': 'мастерская под навесом'}


# облик с картинки (obraz.py): поле паспорта → (параметр, мин, макс); пределы — там, где проверки дома проходят
PREDELY_OBRAZA = {'shirina_m': ('Wb', 7.6, 9.8), 'glubina_m': ('Db', 5.6, 7.2), 'vysota_etazha_m': ('H1', 2.6, 3.1),
                  'svs_m': ('svs', 0.45, 0.9), 'kamen_niza_m': ('cokol', 0.3, 1.1)}
UKLON_OBRAZA = {'kolybel': (38.0, 52.0), 'mangala': (20.0, 34.0)}


def primenit_obraz(p, obraz, predely, uklon):
    """Числа облика с картинки → параметры дома, в пределах (что вне — прижимается к краю). → (p, что прижато)."""
    prizhato = []
    for pole, (kl, lo, hi) in predely.items():
        x = obraz.get(pole)
        if x is None:
            continue
        x = float(x)
        if not lo <= x <= hi:
            prizhato.append(pole)
        p[kl] = sn(min(hi, max(lo, x)))
    x = obraz.get('uklon_krysy_grad')
    if x is not None:
        lo, hi = uklon
        if not lo <= float(x) <= hi:
            prizhato.append('uklon_krysy_grad')
        p['uklon'] = round(min(hi, max(lo, float(x))), 1)
    if obraz.get('stavni') is not None:
        p['stavni'] = bool(obraz['stavni'])
    return p, prizhato


def parametry(zerno, chast=None, prosvet=None, sad_k=None, stil='kolybel', obraz=None):
    r = random.Random(zerno * 7919 + 17)
    p = {'zerno': zerno, 's': 1 if r.random() < 0.5 else -1}
    p['Wb'] = sn(r.uniform(8.0, 9.2))
    p['Db'] = sn(r.uniform(6.0, 6.8))
    p['P'] = sn(r.uniform(0.35, 0.5))
    p['H1'] = sn(r.uniform(2.7, 2.9))
    p['uklon'] = round(r.uniform(42.0, 48.0), 1)          # камыш — круче черепицы
    p['svs'] = sn(r.uniform(0.55, 0.75))
    p['fronton'] = sn(r.uniform(0.35, 0.5))               # вынос кровли за щипец
    p['tolshchina'] = 0.38                                # толстая кровля (камыш)
    p['cokol'] = sn(r.uniform(0.55, 0.8))                 # камень низа над землёй
    p['stavni'] = r.random() < 0.8
    p['zerno_melochej'] = r.randrange(1 << 30)
    p['chast'] = chast or CHASTI[r.randrange(len(CHASTI))]
    p['prosvet'] = list(prosvet or [])                    # стороны, которые держим свободными (к воде): 'sev'|'jug'|'zad'
    p['sad_k'] = sad_k                                    # сторона выразительной части (к соседу и общему двору): 'sev'|'jug'|None
    p['u0'] = sn(SU_D / 2.0 - p['Wb'] / 2.0)
    p['u1'] = sn(p['u0'] + p['Wb'])
    p['v0'] = sn(SV_D / 2.0 - p['Db'] / 2.0)
    p['v1'] = sn(p['v0'] + p['Db'])
    p['stil'] = stil
    if stil == 'mangala':                      # те же вытяжки зерна — в диапазоны облика Мангалы (stil_mangala.STIL)
        p['uklon'] = round(p['uklon'] - 18.0, 1)             # черепица 24–30°
        p['tolshchina'] = 0.16
        p['cokol'] = sn(p['cokol'] + 0.2)                     # красное основание 0,75–1,0
    if obraz:
        p, p['obraz_prizhato'] = primenit_obraz(p, obraz, PREDELY_OBRAZA, UKLON_OBRAZA[stil])
        p['u0'] = sn(SU_D / 2.0 - p['Wb'] / 2.0)
        p['u1'] = sn(p['u0'] + p['Wb'])
        p['v0'] = sn(SV_D / 2.0 - p['Db'] / 2.0)
        p['v1'] = sn(p['v0'] + p['Db'])
    return p


def sobrat(zerno, chast=None, prosvet=None, zemlya=None, sad_k=None, stil='kolybel', obraz=None, osoboe=None):
    """→ (паспорт, план, детали). zemlya(u, v) — высота земли относительно основания дома (для вещей двора); без неё — 0.
    stil — облик земли ('kolybel' | 'mangala'); obraz — числа облика с картинки (obraz.py), в пределах PREDELY_OBRAZA."""
    p = parametry(zerno, chast, prosvet, sad_k, stil, obraz)
    # особые детали двора по месту (улица Колыбели, Астра 28.09): {'konyushnya': True} — навес мастерской под конюшню,
    # {'ulya': N} — ульи в глубине сада, {'kuryatnik': True} — птичник в заднем дворе; своё зерно — остальное не сдвигается
    p['osoboe'] = dict(osoboe or {})
    mg = stil == 'mangala'
    r = random.Random(p['zerno_melochej'])
    D = Detali()
    zh = zemlya or (lambda u, v: 0.0)
    u0, u1, v0, v1, P = p['u0'], p['u1'], p['v0'], p['v1'], p['P']
    H1 = p['H1']
    F1 = P + H1                                  # потолок
    EV = F1 + 0.85                               # верх обвязки — карниз: подкосная стенка чердака 0,85 м
    KR = p['cokol']
    tg = math.tan(math.radians(p['uklon']))
    ui0, ui1, vi0, vi1 = u0 + T, u1 - T, v0 + T, v1 - T
    plan = {'semejstvo': 'dom-dvor', 'etazhi': [], 'proemy': [], 'lestnicy': [], 'ochagi': [], 'vnutr_dveri': [], 'chasti': [],
            'svyazi': [['ulica', 'dvor']], 'vidy': [], 'derevya': [], 'rasteniya': [], 'tropy': []}

    # ---------------- план ----------------
    pu = sn(ui0 + (ui1 - ui0) * 0.58)
    kv = sn(vi0 + (vi1 - vi0) * 0.45)
    gor = {'id': 'gornica', 'imya': 'горница', 'b': [ui0, pu - TV / 2, vi0, vi1]}
    kla = {'id': 'kladovaya', 'imya': 'кладовая', 'b': [pu + TV / 2, ui1, vi0, kv - TV / 2]}
    spa = {'id': 'spalnya', 'imya': 'спальня', 'b': [pu + TV / 2, ui1, kv + TV / 2, vi1]}
    niz = {'w_pola': P, 'komnaty': [gor, kla, spa], 'dveri': [], 'okna': []}
    dv_u1 = sn(pu - TV / 2 - 0.35)
    dv_u0 = sn(dv_u1 - 1.2)

    # ---------------- проёмы ----------------
    pr = []

    def proem(st, a0, a1, w0, w1, vid):
        pr.append((st, round(a0, 3), round(a1, 3), round(w0, 3), round(w1, 3), vid))
    proem('ul', dv_u0, dv_u1, P, P + 2.2, 'dver_vhod')
    okw = sn(r.uniform(0.6, 0.8))
    okh = sn(r.uniform(0.9, 1.1))
    sill = sn(P + 0.9)
    # горница: окно на фасаде у «красного угла» и два в боковой стене; спальня — в задней и боковой; кладовая — малое
    if dv_u0 - ui0 >= okw + 0.8:
        c = ui0 + (dv_u0 - ui0) / 2.0
        proem('ul', c - okw / 2, c + okw / 2, sill, sill + okh, 'okno')
    for c in (vi0 + (vi1 - vi0) * 0.28, vi0 + (vi1 - vi0) * 0.72):
        proem('sev', c - okw / 2, c + okw / 2, sill, sill + okh, 'okno')
    c = (pu + ui1) / 2.0
    proem('zad', c - okw / 2, c + okw / 2, sill, sill + okh, 'okno')
    c = (kv + vi1) / 2.0
    proem('jug', c - okw / 2, c + okw / 2, sill, sill + okh, 'okno')
    c = (vi0 + kv) / 2.0
    proem('jug', c - 0.25, c + 0.25, P + 1.3, P + 1.75, 'okno_malo')
    c = (pu + TV / 2 + ui1) / 2.0
    proem('ul', c - 0.3, c + 0.3, P + 1.15, P + 1.8, 'okno_malo')
    # окна чердака в щипцах
    for st in ('sev', 'jug'):
        vc = (v0 + v1) / 2.0
        proem(st, vc - 0.3, vc + 0.3, EV + 0.55, EV + 1.15, 'okno_cherdak')
    plan['proemy'] = [{'storona': s_, 'a0': a0, 'a1': a1, 'w0': w0, 'w1': w1, 'vid': vid} for (s_, a0, a1, w0, w1, vid) in pr]

    def vyrezy(storona):
        out = []
        for (st, a0, a1, w0, w1, vid) in pr:
            if st != storona:
                continue
            if st in ('ul', 'zad'):
                vv = (v0 - 0.3, v0 + T + 0.3) if st == 'ul' else (v1 - T - 0.3, v1 + 0.3)
                out.append([a0, a1, vv[0], vv[1], w0, w1])
            else:
                uu = (u0 - 0.3, u0 + T + 0.3) if st == 'sev' else (u1 - T - 0.3, u1 + 0.3)
                out.append([uu[0], uu[1], a0, a1, w0, w1])
        return out

    # ---------------- стены: камень низа, кремовая глина выше, щипцы ----------------
    steny = {'ul': [u0, u1, v0, v0 + T], 'zad': [u0, u1, v1 - T, v1], 'sev': [u0, u0 + T, v0 + T, v1 - T],
             'jug': [u1 - T, u1, v0 + T, v1 - T]}
    for st, (a0, a1, b0, b1) in steny.items():
        vy = vyrezy(st)
        D.stena('obolochka', KAM, [a0, a1, b0, b1, 0.0, KR], vy)
        D.stena('obolochka', SHT, [a0, a1, b0, b1, KR, EV], vy)
    # живой камень цоколя: крупные угловые камни, неровный верх, выступы (Астра 28.09, вечер: «объёмный камень») —
    # своим зерном, чтобы остальное в доме не сдвигалось
    _kamen_zhivoj(D, random.Random(p['zerno_melochej'] + 202), u0, u1, v0, v1, KR, pr)
    prof = _profil_pryamoj(p, v0, v1, EV) if mg else _profil_krovli(p, v0, v1, EV)
    WR = prof['WR']
    vc = (v0 + v1) / 2.0
    # щипец — под верхом кровли внутри её толщи (камыш 0,3; тонкая черепица 0,15) по профилю ската
    sv_, ot_ = prof['sv'], (0.15 if mg else 0.3)
    pravo = [(v1 + sv_ - d, w - ot_) for (d, w) in prof['tochki'] if sv_ < d < prof['R'] - 1e-6 and w - ot_ > EV]
    levo = [(v0 - sv_ + d, w - ot_) for (d, w) in reversed(prof['tochki']) if sv_ < d < prof['R'] - 1e-6 and w - ot_ > EV]
    for st, (a0, a1) in (('sev', (u0, u0 + T)), ('jug', (u1 - T, u1))):
        shchipec = [(v0, EV), (v1, EV)] + pravo + [(vc, WR - ot_)] + levo
        D.profil('obolochka', SHT, shchipec, 'vw', a0, a1)
        for (s_, b0_, b1_, w0_, w1_, vid) in pr:
            if s_ == st and vid == 'okno_cherdak':
                D.kor('obolochka', STEK, a0 - 0.02, a1 + 0.02, b0_ + 0.05, b1_ - 0.05, w0_ + 0.05, w1_ - 0.05)   # тёмное стекло чердака
                lico_ = a0 - 0.05 if st == 'sev' else a1 + 0.05                  # рама с крестом — окно, а не синий квадрат
                for (p1, p2) in (((b0_, w0_), (b1_, w0_)), ((b0_, w1_), (b1_, w1_)), ((b0_, w0_), (b0_, w1_)), ((b1_, w0_), (b1_, w1_)),
                                 (((b0_ + b1_) / 2, w0_), ((b0_ + b1_) / 2, w1_)), ((b0_, (w0_ + w1_) / 2), (b1_, (w0_ + w1_) / 2))):
                    D.brus('obolochka', BRUS, (lico_, p1[0], p1[1]), (lico_, p2[0], p2[1]), 0.08, 0.07, (1, 0, 0), 0.006)
    plan['razmery'] = {'F1': F1, 'EV': EV, 'KR': KR, 'korpus': [u0, u1, v0, v1], 'EVe': round(prof['EVe'], 3), 'WR': round(WR, 3)}

    # дневной свет окон
    for i_, (st, a0, a1, w0, w1, vid) in enumerate(pr):
        if not vid.startswith('okno') or vid == 'okno_cherdak':
            continue
        c_ = (a0 + a1) / 2.0
        pt = {'ul': (c_, v0 + T + 0.8), 'zad': (c_, v1 - T - 0.8), 'sev': (u0 + T + 0.8, c_), 'jug': (u1 - T - 0.8, c_)}[st]
        D.istochnik('okno%d' % i_, pt[0], pt[1], (w0 + w1) / 2.0, 2.6, 420.0, (210, 225, 255), False)

    # окна, ставни, подоконники, фахверк
    for (st, a0, a1, w0, w1, vid) in pr:
        if vid.startswith('okno') and vid != 'okno_cherdak':
            os_, lico, znak = ('u', v0, -1) if st == 'ul' else ('u', v1, 1) if st == 'zad' else \
                ('v', u0, -1) if st == 'sev' else ('v', u1, 1)
            D.okno(os_, a0, a1, w0, w1, lico, znak, perepl=1, stavni=(p['stavni'] and vid == 'okno'), steklo=False, glub=0.28)
            _podokonnik(D, st, a0, a1, w0, u0, u1, v0, v1)
            if vid == 'okno':
                _yashchik_cvetov(D, st, a0, a1, w0, u0, u1, v0, v1)
    _dveri(D, pr, u0, u1, v0, v1, F1)
    if mg:
        _peremychki(D, u0, u1, v0, v1, KR, pr)
    else:
        _fahverk(D, u0, u1, v0, v1, KR, EV, WR, pr)

    # ---------------- полы, потолок, балки, перегородки ----------------
    D.kor('poly', DOSKI, ui0, ui1, vi0, vi1, 0.0, P, 0.004)
    D.kor('poly', DOSKI, ui0, ui1, vi0, vi1, F1, F1 + 0.12)
    x = ui0 + 0.55
    while x < ui1 - 0.2:
        D.brus('poly', BRUS, (x, vi0 - 0.1, F1 - 0.09), (x, vi1 + 0.1, F1 - 0.09), 0.16, 0.18, (1, 0, 0))
        x += 0.9
    D.brus('poly', BRUS, (ui0, vc, F1 - 0.27), (ui1, vc, F1 - 0.27), 0.26, 0.26, (0, 1, 0))                # матица
    DV = 2.1
    vy = [[pu - 0.3, pu + 0.3, vi0 + 0.45, vi0 + 1.4, P, P + DV], [pu - 0.3, pu + 0.3, kv + 0.35, kv + 1.3, P, P + DV]]
    D.stena('peregorodki', SHT, [pu - TV / 2, pu + TV / 2, vi0, vi1, P, F1], vy)
    D.stena('peregorodki', SHT, [pu + TV / 2, ui1, kv - TV / 2, kv + TV / 2, P, F1], [])
    niz['dveri'] = [{'iz': 'ulica', 'v': 'gornica', 'shir': dv_u1 - dv_u0}, {'iz': 'gornica', 'v': 'kladovaya', 'shir': 0.95},
                    {'iz': 'gornica', 'v': 'spalnya', 'shir': 0.95}]
    plan['vnutr_dveri'] = [{'etazh': 0, 'b': [pu - TV / 2, pu + TV / 2, vi0 + 0.45, vi0 + 1.4], 'v_komnatu': 1},
                           {'etazh': 0, 'b': [pu - TV / 2, pu + TV / 2, kv + 0.35, kv + 1.3], 'v_komnatu': 1}]
    plan['etazhi'] = [niz]

    # ---------------- кровля: толстый камыш, щипцы с выносом ----------------
    if mg:
        _cherepica_dvuskat(D, p, u0, u1, v0, v1, EV, prof)
    else:
        _kamysh(D, p, u0, u1, v0, v1, EV, prof)

    # ---------------- печь с трубой ----------------
    pch = (pu - TV / 2 - 1.45, pu - TV / 2 - 0.05, vi1 - 1.65, vi1 - 0.05)
    D.kor('mebel', KAM, pch[0], pch[1], pch[2], pch[3], P, P + 0.8, 0.02)
    D.stena('mebel', SHT, [pch[0], pch[1], pch[2], pch[3], P + 0.8, P + 1.75],
            [[pch[0] + 0.35, pch[1] - 0.35, pch[2] - 0.1, pch[2] + 0.45, P + 0.85, P + 1.3]])
    D.kor('mebel', ZHEL, pch[0] + 0.36, pch[1] - 0.36, pch[2] + 0.04, pch[2] + 0.5, P + 0.85, P + 1.29)       # закопчённая топка
    D.kor('mebel', KAM, pch[0] + 0.38, pch[1] - 0.38, pch[2] + 0.05, pch[2] + 0.44, P + 0.85, P + 0.87)
    for k in range(5):
        D.sfera('mebel', UGLI, pch[0] + 0.5 + k * 0.1, pch[2] + 0.2 + 0.06 * (k % 2), P + 0.9, 0.06, (1.0, 1.0, 0.45), 2)
    D.cil_os('mebel', BRUS, (pch[0] + 0.45, pch[2] + 0.3, P + 0.93), (pch[1] - 0.45, pch[2] + 0.36, P + 0.95), 0.045, 6)
    D.kor('mebel', SHT, pch[0] + 0.3, pch[1] - 0.3, pch[2] + 0.5, pch[3] - 0.2, P + 1.75, F1, 0.02)
    D.istochnik('pech', (pch[0] + pch[1]) / 2.0, pch[2] + 0.15, P + 0.93, 0.3, 70.0, (255, 130, 60), False)
    tu, tv_ = (pch[0] + pch[1]) / 2.0, min(pch[3] - 0.4, vc + 0.9)
    w_kr = w_krovli(prof, v0, v1, tv_ + 0.3) if tv_ > vc else WR
    D.kor('krysha', KAM, tu - 0.3, tu + 0.3, tv_ - 0.3, tv_ + 0.3, F1 + 0.012, max(w_kr + 0.9, WR + 0.3), 0.012)  # низ — внутри перекрытия
    D.kor('krysha', KAM, tu - 0.37, tu + 0.37, tv_ - 0.37, tv_ + 0.37, max(w_kr + 0.9, WR + 0.3), max(w_kr + 0.9, WR + 0.3) + 0.1)
    plan['ochagi'] = [{'vid': 'pech', 'b': list(pch), 'truba': True}]

    # ---------------- нутро ----------------
    _mebel_gornicy(D, r, ui0, pu, vi0, vi1, P, F1, dv_u0, dv_u1, pch)
    _mebel_spalni(D, r, spa['b'], P)
    _mebel_kladovoj(D, kla['b'], P, F1)
    D.istochnik('gornica', (ui0 + pu) / 2.0, vc, F1 - 0.5, 1.8, 480.0, (255, 215, 175), False)

    # ---------------- двор: сарай, поленница, грядки, плетень; выразительная часть ----------------
    plan['vhod'] = [dv_u0, dv_u1]
    storony = _storony_dvora(p)
    _dvor(D, r, p, u0, u1, v0, v1, P, zh, storony, plan)
    chast = p['chast']
    if chast == 'krylco':
        _krylco(D, r, u0, u1, v0, P, dv_u0, dv_u1, EV, tg, CHER if mg else DOSKI)
        plan['chasti'].append({'imya': 'крыльцо', 'etazh': 0, 'b': [dv_u0 - 1.4, dv_u1 + 1.6, v0 - 1.9, v0]})
    elif chast == 'sad':
        _sad(D, r, p, u0, u1, v0, v1, zh, storony['sad'], plan, P, EV)
    else:
        _masterskaya(D, r, p, u0, u1, v0, v1, P, zh, storony['sad'], EV, plan)
        if not p['osoboe'].get('konyushnya'):                     # у конюшни своя часть («конюшня»)
            m_ = (u1, u1 + 2.6) if storony['sad'] == 'jug' else (u0 - 2.6, u0)
            plan['chasti'].append({'imya': 'мастерская', 'etazh': 0, 'b': [m_[0], m_[1], v0 + 0.3, v1 - 0.3]})
    D.istochnik('fonar', dv_u1 + 0.3, v0 - 0.25, P + 2.0, 3.0, 300.0, (255, 196, 140), False)
    D.kor('melochi', ZHEL, dv_u1 + 0.2, dv_u1 + 0.4, v0 - 0.35, v0 - 0.15, P + 1.85, P + 2.15)
    D.kor('melochi', STEK, dv_u1 + 0.23, dv_u1 + 0.37, v0 - 0.32, v0 - 0.18, P + 1.88, P + 2.12)
    # лавка у стены у входа — на земле (была на высоте пола, ≈1,1 м), до помоста крыльца
    kon = dv_u0 - (1.6 if chast == 'krylco' else 0.55 if chast == 'sad' else 0.3)
    if kon - (ui0 + 0.1) >= 1.0:
        hz = zh((ui0 + kon) / 2.0, v0 - 0.3)
        D.kor('melochi', BRUS, ui0 + 0.1, kon, v0 - 0.45, v0 - 0.12, hz + 0.42, hz + 0.48, 0.008)
        for a_ in (ui0 + 0.2, kon - 0.3):
            D.kor('melochi', BRUS, a_, a_ + 0.1, v0 - 0.42, v0 - 0.15, hz - 0.05, hz + 0.42)
    if chast == 'masterskaya':                                   # у крыльца и садового крыльца — свой помост
        D.kor('obolochka', KAM, dv_u0 - 0.4, dv_u1 + 0.4, v0 - 0.7, v0 + 0.02, 0.0, P, 0.02)              # ступень-плита у входа

    # ---------------- камеры ----------------
    dvc = (dv_u0 + dv_u1) / 2.0
    pech_pered = (pch[0] + pch[1]) / 2.0, pch[2] - 0.4
    plan['kamery'] = {
        'd-vhod': [[dvc - 2.5, v0 - 6.5, 1.7], [dvc, v0 + 1.0, 1.9]],
        'd-dvor': [[(u0 + u1) / 2.0 + 1.2, v1 + 5.4, 2.8], [(u0 + u1) / 2.0, v0 + 1.0, 2.2]],
        'd-gornica': [[dvc, vi0 + 0.5, P + 1.6], [ui0 + 0.6, vi1 - 1.0, P + 0.9]],
        'd-pech': [[ui0 + 0.8, vi0 + 0.7, P + 1.6], [pech_pered[0], pech_pered[1], P + 1.0]],
        'd-spalnya': [[pu + 0.45, kv + 0.55, P + 1.6], [ui1 - 0.4, vi1 - 0.5, P + 0.7]],
    }
    plan['vidy'] = [{'imya': 'от входа в горницу', 'ot': [dvc, vi0 + 0.5], 'na': [ui0 + 0.6, vi1 - 1.0]}]
    pas = {'semejstvo': 'dom-dvor', 'zemlya': stil, 'zerno': zerno, 'sled': [SU_D, SV_D], 'etazhi': 1, 'parametry': p,
           'chast': chast, 'chast_imya': 'конюшня под навесом' if p['osoboe'].get('konyushnya') else IMENA_CHASTEJ[chast],
           'osoboe': p['osoboe'], 'krysha': 'cherepica' if mg else 'kamysh', 'nutro': 'polnoe'}
    if p['s'] < 0:
        zerkalo_detalej(D.spisok, D.svet, SU_D)
        for k, (ot, na) in plan['kamery'].items():
            plan['kamery'][k] = [[SU_D - ot[0], ot[1], ot[2]], [SU_D - na[0], na[1], na[2]]]
        for dr in plan['derevya']:
            dr[0] = round(SU_D - dr[0], 3)
        for rs in plan['rasteniya']:
            rs[0] = round(SU_D - rs[0], 3)
            rs[4] = round(180.0 - rs[4], 1)
        for tr in plan.get('tropy', []):
            for t_ in tr:
                t_[0] = round(SU_D - t_[0], 3)
    return pas, plan, D


# ======================================================================================================================

def _storony_dvora(p):
    """Какая сторона — под сад/мастерскую, какая — под сарай; сторона просвета к воде остаётся свободной.
    Стороны в осях до отражения: 'sev' (u0), 'jug' (u1); при s = −1 дом отражается — сторона меняется местами."""
    def v_generator(st):                      # сторона в мире → в осях генератора (до отражения)
        if st in ('sev', 'jug') and p['s'] < 0:
            return 'jug' if st == 'sev' else 'sev'
        return st
    prosvet = {v_generator(x) for x in p['prosvet']}
    sk = v_generator(p.get('sad_k')) if p.get('sad_k') in ('sev', 'jug') else None
    sad = sk if sk and sk not in prosvet else next((x for x in ('jug', 'sev') if x not in prosvet), 'jug')
    drugoj = 'sev' if sad == 'jug' else 'jug'
    # у дома с крыльцом бок «к соседу» свободен — сарай туда; иначе — на другой бок или назад; не в просвет
    kand = [sad, drugoj, 'zad'] if p['chast'] == 'krylco' else [drugoj, 'zad', sad]
    saraj = next((x for x in kand if x not in prosvet), None)      # все стороны в просвете — сарая у дома нет
    return {'sad': sad, 'saraj': saraj, 'prosvet': prosvet}


def _yashchik_cvetov(D, st, a0, a1, w0, u0, u1, v0, v1):
    """Ящик с цветами под окном (как у домов Колыбели)."""
    if st == 'ul':
        D.kor('obolochka', BRUS, a0 - 0.05, a1 + 0.05, v0 - 0.3, v0 - 0.06, w0 - 0.3, w0 - 0.1, 0.01)
        for k in range(4):
            D.sfera('melochi', CVET, a0 + (a1 - a0) * (k + 0.5) / 4.0, v0 - 0.18, w0 - 0.02, 0.1, (1.0, 1.0, 0.8), 2)
    elif st == 'zad':
        D.kor('obolochka', BRUS, a0 - 0.05, a1 + 0.05, v1 + 0.06, v1 + 0.3, w0 - 0.3, w0 - 0.1, 0.01)
        for k in range(4):
            D.sfera('melochi', CVET, a0 + (a1 - a0) * (k + 0.5) / 4.0, v1 + 0.18, w0 - 0.02, 0.1, (1.0, 1.0, 0.8), 2)
    elif st == 'sev':
        D.kor('obolochka', BRUS, u0 - 0.3, u0 - 0.06, a0 - 0.05, a1 + 0.05, w0 - 0.3, w0 - 0.1, 0.01)
        for k in range(4):
            D.sfera('melochi', CVET, u0 - 0.18, a0 + (a1 - a0) * (k + 0.5) / 4.0, w0 - 0.02, 0.1, (1.0, 1.0, 0.8), 2)
    else:
        D.kor('obolochka', BRUS, u1 + 0.06, u1 + 0.3, a0 - 0.05, a1 + 0.05, w0 - 0.3, w0 - 0.1, 0.01)
        for k in range(4):
            D.sfera('melochi', CVET, u1 + 0.18, a0 + (a1 - a0) * (k + 0.5) / 4.0, w0 - 0.02, 0.1, (1.0, 1.0, 0.8), 2)


def _mimo_dverej(a_nach, a_kon, proemy, st, w_do, zazor=0.1):
    """Куски бруса вдоль стены st от a_nach до a_kon в обход проёмов, опущенных ниже w_do (двери): брус лежня на высоте
    колена поперёк двери не пускал в дом (29.09, проход по улице)."""
    kuski, a = [], a_nach
    for (d0, d1) in sorted((a0, a1) for (s_, a0, a1, w0, w1, vid) in proemy if s_ == st and w0 < w_do):
        if d0 - zazor - a > 0.05:
            kuski.append((a, d0 - zazor))
        a = max(a, d1 + zazor)
    if a_kon - a > 0.05:
        kuski.append((a, a_kon))
    return kuski


def _fahverk(D, u0, u1, v0, v1, KR, EV, WR, proemy):
    """Тёмный брус по кремовой глине (Астра: «тёмное дерево»): лежень над камнем, обвязка у карниза, стойки на углах и у
    проёмов, раскосы в широких простенках; на щипцах — стойка, ригель и раскосы."""
    def na_stene(st, a0, a1, w0, w1, shir=0.16):
        lico = {'ul': v0 - 0.04, 'zad': v1 + 0.04, 'sev': u0 - 0.04, 'jug': u1 + 0.04}[st]
        if st in ('ul', 'zad'):
            D.brus('obolochka', BRUS, (a0, lico, w0), (a1, lico, w1), 0.1, shir, (0, 1, 0))
        else:
            D.brus('obolochka', BRUS, (lico, a0, w0), (lico, a1, w1), 0.1, shir, (1, 0, 0))
    for st, (a_nach, a_kon) in (('ul', (u0, u1)), ('zad', (u0, u1)), ('sev', (v0, v1)), ('jug', (v0, v1))):
        for a_, b_ in _mimo_dverej(a_nach - 0.05, a_kon + 0.05, proemy, st, KR + 0.2):    # лежень — не поперёк двери
            na_stene(st, a_, b_, KR + 0.08, KR + 0.08, 0.2)
        # обвязка: на фасадах под скатом — ниже толстого камыша у стены (иначе выходит полосой поверх кровли)
        w_ob = EV - 0.1 if st in ('sev', 'jug') else EV - 0.72
        na_stene(st, a_nach - 0.05, a_kon + 0.05, w_ob, w_ob, 0.2)
        ok = sorted((a0, a1, w0, w1) for (s_, a0, a1, w0, w1, vid) in proemy if s_ == st and w0 < EV)
        stoiki = [a_nach + 0.08, a_kon - 0.08]
        for (a0, a1, w0, w1) in ok:
            stoiki += [a0 - 0.1, a1 + 0.1]
        stoiki = sorted(set(round(x, 3) for x in stoiki))
        for a in stoiki:
            na_stene(st, a, a, KR + 0.16, w_ob - 0.08)
        # раскосы в простенках шире 1,4 м
        for a, b in zip(stoiki, stoiki[1:]):
            if b - a < 1.4 or any(a0 < (a + b) / 2 < a1 for (a0, a1, w0, w1) in ok):
                continue
            na_stene(st, a + 0.08, b - 0.08, KR + 0.2, w_ob - 0.12, 0.13)
        # ригель под окнами
        for (a0, a1, w0, w1) in ok:
            if w0 > KR + 0.3:
                na_stene(st, a0 - 0.1, a1 + 0.1, w0 - 0.06, w0 - 0.06, 0.12)
                na_stene(st, a0 - 0.1, a1 + 0.1, w1 + 0.06, w1 + 0.06, 0.12)
    vc = (v0 + v1) / 2.0
    for st in ('sev', 'jug'):
        lico = u0 - 0.04 if st == 'sev' else u1 + 0.04
        D.brus('obolochka', BRUS, (lico, vc, EV), (lico, vc, WR - 0.3), 0.1, 0.16, (1, 0, 0))
        wr_ = EV + (WR - EV) * 0.45
        dl = ((v1 - v0) / 2.0) * 0.35                  # ригель внутри щипца с переломом
        D.brus('obolochka', BRUS, (lico, vc - dl, wr_), (lico, vc + dl, wr_), 0.1, 0.14, (1, 0, 0))
        for zn in (-1, 1):
            D.brus('obolochka', BRUS, (lico, vc + zn * ((v1 - v0) / 2.0 - 0.35), EV + 0.1), (lico, vc + zn * 0.2, wr_ - 0.05),
                   0.1, 0.12, (1, 0, 0))


ZAPAS_STENY = 0.12          # камыш над верхом стены у её лица: стена не прорезает кровлю (28.09: светлая полоса-«пояс»)


def _profil_krovli(p, v0, v1, EV):
    """Профиль ската (верх камыша) от кромки свеса к коньку — четыре грани мягким переломом: уклоны uklon−10,5 … uklon+4,5
    через 5° на равных горизонтальных долях (Астра 28.09: «перелом скатов полезен, но широкие горизонтальные полосы
    напоминают панели — ослабить пояса»). У лица стены камыш на ZAPAS_STENY выше её верха EV (прежде нижняя грань была
    положе среднего уклона, и кремовая стена прорезала кровлю светлой полосой). → {'tochki': [(d, w)] — d по горизонтали
    от кромки свеса; 'R', 'EVe' (кромка), 'WR' (конёк), 'ugly', 'sv'}."""
    sv = p['svs']
    R = sv + (v1 - v0) / 2.0
    ugly = [p['uklon'] - 3.0 + d for d in (-7.5, -2.5, 2.5, 7.5)]
    shag = R / len(ugly)
    tg_ = [math.tan(math.radians(a)) for a in ugly]
    pod, ost = 0.0, sv                   # подъём от кромки до линии стены
    for k in range(len(ugly)):
        dd = min(ost, shag)
        pod += dd * tg_[k]
        ost -= dd
        if ost <= 1e-9:
            break
    EVe = EV + ZAPAS_STENY - pod
    tochki = [(0.0, EVe)]
    for k in range(len(ugly)):
        tochki.append((shag * (k + 1), tochki[-1][1] + shag * tg_[k]))
    return {'tochki': tochki, 'R': R, 'EVe': EVe, 'WR': tochki[-1][1], 'ugly': ugly, 'sv': sv}


def _profil_pryamoj(p, v0, v1, EV):
    """Прямой скат (черепица Мангалы) с тем же правилом стены: у её лица верх кровли на ZAPAS_STENY выше EV."""
    sv = p['svs']
    R = sv + (v1 - v0) / 2.0
    tg = math.tan(math.radians(p['uklon']))
    EVe = EV + ZAPAS_STENY - sv * tg
    return {'tochki': [(0.0, EVe), (R, EVe + R * tg)], 'R': R, 'EVe': EVe, 'WR': EVe + R * tg, 'ugly': [p['uklon']],
            'sv': sv}


def _cherepica_dvuskat(D, p, u0, u1, v0, v1, EV, prof):
    """Двускатная черепичная кровля Мангалы: тонкие скаты, ряды черепицы у обоих карнизов, конёк валиком, ветровые доски
    по щипцам, подшива карнизов, выпуски стропил под свесом — ряд теней (Астра 28.09: «усиль тень под кровлей»)."""
    sv, fr, tol = p['svs'], p['fronton'], p['tolshchina']
    vc = (v0 + v1) / 2.0
    EVe, WR = prof['EVe'], prof['WR']
    a0, a1 = u0 - fr, u1 + fr
    ug = prof['ugly'][0]
    c, s_ = math.cos(math.radians(ug)), math.sin(math.radians(ug))
    tg = math.tan(math.radians(ug))
    D.plita('krysha', CHER, [(a0, v0 - sv, EVe), (a1, v0 - sv, EVe), (a1, vc, WR), (a0, vc, WR)], tol)
    D.plita('krysha', CHER, [(a1, v1 + sv, EVe), (a0, v1 + sv, EVe), (a0, vc, WR), (a1, vc, WR)], tol)
    D.cil_os('krysha', CHER, (a0 - 0.05, vc, WR + 0.06), (a1 + 0.05, vc, WR + 0.06), 0.13, 6)
    D.cherepica(v0 - sv, EVe, c, s_, -s_, c, a0 + 0.25, a1 - 0.25, ryadov=4, os_karniza='u')
    D.cherepica(v1 + sv, EVe, -c, s_, s_, c, a0 + 0.25, a1 - 0.25, ryadov=4, os_karniza='u')
    for a in (a0 + 0.04, a1 - 0.04):                                     # ветровые доски по щипцам
        for vk in (v0 - sv, v1 + sv):
            D.brus('krysha', BRUS, (a, vk, EVe - 0.12), (a, vc, WR - 0.12), 0.08, 0.26, (1, 0, 0), 0.01)
    for vk in (v0 - sv, v1 + sv):                                        # подшива карнизов
        D.brus('krysha', BRUS, (a0, vk, EVe - 0.2), (a1, vk, EVe - 0.2), 0.08, 0.26, (0, 0, 1), 0.01)
    niz = tol / c + 0.07                                                 # выпуски стропил через 0,6 м по карнизам
    for (lico, zn) in ((v0, -1), (v1, 1)):
        a = u0 + 0.35
        while a <= u1 - 0.35 + 1e-6:
            d0, d1 = -0.1, sv - 0.1
            D.brus('krysha', BRUS, (a, lico + zn * d0, EV + ZAPAS_STENY - d0 * tg - niz),
                   (a, lico + zn * d1, EV + ZAPAS_STENY - d1 * tg - niz), 0.09, 0.13, (1, 0, 0), 0.01)
            a += 0.6


def _peremychki(D, u0, u1, v0, v1, KR, proemy):
    """Мангала без фахверка: тёмные перемычки над проёмами с выносом за откосы и лежень над красным основанием."""
    def na_stene(st, a0, a1, w0, w1, shir=0.16):
        lico = {'ul': v0 - 0.04, 'zad': v1 + 0.04, 'sev': u0 - 0.04, 'jug': u1 + 0.04}[st]
        if st in ('ul', 'zad'):
            D.brus('obolochka', BRUS, (a0, lico, w0), (a1, lico, w1), 0.1, shir, (0, 1, 0))
        else:
            D.brus('obolochka', BRUS, (lico, a0, w0), (lico, a1, w1), 0.1, shir, (1, 0, 0))
    for st, (a_n, a_k) in (('ul', (u0, u1)), ('zad', (u0, u1)), ('sev', (v0, v1)), ('jug', (v0, v1))):
        for a_, b_ in _mimo_dverej(a_n - 0.05, a_k + 0.05, proemy, st, KR + 0.2):          # лежень — не поперёк двери
            na_stene(st, a_, b_, KR + 0.06, KR + 0.06, 0.12)
    for (st, a0, a1, w0, w1, vid) in proemy:
        if vid == 'okno_cherdak':
            continue
        na_stene(st, a0 - 0.22, a1 + 0.22, w1 + 0.1, w1 + 0.1, 0.2)


def w_krovli(prof, v0, v1, v):
    """Высота верха камыша над точкой v (по профилю ската ближней кромки)."""
    vc = (v0 + v1) / 2.0
    d = (v - (v0 - prof['sv'])) if v <= vc else ((v1 + prof['sv']) - v)
    pts = prof['tochki']
    for (d0, w0), (d1, w1) in zip(pts, pts[1:]):
        if d <= d1:
            t_ = max(0.0, min(1.0, (d - d0) / (d1 - d0)))
            return w0 + (w1 - w0) * t_
    return pts[-1][1]


def _kamysh(D, p, u0, u1, v0, v1, EV, prof):
    """Толстая камышовая кровля: два ската по профилю с мягким переломом, грани встык (нахлёст давал ступени-пояса),
    рисунок камыша сплошь через переломы; кромка свеса — гладкий валик по толщине камыша, чуть неровный (Астра 28.09:
    «соломенную кромку мягче и менее равномерной»), валики по торцам, приподнятый гребень с фестонами."""
    sv, fr, tol = p['svs'], p['fronton'], p['tolshchina']
    vc = (v0 + v1) / 2.0
    pts, WR, EVe = prof['tochki'], prof['WR'], prof['EVe']
    a0, a1 = u0 - fr, u1 + fr
    rr = random.Random(int(p['zerno']) * 31 + 7)
    for (vk, zn) in ((v0 - sv, 1), (v1 + sv, -1)):
        s_nak = 0.0
        normali = []
        for (d0, w0), (d1, w1) in zip(pts, pts[1:]):
            vA, vB = vk + zn * d0, vk + zn * d1
            # порядок точек — чтобы вторая ось плиты шла вверх по скату на обоих скатах (сплошная развёртка)
            ua, ub = (a0, a1) if zn > 0 else (a1, a0)
            D.plita('krysha', CHER, [(ua, vA, w0), (ub, vA, w0), (ub, vB, w1), (ua, vB, w1)], tol, uv_v=s_nak)
            dl = math.hypot(d1 - d0, w1 - w0)
            normali.append((-zn * (w1 - w0) / dl, (d1 - d0) / dl))            # нормаль грани вверх-наружу в (v, w)
            s_nak += dl
        # валик кромки: центр — середина торца нижней грани, радиус — полтолщины (чуть больше), звенья с плавным блужданием
        n1v, n1w = normali[0]
        cv_, cw_ = vk - n1v * tol / 2.0, EVe - n1w * tol / 2.0
        uzly = [a0 - 0.02]
        while uzly[-1] < a1 - 0.9:
            uzly.append(uzly[-1] + rr.uniform(0.7, 1.3))
        uzly.append(a1 + 0.02)
        rad = [tol / 2.0 * rr.uniform(1.0, 1.12) for _ in uzly]
        sdv = [(rr.uniform(0.0, 0.035), rr.uniform(-0.025, 0.015)) for _ in uzly]
        tv, tw = -zn * (pts[1][0] - pts[0][0]), -(pts[1][1] - pts[0][1])      # вниз по скату, к кромке
        tl = math.hypot(tv, tw)
        tv, tw = tv / tl, tw / tl
        for i in range(len(uzly) - 1):
            p1 = (uzly[i], cv_ + tv * sdv[i][0] + n1v * sdv[i][1], cw_ + tw * sdv[i][0] + n1w * sdv[i][1])
            p2 = (uzly[i + 1], cv_ + tv * sdv[i + 1][0] + n1v * sdv[i + 1][1], cw_ + tw * sdv[i + 1][0] + n1w * sdv[i + 1][1])
            D.cil_os('krysha', CHER, p1, p2, rad[i], 16, rad[i + 1])
        # валики по торцам (на щипцах) по серединам граней, шары в переломах и на углах
        for a in (a0, a1):
            for k_, ((d0, w0), (d1, w1)) in enumerate(zip(pts, pts[1:])):
                nv, nw = normali[k_]
                q0 = (a, vk + zn * d0 - nv * tol / 2.0, w0 - nw * tol / 2.0)
                q1 = (a, vk + zn * d1 - nv * tol / 2.0, w1 - nw * tol / 2.0)
                D.cil_os('krysha', CHER, q0, q1, tol / 2.0, 12)
                D.sfera('krysha', CHER, q0[0], q0[1], q0[2], tol / 2.0 * 1.04, (1.0, 1.0, 1.0), 2)
    # приподнятый гребень: скруглённая трапеция вдоль конька, нижние углы — на верхних гранях; фестоны по краям
    tg4 = math.tan(math.radians(prof['ugly'][-1]))
    h_kr = WR - 0.55 * tg4
    D.profil('krysha', CHER, [(vc - 0.55, h_kr - 0.05), (vc + 0.55, h_kr - 0.05), (vc + 0.28, WR + 0.3), (vc - 0.28, WR + 0.3)], 'vw',
             a0 - 0.1, a1 + 0.1, 0.06)
    x_ = a0 + 0.1
    while x_ < a1 - 0.1:
        for zn in (-1, 1):
            D.sfera('krysha', CHER, x_, vc + zn * 0.56, h_kr - 0.02, 0.2, (1.0, 0.55, 0.35), 2)
        x_ += 0.42
    # ветровые доски у щипцов под камышом — по граням
    for a in (u0 - fr + 0.05, u1 + fr - 0.05):
        for (vk, zn) in ((v0 - sv, 1), (v1 + sv, -1)):
            for (d0, w0), (d1, w1) in zip(pts, pts[1:]):
                dl = math.hypot(d1 - d0, w1 - w0)
                nv, nw = -zn * (w1 - w0) / dl, (d1 - d0) / dl
                o = tol + 0.1
                D.brus('krysha', BRUS, (a, vk + zn * d0 - nv * o, w0 - nw * o), (a, vk + zn * d1 - nv * o, w1 - nw * o),
                       0.06, 0.22, (1, 0, 0), 0.01)


def _mebel_gornicy(D, r, ui0, pu, vi0, vi1, P, F1, dv_u0, dv_u1, pch):
    """Горница: «красный угол» — стол у окон с лавками по двум стенам, полка с посудой; печь; лавка вдоль стены,
    прялка, сундук, половик."""
    pl = pu - TV / 2
    # лавки по стенам в красном углу (у боковой стены и у фасада слева от двери)
    D.kor('mebel', BRUS, ui0 + 0.02, ui0 + 0.4, vi0 + 0.05, vi1 - 1.9, P + 0.42, P + 0.48, 0.008)
    for vv in (vi0 + 0.2, vi1 - 2.1):
        D.kor('mebel', BRUS, ui0 + 0.05, ui0 + 0.35, vv, vv + 0.1, P, P + 0.42)
    if dv_u0 - ui0 > 1.0:
        D.kor('mebel', BRUS, ui0 + 0.4, dv_u0 - 0.2, vi0 + 0.02, vi0 + 0.4, P + 0.42, P + 0.48, 0.008)
    # стол в красном углу
    t_u0, t_v0 = ui0 + 0.55, vi0 + 0.55
    _stol(D, r, 'v', t_v0, t_v0 + 1.8, t_u0 + 0.43, P, lavki=(1,))
    D.kor('mebel', TKAN, t_u0 + 0.2, t_u0 + 0.66, t_v0 + 0.1, t_v0 + 1.7, P + 0.8, P + 0.806)
    # полка с посудой над лавкой у боковой стены
    D.kor('mebel', BRUS, ui0, ui0 + 0.25, vi0 + 0.6, vi0 + 2.0, P + 1.75, P + 1.8)
    for k in range(5):
        D.cil('mebel', KAM if k % 2 else ZHEL, ui0 + 0.12, vi0 + 0.75 + k * 0.28, P + 1.8, 0.07, 0.16 if k % 2 else 0.06, 8)
    # у печи — ухваты и кадка; прялка и сундук у задней стены
    D.cil('mebel', BRUS, pch[0] - 0.4, vi1 - 0.4, P, 0.25, 0.55, 12)
    for k in range(2):
        D.cil_os('mebel', ZHEL, (pch[0] - 0.12 - k * 0.12, pch[2] - 0.05, P), (pch[0] - 0.2 - k * 0.12, pch[2] - 0.1, P + 1.5), 0.012, 4)
    D.kor('mebel', BRUS, ui0 + 0.1, ui0 + 1.0, vi1 - 0.6, vi1 - 0.1, P, P + 0.5, 0.02)
    D.kor('mebel', ZHEL, ui0 + 0.08, ui0 + 1.02, vi1 - 0.62, vi1 - 0.08, P + 0.22, P + 0.26)
    D.cil('mebel', BRUS, ui0 + 1.6, vi1 - 0.9, P, 0.03, 0.75, 6)                                        # прялка
    D.cil_os('mebel', BRUS, (ui0 + 1.6, vi1 - 0.9, P + 0.75), (ui0 + 1.6, vi1 - 0.85, P + 0.75), 0.25, 14, 0.25)   # колесо
    D.kor('mebel', KRAS, (ui0 + pl) / 2.0 - 0.9, (ui0 + pl) / 2.0 + 0.9, vi0 + 2.1, vi1 - 1.9, P + 0.004, P + 0.016)   # половик
    D.kor('mebel', BRUS, pl - 0.3, pl - 0.02, vi0 + 1.6, vi1 - 1.8, P + 0.42, P + 0.48, 0.008)       # лавка у перегородки
    D.kor('mebel', KRAS, pch[0] - 0.05, pch[0] - 0.02, pch[2] + 0.2, pch[2] + 0.6, P + 1.05, P + 1.65)   # полотенце у печи
    for k in range(4):                                                                                # пучки трав на балке
        x_ = ui0 + 1.2 + k * 0.55
        D.cil_os('mebel', ZHEL, (x_, vi0 + 2.0, F1 - 0.18), (x_, vi0 + 2.0, F1 - 0.45), 0.005, 3)
        D.sfera('mebel', TRAV, x_, vi0 + 2.0, F1 - 0.55, 0.12, (0.8, 0.8, 1.4), 2)
    D.kor('mebel', BRUS, ui0 + 1.2, ui0 + 2.6, vi1 - 0.22, vi1 - 0.02, P + 1.55, P + 1.6)               # полка на задней стене
    for k in range(4):
        D.cil('mebel', KAM if k % 2 else ZHEL, ui0 + 1.35 + k * 0.35, vi1 - 0.12, P + 1.6, 0.07, 0.2 if k % 2 else 0.08, 8)
    D.kor('mebel', BRUS, ui0 + 0.02, ui0 + 0.3, vi0 + 0.02, vi0 + 0.3, P + 1.85, P + 1.9)                # полочка в красном углу
    D.kor('mebel', KRAS, ui0 + 0.02, ui0 + 0.26, vi0 + 0.02, vi0 + 0.26, P + 1.6, P + 1.85)


def _mebel_spalni(D, r, b, P):
    u0, u1, v0, v1 = b
    bb = (u1 - 1.05, u1 - 0.1, v1 - 2.1, v1 - 0.1)
    _krovat(D, bb, 'zad', P, KRAS)
    D.kor('mebel', BRUS, u0 + 0.1, u0 + 0.6, v1 - 0.9, v1 - 0.1, P, P + 0.5, 0.02)                     # сундук у стены
    D.kor('mebel', ZHEL, u0 + 0.08, u0 + 0.62, v1 - 0.92, v1 - 0.08, P + 0.22, P + 0.26)
    D.kor('mebel', TKAN, u0 + 0.4, bb[0] - 0.1, v0 + 0.5, v1 - 0.6, P + 0.004, P + 0.016)
    _kryuchki(D, r, u0, u1, v0, v1, [bb, (u0, u0 + 0.7, v1 - 1.0, v1)], P)


def _mebel_kladovoj(D, b, P, F1):
    u0, u1, v0, v1 = b
    D.kor('mebel', BRUS, u1 - 0.4, u1 - 0.05, v0 + 0.1, v1 - 0.1, P + 0.9, P + 0.95)
    D.kor('mebel', BRUS, u1 - 0.4, u1 - 0.05, v0 + 0.1, v1 - 0.1, P + 1.5, P + 1.55)
    for k in range(3):
        D.cil('mebel', KAM if k % 2 else BRUS, u1 - 0.22, v0 + 0.35 + k * 0.4, P + 0.95, 0.1, 0.25, 8)
    for k in range(2):
        D.cil('mebel', BRUS, u0 + 0.4 + k * 0.6, v1 - 0.4, P, 0.26, 0.7, 12)
    D.sfera('mebel', TKAN, u0 + 0.35, v0 + 0.4, P + 0.28, 0.28, (1.0, 1.0, 1.1), 3)


def _dvor(D, r, p, u0, u1, v0, v1, P, zh, storony, plan):
    """Двор за домом: плетень вокруг заднего двора (перед домом — открыто к общему двору), сарай с поленницей у бока,
    грядки. Сторона просвета — без сарая и плетня."""
    zv = v1 + 4.2                              # задняя кромка двора
    su = storony['saraj']
    # плетень: задняя кромка и бока заднего двора, кроме стороны просвета
    kuski = [('zad', (u0 - 1.2, u1 + 1.2)), ('sev', (v1 - 0.5, zv)), ('jug', (v1 - 0.5, zv))]
    otkryt = 'zad' in storony['prosvet']          # просвет позади дома — задний двор не огораживается
    for st, (a, b) in kuski:
        if otkryt or st in storony['prosvet']:
            continue
        _pleten(D, st, a, b, u0 - 1.2, u1 + 1.2, zv, zh)
    if not otkryt:
        plan['chasti'].append({'imya': 'задний двор', 'etazh': 0, 'b': [u0 - 1.2, u1 + 1.2, v1, zv]})
    # сарай: бревенчатый короб с односкатной камышовой кровлей у бока заднего двора
    if su is None:
        return
    if su == 'zad':
        sb = (u0 + 0.5, u0 + 3.3, zv - 2.6, zv - 0.2)
    elif su == 'sev':
        sb = (u0 - 1.1, u0 + 1.7, v1 + 1.2, v1 + 3.8)
    else:
        sb = (u1 - 1.7, u1 + 1.1, v1 + 1.2, v1 + 3.8)
    h0 = zh((sb[0] + sb[1]) / 2.0, (sb[2] + sb[3]) / 2.0)
    D.kor('obolochka', KAM, sb[0], sb[1], sb[2], sb[3], h0 - 0.3, h0 + 0.25, 0.02)
    for (a0, a1, b0, b1) in ((sb[0], sb[1], sb[2], sb[2] + 0.18), (sb[0], sb[1], sb[3] - 0.18, sb[3]),
                             (sb[0], sb[0] + 0.18, sb[2], sb[3]), (sb[1] - 0.18, sb[1], sb[2], sb[3])):
        vy = []
        if b0 == sb[2] and b1 == sb[2] + 0.18:
            c = (sb[0] + sb[1]) / 2.0
            vy = [[c - 0.55, c + 0.55, b0 - 0.1, b1 + 0.1, h0 + 0.25, h0 + 2.15]]
        D.stena('obolochka', DOSKI, [a0, a1, b0, b1, h0 + 0.25, h0 + 2.3], vy)
    w_n, w_v = h0 + 2.35, h0 + 2.95
    D.plita('krysha', CHER, [(sb[0] - 0.35, sb[2] - 0.45, w_v), (sb[1] + 0.35, sb[2] - 0.45, w_v),
                             (sb[1] + 0.35, sb[3] + 0.45, w_n), (sb[0] - 0.35, sb[3] + 0.45, w_n)], 0.3)
    plan['chasti'].append({'imya': 'сарай', 'etazh': 0, 'b': list(sb)})
    # поленница вдоль сарая, колода с топором
    for ryad in range(5):
        for j in range(max(0, int(((sb[0] + sb[1]) / 2.0 - 0.75 - sb[0] - 0.2) / 0.16))):
            uu = sb[0] + 0.2 + j * 0.16 + (0.08 if ryad % 2 else 0.0)
            D.cil_os('melochi', BRUS, (uu, sb[2] - 0.55, h0 + 0.08 + ryad * 0.14), (uu, sb[2] - 0.12, h0 + 0.08 + ryad * 0.14), 0.07, 7)
    ku, kv_ = sb[1] + 0.8, sb[2] - 0.9
    D.cil('melochi', BRUS, ku, kv_, zh(ku, kv_), 0.3, 0.55, 12)
    D.cil_os('melochi', ZHEL, (ku, kv_, zh(ku, kv_) + 0.55), (ku + 0.25, kv_ + 0.1, zh(ku, kv_) + 0.95), 0.02, 4)
    ptichnik = None
    if p.get('osoboe', {}).get('kuryatnik') and not otkryt:               # птичник — напротив сарая, на ножках, со сходнями
        pb = (u1 - 1.7, u1 - 0.3, zv - 1.5, zv - 0.4) if su != 'jug' else (u0 + 0.3, u0 + 1.7, zv - 1.5, zv - 0.4)
        if not _peresek2(pb, sb):
            ptichnik = pb
            hp = zh((pb[0] + pb[1]) / 2.0, (pb[2] + pb[3]) / 2.0)
            for (x_, y_) in ((pb[0] + 0.1, pb[2] + 0.1), (pb[1] - 0.1, pb[2] + 0.1), (pb[0] + 0.1, pb[3] - 0.1), (pb[1] - 0.1, pb[3] - 0.1)):
                D.cil('melochi', BRUS, x_, y_, hp - 0.03, 0.04, 0.5, 5)
            D.kor('melochi', DOSKI, pb[0], pb[1], pb[2], pb[3], hp + 0.45, hp + 1.35, 0.01)
            D.plita('melochi', CHER, [(pb[0] - 0.15, pb[2] - 0.2, hp + 1.55), (pb[1] + 0.15, pb[2] - 0.2, hp + 1.55),
                                      (pb[1] + 0.15, pb[3] + 0.2, hp + 1.35), (pb[0] - 0.15, pb[3] + 0.2, hp + 1.35)], 0.08)
            cx_ = (pb[0] + pb[1]) / 2.0
            D.brus('melochi', DOSKI, (cx_, pb[2] - 0.05, hp + 0.6), (cx_, pb[2] - 0.75, zh(cx_, pb[2] - 0.75) + 0.02), 0.28, 0.03,
                   (1, 0, 0), 0.004)
            plan['chasti'].append({'imya': 'птичник', 'etazh': 0, 'b': list(pb)})
    # грядки на заднем дворе (при открытом просвете — только у сарая)
    for k in range(1 if otkryt else 3):
        gu0 = u0 + 0.3 + k * 1.5 if su != 'sev' else u1 - 1.5 - k * 1.5
        gv0 = v1 + 1.3
        if _peresek2((gu0, gu0 + 1.1, gv0, gv0 + 2.4), sb) or (ptichnik and _peresek2((gu0, gu0 + 1.1, gv0, gv0 + 2.4), ptichnik)):
            continue
        hg = zh(gu0 + 0.55, gv0 + 1.2)
        D.kor('melochi', DOSKI, gu0, gu0 + 1.1, gv0, gv0 + 2.4, hg - 0.1, hg + 0.18, 0.01)
        for j in range(3):
            plan['rasteniya'].append([round(gu0 + 0.55, 3), round(gv0 + 0.4 + j * 0.8, 3), 0.17, 'shchavel',
                                      round(r.uniform(0, 360), 1), 0.8])


def _pleten(D, st, a, b, u_l, u_r, zv, zh):
    """Плетень: колья через 0,5 м и три лозы-жерди; по земле."""
    n = max(2, int((b - a) / 0.5))
    for k in range(n + 1):
        t = a + (b - a) * k / n
        x, y = (t, zv) if st == 'zad' else (u_l if st == 'sev' else u_r, t)
        h = zh(x, y)
        D.cil_os('melochi', BRUS, (x, y, h - 0.1), (x, y, h + 1.05), 0.035, 5)
    for w in (0.35, 0.6, 0.85):
        if st == 'zad':
            D.cil_os('melochi', BRUS, (a, zv, zh(a, zv) + w), (b, zv, zh(b, zv) + w), 0.03, 5)
        else:
            x = u_l if st == 'sev' else u_r
            D.cil_os('melochi', BRUS, (x, a, zh(x, a) + w), (x, b, zh(x, b) + w), 0.03, 5)


def _krylco(D, r, u0, u1, v0, P, dv_u0, dv_u1, EV, tg, mat_naves=DOSKI):
    """Выразительная часть «крыльцо»: крытое крыльцо к общему двору — помост, резные столбы, навес под камышом, лавка,
    кадки с цветами."""
    k0, k1 = dv_u0 - 1.4, dv_u1 + 1.6
    kv0 = v0 - 1.9
    D.kor('obolochka', DOSKI, k0, k1, kv0, v0 + 0.02, 0.0, P, 0.01)
    D.kor('obolochka', KAM, dv_u0 - 0.3, dv_u1 + 0.3, kv0 - 0.4, kv0 + 0.02, 0.0, P * 0.5, 0.01)
    wv0 = EV - 1.15                               # под кромкой камыша (её низ ≈ EV − 0,8), выше верха двери
    wv1 = wv0 - (v0 - kv0 + 0.3) * 0.25
    # навес — тонкий дощатый (Астра: «облегчить конструкцию, яснее показать покрытие навеса»)
    D.plita('obolochka', mat_naves, [(k0 - 0.25, v0, wv0), (k1 + 0.25, v0, wv0), (k1 + 0.25, kv0 - 0.3, wv1), (k0 - 0.25, kv0 - 0.3, wv1)], 0.08)
    x_ = k0 - 0.2
    while x_ < k1 + 0.2:                                                         # стропила навеса снизу
        D.brus('obolochka', BRUS, (x_, v0, wv0 - 0.1), (x_, kv0 - 0.25, wv1 - 0.1), 0.07, 0.1, (1, 0, 0), 0.006)
        x_ += 0.55
    for x_ in (k0 + 0.15, (k0 + k1) / 2.0 if (k1 - k0) > 4.0 else None, k1 - 0.15):
        if x_ is None or dv_u0 - 0.15 < x_ < dv_u1 + 0.15:
            continue
        D.brus('obolochka', BRUS, (x_, kv0 + 0.15, P), (x_, kv0 + 0.15, wv1 - 0.05), 0.13, 0.13, (1, 0, 0))
        D.kor('obolochka', BRUS, x_ - 0.09, x_ + 0.09, kv0 + 0.06, kv0 + 0.24, P + 1.1, P + 1.16, 0.015)     # резной поясок
        for zn in (-1, 1):
            D.brus('obolochka', BRUS, (x_ + zn * 0.06, kv0 + 0.15, wv1 - 0.45), (x_ + zn * 0.35, kv0 + 0.15, wv1 - 0.1), 0.07, 0.07, (0, 1, 0))
    D.brus('obolochka', BRUS, (k0 - 0.2, kv0 + 0.15, wv1 - 0.06), (k1 + 0.2, kv0 + 0.15, wv1 - 0.06), 0.1, 0.12, (0, 1, 0))
    # лавка на крыльце и кадки с цветами у ступени
    D.kor('melochi', BRUS, dv_u1 + 0.4, k1 - 0.2, v0 - 0.45, v0 - 0.12, P + 0.42, P + 0.48, 0.008)
    for x_ in (dv_u0 - 0.7, dv_u1 + 0.7):
        D.cil('melochi', BRUS, x_, kv0 - 0.35, 0.0, 0.24, 0.4, 12)
        for k in range(5):
            D.sfera('melochi', CVET, x_ + 0.14 * math.cos(k * 1.3), kv0 - 0.35 + 0.14 * math.sin(k * 1.3), 0.52, 0.08, (1, 1, 1), 2)


def _sad(D, r, p, u0, u1, v0, v1, zh, storona, plan, P=0.7, EV=4.0):
    """Выразительная часть «сад»: у бока дома — три-четыре плодовых дерева, грядка цветов, низкий плетень, скамья под
    деревом; деревья ставит движок набора (plan['derevya']). У входа — садовое крыльцо с лёгкой решёткой, от сада к нему —
    сплошной цветущий край (Астра 28.09: «различить фасады по роли: у №21 — садовое крыльцо с лёгкой решёткой»; «цветущий
    край сделать заметным непрерывным пятном от сада к крыльцу — мелкие растения теряются в общей траве»)."""
    # кроны плодовых деревьев ~3 м в поперечнике — стволы не ближе 3,3 м к стене (листва не входит в дом)
    if storona == 'jug':
        a0, a1 = u1 + 2.4, u1 + 6.2
    else:
        a0, a1 = u0 - 6.2, u0 - 2.4
    b0, b1 = v0 - 1.0, v1 + 0.5
    for k in range(4):
        uu = a0 + (a1 - a0) * (0.28 if k % 2 == 0 else 0.72) + r.uniform(-0.3, 0.3)
        vv = b0 + (b1 - b0) * (k + 0.5) / 4.0 + r.uniform(-0.3, 0.3)
        plan['derevya'].append([round(uu, 3), round(vv, 3), round(zh(uu, vv), 3), round(r.uniform(0.36, 0.42), 3),
                                round(r.uniform(0, 360), 1)])
        D.cil('melochi', TRAV, uu, vv, zh(uu, vv) - 0.02, 0.6, 0.04, 12)                                   # приствольный круг
    n_ulev = int(p.get('osoboe', {}).get('ulya') or 0)
    if n_ulev:                                                           # ульи — в глубине сада, между стволами
        import random
        rr = random.Random(p['zerno_melochej'] + 404)
        stvoly = [(d_[0], d_[1]) for d_ in plan['derevya']]
        postavleno, popytki = 0, 0
        while postavleno < n_ulev and popytki < 60:
            popytki += 1
            uu, vv = rr.uniform(a0 + 0.5, a1 - 0.5), rr.uniform(v1 - 1.0, b1 - 0.4)
            if any(math.hypot(uu - x, vv - y) < 0.9 for x, y in stvoly):
                continue
            hz = zh(uu, vv)
            for (du, dv) in ((-0.18, -0.18), (0.18, -0.18), (-0.18, 0.18), (0.18, 0.18)):
                D.cil('melochi', BRUS, uu + du, vv + dv, hz - 0.03, 0.03, 0.38, 5)
            D.kor('melochi', DOSKI, uu - 0.24, uu + 0.24, vv - 0.24, vv + 0.24, hz + 0.35, hz + 0.85, 0.01)
            D.kor('melochi', DOSKI, uu - 0.31, uu + 0.31, vv - 0.31, vv + 0.31, hz + 0.85, hz + 0.91, 0.01)
            stvoly.append((uu, vv))
            postavleno += 1
        plan['chasti'].append({'imya': 'ульи', 'etazh': 0, 'b': [a0, a1, v1 - 1.0, b1]})
    # цветник вдоль стены дома
    su = u1 + 0.1 if storona == 'jug' else u0 - 0.7
    for k in range(int((v1 - v0 - 0.4) / 1.3)):
        vv = v0 + 0.8 + k * 1.3
        plan['rasteniya'].append([round(su + 0.3, 3), round(vv, 3), 0.0,
                                  'cvety-nizkie' if k % 2 == 0 else 'cvety-vysokie', round(r.uniform(0, 360), 1), 0.42])
    # садовое крыльцо: помост у двери, лёгкий дощатый навес на двух стойках, решётка со стороны сада с вьющимися цветами
    dv0, dv1 = plan['vhod']
    k0, k1 = dv0 - 0.35, dv1 + 0.45
    kv0 = v0 - 1.25
    D.kor('obolochka', DOSKI, k0, k1, kv0, v0 + 0.02, 0.0, P, 0.01)
    D.kor('obolochka', KAM, dv0 - 0.15, dv1 + 0.15, kv0 - 0.4, kv0 + 0.02, 0.0, P * 0.5, 0.01)          # ступень
    wv0 = EV - 1.15
    wv1 = wv0 - (v0 - kv0 + 0.25) * 0.22
    D.plita('obolochka', CHER if p.get('stil') == 'mangala' else DOSKI,
            [(k0 - 0.2, v0, wv0), (k1 + 0.2, v0, wv0), (k1 + 0.2, kv0 - 0.25, wv1), (k0 - 0.2, kv0 - 0.25, wv1)], 0.06)
    for x_ in (k0 + 0.08, k1 - 0.08):
        D.brus('obolochka', BRUS, (x_, kv0 + 0.1, P), (x_, kv0 + 0.1, wv1 - 0.04), 0.09, 0.09, (1, 0, 0))
    D.brus('obolochka', BRUS, (k0 - 0.15, kv0 + 0.1, wv1 - 0.05), (k1 + 0.15, kv0 + 0.1, wv1 - 0.05), 0.08, 0.1, (0, 1, 0))
    ur = k1 - 0.08 if storona == 'jug' else k0 + 0.08                     # решётка — со стороны сада
    re0, re1, rh0, rh1 = kv0 + 0.2, v0 - 0.08, P + 0.1, wv1 - 0.15
    for (pa, pb) in (((re0, rh0), (re1, rh0)), ((re0, rh1), (re1, rh1)), ((re0, rh0), (re0, rh1)), ((re1, rh0), (re1, rh1))):
        D.brus('obolochka', BRUS, (ur, pa[0], pa[1]), (ur, pb[0], pb[1]), 0.05, 0.05, (1, 0, 0), 0.004)
    shag = 0.32
    dl = (re1 - re0) + (rh1 - rh0)
    t_ = shag
    while t_ < dl:                                                        # косые рейки в две стороны
        for zn_ in (1, -1):
            a_v = re0 + min(t_, re1 - re0) if zn_ > 0 else re1 - min(t_, re1 - re0)
            a_w = rh0 + max(0.0, t_ - (re1 - re0))
            b_v = re0 + max(0.0, t_ - (rh1 - rh0)) if zn_ > 0 else re1 - max(0.0, t_ - (rh1 - rh0))
            b_w = rh0 + min(t_, rh1 - rh0)
            D.brus('obolochka', BRUS, (ur, a_v, a_w), (ur, b_v, b_w), 0.025, 0.03, (1, 0, 0), 0.0)
        t_ += shag
    for k in range(16):                                                   # вьющиеся цветы и листья по решётке
        vv, ww = r.uniform(re0 + 0.05, re1 - 0.05), r.uniform(rh0 + 0.2, rh1 - 0.05)
        D.sfera('melochi', CVET if k % 3 == 0 else TRAV, ur + (0.04 if storona == 'jug' else -0.04), vv, ww,
                r.uniform(0.07, 0.12), (1.0, 1.0, 0.9), 2)
    # цветущий край сада — сплошная полоса от сада вдоль фасада к крыльцу (два ряда через 0,45 м, крупнее) и низкий бордюр
    fv0, fv1 = v0 - 0.35, v0 - 1.0
    f0, f1 = (k1 + 0.15, u1 + 1.6) if storona == 'jug' else (u0 - 1.6, k0 - 0.15)
    n = max(2, int((f1 - f0) / 0.45))
    for k in range(n + 1):
        gx = f0 + (f1 - f0) * k / n
        for j, vv in enumerate((fv0, fv1)):
            vid = ('cvety-vysokie' if (k + j) % 3 == 0 else 'cvety-nizkie') if (k + j) % 4 != 3 else 'shchavel'
            plan['rasteniya'].append([round(gx + r.uniform(-0.12, 0.12) + (0.22 if j else 0.0), 3), round(vv + r.uniform(-0.1, 0.1), 3),
                                      0.0, vid, round(r.uniform(0, 360), 1), 1.0 if vid == 'shchavel' else 0.8])
    for (a_, b_) in (((f0, fv1 - 0.3), (f1, fv1 - 0.3)),):
        D.cil_os('melochi', BRUS, (a_[0], a_[1], zh(a_[0], a_[1]) + 0.06), (b_[0], b_[1], zh(b_[0], b_[1]) + 0.06), 0.06, 7)
    # к саду вдоль бока: от угла дома до деревьев
    su_ = u1 + 0.6 if storona == 'jug' else u0 - 0.6
    for k in range(4):
        vv = v0 - 0.6 + k * 0.5
        plan['rasteniya'].append([round(su_ + r.uniform(-0.2, 0.2), 3), round(vv, 3), 0.0,
                                  'cvety-nizkie' if k % 2 else 'cvety-vysokie', round(r.uniform(0, 360), 1), 0.8])
    bu = (a0 + 0.8) if storona == 'jug' else (a1 - 0.8)
    D.kor('melochi', BRUS, bu - 0.7, bu + 0.7, b0 - 0.9, b0 - 0.55, zh(bu, b0) + 0.42, zh(bu, b0) + 0.48, 0.008)
    for x2 in (bu - 0.6, bu + 0.5):
        D.kor('melochi', BRUS, x2, x2 + 0.1, b0 - 0.87, b0 - 0.58, zh(x2, b0) - 0.1, zh(x2, b0) + 0.42)
    # скамья под деревом и низкий плетень по наружной кромке сада
    cu, cv = (a0 + a1) / 2.0, (b0 + b1) / 2.0
    D.kor('melochi', BRUS, cu - 0.7, cu + 0.7, cv - 0.18, cv + 0.18, zh(cu, cv) + 0.42, zh(cu, cv) + 0.48, 0.008)
    for x_ in (cu - 0.6, cu + 0.5):
        D.kor('melochi', BRUS, x_, x_ + 0.1, cv - 0.15, cv + 0.15, zh(x_, cv), zh(x_, cv) + 0.42)
    kr = a1 + 0.3 if storona == 'jug' else a0 - 0.3
    n = int((b1 - b0) / 0.5)
    for k in range(n + 1):
        vv = b0 + (b1 - b0) * k / n
        D.cil_os('melochi', BRUS, (kr, vv, zh(kr, vv) - 0.1), (kr, vv, zh(kr, vv) + 0.7), 0.03, 5)
    for w in (0.3, 0.55):
        D.cil_os('melochi', BRUS, (kr, b0, zh(kr, b0) + w), (kr, b1, zh(kr, b1) + w), 0.028, 5)
    plan['chasti'].append({'imya': 'сад', 'etazh': 0, 'b': [min(a0, a1), max(a0, a1), b0, b1]})


def _konyushnya(D, p, lico, zn, uo, b0, b1, h, v0, zh, plan):
    """Конюшня под навесом мастерской (Астра 28.09, улица Колыбели №14: «сохранить смысл конюшни: навес для ухода за
    упряжью, широкая калитка во двор»): коновязь у открытого края, поилка, седло на козлах, упряжь на крюках у стены,
    тюки сена в глубине; широкие ворота — рама из двух столбов с перекладиной у переднего конца навеса."""
    import random
    rr = random.Random(p['zerno_melochej'] + 303)
    seno = CHER if p['stil'] == 'kolybel' else TKAN
    for k in range(5):                                                  # тюки сена в глубине, стопкой
        a_ = uo - zn * (1.0 + (k % 2) * 0.9)
        w_ = h + 0.12 + (k // 2) * 0.45
        D.kor('melochi', seno, min(a_, a_ - zn * 0.85), max(a_, a_ - zn * 0.85), b1 - 1.3 - (k % 3) * 0.1, b1 - 0.3, w_,
              w_ + 0.42, 0.04)
    # коновязь: бревно на двух столбиках вдоль открытого края
    ck = uo + zn * 0.35
    for vv in (b0 + 0.8, b0 + 2.6):
        D.cil('melochi', BRUS, ck, vv, zh(ck, vv) - 0.05, 0.07, 1.15, 8)
    D.cil_os('melochi', BRUS, (ck, b0 + 0.65, h + 0.98), (ck, b0 + 2.75, h + 0.98), 0.06, 8)
    # поилка — долблёная колода у коновязи
    D.kor('melochi', DOSKI, ck + zn * 0.3 - 0.3, ck + zn * 0.3 + 0.3, b0 + 1.1, b0 + 2.3, zh(ck, b0 + 1.7), zh(ck, b0 + 1.7) + 0.5, 0.03)
    D.kor('melochi', STEK, ck + zn * 0.3 - 0.22, ck + zn * 0.3 + 0.22, b0 + 1.18, b0 + 2.22, zh(ck, b0 + 1.7) + 0.44,
          zh(ck, b0 + 1.7) + 0.46)
    # седло на козлах — у стены под навесом
    cs = lico + zn * 0.7
    for s_ in (-1, 1):
        D.cil_os('mebel', BRUS, (cs + s_ * 0.25, b1 - 2.4, h + 0.12), (cs, b1 - 2.4, h + 0.85), 0.035, 5)
        D.cil_os('mebel', BRUS, (cs + s_ * 0.25, b1 - 1.7, h + 0.12), (cs, b1 - 1.7, h + 0.85), 0.035, 5)
    D.brus('mebel', BRUS, (cs, b1 - 2.5, h + 0.86), (cs, b1 - 1.6, h + 0.86), 0.12, 0.1, (1, 0, 0), 0.01)
    D.sfera('mebel', KRAS, cs, b1 - 2.05, h + 0.98, 0.3, (1.0, 1.5, 0.45), 3)
    # упряжь на крюках у стены
    for k in range(3):
        vv = b0 + 0.6 + k * 0.55
        D.cil_os('mebel', ZHEL, (lico, vv, h + 1.7), (lico + zn * 0.12, vv, h + 1.7), 0.015, 4)
        D.cil_os('mebel', KRAS if k == 1 else DOSKI, (lico + zn * 0.1, vv, h + 1.68), (lico + zn * 0.1, vv + rr.uniform(-0.05, 0.05),
                 h + 1.0 + rr.uniform(0.0, 0.2)), 0.03, 5)
    # широкие ворота: рама из двух столбов и перекладины у переднего конца навеса — вход во двор
    for vv in (b0 - 0.2, b0 - 0.2 + 0.001):
        pass
    for a_ in (lico + zn * 0.2, uo + zn * 0.2):
        D.cil('obolochka', BRUS, a_, b0 - 0.25, zh(a_, b0 - 0.25) - 0.05, 0.09, 2.45, 8)
    D.brus('obolochka', BRUS, (lico + zn * 0.1, b0 - 0.25, h + 2.35), (uo + zn * 0.3, b0 - 0.25, h + 2.35), 0.16, 0.18, (0, 1, 0), 0.01)
    plan['chasti'].append({'imya': 'конюшня', 'etazh': 0, 'b': [min(lico, uo), max(lico, uo), b0, b1]})


def _masterskaya(D, r, p, u0, u1, v0, v1, P, zh, storona, EV, plan):
    """Выразительная часть «мастерская»: навес у бока дома с подкосами; рабочее место — у открытого края, ближе к двору
    (Астра 28.09: «с подхода занятие хозяина почти не считывается: выдвинуть к открытому краю навеса верстак или козлы с
    одной заготовкой, связать рабочее место вытоптанной землёй с входом»): козлы с брусом-заготовкой и колода с топором у
    кромки, верстак у стены, инструмент над ним, доски стопкой в глубине; тропа от рабочего места к двери."""
    if storona == 'jug':
        m0, m1, lico, zn = u1, u1 + 2.6, u1, 1
    else:
        m0, m1, lico, zn = u0 - 2.6, u0, u0, -1
    b0, b1 = v0 + 0.3, v1 - 0.3
    uo = m1 if zn > 0 else m0
    h = zh((m0 + m1) / 2.0, (b0 + b1) / 2.0)
    D.kor('obolochka', DOSKI, m0, m1, b0, b1, h - 0.1, h + 0.12, 0.01)
    wv = EV - 1.15
    wn = wv - 2.95 * 0.3
    D.plita('obolochka', CHER, [(lico, b0 - 0.3, wv), (lico, b1 + 0.3, wv), (uo + zn * 0.35, b1 + 0.3, wn), (uo + zn * 0.35, b0 - 0.3, wn)], 0.3)
    stolby = [b0 + 0.15, (b0 + b1) / 2.0, b1 - 0.15] if b1 - b0 > 4.5 else [b0 + 0.15, b1 - 0.15]
    for vv in stolby:
        D.brus('obolochka', BRUS, (uo - zn * 0.15, vv, h + 0.12), (uo - zn * 0.15, vv, wn + 0.15), 0.18, 0.18, (1, 0, 0))
        for s_ in (-1, 1):                                                     # подкосы к прогону
            if b0 + 0.1 < vv + s_ * 0.6 < b1 - 0.1:
                D.brus('obolochka', BRUS, (uo - zn * 0.15, vv, wn - 0.45), (uo - zn * 0.15, vv + s_ * 0.6, wn + 0.12), 0.1, 0.1, (1, 0, 0))
    D.brus('obolochka', BRUS, (uo - zn * 0.15, b0 - 0.1, wn + 0.2), (uo - zn * 0.15, b1 + 0.1, wn + 0.2), 0.18, 0.2, (1, 0, 0))
    if p.get('osoboe', {}).get('konyushnya'):
        _konyushnya(D, p, lico, zn, uo, b0, b1, h, v0, zh, plan)
        return
    # верстак у стены — у переднего конца навеса; инструмент над ним
    vu0, vu1 = (lico + zn * 0.1, lico + zn * 0.8)
    D.kor('mebel', BRUS, min(vu0, vu1), max(vu0, vu1), b0 + 0.4, b0 + 2.2, h + 0.85, h + 0.95, 0.01)
    for vv in (b0 + 0.5, b0 + 2.0):
        D.kor('mebel', BRUS, min(vu0, vu1) + 0.05, max(vu0, vu1) - 0.05, vv, vv + 0.1, h + 0.12, h + 0.85)
    for k in range(4):
        D.cil_os('mebel', ZHEL, (lico + zn * 0.03, b0 + 0.7 + k * 0.4, h + 1.3), (lico + zn * 0.03, b0 + 0.7 + k * 0.4, h + 1.75), 0.015, 4)
    D.kor('mebel', ZHEL, lico + zn * 0.02, lico + zn * 0.05, b0 + 2.3, b0 + 2.95, h + 1.25, h + 1.45)        # пила на стене
    # козлы с брусом-заготовкой — у открытого края, у переднего конца (виден со двора и с подхода)
    cu = uo - zn * 0.75
    for vv in (b0 + 0.6, b0 + 1.9):
        for s_ in (-1, 1):
            D.cil_os('melochi', BRUS, (cu + s_ * 0.3, vv, h + 0.12), (cu - s_ * 0.1, vv, h + 0.9), 0.04, 5)
    D.brus('melochi', BRUS, (cu, b0 + 0.2, h + 1.0), (cu, b0 + 2.4, h + 1.0), 0.2, 0.18, (1, 0, 0), 0.01)
    D.brus('melochi', DOSKI, (cu + zn * 0.35, b0 + 2.55, h + 0.12), (cu + zn * 0.05, b0 + 2.75, h + 1.5), 0.25, 0.03, (0, 1, 0), 0.004)
    # колода с топором — снаружи у переднего угла навеса
    ku, kv_ = uo + zn * 0.55, b0 - 0.35
    D.cil('melochi', BRUS, ku, kv_, zh(ku, kv_), 0.3, 0.55, 12)
    D.cil_os('melochi', ZHEL, (ku, kv_, zh(ku, kv_) + 0.55), (ku - zn * 0.2, kv_ + 0.12, zh(ku, kv_) + 0.95), 0.02, 4)
    # доски стопкой в глубине навеса
    for k in range(5):
        D.kor('melochi', DOSKI, uo - zn * 1.9, uo - zn * 1.3, b1 - 2.4, b1 - 0.4, h + 0.14 + k * 0.05, h + 0.18 + k * 0.05)
    # вытоптанная тропа: рабочее место → перед фасадом → дверь (декали ставит набор пары)
    dvc = (plan['vhod'][0] + plan['vhod'][1]) / 2.0
    plan.setdefault('tropy', []).append([[round(cu, 3), round(b0 + 1.2, 3)], [round(uo - zn * 0.4, 3), round(v0 - 1.0, 3)],
                                         [round((uo + dvc) / 2.0, 3), round(v0 - 1.3, 3)], [round(dvc, 3), round(v0 - 1.0, 3)]])
