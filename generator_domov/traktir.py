# -*- coding: utf-8 -*-
"""Семейство «трактир-мастерская» Мангалы — гостевой дом-кузня, первый образец генератора (Астра 28.09: «первый образец
генератора — нынешняя кузня: исправить силуэт, глубину фасада и свет, затем показать три варианта из разных зёрен»).

Композиции (Астра, разбор первого образца 28.09: «генератору нужны три различимых варианта композиции… сохраняй
семейство кровель, материалов и опор; меняй крупные объёмы и расположение открытых пространств; горн, очаг и трубу
перемещай согласованно»):
- naves — первый образец: кузня под двускатным навесом щипцом к улице, наружная лестница с площадкой вдоль бока,
  галерея у двери коридора;
- galereya — широкая двухъярусная галерея во весь фасад под продлённым скатом (внизу крыльцо зала, вверху галерея
  комнат), кузня у края — открытый навес у бока под половиной вальмы;
- ugol — терраса верха поворачивает за угол, кузня занимает угол под ней, лестница поднимается к террасе со двора;
- pristrojka — корпус и низкая боковая пристройка (кузня спереди, кладовая сзади) под своей половиной вальмы: крыши
  двумя ступенями.

Зерно выбирает композицию (или её задают явно) и внутри диапазонов Астры: сторону лестницы, габарит корпуса, высоту
камня, уклон вальмовой кровли и свес, ставни, размеры галерей и пристроек. Всегда: зал с очагом, место встречи у огня,
общий стол, стойка хозяйки, поварня, лестница вдоль стены, коридор и комнаты наверху, задняя дверь во двор, горн и
очаг на одной трубе, три уровня (крыльцо, помост кузни, верх).

Корпус строится с лестницей слева и кузней справа (s = +1); при s = −1 весь дом отражается по u.
"""
import math
import random

from .detali import Detali, zerkalo_detalej
from .stil_mangala import (BRUS, CHER, CVET, DOSKI, KAM, KRAS, MOSH, SHT, STEK, STIL, TKAN, TRAV, UGLI, ZHEL)

SU, SV = 11.7, 10.25        # след слота dom-traktir
T, TV = 0.5, 0.18           # наружная стена, перегородка
KOMPOZ = ('naves', 'galereya', 'ugol', 'pristrojka')
IMENA_KOMPOZ = {'naves': 'кузня под навесом щипцом к улице',
                'galereya': 'широкая передняя галерея, кузня у края',
                'ugol': 'терраса за угол, кузня в углу',
                'pristrojka': 'низкая боковая пристройка, крыши ступенями'}


def sn(x, k=0.05):
    return round(round(x / k) * k, 3)


class Rama:
    """Местные оси стены: a — вдоль стены, d — от её лица (в комнату или наружу), w — вверх. os_ — вдоль какой оси идёт
    стена ('u' или 'v'), lico — где лицо по другой оси, zn — куда растёт d (+1/−1)."""

    def __init__(self, os_, lico, zn):
        self.os, self.lico, self.zn = os_, lico, zn

    def t(self, a, d):
        return (a, self.lico + self.zn * d) if self.os == 'u' else (self.lico + self.zn * d, a)

    def p(self, a, d, w):
        x, y = self.t(a, d)
        return (x, y, w)

    def box(self, a0, a1, d0, d1):
        x0, y0 = self.t(a0, d0)
        x1, y1 = self.t(a1, d1)
        return (min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1))

    def kor(self, D, g, m, a0, a1, d0, d1, w0, w1, fs=0.0):
        b = self.box(a0, a1, d0, d1)
        return D.kor(g, m, b[0], b[1], b[2], b[3], w0, w1, fs)

    def profil(self, D, g, m, tochki_aw, d0, d1, fs=0.0):
        """Многоугольник в плоскости (a, w), выдавленный по d от d0 до d1."""
        x0, y0 = self.t(0.0, d0)
        x1, y1 = self.t(0.0, d1)
        if self.os == 'u':
            return D.profil(g, m, tochki_aw, 'uw', min(y0, y1), max(y0, y1), fs)
        return D.profil(g, m, tochki_aw, 'vw', min(x0, x1), max(x0, x1), fs)


# облик с картинки (obraz.py): поле паспорта → (параметр, мин, макс); размеры держит слот
PREDELY_OBRAZA = {'svs_m': ('svs', 0.5, 0.9), 'kamen_niza_m': ('kam', 0.6, 1.6), 'vysota_etazha_m': ('H2', 2.6, 3.0)}
UKLON_OBRAZA = (20.0, 34.0)


KRYSHI = ('valma', 'dvuskat')     # вальмовая (образец Астры, зерно 13) или двускатная со щипцами (рисунок дома-кузни)


def parametry(zerno, kompoz=None, obraz=None, krysha=None):
    r = random.Random(zerno)
    p = {'zerno': zerno, 's': 1 if r.random() < 0.5 else -1}
    p['Wb'] = sn(r.uniform(8.4, 9.2))
    p['Db'] = sn(r.uniform(6.9, 7.5))
    p['u0'] = sn(r.uniform(0.45, 0.7))
    p['v1'] = sn(SV - 0.25)
    p['P'] = sn(r.uniform(0.45, 0.6))
    p['kam'] = sn(r.uniform(0.9, 1.35))          # красный камень низа над полом зала
    p['H1'], p['plita'], p['H2'] = 3.1, 0.3, sn(r.uniform(2.7, 2.9))
    p['uklon'] = round(r.uniform(24.0, 30.0), 1)
    p['svs'] = sn(r.uniform(0.6, 0.85))
    p['kuz_w'] = sn(r.uniform(4.0, 4.6))
    p['kuz_uklon'] = round(r.uniform(30.0, 36.0), 1)
    p['NV0'] = sn(r.uniform(0.45, 0.65))          # передняя кромка навесов
    r.choice([3, 4])                              # прежний выбор числа комнат: теперь по ширине полосы (зёрна не сдвигаются)
    p['stavni'] = r.random() < STIL['stavni_dolya']
    p['okon_krylco'] = r.choice([1, 2])
    p['wk'] = sn(r.uniform(3.3, 3.7))              # задний блок: поварня + кладовая (зал просторнее, 28.09)
    p['dk'] = sn(r.uniform(2.7, 3.0))
    p['gal_gl'] = sn(r.uniform(1.4, 1.7))
    p['zerno_melochej'] = r.randrange(1 << 30)
    # композиция и её размеры — после прежних выборов
    k = r.randrange(len(KOMPOZ))
    p['kompoz'] = kompoz or KOMPOZ[k]
    p['gal_g'] = sn(r.uniform(1.15, 1.3))          # galereya: глубина передней галереи
    p['lp_w'] = sn(r.uniform(2.1, 2.4))            # galereya: навес кузни у бока
    p['pr_w'] = sn(r.uniform(2.8, 3.1))            # pristrojka: ширина пристройки
    p['pr_d0'] = sn(r.uniform(0.6, 1.3))           # pristrojka: вынос пристройки вперёд корпуса
    p['pr_d1'] = sn(r.uniform(0.5, 0.9))           # pristrojka: отступ от задней стены
    p['pr_uklon'] = round(r.uniform(18.0, 21.0), 1)   # пристройки и навесы — положе (семейство кузни 15–22°)
    p['ter_gf'] = sn(r.uniform(1.9, 2.3))          # ugol: глубина террасы над кузней
    p['ter_gs'] = sn(r.uniform(1.3, 1.45))         # ugol: плечо террасы вдоль бока
    p['ter_lf'] = sn(r.uniform(4.1, 4.6))          # ugol: длина террасы вдоль фасада от угла
    kz = p['kompoz']
    if kz == 'pristrojka':
        p['Wb'] = sn(7.7 + (p['Wb'] - 8.4) * 0.6)
        p['u0'] = sn(0.3 + (p['u0'] - 0.45) * 0.6)
    elif kz == 'galereya':
        p['Wb'] = sn(min(p['Wb'], 8.9))
        p['u0'] = sn(0.3 + (p['u0'] - 0.45) * 0.6)
    elif kz == 'ugol':
        p['Wb'] = sn(min(p['Wb'], 8.9))
    p['u1'] = sn(p['u0'] + p['Wb'])
    p['v0'] = sn(p['v1'] - p['Db'])
    if kz == 'pristrojka':
        p['pr_w'] = sn(min(p['pr_w'], SU - 0.1 - p['u1']))
    if obraz:
        from .dom_dvor import primenit_obraz
        p, p['obraz_prizhato'] = primenit_obraz(p, obraz, PREDELY_OBRAZA, UKLON_OBRAZA)
    k_ = krysha or (obraz or {}).get('krysha')             # по умолчанию — вальма: зёрна прежних домов не меняются
    p['krysha'] = k_ if k_ in KRYSHI else 'valma'
    return p


def sobrat(zerno, kompoz=None, obraz=None, krysha=None):
    """→ (паспорт, план, детали) дома; детали уже в осях слота (с отражением, если s = −1). obraz — числа облика с
    картинки (obraz.py), в пределах PREDELY_OBRAZA."""
    p = parametry(zerno, kompoz, obraz, krysha)
    kz = p['kompoz']
    r = random.Random(p['zerno_melochej'])
    D = Detali()
    u0, u1, v0, v1, P = p['u0'], p['u1'], p['v0'], p['v1'], p['P']
    H1, H2 = p['H1'], p['H2']
    F1 = P + H1
    F2 = F1 + p['plita']
    EV = F2 + H2
    KR = P + p['kam']
    Pk = sn(P - 0.15)                                     # помост кузни — на ступень ниже пола зала
    ui0, ui1, vi0, vi1 = u0 + T, u1 - T, v0 + T, v1 - T
    NV0 = p['NV0']
    tg = math.tan(math.radians(p['uklon']))
    tg_a = math.tan(math.radians(p['pr_uklon']))
    plan = {'kompoz': kz, 'etazhi': [], 'proemy': [], 'lestnicy': [], 'ochagi': [], 'utvar': {}, 'vnutr_dveri': [],
            'chasti': [], 'svyazi': [['zal', 'lestnica'], ['lestnica', 'koridor']], 'proverki_dannye': {}}

    # ---------------- план низа ----------------
    kl_v_pr = kz == 'pristrojka'                          # у пристройки кладовая — в ней, в корпусе только поварня
    wk = sn(p['wk'] * 0.68) if kl_v_pr else p['wk']
    kb_u0, kb_v0 = sn(ui1 - wk), sn(vi1 - p['dk'])
    pov_u1 = ui1 if kl_v_pr else sn(kb_u0 + wk * 0.6)
    # внутренняя лестница вдоль левой стены, от передней части зала вглубь; 34°, ширина 1,25
    L_sh = 1.25
    podem = F2 - P
    dl = sn(podem / math.tan(math.radians(STIL['lestnica_ugol'])), 0.01)
    # Верхняя площадка лестницы и ширина коридора
    w_kor = sn(max(1.3, min(2.0, (vi1 - vi0) * 0.18)))
    kor_v0 = sn(vi1 - w_kor)
    zapas_v = (vi1 - vi0) - dl
    top_land = sn(min(w_kor, max(0.55, zapas_v - 0.45)))
    st_v1 = sn(vi1 - top_land, 0.01)
    st_v0 = sn(st_v1 - dl, 0.01)
    # очаг зала и горн — спиной друг к другу на одной стене: у передней (naves, ugol) или у правой (galereya, pristrojka)
    if kz in ('naves', 'ugol'):
        ca = sn(u1 - 1.35) if kz == 'naves' else sn(u1 - 2.9)
        S_in, S_out = Rama('u', vi0, 1), Rama('u', v0, -1)
    else:
        ca = sn(vi0 + 1.3)
        S_in, S_out = Rama('v', ui1, -1), Rama('v', u1, 1)
    # вход зала — правее подножия лестницы: из двери видны очаг и общий стол (Астра 28.09)
    dv_u0 = sn(ui0 + L_sh + 0.2)
    dv_u1 = sn(dv_u0 + 1.4)
    pro_u0 = pro_u1 = None
    nk_u0 = nk_u1 = tf_u0 = None
    if kz == 'naves':
        nk_u1 = sn(u1 + 0.2)
        nk_u0 = sn(nk_u1 - p['kuz_w'])
        pro_u0 = sn(nk_u0 + 0.35)
        pro_u1 = sn(min(pro_u0 + 2.2, ca - 1.1))
        kr_u0, kr_u1 = sn(u0 - 0.3), sn(nk_u0 - 0.05)
    elif kz == 'ugol':
        tf_u0 = sn(u1 - p['ter_lf'])
        pro_u0 = sn(ca + 1.1)
        pro_u1 = sn(min(pro_u0 + 1.6, u1 - 0.45))
        kr_u0, kr_u1 = sn(u0 - 0.3), sn(tf_u0 - 0.15)
    elif kz == 'galereya':
        kr_u0, kr_u1 = sn(u0 - 0.15), sn(u1 + 0.05)
    else:
        kr_u0, kr_u1 = sn(u0 - 0.3), sn(min(u1 - 0.6, dv_u1 + 2.2))
    zal = {'id': 'zal', 'imya': 'общий зал', 'b': [ui0, ui1, vi0, vi1], 'bez': [[kb_u0 - TV / 2, ui1, kb_v0 - TV / 2, vi1]]}
    pov = {'id': 'povarnya', 'imya': 'поварня', 'b': [kb_u0 + TV / 2, pov_u1 - (0 if kl_v_pr else TV / 2), kb_v0 + TV / 2, vi1]}
    komnaty_niz = [zal, pov]
    if not kl_v_pr:
        komnaty_niz.append({'id': 'kladovaya', 'imya': 'кладовая', 'b': [pov_u1 + TV / 2, ui1, kb_v0 + TV / 2, vi1]})
    niz = {'w_pola': P, 'komnaty': komnaty_niz, 'dveri': [], 'okna': []}

    # ---------------- план верха ----------------
    # kor_v0 рассчитан выше с учётом пропорций
    polosa_u0 = sn(ui0 + L_sh + TV)
    shir = ui1 - polosa_u0
    if shir >= 5.9:
        doli = [0.31, 0.38, 0.31]
        imena = [('hozyajskaya', 'хозяйская'), ('nochlezhka', 'ночлежка'), ('gostevaya', 'гостевая')] if kz == 'ugol' else \
            [('gostevaya', 'гостевая'), ('nochlezhka', 'ночлежка'), ('hozyajskaya', 'хозяйская')]
    else:
        doli = [0.5, 0.5]
        imena = [('gostevaya', 'гостевая'), ('hozyajskaya', 'хозяйская')]
    komn = []
    x = polosa_u0
    for i, (d, (kid, kim)) in enumerate(zip(doli, imena)):
        x1 = ui1 if i == len(doli) - 1 else sn(x + shir * d)
        komn.append({'id': kid, 'imya': kim, 'b': [x + (TV / 2 if i else 0), x1 - (TV / 2 if i < len(doli) - 1 else 0),
                                                    vi0, kor_v0 - TV / 2]})
        x = x1
    koridor = {'id': 'koridor', 'imya': 'коридор и площадка', 'b': [ui0, ui1, kor_v0 + TV / 2, vi1]}
    verh = {'w_pola': F2, 'komnaty': komn + [koridor], 'dveri': [], 'okna': []}

    # ---------------- наружные проёмы низа ----------------
    proemy_niz = []                                       # (сторона, a0, a1, w0, w1, вид)

    def proem(storona, a0, a1, w0, w1, vid, spisok):
        spisok.append((storona, round(a0, 3), round(a1, 3), round(w0, 3), round(w1, 3), vid))

    proem('ul', dv_u0, dv_u1, P, P + 2.45, 'dver_vhod', proemy_niz)
    if pro_u0 is not None:
        proem('ul', pro_u0, pro_u1, P, P + 2.6, 'proem_kuzni', proemy_niz)
    okw = sn(r.uniform(*STIL['okno_shir']))
    okh = sn(r.uniform(*STIL['okno_vys']))
    sill = sn(P + 0.95)
    # окна зала по фасаду — в свободных кусках стены между дверью, проёмом кузни и очагом
    zanyato = [(dv_u0 - 0.4, dv_u1 + 0.4)]
    if pro_u0 is not None:
        zanyato.append((pro_u0 - 0.4, pro_u1 + 0.4))
    if S_in.os == 'u':
        zanyato.append((ca - 1.05, ca + 1.05))
    for (a, b) in _svobodno(u0 + 0.45, u1 - 0.45, zanyato):
        n_ok = 2 if b - a >= 2 * okw + 2.2 else (1 if b - a >= okw + 0.2 else 0)
        for k in range(n_ok):
            c = a + (b - a) * (k + 1) / (n_ok + 1)
            proem('ul', c - okw / 2, c + okw / 2, sill, sill + okh, 'okno', proemy_niz)
    # левая стена: окно зала перед началом лестницы
    if st_v0 - vi0 > okw + 0.6:
        a = vi0 + (st_v0 - vi0) / 2.0 - okw / 2.0
        proem('sev', a, a + okw, sill, sill + okh, 'okno', proemy_niz)
    # задняя стена: окно поварни, задняя дверь (кладовой или поварни)
    if kl_v_pr:
        proem('zad', kb_u0 + 0.35, kb_u0 + 0.35 + min(okw, 0.7), sill, sill + okh * 0.85, 'okno', proemy_niz)
        # дверь из поварни в кладовую пристройки — в правой стене
        proem('jug', kb_v0 + 0.35, kb_v0 + 1.3, P, P + 2.2, 'dver_vn', proemy_niz)
    else:
        a = (kb_u0 + pov_u1) / 2.0 - min(okw, 0.75) / 2.0
        proem('zad', a, a + min(okw, 0.75), sill, sill + okh * 0.85, 'okno', proemy_niz)
        a = (pov_u1 + ui1) / 2.0 - 0.5
        proem('zad', a, a + 1.0, P, P + 2.2, 'dver_zad', proemy_niz)
        # правая стена: малое окно кладовой с решёткой
        a = vi1 - 1.1
        proem('jug', a, a + 0.55, P + 1.5, P + 2.05, 'okno_reshetka', proemy_niz)

    # ---------------- наружные проёмы верха ----------------
    proemy_verh = []
    kuz_krysha = _kuz_krysha(p, nk_u0, nk_u1, v0) if kz == 'naves' else (lambda u: 0.0)
    s0 = sn(F2 + 0.85)
    truba_pered = [(ca - 0.65, ca + 0.65)] if S_in.os == 'u' else []
    for i, k in enumerate(komn):
        a0, a1 = k['b'][0], k['b'][1]
        k['okna'] = []
        svob = [x_ for x_ in _svobodno(a0 + 0.1, a1 - 0.1, truba_pered) if x_[1] - x_[0] > 0.3]
        a_, b_ = max(svob, key=lambda x_: x_[1] - x_[0]) if svob else (a0, a0)
        na_galereyu = kz == 'galereya' or (kz == 'ugol' and i == len(komn) - 1)
        if na_galereyu and b_ - a_ >= 0.95:
            # дверь на галерею (террасу): у галереи — у правого края куска, у террасы — у левого; окно — рядом
            d0_, d1_ = (b_ - 0.95, b_) if kz == 'galereya' else (a_, a_ + 0.95)
            proem('ul', d0_, d1_, F2, F2 + min(2.2, EV - F2 - 0.25), 'dver_galereya', proemy_verh)
            verh['dveri'].append({'iz': 'galereya', 'v': k['id'], 'shir': 0.95})
            k['dver_pered'] = [d0_, d1_]
            ost = (a_, d0_ - 0.15) if kz == 'galereya' else (d1_ + 0.15, b_)
            w_ok = sn(min(r.uniform(*STIL['okno_shir']), ost[1] - ost[0] - 0.05), 0.05)
            if w_ok >= 0.4:
                x0 = ost[0] + 0.05 if kz == 'galereya' else ost[1] - 0.05 - w_ok
                proem('ul', x0, x0 + w_ok, s0, s0 + min(1.2, EV - 0.2 - s0), 'okno_galereya', proemy_verh)
                k['okna'] = [[x0, x0 + w_ok]]
            continue
        w_ok = sn(min(r.uniform(*STIL['okno_shir']), b_ - a_ - 0.3))
        if w_ok < 0.45:
            k['bok'] = True                                  # фасад занят трубой — окно в боковой стене
            continue
        c = (a_ + b_) / 2.0
        s_ = s0
        nizh = max(kuz_krysha(c - w_ok / 2.0), kuz_krysha(c + w_ok / 2.0)) + 0.2   # над навесом кузни — выше кровли навеса
        if nizh > s_:
            s_ = sn(min(nizh, EV - 1.35))
        proem('ul', c - w_ok / 2.0, c + w_ok / 2.0, s_, s_ + min(1.2, EV - 0.2 - s_), 'okno', proemy_verh)
        k['okna'] = [[c - w_ok / 2.0, c + w_ok / 2.0]]
    # правая стена верха: у naves — дверь коридора на галерею; крайней комнате — окно в боку (мимо трубы у бока)
    if kz == 'naves':
        proem('jug', kor_v0 + 0.15, kor_v0 + 1.15, F2, F2 + 2.15, 'dver_galereya', proemy_verh)
        verh['dveri'].append({'iz': 'koridor', 'v': 'galereya', 'shir': 1.0})
    kr_k = komn[-1]
    if kz != 'naves' or kr_k.get('bok') or not kr_k['okna']:
        ob = (vi0 + 0.7, vi0 + 1.4)
        if S_in.os == 'v' and ob[1] > ca - 0.7 and ob[0] < ca + 0.7:
            ob = (ca + 0.9, ca + 1.6)
        proem('jug', ob[0], ob[1], F2 + 0.9, F2 + 1.95, 'okno', proemy_verh)
        kr_k['okno_bok'] = list(ob)
    for a in (ui0 + 1.6, ui1 - 2.4):
        proem('zad', a, a + 0.75, F2 + 0.9, F2 + 1.95, 'okno', proemy_verh)
    if st_v0 - vi0 > 0.9:
        a = vi0 + 0.25
        proem('sev', a, a + 0.7, F2 + 0.9, F2 + 1.9, 'okno', proemy_verh)

    def vyrezy(proemy, storona):
        out = []
        for (st, a0, a1, w0, w1, vid) in proemy:
            if st != storona:
                continue
            if st in ('ul', 'zad'):
                vv = (v0 - 0.3, v0 + T + 0.3) if st == 'ul' else (v1 - T - 0.3, v1 + 0.3)
                out.append([a0, a1, vv[0], vv[1], w0, w1])
            else:
                uu = (u0 - 0.3, u0 + T + 0.3) if st == 'sev' else (u1 - T - 0.3, u1 + 0.3)
                out.append([uu[0], uu[1], a0, a1, w0, w1])
        return out

    vse = proemy_niz + proemy_verh
    steny = {'ul': [u0, u1, v0, v0 + T], 'zad': [u0, u1, v1 - T, v1], 'sev': [u0, u0 + T, v0 + T, v1 - T],
             'jug': [u1 - T, u1, v0 + T, v1 - T]}
    for st, (a0, a1, b0, b1) in steny.items():
        vy = vyrezy(vse, st)
        D.stena('obolochka', KAM, [a0, a1, b0, b1, 0.0, KR], vy)
        # известь низа — тоньше на 3 см: камень читается выступом
        d_ = 0.03
        if st == 'ul':
            box = [a0 + d_, a1 - d_, b0 + d_, b1, KR, F2]
        elif st == 'zad':
            box = [a0 + d_, a1 - d_, b0, b1 - d_, KR, F2]
        elif st == 'sev':
            box = [a0 + d_, a1, b0, b1, KR, F2]
        else:
            box = [a0, a1 - d_, b0, b1, KR, F2]
        D.stena('obolochka', SHT, box, vy)
        D.stena('obolochka', SHT, [a0, a1, b0, b1, F2, EV], vy)
    plan['proemy'] = [{'storona': s_, 'a0': a0, 'a1': a1, 'w0': w0, 'w1': w1, 'vid': vid} for (s_, a0, a1, w0, w1, vid) in vse]

    # дневной свет от окон: мягкий холодный источник в 0,9 м от окна внутри, без теней (как подсветка окон в играх)
    for i_, (st, a0, a1, w0, w1, vid) in enumerate(vse):
        if not vid.startswith('okno'):
            continue
        c_ = (a0 + a1) / 2.0
        wm = (w0 + w1) / 2.0
        pt = {'ul': (c_, v0 + T + 0.9), 'zad': (c_, v1 - T - 0.9), 'sev': (u0 + T + 0.9, c_), 'jug': (u1 - T - 0.9, c_)}[st]
        D.istochnik('okno%d' % i_, pt[0], pt[1], wm, 3.0, 450.0, (210, 225, 255), False)

    def _zapasy_peremychki(st_, a0_, a1_):
        zap = 0.18
        zap_l = zap
        zap_r = zap
        for (st_o, o0, o1, _, _, _) in vse:
            if st_o != st_ or (abs(o0 - a0_) < 1e-4 and abs(o1 - a1_) < 1e-4):
                continue
            if o1 <= a0_ and a0_ - o1 < 2 * zap:
                zap_l = min(zap_l, max(0.01, (a0_ - o1) / 2.0 - 0.005))
            if o0 >= a1_ and o0 - a1_ < 2 * zap:
                zap_r = min(zap_r, max(0.01, (o0 - a1_) / 2.0 - 0.005))
        return zap_l, zap_r

    # окна (утоплены на 0,3 — Астра: «утопи окна»), двери, перемычки, подоконники
    for (st, a0, a1, w0, w1, vid) in vse:
        zl, zr = _zapasy_peremychki(st, a0, a1)
        if vid.startswith('okno'):
            os_, lico, znak = ('u', v0, -1) if st == 'ul' else ('u', v1, 1) if st == 'zad' else \
                ('v', u0, -1) if st == 'sev' else ('v', u1, 1)
            D.okno(os_, a0, a1, w0, w1, lico, znak, perepl=1, stavni=(p['stavni'] and vid == 'okno'), steklo=False, glub=0.3, otliv=True)
            if vid == 'okno_reshetka':
                for k in range(4):
                    x_ = a0 + (a1 - a0) * (k + 0.5) / 4.0
                    if os_ == 'v':
                        D.cil_os('obolochka', ZHEL, (lico + znak * 0.05, x_, w0), (lico + znak * 0.05, x_, w1), 0.012, 6)
            _peremychka(D, st, a0, a1, w1, u0, u1, v0, v1, kam=w1 < KR + 0.3, zap_l=zl, zap_r=zr)
            if w0 < F1:
                _podokonnik(D, st, a0, a1, w0, u0, u1, v0, v1)
        else:
            _peremychka(D, st, a0, a1, w1, u0, u1, v0, v1, kam=False, dver=True, zap_l=zl, zap_r=zr)
    _dveri(D, vse, u0, u1, v0, v1, F1)

    # ---------------- полы, перекрытие, потолок, лестница ----------------
    D.kor('poly', MOSH, ui0, ui1, vi0, vi1, 0.0, P, 0.004)
    D.kor('poly', DOSKI, ui0, ui0 + L_sh, vi0, st_v0, F1, F2)
    if st_v1 < vi1 - 0.05:
        D.kor('poly', DOSKI, ui0, ui0 + L_sh, st_v1, vi1, F1, F2)       # пол верхней площадки лестницы
    D.kor('poly', DOSKI, ui0 + L_sh, ui1, vi0, vi1, F1, F2)
    D.kor('poly', DOSKI, ui0, ui1, vi0, vi1, EV - 0.06, EV)            # потолок верха
    x = ui0 + L_sh + 0.5
    while x < ui1 - 0.2:
        v_end = kb_v0 - TV / 2 if x > kb_u0 else vi1
        D.brus('poly', BRUS, (x, vi0, F1 - 0.12), (x, v_end, F1 - 0.12), 0.2, 0.24, (1, 0, 0))
        x += sn(r.uniform(1.0, 1.2))
    D.brus('poly', BRUS, (ui0 + L_sh, (vi0 + kb_v0) / 2.0, F1 - 0.36), (ui1, (vi0 + kb_v0) / 2.0, F1 - 0.36), 0.3, 0.3, (0, 1, 0))
    n_st = max(10, int(round(podem / 0.19)))
    for k in range(n_st):                # ступень — столбик под своей проступью (28.09: коробки «до конца марша» мигали
        va = st_v0 + dl * k / n_st           # боковыми гранями в одной плоскости при чередовании доски и бруса)
        vb = st_v1 if k == n_st - 1 else st_v0 + dl * (k + 1) / n_st
        D.kor('poly', DOSKI if k % 2 else BRUS, ui0, ui0 + L_sh, va, vb, P, P + podem * (k + 1) / n_st, 0.006)
    # перила лестницы идут только до входа в коридор (kor_v0), чтобы выход на 2-й этаж оставался открыт
    v_perila_end = min(kor_v0, st_v1)
    k_end = max(0, int((v_perila_end - st_v0) / dl * n_st))
    for k in range(0, k_end + 1, 3):
        va = st_v0 + dl * k / n_st
        D.brus('poly', BRUS, (ui0 + L_sh - 0.06, va, P + podem * k / n_st), (ui0 + L_sh - 0.06, va, P + podem * k / n_st + 0.95),
               0.07, 0.07, (1, 0, 0))
    w_end = P + podem * (v_perila_end - st_v0) / dl
    D.brus('poly', BRUS, (ui0 + L_sh - 0.06, st_v0, P + 0.95), (ui0 + L_sh - 0.06, v_perila_end, w_end + 0.95), 0.08, 0.06, (1, 0, 0))
    D.brus('poly', BRUS, (ui0 + L_sh + 0.04, st_v0, F2 + 1.0), (ui0 + L_sh + 0.04, kor_v0, F2 + 1.0), 0.08, 0.07, (1, 0, 0))
    D.brus('poly', BRUS, (ui0 + 0.04, st_v0 + 0.04, F2 + 1.0), (ui0 + L_sh + 0.04, st_v0 + 0.04, F2 + 1.0), 0.08, 0.07, (0, 1, 0))
    vv = st_v0
    while vv < kor_v0:
        D.brus('poly', BRUS, (ui0 + L_sh + 0.04, vv, F2), (ui0 + L_sh + 0.04, vv, F2 + 1.0), 0.05, 0.05, (1, 0, 0), 0.004)
        vv += 0.3
    plan['lestnicy'].append({'vid': 'vnutr', 'b': [ui0, ui0 + L_sh, st_v0, st_v1], 'podem': podem, 'dlina': dl,
                             'ugol': round(math.degrees(math.atan2(podem, dl)), 1), 'shir': L_sh})

    # ---------------- перегородки, внутренние двери ----------------
    DV = STIL['dver_vys']
    vy = [[kb_u0 + 0.3, kb_u0 + 1.25, kb_v0 - 0.3, kb_v0 + 0.3, P, P + DV]]
    niz['dveri'] += [{'iz': 'ulica', 'v': 'zal', 'shir': dv_u1 - dv_u0}, {'iz': 'zal', 'v': 'povarnya', 'shir': 0.95}]
    plan['vnutr_dveri'].append({'etazh': 0, 'b': [kb_u0 + 0.3, kb_u0 + 1.25, kb_v0 - TV / 2, kb_v0 + TV / 2], 'v_komnatu': 1})
    if not kl_v_pr:
        vy.append([pov_u1 + 0.2, pov_u1 + 1.15, kb_v0 - 0.3, kb_v0 + 0.3, P, P + DV])
        niz['dveri'] += [{'iz': 'zal', 'v': 'kladovaya', 'shir': 0.95}, {'iz': 'kladovaya', 'v': 'dvor', 'shir': 1.0}]
        plan['vnutr_dveri'].append({'etazh': 0, 'b': [pov_u1 + 0.2, pov_u1 + 1.15, kb_v0 - TV / 2, kb_v0 + TV / 2], 'v_komnatu': 1})
    else:
        niz['dveri'] += [{'iz': 'povarnya', 'v': 'kladovaya', 'shir': 0.95}, {'iz': 'kladovaya', 'v': 'dvor', 'shir': 1.0}]
    D.stena('peregorodki', SHT, [kb_u0 - TV / 2, ui1, kb_v0 - TV / 2, kb_v0 + TV / 2, P, F1], vy)
    D.stena('peregorodki', SHT, [kb_u0 - TV / 2, kb_u0 + TV / 2, kb_v0 + TV / 2, vi1, P, F1], [])     # левая стенка поварни
    if not kl_v_pr:
        D.stena('peregorodki', SHT, [pov_u1 - TV / 2, pov_u1 + TV / 2, kb_v0 + TV / 2, vi1, P, F1], [])
    if pro_u0 is not None:
        niz['dveri'].append({'iz': 'zal', 'v': 'kuznya', 'shir': pro_u1 - pro_u0})
    plan['svyazi'].append(['ulica', 'kuznya'])            # кузня открыта к улице во всех композициях
    vy = []
    for k in komn:
        a = k['b'][0] + 0.12
        k['dver_kor'] = [a, a + 0.95]
        vy.append([a, a + 0.95, kor_v0 - 0.3, kor_v0 + 0.3, F2, F2 + min(DV, EV - F2 - 0.3)])
        verh['dveri'].append({'iz': 'koridor', 'v': k['id'], 'shir': 0.95})
        plan['vnutr_dveri'].append({'etazh': 1, 'b': [a, a + 0.95, kor_v0 - TV / 2, kor_v0 + TV / 2], 'v_komnatu': -1})
    D.stena('peregorodki', SHT, [polosa_u0 - TV, ui1, kor_v0 - TV / 2, kor_v0 + TV / 2, F2, EV], vy)
    D.stena('peregorodki', SHT, [polosa_u0 - TV, polosa_u0, vi0, kor_v0, F2, EV], [])
    for k in komn[1:]:
        D.stena('peregorodki', SHT, [k['b'][0] - TV, k['b'][0], vi0, kor_v0 - TV / 2, F2, EV], [])
    plan['etazhi'] = [niz, verh]

    # ---------------- кровля (вальма; у galereya передний скат продлён над галереей) ----------------
    g = p['gal_g']
    pered_ = (g + 0.3 - p['svs']) if kz == 'galereya' else 0.0
    if p['krysha'] == 'dvuskat':
        _dvuskat(D, p, u0, u1, v0, v1, EV, pered=pered_)
    else:
        _valma(D, p, u0, u1, v0, v1, EV, pered=pered_)
    WR = EV + ((v1 - v0) / 2.0) * tg

    def w_krovli(uu, vv_):
        if p['krysha'] == 'dvuskat':
            return min(EV + min(vv_ - v0, v1 - vv_) * tg, WR)
        dd = min(uu - u0, u1 - uu, vv_ - v0, v1 - vv_)
        return min(EV + dd * tg, WR)

    # ---------------- очаг зала, горн, одна труба ----------------
    w_gorna = Pk
    _ochag(D, S_in, ca, P, F1, F2, EV)
    _gorn(D, S_out, ca, w_gorna)
    tb = S_out.box(ca - 0.5, ca + 0.5, -0.9, -0.02)
    w_tr = max(w_krovli(min(max(x_, u0), u1), min(max(y_, v0), v1)) for x_ in (tb[0], tb[1]) for y_ in (tb[2], tb[3]))
    _truba(D, tb, EV - 0.3, w_tr)
    plan['ochagi'] = [{'vid': 'ochag_zala', 'rama': [S_in.os, S_in.lico, S_in.zn], 'a': ca, 'truba': True},
                      {'vid': 'gorn', 'rama': [S_out.os, S_out.lico, S_out.zn], 'a': ca, 'truba': 'ta_zhe'}]

    # ---------------- уровни и открытые пространства по композиции ----------------
    GL = 1.6
    if kz == 'naves':
        _pomost_i_krylco(D, u0, v0, P, NV0, kr_u0, kr_u1, F1, dv_u0, dv_u1)
        _vyveska(D, dv_u1 + 0.25, NV0 + 0.42, 2.5)
        _naves_kuzni(D, p, nk_u0, nk_u1, v0, P, NV0)
        LU0, LU1 = u1 + 0.1, u1 + 1.35
        vg0 = _lestnica_naruzh(D, LU0, LU1, 0.25, 1, F2, 34.0, 1.25)
        _galereya_boka(D, p, u1, vg0, v1, F2, EV)
        plan['lestnicy'].append({'vid': 'naruzh', 'ploshchadka': True, 'shir': 1.25})
        plan['svyazi'].append(['ulica', 'galereya'])
        plan['chasti'] += [{'imya': 'крыльцо', 'etazh': 0, 'b': [kr_u0, kr_u1, NV0, v0]},
                           {'imya': 'кузня', 'etazh': 0, 'b': [nk_u0, nk_u1, NV0, v0]},
                           {'imya': 'лестница', 'etazh': 0, 'b': [LU0, LU1 + 0.3, 0.25, vg0]},
                           {'imya': 'галерея', 'etazh': 1, 'b': [u1, u1 + p['gal_gl'], vg0, v1]}]
        kuz_kam = [[ca - 2.1, NV0 + 0.2, 1.75], [ca - 0.1, v0 - 0.5, P + 1.0]]
        bok_kam = [[u1 + 3.6, -2.8, 2.1], [u1 + 0.6, 3.2, 2.2]]
        kr_pered = NV0 - 0.25
    elif kz == 'galereya':
        _galereya_perednyaya(D, r, u0, u1, v0, P, F2, EV, g, dv_u0, dv_u1, tg)
        _vyveska(D, dv_u1 + 0.25, v0 - g + 0.13, 2.5)
        vf, vb = sn(v0 - g - 0.05), sn(ca + 1.6)
        _kuznya_prislon(D, u1, p['lp_w'], vf, vb, Pk, F2 + 0.2, tg_a)
        plan['chasti'] += [{'imya': 'крыльцо', 'etazh': 0, 'b': [u0, u1, v0 - g, v0]},
                           {'imya': 'галерея', 'etazh': 1, 'b': [u0, u1, v0 - g, v0]},
                           {'imya': 'кузня', 'etazh': 0, 'b': [u1, u1 + p['lp_w'], vf, vb]}]
        kuz_kam = [[u1 + 1.7, v0 - 3.0, 1.7], [u1 + 0.45, ca, Pk + 1.0]]
        bok_kam = [[u0 - 1.4, -3.3, 2.0], [u0 + 3.6, v0 - 0.6, 3.7]]
        kr_pered = v0 - g - 0.4
    elif kz == 'ugol':
        _pomost_i_krylco(D, u0, v0, P, NV0, kr_u0, kr_u1, F1, dv_u0, dv_u1)
        _kozyrek_i_vyveska(D, v0, P, NV0, dv_u0, dv_u1, F1)
        LU0, LU1 = u1 + 0.1, u1 + 1.35
        vb_l = sn(v1 - 0.15)
        vt1 = _lestnica_naruzh(D, LU0, LU1, vb_l, -1, F2, 36.0, 0.9)
        vt1 = max(vt1, v0 + 0.2)
        _terrasa_ugol(D, r, u1, v0, tf_u0, p['ter_gf'], p['ter_gs'], vt1, F2, Pk)
        plan['lestnicy'].append({'vid': 'naruzh', 'ploshchadka': True, 'shir': 1.25})
        plan['svyazi'].append(['ulica', 'galereya'])
        ve = v0 - p['ter_gf']
        plan['chasti'] += [{'imya': 'крыльцо', 'etazh': 0, 'b': [kr_u0, kr_u1, NV0, v0]},
                           {'imya': 'кузня', 'etazh': 0, 'b': [tf_u0, u1 + p['ter_gs'], ve, v0]},
                           {'imya': 'терраса', 'etazh': 1, 'b': [tf_u0, u1 + p['ter_gs'], ve, v0]},
                           {'imya': 'терраса', 'etazh': 1, 'b': [u1, u1 + p['ter_gs'], v0, vt1]},
                           {'imya': 'лестница', 'etazh': 0, 'b': [LU0, LU1 + 0.3, vt1, vb_l]}]
        kuz_kam = [[u1 + 1.3, ve - 2.9, 1.8], [ca + 0.3, v0 - 0.5, Pk + 1.1]]
        bok_kam = [[u1 + 3.0, -3.3, 2.3], [u1 + 0.1, v0 + 0.8, 3.3]]
        kr_pered = NV0 - 0.25
    else:
        kr_u1 = sn(u1 - 0.02)                                # крыльцо до пристройки — общий каменный цоколь (Астра)
        _pomost_i_krylco(D, u0, v0, P, NV0, kr_u0, kr_u1, F1, dv_u0, dv_u1)
        _kozyrek_i_vyveska(D, v0, P, NV0, dv_u0, dv_u1, F1)
        aw = p['pr_w']
        va0, va1 = sn(v0 - p['pr_d0']), sn(v1 - p['pr_d1'])
        ap = sn(ca + 1.5)
        _pristrojka(D, r, u1, v0, va0, va1, aw, ap, Pk, F2 + 0.35, tg_a, KR)
        niz['komnaty'].append({'id': 'kladovaya', 'imya': 'кладовая (пристройка)', 'b': [u1 + 0.02, u1 + aw - 0.45, ap + TV, va1 - 0.45]})
        plan['vnutr_dveri'].append({'etazh': 0, 'b': [u1 + aw - 1.75, u1 + aw - 0.75, ap, ap + TV], 'v_komnatu': 1})
        plan['svyazi'].append(['kuznya', 'kladovaya'])
        plan['chasti'] += [{'imya': 'крыльцо', 'etazh': 0, 'b': [kr_u0, kr_u1, NV0, v0]},
                           {'imya': 'кузня', 'etazh': 0, 'b': [u1, u1 + aw, va0, ap]}]
        kuz_kam = [[u1 + 1.45, va0 - 3.1, 1.7], [u1 + 0.45, ca, Pk + 1.0]]
        bok_kam = [[u1 + 2.7, -3.4, 1.9], [u1 + 0.9, va0 + 1.6, 2.4]]
        kr_pered = NV0 - 0.25

    # ---------------- против ровности: цоколь, камень, выпуски балок, кронштейны, каркас верха ----------------
    _cokol(D, u0, u1, v0, v1, vse)
    _kamen_zhivoj(D, r, u0, u1, v0, v1, KR, vse)
    _glyby_u_uglov(D, random.Random(p['zerno_melochej'] + 101), u0, u1, v0, v1,     # своё зерно: остальное не сдвигается
                   zanyato=[(u0 - 2.0, u1 + 3.0, v0 - 3.5, v0 + 0.2), (u1, u1 + 4.5, v0 - 3.5, v1 + 1.0)])
    bez_pered = [(u0 - 1.0, u1 + 1.0)] if kz == 'galereya' else ([(tf_u0 - 0.2, u1 + 1.0)] if kz == 'ugol' else [])
    _karkas_verha(D, r, u0, u1, v0, v1, F1, F2, EV, proemy_verh, bez_pered, kz == 'galereya', stavni=p['stavni'])

    # ---------------- нутро: зал (место у огня, общий стол, стойка), комнаты ----------------
    stol_c = _mebel_zala(D, r, S_in, ca, ui0, ui1, vi0, vi1, L_sh, kb_u0, kb_v0, pov_u1, P, F1, dv_u0, dv_u1, kl_v_pr)
    _mebel_povarni(D, kb_u0, kb_v0, pov_u1, vi1, ui1, P, F1, kl_v_pr)
    truba_verh = S_in.box(ca - 0.5, ca + 0.5, 0.0, 0.5)
    _mebel_komnat(D, r, komn, F2, vi0, kor_v0, truba_verh)
    _koridor(D, ui0, ui1, vi1, L_sh, kor_v0, F2, EV, kz)
    _melochi_ulicy(D, r, kz, kr_u0, kr_u1, v0, P, NV0, dv_u0, dv_u1)
    D.istochnik('zal', (ui0 + L_sh + ui1) / 2.0, (vi0 + kb_v0) / 2.0, F1 - 0.9, 2.5, 600.0, (255, 215, 175), False)
    D.istochnik('fonar', dv_u0 - 0.35, v0 - 0.25, P + 2.2, 4.0, 330.0, (255, 196, 140), False)

    # утварь Blacksmith Props — точки для dk1_utvar_fab_ue.py (в осях дома до отражения)
    plan['utvar'] = {'nakovalnya': list(S_out.p(ca - 0.1, 1.6, w_gorna)), 'kad': list(S_out.p(ca + 1.35, 0.7, w_gorna)),
                     'tochilo': list(S_out.p(ca - 1.6, 0.9, w_gorna))}
    plan['utvar'] = {k_: [sn(x_, 0.01) for x_ in v_] for k_, v_ in plan['utvar'].items()}
    plan['utvar_fab'] = _utvar_fab(S_out, ca, w_gorna, plan, kz, pro_u0, pro_u1)

    # ---------------- камеры и проход в дом ----------------
    dvc = (dv_u0 + dv_u1) / 2.0
    och = S_in.p(ca, 1.0, P + 0.8)
    E = (dvc - 0.1, vi0 + 1.0, P + GL)
    cel = _mezhdu(E, och, (stol_c[0], stol_c[1], P + 0.8))
    K = (ui0 + L_sh + 0.6, kb_v0 - 0.35, P + GL)
    km = komn[len(komn) // 2]
    kmc = (km['b'][0] + km['b'][1]) / 2.0
    plan['kamery'] = {
        'g-zal-ot-dveri': [list(E), list(cel)],
        'g-zal-k-ochagu': [list(K), list(och)],
        'g-kuznya': kuz_kam,
        'g-verh-koridor': [[ui0 + 0.7, vi1 - 0.65, F2 + GL], [ui1 - 0.3, vi1 - 0.7, F2 + 1.2]],
        'g-komnata': [[km['dver_kor'][0] + 0.45, kor_v0 - 0.35, F2 + 1.55], [kmc, vi0 + 0.4, F2 + 0.9]],
        'g-bok': bok_kam,
    }
    plan['vid_ot_vhoda'] = {'ot': [E[0], E[1]], 'ochag': [och[0], och[1]], 'stol': [stol_c[0], stol_c[1]], 'w': P + GL}
    plan['vidy'] = [{'imya': 'от входа на очаг', 'ot': [E[0], E[1]], 'na': [och[0], och[1]]},
                    {'imya': 'от входа на общий стол', 'ot': [E[0], E[1]], 'na': [stol_c[0], stol_c[1]]},
                    {'imya': 'от общего стола на очаг', 'ot': [K[0], K[1]], 'na': [och[0], och[1]]}]
    GLZ = 1.62
    och2 = S_in.p(ca, 0.6, P + 0.9)
    plan['prohod'] = [
        [0.0, [dvc, -6.0, GLZ], [dvc, v0 + 3.0, 1.9]],
        [3.5, [dvc, -2.4, GLZ], [dvc, v0 + 3.0, 1.9]],
        [5.2, [dvc, kr_pered, GLZ + P * 0.5], [dvc, v0 + 4.0, 1.9]],
        [6.6, [dvc - 0.05, v0 - 1.0, GLZ + P], [dvc, vi0 + 3.5, 1.8]],
        [7.9, [dvc - 0.1, v0 + 0.3, GLZ + P], [dvc + 0.3, vi1 - 0.5, 1.5]],
        [9.4, [dvc - 0.1, vi0 + 1.1, GLZ + P], list(cel)],
        [11.2, [dvc + 0.2, vi0 + 1.4, GLZ + P], list(och)],
        [13.0, [dvc + 0.35, vi0 + 1.55, GLZ + P], list(och2)],
    ]
    pasport = {'semejstvo': 'm-traktir-masterskaya', 'zemlya': 'mangala', 'zerno': zerno, 'sled': [SU, SV],
               'etazhi': 2, 'parametry': p, 'kompoz': kz, 'kompoz_imya': IMENA_KOMPOZ[kz], 'krysha': 'valmovaya' if p['krysha'] == 'valma' else 'dvuskatnaya',
               'nutro': 'polnoe'}
    plan['razmery'] = {'F1': F1, 'F2': F2, 'EV': EV, 'KR': KR, 'korpus': [u0, u1, v0, v1]}
    if p['s'] < 0:
        zerkalo_detalej(D.spisok, D.svet, SU)
        for k in plan['utvar']:
            plan['utvar'][k][0] = round(SU - plan['utvar'][k][0], 3)
        for x_ in plan['utvar_fab']:
            x_[2] = round(SU - x_[2], 3)
            x_[5] = round(180.0 - x_[5], 1)
        for k, (ot, na) in plan['kamery'].items():
            plan['kamery'][k] = [[SU - ot[0], ot[1], ot[2]], [SU - na[0], na[1], na[2]]]
        plan['prohod'] = [[t_, [SU - a[0], a[1], a[2]], [SU - b[0], b[1], b[2]]] for (t_, a, b) in plan['prohod']]
    return pasport, plan, D


# ======================================================================================================================

def _utvar_fab(S, ca, Pw, plan, kz, pro_u0, pro_u1):
    """Рабочая группа кузни (Астра 28.09: «горн → наковальня → инструмент»): наковальня перед горном, бадья, ящик с
    топором, лопата у горна — утварь набора Blacksmith Props. Каждая вещь — в первое место, где она целиком в кузне и
    не заслоняет проём в зал. → [(имя, сетка, u, v, w, поворот°)] в осях до отражения; поворот 0° — лицом к улице."""
    kuz = [ch['b'] for ch in plan['chasti'] if ch['imya'] == 'кузня']
    zapret = []
    if pro_u0 is not None:
        zapret.append((pro_u0 - 0.2, pro_u1 + 0.2, S.lico - 1.3, S.lico + 0.1) if S.os == 'u' else None)
    zapret = [z for z in zapret if z]
    vdol = 90.0 if S.os == 'u' else 0.0              # поворот «вдоль стены горна»
    out, zanyato = [], [S.box(ca - 0.85, ca + 0.85, 0.0, 1.1)]

    def postavit(imya, setka, kand, polu, ugol, w=None):
        for (a, d) in kand:
            c = S.t(a, d)
            b = (c[0] - polu[0], c[0] + polu[0], c[1] - polu[1], c[1] + polu[1])
            if not any(k[0] <= b[0] and b[1] <= k[1] and k[2] <= b[2] and b[3] <= k[3] for k in kuz):
                continue
            if any(_peresek2(b, z) for z in zanyato + zapret):
                continue
            zanyato.append(b)
            out.append([imya, setka, round(c[0], 3), round(c[1], 3), round(Pw if w is None else w, 3), ugol])
            return c
        return None
    pol = (lambda a, b: (a, b)) if S.os == 'u' else (lambda a, b: (b, a))
    postavit('nakovalnya', 'SM_Anvil/Meshes/SM_Anvil', [(ca - 0.1, 1.55), (ca - 0.1, 1.35), (ca + 0.3, 1.5)], pol(0.3, 0.3), vdol)
    postavit('kad', 'SM_WaterForgeBucket/Meshes/SM_WaterForgeBucket',
             [(ca + 1.45, 0.6), (ca - 1.55, 0.6), (ca - 1.3, 1.9), (ca + 1.3, 1.9)], (0.5, 0.5), 0.0)
    c = postavit('yashchik', 'SM_WoodBox/Meshes/SM_WoodBox', [(ca + 1.3, 1.55), (ca - 1.4, 1.55), (ca + 1.6, 0.35), (ca - 1.6, 0.4)],
                 pol(0.3, 0.25), vdol)
    if c:
        out.append(['topor', 'SM_WoodAxe/Meshes/SM_WoodAxe', out[-1][2], out[-1][3], None, vdol + 60.0])
    postavit('lopata', 'SM_Shovel/Meshes/SM_Shovel', [(ca - 0.98, 0.2), (ca + 0.98, 0.2)], (0.1, 0.1), vdol)
    return out


def _svobodno(a0, a1, zanyato):
    """Свободные куски отрезка [a0, a1] за вычетом занятых отрезков."""
    kuski = [(a0, a1)]
    for (z0, z1) in zanyato:
        novye = []
        for (x0, x1) in kuski:
            if z1 <= x0 or z0 >= x1:
                novye.append((x0, x1))
                continue
            if z0 > x0:
                novye.append((x0, z0))
            if z1 < x1:
                novye.append((z1, x1))
        kuski = novye
    return kuski


def _mezhdu(E, A, B):
    """Точка взгляда из E между A и B — по биссектрисе направлений (из двери видны и очаг, и общий стол)."""
    def ed(p):
        dx, dy = p[0] - E[0], p[1] - E[1]
        d = math.hypot(dx, dy) or 1.0
        return dx / d, dy / d
    a, b = ed(A), ed(B)
    x, y = a[0] + b[0], a[1] + b[1]
    d = math.hypot(x, y) or 1.0
    return (E[0] + 3.0 * x / d, E[1] + 3.0 * y / d, (A[2] + B[2]) / 2.0)


def _kuz_krysha(p, nk_u0, nk_u1, v0):
    """Высота кровли навеса кузни у стены корпуса в точке u (для окон верха над навесом)."""
    NWE = 3.3
    uk = (nk_u0 + nk_u1) / 2.0
    tg = math.tan(math.radians(p['kuz_uklon']))

    def h(u):
        if u < nk_u0 - 0.25 or u > nk_u1 + 0.25:
            return 0.0
        return NWE + (min(u, 2 * uk - u) - (nk_u0 - 0.25)) * tg if u <= uk else NWE + ((nk_u1 + 0.25) - u) * tg
    return h


def _peremychka(D, st, a0, a1, w1, u0, u1, v0, v1, kam=False, dver=False, zap_l=0.18, zap_r=0.18):
    m = KAM if kam else BRUS
    h = 0.22 if not dver else 0.26
    # Опускаем низ перемычки на 1.5 см в проём, чтобы он не совпадал с верхним откосом стены (z-fighting)
    w_niz = round(w1 - 0.015, 4)
    if st == 'ul':
        D.kor('obolochka', m, a0 - zap_l, a1 + zap_r, v0 - 0.05, v0 + 0.14, w_niz, w1 + h, 0.012)
    elif st == 'zad':
        D.kor('obolochka', m, a0 - zap_l, a1 + zap_r, v1 - 0.14, v1 + 0.05, w_niz, w1 + h, 0.012)
    elif st == 'sev':
        D.kor('obolochka', m, u0 - 0.05, u0 + 0.14, a0 - zap_l, a1 + zap_r, w_niz, w1 + h, 0.012)
    else:
        D.kor('obolochka', m, u1 - 0.14, u1 + 0.05, a0 - zap_l, a1 + zap_r, w_niz, w1 + h, 0.012)


def _podokonnik(D, st, a0, a1, w0, u0, u1, v0, v1):
    # Каменная консоль-основание под деревянным подоконником (от w0 - 0.08 до w0 - 0.035)
    w_kam_top = round(w0 - 0.035, 4)
    if st == 'ul':
        D.kor('obolochka', KAM, a0 - 0.08, a1 + 0.08, v0 - 0.09, v0 + 0.05, w0 - 0.08, w_kam_top, 0.01)
    elif st == 'zad':
        D.kor('obolochka', KAM, a0 - 0.08, a1 + 0.08, v1 - 0.05, v1 + 0.09, w0 - 0.08, w_kam_top, 0.01)
    elif st == 'sev':
        D.kor('obolochka', KAM, u0 - 0.09, u0 + 0.05, a0 - 0.08, a1 + 0.08, w0 - 0.08, w_kam_top, 0.01)
    else:
        D.kor('obolochka', KAM, u1 - 0.05, u1 + 0.09, a0 - 0.08, a1 + 0.08, w0 - 0.08, w_kam_top, 0.01)


VYSTUP_KOSYAKA = 0.02      # косяк стоит в проёме на 2 см ближе откоса стены: грани не в одной плоскости


def _dveri(D, proemy, u0, u1, v0, v1, F1):
    """Полотна дверей: вход зала и двери на галерею распахнуты внутрь к стене, задняя и боковые — приоткрыты."""
    for (st, a0, a1, w0, w1, vid) in proemy:
        if not vid.startswith('dver'):
            continue
        # Зазор снизу двери над полом 1.5 см, чтобы низ полотна не совпадал с плоскостью чистого пола
        w_bot = w0 + 0.015
        h = w1 - w_bot - 0.015
        shir = a1 - a0
        if st == 'ul':
            if vid == 'dver_vhod':
                pet = (a1 - 0.05, v0 + T - 0.05)
                ug = math.radians(14.0)                  # распахнута к стене зала: проход свободен (проход камерой 28.09)
            else:
                # дверь на галерею: распахивается внутрь спальни вдоль боковой стены (+v),
                # а не направо (+u) сквозь межкомнатные перегородки поперек соседних окон и наружу дома
                pet = (a1 - 0.05, v0 + T - 0.05)
                ug = math.radians(105.0)                 # приоткрыта внутрь комнаты вдоль правой стены
        elif st == 'zad':
            pet = (a0 + 0.05, v1 - T + 0.05)
            ug = math.radians(-60.0)
        elif st == 'jug':
            pet = (u1 - T + 0.05, a0 + 0.05)
            ug = math.radians(160.0)
        else:
            continue
        kon = (pet[0] + shir * math.cos(ug), pet[1] + shir * math.sin(ug))
        w_mid = w_bot + h / 2.0
        D.brus('obolochka', BRUS, (pet[0], pet[1], w_mid), (kon[0], kon[1], w_mid), h, 0.06, (0, 0, 1), 0.006)
        # коробка двери: косяки выступают в проём на VYSTUP_KOSYAKA и примыкают к низу перемычки (w1 - 0.015)
        # снизу начинаются на 5 мм выше уровня пола, чтобы не совпадать с гранью пола (z-fighting)
        kosyaki = ((a0 - 0.14, a0 + VYSTUP_KOSYAKA), (a1 - VYSTUP_KOSYAKA, a1 + 0.14))
        if st in ('ul', 'zad'):
            vv0, vv1 = (v0 - 0.06, v0 + 0.1) if st == 'ul' else (v1 - 0.1, v1 + 0.06)
            for (k0, k1) in kosyaki:
                D.kor('obolochka', BRUS, k0, k1, vv0, vv1, w0 + 0.005, w1 - 0.015, 0.01)
            # деревянный порог дверного проёма
            D.kor('obolochka', BRUS, a0 - 0.02, a1 + 0.02, vv0, vv1, w0 - 0.03, w0 + 0.012, 0.008)
        else:
            for (k0, k1) in kosyaki:
                D.kor('obolochka', BRUS, u1 - 0.1, u1 + 0.06, k0, k1, w0 + 0.005, w1 - 0.015, 0.01)
            # деревянный порог дверного проёма
            D.kor('obolochka', BRUS, u1 - 0.1, u1 + 0.06, a0 - 0.02, a1 + 0.02, w0 - 0.03, w0 + 0.012, 0.008)


def _valma(D, p, u0, u1, v0, v1, EV, pered=0.0):
    """Вальмовая кровля над корпусом: два ската-трапеции, две вальмы-треугольника, свес, черепица у карнизов, конёк,
    подшива, выпуски стропил под свесом. pered > 0 — передний скат продлён тем же уклоном ещё на pered за свес (над
    галереей: одна плоскость, карниз ниже)."""
    tg = math.tan(math.radians(p['uklon']))
    c, s = math.cos(math.radians(p['uklon'])), math.sin(math.radians(p['uklon']))
    sv = p['svs']
    Db = v1 - v0
    vc = (v0 + v1) / 2.0
    WR = EV + (Db / 2.0) * tg
    EVe = EV - sv * tg
    ur0, ur1 = u0 + Db / 2.0, u1 - Db / 2.0
    A, B = (u0 - sv, v0 - sv, EVe), (u1 + sv, v0 - sv, EVe)
    C, Dd = (u1 + sv, v1 + sv, EVe), (u0 - sv, v1 + sv, EVe)
    R0, R1 = (ur0, vc, WR), (ur1, vc, WR)
    tol = 0.16
    D.plita('krysha', CHER, [A, B, R1, R0], tol)
    D.plita('krysha', CHER, [C, Dd, R0, R1], tol)
    D.plita('krysha', CHER, [Dd, A, R0], tol)
    D.plita('krysha', CHER, [B, C, R1], tol)
    D.cil_os('krysha', CHER, (ur0 - 0.05, vc, WR + 0.06), (ur1 + 0.05, vc, WR + 0.06), 0.13, 6)
    for (x, y) in ((A, R0), (B, R1), (C, R1), (Dd, R0)):
        D.cil_os('krysha', CHER, (x[0], x[1], x[2] + 0.06), (y[0], y[1], y[2] + 0.06), 0.1, 6)
    zap = 0.75
    if pered > 0:
        e = sv + pered
        We = EV - e * tg
        A2, B2 = (u0 - sv, v0 - e, We), (u1 + sv, v0 - e, We)
        D.plita('krysha', CHER, [A2, B2, B, A], tol)
        D.cherepica(v0 - e, We, c, s, -s, c, u0 - sv + 0.2, u1 + sv - 0.2, ryadov=4, os_karniza='u')
        for (x, y) in ((A, A2), (B, B2)):             # торцы продления — доска по наклонному краю
            D.brus('krysha', BRUS, (x[0], x[1], x[2] - 0.12), (y[0], y[1], y[2] - 0.12), 0.08, 0.28, (1, 0, 0), 0.01)
        kraya = ((A2, B2), (B, C), (C, Dd), (Dd, A))
    else:
        D.cherepica(v0 - sv, EVe, c, s, -s, c, u0 - sv + zap, u1 + sv - zap, ryadov=4, os_karniza='u')
        kraya = ((A, B), (B, C), (C, Dd), (Dd, A))
    D.cherepica(v1 + sv, EVe, -c, s, s, c, u0 - sv + zap, u1 + sv - zap, ryadov=3, os_karniza='u')
    D.cherepica(u0 - sv, EVe, c, s, -s, c, v0 - sv + zap, v1 + sv - zap, ryadov=3, os_karniza='v')
    D.cherepica(u1 + sv, EVe, -c, s, s, c, v0 - sv + zap, v1 + sv - zap, ryadov=3, os_karniza='v')
    # подшива свеса и ветровая доска по карнизу — толщина кровли читается с земли (Астра: «тонкие навесы»)
    for (a, b) in kraya:
        D.brus('krysha', BRUS, (a[0], a[1], a[2] - 0.2), (b[0], b[1], b[2] - 0.2), 0.08, 0.26, (0, 0, 1), 0.01)
    _vypuski_stropil(D, tg, u0, u1, v0, v1, EV, sv, pered)


def _dvuskat(D, p, u0, u1, v0, v1, EV, pered=0.0):
    """Двускатная кровля над корпусом (паспорт 'krysha': 'dvuskat' — как на рисунке дома-кузни Астры 27.09): конёк
    вдоль фасада, кровля выходит за щипцы на fr; щипцы — треугольники извести до ската со стойкой и раскосами тёмного
    бруса; ветровые доски по наклонным краям, черепица у обоих карнизов, подшива карнизов, выпуски прогонов на щипцах,
    выпуски стропил под свесом. pered > 0 — передний скат продлён над галереей (как у вальмы)."""
    tg = math.tan(math.radians(p['uklon']))
    c, s = math.cos(math.radians(p['uklon'])), math.sin(math.radians(p['uklon']))
    sv = p['svs']
    fr = sn(min(0.6, max(0.4, sv * 0.8)))                # вынос за щипец — без новых вытяжек зерна
    Db = v1 - v0
    vc = (v0 + v1) / 2.0
    WR = EV + (Db / 2.0) * tg
    EVe = EV - sv * tg
    a0, a1 = u0 - fr, u1 + fr
    tol = 0.16
    A, B = (a0, v0 - sv, EVe), (a1, v0 - sv, EVe)
    C, Dd = (a1, v1 + sv, EVe), (a0, v1 + sv, EVe)
    R0, R1 = (a0, vc, WR), (a1, vc, WR)
    D.plita('krysha', CHER, [A, B, R1, R0], tol)
    D.plita('krysha', CHER, [C, Dd, R0, R1], tol)
    D.cil_os('krysha', CHER, (a0 - 0.05, vc, WR + 0.06), (a1 + 0.05, vc, WR + 0.06), 0.13, 6)
    zap = 0.25
    if pered > 0:                                        # над галереей передний скат длиннее, карниз ниже
        e = sv + pered
        We = EV - e * tg
        A2, B2 = (a0, v0 - e, We), (a1, v0 - e, We)
        D.plita('krysha', CHER, [A2, B2, B, A], tol)
        D.cherepica(v0 - e, We, c, s, -s, c, a0 + zap, a1 - zap, ryadov=4, os_karniza='u')
        v_pr, w_pr = v0 - e, We
    else:
        D.cherepica(v0 - sv, EVe, c, s, -s, c, a0 + zap, a1 - zap, ryadov=4, os_karniza='u')
        v_pr, w_pr = v0 - sv, EVe
    D.cherepica(v1 + sv, EVe, -c, s, s, c, a0 + zap, a1 - zap, ryadov=3, os_karniza='u')
    for a in (a0 + 0.04, a1 - 0.04):                     # ветровые доски по наклонным краям
        for (vk, wk) in ((v_pr, w_pr), (v1 + sv, EVe)):
            D.brus('krysha', BRUS, (a, vk, wk - 0.12), (a, vc, WR - 0.12), 0.08, 0.28, (1, 0, 0), 0.01)
    for (vk, wk) in ((v_pr, w_pr), (v1 + sv, EVe)):      # подшива карнизов
        D.brus('krysha', BRUS, (a0, vk, wk - 0.2), (a1, vk, wk - 0.2), 0.08, 0.26, (0, 0, 1), 0.01)
    ot = 0.22                                            # щипец — под скатом, внутри толщи кровли
    for (g0, g1) in ((u0, u0 + T), (u1 - T, u1)):
        D.profil('obolochka', SHT, [(v0, EV - 0.02), (v1, EV - 0.02), (vc, WR - ot)], 'vw', g0, g1)
    for (lico, zn, a_kr) in ((u0, -1, a0), (u1, 1, a1)):
        x = lico + zn * 0.06                             # брус щипца по лицу: стойка под коньком и два раскоса
        D.brus('obolochka', BRUS, (x, vc, EV - 0.05), (x, vc, WR - ot - 0.08), 0.18, 0.2, (0, 1, 0))
        dl = Db * 0.28
        for zz in (-1, 1):
            D.brus('obolochka', BRUS, (x, vc + zz * dl, EV + 0.02), (x, vc, EV + (WR - EV) * 0.55), 0.15, 0.18, (0, 1, 0))
        konec = a_kr - zn * 0.08                         # выпуски прогонов — конёк и середины скатов
        for (vv, ww) in ((vc, WR - 0.34), (v0 + Db * 0.25, EV + Db * 0.25 * tg - 0.3), (v1 - Db * 0.25, EV + Db * 0.25 * tg - 0.3)):
            D.brus('krysha', BRUS, (lico - zn * 0.1, vv, ww), (konec, vv, ww), 0.14, 0.16, (0, 1, 0), 0.01)
    _vypuski_stropil(D, tg, u0, u1, v0, v1, EV, sv, pered, storony=('ul', 'zad'))


def _vypuski_stropil(D, tg, u0, u1, v0, v1, EV, sv, pered, storony=('ul', 'zad', 'sev', 'jug')):
    """Концы стропил под свесом через 0,6 м — ряд теней под кровлей (Астра 28.09: «усиль тень под кровлей»).
    storony — у двускатной только карнизы ('ul', 'zad'): на щипцах стропил нет."""
    c = 1.0 / math.sqrt(1.0 + tg * tg)
    niz = 0.16 / c + 0.07
    for (st, a0, a1, lico, zn, e) in (('ul', u0 + 0.35, u1 - 0.35, v0, -1, sv + pered), ('zad', u0 + 0.35, u1 - 0.35, v1, 1, sv),
                                       ('sev', v0 + 0.35, v1 - 0.35, u0, -1, sv), ('jug', v0 + 0.35, v1 - 0.35, u1, 1, sv)):
        if st not in storony:
            continue
        a = a0
        while a <= a1 + 1e-6:
            d0, d1 = -0.1, e - 0.1
            w0, w1 = EV - d0 * tg - niz, EV - d1 * tg - niz
            if st in ('ul', 'zad'):
                D.brus('krysha', BRUS, (a, lico + zn * d0, w0), (a, lico + zn * d1, w1), 0.09, 0.13, (1, 0, 0), 0.01)
            else:
                D.brus('krysha', BRUS, (lico + zn * d0, a, w0), (lico + zn * d1, a, w1), 0.09, 0.13, (0, 1, 0), 0.01)
            a += 0.6


def _prislon_krysha(D, u_st, shir, vf, vb, Hw, tg, tol=0.14):
    """Прислонная кровля с вальмами на торцах — половина вальмы у стены корпуса (u = u_st), скат наружу (+u): то же
    семейство кровель, ниже карниза корпуса (Астра: «крыши образуют две ступени»). shir — от стены до карниза (со
    свесом), vf/vb — передний и задний карниз. → высота карниза."""
    uo = u_st + shir
    He = Hw - shir * tg
    c, s = math.cos(math.atan(tg)), math.sin(math.atan(tg))
    vh0, vh1 = vf + shir, vb - shir
    if vh1 < vh0 + 0.1:
        vm = (vf + vb) / 2.0
        vh0 = vh1 = vm
        Hw = He + (vm - vf) * tg
    D.plita('krysha', CHER, [(uo, vf, He), (uo, vb, He), (u_st, vh1, Hw), (u_st, vh0, Hw)], tol)
    D.plita('krysha', CHER, [(u_st, vf, He), (uo, vf, He), (u_st, vh0, Hw)], tol)
    D.plita('krysha', CHER, [(uo, vb, He), (u_st, vb, He), (u_st, vh1, Hw)], tol)
    D.cil_os('krysha', CHER, (uo, vf, He + 0.05), (u_st, vh0, Hw + 0.05), 0.08, 6)
    D.cil_os('krysha', CHER, (uo, vb, He + 0.05), (u_st, vh1, Hw + 0.05), 0.08, 6)
    if vh1 > vh0:
        D.kor('krysha', CHER, u_st, u_st + 0.14, vh0, vh1, Hw - 0.06, Hw + 0.07)          # примыкание к стене
    D.cherepica(uo, He, -c, s, s, c, vf + 0.45, vb - 0.45, ryadov=3, os_karniza='v')
    D.cherepica(vf, He, c, s, -s, c, u_st + 0.25, uo - 0.4, ryadov=3, os_karniza='u')
    D.cherepica(vb, He, -c, s, s, c, u_st + 0.25, uo - 0.4, ryadov=3, os_karniza='u')
    for (a, b) in (((u_st, vf), (uo, vf)), ((uo, vf), (uo, vb)), ((uo, vb), (u_st, vb))):
        D.brus('krysha', BRUS, (a[0], a[1], He - 0.18), (b[0], b[1], He - 0.18), 0.08, 0.24, (0, 0, 1), 0.01)
    # стропила изнутри — от стены к карнизу через 0,7 м
    niz = tol / c + 0.07
    vv = vf + 0.5
    while vv < vb - 0.4:
        D.brus('krysha', BRUS, (u_st, vv, min(Hw, He + (min(vv - vf, vb - vv)) * tg) - niz), (uo - 0.1, vv, He + 0.1 * tg - niz),
               0.09, 0.13, (0, 1, 0), 0.01)
        vv += 0.7
    return He


def _ochag(D, S, ca, P, F1, F2, EV):
    """Очаг зала у стены (рама S — внутреннее лицо, d — в комнату): под, топка, полка-матица, короб трубы в оба этажа,
    поленья и угли (светятся), котёл на перекладине."""
    S.kor(D, 'mebel', KAM, ca - 0.95, ca + 0.95, 0.0, 0.8, P, P + 0.3, 0.012)
    b = S.box(ca - 0.85, ca + 0.85, 0.0, 0.7)
    vy = S.box(ca - 0.5, ca + 0.5, 0.2, 0.9)
    D.stena('mebel', KAM, [b[0], b[1], b[2], b[3], P + 0.3, P + 1.45], [[vy[0], vy[1], vy[2], vy[3], P + 0.3, P + 1.1]])
    S.kor(D, 'mebel', BRUS, ca - 1.0, ca + 1.0, 0.0, 0.85, P + 1.45, P + 1.58, 0.012)       # полка-матица
    S.kor(D, 'mebel', KAM, ca - 0.6, ca + 0.6, 0.0, 0.55, P + 1.58, F1, 0.012)              # короб трубы
    S.kor(D, 'mebel', KAM, ca - 0.45, ca + 0.45, 0.0, 0.45, F2, EV, 0.012)                  # короб трубы наверху
    for k in range(3):
        D.cil_os('mebel', BRUS, S.p(ca - 0.3 + k * 0.25, 0.35, P + 0.36), S.p(ca - 0.2 + k * 0.22, 0.65, P + 0.4), 0.06, 7)
    S.kor(D, 'mebel', UGLI, ca - 0.32, ca + 0.32, 0.3, 0.62, P + 0.3, P + 0.34)
    D.cil_os('mebel', ZHEL, S.p(ca - 0.45, 0.45, P + 1.0), S.p(ca + 0.45, 0.45, P + 1.0), 0.02, 6)          # перекладина
    c = S.p(ca, 0.45, 0.0)
    D.cil('mebel', ZHEL, c[0], c[1], P + 0.55, 0.2, 0.28, 12, 0.16)                                       # котёл
    D.cil_os('mebel', ZHEL, S.p(ca, 0.45, P + 0.83), S.p(ca, 0.45, P + 1.0), 0.008, 4)
    # на полке — кувшины и миски
    for k, x_ in enumerate((-0.7, -0.35, 0.4, 0.75)):
        q = S.p(ca + x_, 0.45, 0.0)
        if k % 2:
            D.cil('mebel', KAM, q[0], q[1], P + 1.58, 0.08, 0.24, 10, 0.05)
        else:
            D.cil('mebel', ZHEL, q[0], q[1], P + 1.58, 0.1, 0.05, 10)
    D.istochnik('ochag', *S.p(ca, 0.42, P + 0.42), 2.4, 190.0, (255, 145, 75), True)


def _gorn(D, S, ca, Pw):
    """Горн у наружного лица той же стены: тумба, угли низко (светятся), тёмный железный колпак, дымоход в стену; за
    горном — огнеупорная кладка до колпака: огонь ложится на камень, фактура видна (Астра 28.09: «сосредоточь яркость на
    углях и ближайшей кладке, сохрани фактуру стены»)."""
    S.kor(D, 'mebel', KAM, ca - 1.05, ca + 1.05, -0.01, 0.07, Pw + 0.8, Pw + 2.75, 0.01)
    S.kor(D, 'mebel', KAM, ca - 0.8, ca + 0.8, 0.0, 1.05, Pw, Pw + 0.82, 0.02)
    S.kor(D, 'mebel', KAM, ca - 0.85, ca + 0.85, 0.0, 1.1, Pw + 0.82, Pw + 0.9, 0.012)
    S.kor(D, 'mebel', ZHEL, ca - 0.4, ca + 0.4, 0.25, 0.8, Pw + 0.9, Pw + 0.93)
    for k in range(5):
        q = S.p(ca - 0.3 + k * 0.15, 0.52 + 0.05 * (k % 2), Pw + 0.96)
        D.sfera('mebel', UGLI, q[0], q[1], q[2], 0.09, (1.0, 1.0, 0.4), 3)
    kolpak = [(ca - 0.8, Pw + 1.75), (ca + 0.8, Pw + 1.75), (ca + 0.3, Pw + 2.55), (ca - 0.3, Pw + 2.55)]
    S.profil(D, 'mebel', ZHEL, kolpak, 0.0, 1.0, 0.01)
    S.kor(D, 'mebel', KAM, ca - 0.3, ca + 0.3, 0.0, 0.45, Pw + 2.55, Pw + 3.0, 0.01)
    # клещи и кочерга у горна
    D.cil_os('mebel', ZHEL, S.p(ca + 0.9, 0.3, Pw), S.p(ca + 0.95, 0.35, Pw + 0.95), 0.012, 4)
    D.cil_os('mebel', ZHEL, S.p(ca + 1.0, 0.25, Pw), S.p(ca + 1.03, 0.3, Pw + 1.0), 0.012, 4)
    D.istochnik('gorn', *S.p(ca, 0.62, Pw + 1.02), 2.0, 160.0, (255, 120, 45), True)


def _truba(D, box, w0, w_krysha):
    """Оголовок трубы над кровлей: ствол, пояс, два столбика и шапка."""
    tu0, tu1, tv0, tv1 = box
    verh = max(w_krysha + 1.1, w0 + 1.5)
    D.kor('krysha', KAM, tu0, tu1, tv0, tv1, w0, verh, 0.012)
    D.kor('krysha', KAM, tu0 - 0.08, tu1 + 0.08, tv0 - 0.08, tv1 + 0.08, verh, verh + 0.12, 0.01)
    if tu1 - tu0 >= tv1 - tv0:
        for a in (tu0 + 0.08, tu1 - 0.28):
            D.kor('krysha', KAM, a, a + 0.2, tv0 + 0.08, tv1 - 0.08, verh + 0.12, verh + 0.38)
    else:
        for a in (tv0 + 0.08, tv1 - 0.28):
            D.kor('krysha', KAM, tu0 + 0.08, tu1 - 0.08, a, a + 0.2, verh + 0.12, verh + 0.38)
    D.kor('krysha', KAM, tu0, tu1, tv0, tv1, verh + 0.38, verh + 0.48, 0.01)


def _cokol(D, u0, u1, v0, v1, proemy):
    """Каменный цоколь-пояс у земли — низ читается основанием (Астра 28.09: «выдели каменный низ»)."""
    h, vy = 0.32, 0.07
    dveri = [(st, a0, a1) for (st, a0, a1, w0, w1, vid) in proemy if vid.startswith(('dver', 'proem')) and w0 < 1.2]
    for st, a_nach, a_kon in (('ul', u0 - vy, u1 + vy), ('zad', u0 - vy, u1 + vy), ('sev', v0, v1), ('jug', v0, v1)):
        for (x0, x1) in _svobodno(a_nach, a_kon, [(a0 - 0.02, a1 + 0.02) for (s_, a0, a1) in dveri if s_ == st]):
            if x1 - x0 < 0.05:
                continue
            if st == 'ul':
                D.kor('obolochka', KAM, x0, x1, v0 - vy, v0 + 0.1, 0.0, h, 0.02)
            elif st == 'zad':
                D.kor('obolochka', KAM, x0, x1, v1 - 0.1, v1 + vy, 0.0, h, 0.02)
            elif st == 'sev':
                D.kor('obolochka', KAM, u0 - vy, u0 + 0.1, x0, x1, 0.0, h, 0.02)
            else:
                D.kor('obolochka', KAM, u1 - 0.1, u1 + vy, x0, x1, 0.0, h, 0.02)


def _kozyrek_i_vyveska(D, v0, P, NV0, dv_u0, dv_u1, F1):
    """Вход яснее (Астра 28.09): над дверью — щипцовый козырёк поверх навеса крыльца на двух столбах, щипец зашит
    доской; рядом — вывеска трактира на кронштейне."""
    hg0, hg1 = dv_u0 - 0.45, dv_u1 + 0.45
    hc = (hg0 + hg1) / 2.0
    vf = NV0 - 0.12
    we = 3.05
    wr = we + (hc - hg0) * math.tan(math.radians(40.0))
    for (a, b) in ((hg0, hc), (hg1, hc)):
        D.plita('obolochka', CHER, [(a, vf, we), (b, vf, wr), (b, v0, wr), (a, v0, we)], 0.14)
    D.cil_os('obolochka', CHER, (hc, vf - 0.05, wr + 0.05), (hc, v0, wr + 0.05), 0.09, 6)
    D.profil('obolochka', DOSKI, [(hg0 + 0.12, we - 0.08), (hg1 - 0.12, we - 0.08), (hc, wr - 0.14)], 'uw', vf + 0.06, vf + 0.12, 0.005)
    for x_ in (hg0 + 0.14, hg1 - 0.14):
        D.brus('obolochka', BRUS, (x_, vf + 0.25, P * 0.5), (x_, vf + 0.25, we - 0.05), 0.18, 0.18, (1, 0, 0))
    D.brus('obolochka', BRUS, (hg0 + 0.05, vf + 0.25, we - 0.12), (hg1 - 0.05, vf + 0.25, we - 0.12), 0.16, 0.2, (0, 1, 0))
    # вывеска: кронштейн от столба козырька наружу, доска на двух цепях
    xs = hg1 - 0.14
    D.cil_os('obolochka', ZHEL, (xs, vf + 0.25, 2.55), (xs + 0.85, vf + 0.25, 2.55), 0.02, 6)
    for dx in (0.3, 0.75):
        D.cil_os('obolochka', ZHEL, (xs + dx, vf + 0.25, 2.55), (xs + dx, vf + 0.25, 2.38), 0.006, 4)
    D.kor('obolochka', KRAS, xs + 0.22, xs + 0.83, vf + 0.22, vf + 0.28, 1.95, 2.38, 0.01)
    D.kor('obolochka', ZHEL, xs + 0.2, xs + 0.85, vf + 0.21, vf + 0.29, 2.36, 2.4)


def _vyveska(D, u, v, w):
    """Вывеска трактира на кронштейне: железный прут наружу, доска на двух цепях."""
    D.cil_os('obolochka', ZHEL, (u, v, w), (u + 0.8, v, w), 0.02, 6)
    for dx in (0.25, 0.7):
        D.cil_os('obolochka', ZHEL, (u + dx, v, w), (u + dx, v, w - 0.17), 0.006, 4)
    D.kor('obolochka', KRAS, u + 0.17, u + 0.78, v - 0.03, v + 0.03, w - 0.6, w - 0.17, 0.01)
    D.kor('obolochka', ZHEL, u + 0.15, u + 0.8, v - 0.04, v + 0.04, w - 0.19, w - 0.15)


def _pomost_i_krylco(D, u0, v0, P, NV0, kr_u0, kr_u1, F1, dv_u0, dv_u1):
    """Крыльцо зала: помост на высоте пола, ступени, односкатный навес на столбах с каменными базами."""
    D.kor('obolochka', MOSH, kr_u0, kr_u1 + 0.02, NV0 + 0.15, v0 + 0.02, 0.0, P, 0.01)
    a = sn(dv_u0 - 0.6)
    D.kor('obolochka', MOSH, a, dv_u1 + 0.6, NV0 - 0.35, NV0 + 0.16, 0.0, P * 0.5, 0.01)
    D.kor('obolochka', MOSH, a + 0.1, dv_u1 + 0.5, NV0 - 0.05, NV0 + 0.16, P * 0.5, P, 0.01)
    wv0, wv1 = F1 + 0.05, 2.95
    D.plita('obolochka', CHER, [(kr_u0 - 0.2, v0, wv0), (kr_u1, v0, wv0), (kr_u1, NV0 + 0.1, wv1),
                                 (kr_u0 - 0.2, NV0 + 0.1, wv1)], 0.2)
    D.brus('obolochka', BRUS, (kr_u0 - 0.2, NV0 + 0.08, wv1 - 0.18), (kr_u1, NV0 + 0.08, wv1 - 0.18), 0.08, 0.26, (0, 0, 1))
    n = max(3, int(round((kr_u1 - kr_u0) / 2.0)) + 1)
    stolby = [kr_u0 + 0.15 + (kr_u1 - kr_u0 - 0.3) * k / (n - 1) for k in range(n)]
    stolby = [x for x in stolby if not (dv_u0 - 0.15 < x < dv_u1 + 0.15)]
    for uu in stolby:
        D.kor('obolochka', KAM, uu - 0.22, uu + 0.22, NV0 + 0.2, NV0 + 0.64, P, P + 0.42, 0.02)
        D.brus('obolochka', BRUS, (uu, NV0 + 0.42, P + 0.42), (uu, NV0 + 0.42, wv1 + 0.02), 0.22, 0.22, (1, 0, 0))
        D.brus('obolochka', BRUS, (uu + 0.08, NV0 + 0.42, wv1 - 0.55), (uu + 0.55, NV0 + 0.42, wv1 - 0.02), 0.12, 0.12, (0, 1, 0))
    D.brus('obolochka', BRUS, (kr_u0 - 0.2, NV0 + 0.42, wv1 + 0.1), (kr_u1, NV0 + 0.42, wv1 + 0.1), 0.2, 0.24, (0, 1, 0))
    k = 0
    while kr_u0 + k * 0.6 < kr_u1:
        uu = kr_u0 + k * 0.6
        D.brus('obolochka', BRUS, (uu, v0 - 0.05, wv0 - 0.14), (uu, NV0 + 0.15, wv1 - 0.06), 0.08, 0.14, (1, 0, 0), 0.008)
        k += 1


def _naves_kuzni(D, p, nk_u0, nk_u1, v0, P, NV0):
    """Помост кузни (ниже пола зала на ступень) и двускатный навес щипцом к улице с треугольной фермой."""
    Pk = sn(P - 0.15)
    D.kor('obolochka', MOSH, nk_u0 - 0.1, nk_u1, NV0 + 0.1, v0 + 0.02, 0.0, Pk, 0.01)
    D.kor('obolochka', MOSH, nk_u0 + 0.7, nk_u1 - 0.7, NV0 - 0.3, NV0 + 0.12, 0.0, Pk * 0.5, 0.01)
    NWE = 3.3
    uk = (nk_u0 + nk_u1) / 2.0
    tg = math.tan(math.radians(p['kuz_uklon']))
    NWK = NWE + (uk - nk_u0 + 0.25) * tg
    e0, e1 = nk_u0 - 0.25, nk_u1 + 0.25
    for (ua, ub) in ((e0, uk), (e1, uk)):
        D.plita('obolochka', CHER, [(ua, NV0 - 0.05, NWE - 0.1), (ua, v0 + 0.02, NWE - 0.1), (ub, v0 + 0.02, NWK),
                                    (ub, NV0 - 0.05, NWK)], 0.2)
    D.cil_os('obolochka', CHER, (uk, NV0 - 0.1, NWK + 0.05), (uk, v0, NWK + 0.05), 0.11, 6)
    for (ua, ub) in ((e0, uk), (e1, uk)):
        D.brus('obolochka', BRUS, (ua, NV0 - 0.08, NWE - 0.25), (ub, NV0 - 0.08, NWK - 0.15), 0.07, 0.26, (0, 1, 0))
    vf = NV0 + 0.25
    for uu in (nk_u0 + 0.25, nk_u1 - 0.25):
        D.kor('obolochka', KAM, uu - 0.26, uu + 0.26, vf - 0.26, vf + 0.26, Pk, Pk + 0.5, 0.02)
        D.brus('obolochka', BRUS, (uu, vf, Pk + 0.5), (uu, vf, NWE - 0.05), 0.28, 0.28, (1, 0, 0))
        D.brus('obolochka', BRUS, (uu, vf, NWE - 0.08), (uu, v0 - 0.05, NWE - 0.08), 0.22, 0.26, (1, 0, 0))
    D.brus('obolochka', BRUS, (nk_u0 - 0.1, vf, NWE + 0.05), (nk_u1 + 0.1, vf, NWE + 0.05), 0.26, 0.28, (0, 1, 0))
    D.brus('obolochka', BRUS, (nk_u0 - 0.1, vf, NWE + 0.12), (uk, vf, NWK - 0.02), 0.24, 0.26, (0, 1, 0))
    D.brus('obolochka', BRUS, (nk_u1 + 0.1, vf, NWE + 0.12), (uk, vf, NWK - 0.02), 0.24, 0.26, (0, 1, 0))
    D.brus('obolochka', BRUS, (uk, vf, NWE + 0.15), (uk, vf, NWK - 0.15), 0.24, 0.24, (0, 1, 0))
    for zn in (-1, 1):
        D.brus('obolochka', BRUS, (uk, vf, NWE + 0.35), (uk + zn * 1.05, vf, NWE + 0.12 + 1.05 * tg * 0.95), 0.17, 0.19, (0, 1, 0))
        D.brus('obolochka', BRUS, (uk + zn * 2.0, vf, NWE - 0.7), (uk + zn * 1.45, vf, NWE + 0.02), 0.15, 0.17, (0, 1, 0))
    D.brus('obolochka', BRUS, (uk, vf, NWK - 0.12), (uk, v0, NWK - 0.12), 0.2, 0.22, (1, 0, 0))


def _lestnica_naruzh(D, LU0, LU1, v_start, zn, W, ugol=34.0, plosh=1.25, rr=None):
    """Наружная каменная лестница вдоль бока (u от LU0 до LU1): от земли у v_start поднимается в сторону zn (±v) до
    высоты W; площадка посередине, ниша под вторым маршем (не монолит), стенка-парапет с выступами, столбики с шапкой.
    → v верхней ступени."""
    uk = math.tan(math.radians(ugol))
    h1 = W * 0.5
    d1 = h1 / uk
    d2 = (W - h1) / uk

    def kor_v(m, x0, x1, w0, w1, fs=0.008, a0=LU0, a1=LU1):
        y0, y1 = sorted((v_start + zn * x0, v_start + zn * x1))
        D.kor('obolochka', m, a0, a1, y0, y1, w0, w1, fs)
    n1 = int(round(h1 / 0.19))
    for k in range(n1):                  # ступень — столбик под своей проступью (не «до площадки»: грани в одной плоскости)
        kor_v(MOSH if k % 3 else KAM, d1 * k / n1, d1 * (k + 1) / n1, 0.0, h1 * (k + 1) / n1)
    kor_v(KAM, d1, d1 + plosh, 0.0, h1, 0.01)                                         # площадка на каменном столбе
    x2 = d1 + plosh
    n2 = int(round((W - h1) / 0.19))
    for k in range(n2):
        kor_v(MOSH if k % 3 else KAM, x2 + d2 * k / n2, x2 + d2 * (k + 1) / n2, h1 + (W - h1) * k / n2 - 0.35,
              h1 + (W - h1) * (k + 1) / n2)
    # щёки ниши под вторым маршем — на 1 см уже марша с каждой стороны: боковые грани не совпадают со ступенями
    kor_v(KAM, x2, x2 + 0.45, 0.0, h1, 0.0, LU0 + 0.01, LU1 - 0.01)
    kor_v(KAM, x2 + d2 - 0.45, x2 + d2, 0.0, W - 0.35, 0.0, LU0 + 0.01, LU1 - 0.01)
    rr = rr or random.Random(int(W * 1000) + int(LU1 * 100))
    for (a, b, w0, w1) in ((0.0, d1, 0.0, h1), (x2, x2 + d2, h1, W)):
        n = 6
        for k in range(n):
            y0 = a + (b - a) * k / n
            y1 = a + (b - a) * (k + 1) / n
            verh = w0 + (w1 - w0) * (k + 1) / n + 0.8 + rr.uniform(-0.035, 0.035)     # парапет — неровный верх
            nar = LU1 + 0.3 + rr.uniform(-0.02, 0.05)                              # и неровное лицо
            kor_v(KAM, y0, y1 + 0.01, 0.0 if w0 == 0.0 else w0 - 0.4, verh, 0.012, LU1, nar)
            # накрывной камень на каждом блоке, разной толщины и выноса (через один — выходили зубцы крепости)
            kor_v(KAM, y0 - 0.02, y1 + 0.03, verh, verh + rr.uniform(0.06, 0.1), 0.015, LU1 - rr.uniform(0.02, 0.05),
                  nar + rr.uniform(0.03, 0.06))
    for _ in range(rr.choice((2, 3))):                                              # глыбы у подножия
        y = rr.uniform(-0.2, 0.5)
        D.sfera('melochi', KAM, LU1 + rr.uniform(0.45, 0.8), v_start + zn * y, rr.uniform(-0.05, 0.03), rr.uniform(0.22, 0.34),
                (rr.uniform(1.1, 1.4), rr.uniform(0.9, 1.2), rr.uniform(0.45, 0.62)), 3)
    for (y, ww) in ((0.05, 0.0), (d1 + 0.1, h1)):
        kor_v(KAM, y, y + 0.4, ww, ww + 1.05, 0.02, LU1 - 0.02, LU1 + 0.36)
        kor_v(KAM, y - 0.05, y + 0.45, ww + 1.05, ww + 1.17, 0.012, LU1 - 0.07, LU1 + 0.41)
    return v_start + zn * (x2 + d2)


def _galereya_boka(D, p, u1, vg0, v1, F2, EV):
    """Галерея у двери коридора (naves): настил на брусьях-консолях из стены, столбы, перила, навес, мареновый полог."""
    GU1 = u1 + p['gal_gl']
    D.kor('obolochka', DOSKI, u1, GU1, vg0, v1, F2 - 0.08, F2, 0.005)
    vv = vg0 + 0.2
    while vv < v1:
        D.brus('obolochka', BRUS, (u1 - 0.2, vv, F2 - 0.16), (GU1 + 0.08, vv, F2 - 0.16), 0.14, 0.18, (0, 1, 0))
        D.brus('obolochka', BRUS, (u1 + 0.02, vv, F2 - 1.0), (u1 + 0.75, vv, F2 - 0.2), 0.12, 0.12, (0, 1, 0))
        vv += 0.9
    wv = EV - 0.35
    for vv in (vg0 + 0.1, (vg0 + v1) / 2.0, v1 - 0.1):
        D.brus('obolochka', BRUS, (GU1 - 0.1, vv, F2), (GU1 - 0.1, vv, wv - 0.08), 0.16, 0.16, (1, 0, 0))
    D.brus('obolochka', BRUS, (GU1 - 0.1, vg0, wv), (GU1 - 0.1, v1, wv), 0.16, 0.2, (0, 0, 1))
    for w in (F2 + 0.45, F2 + 1.0):
        D.brus('obolochka', BRUS, (GU1 - 0.1, vg0 + 0.1, w), (GU1 - 0.1, v1 - 0.1, w), 0.08, 0.07, (0, 0, 1))
    k = 0
    while vg0 + 0.3 + k * 0.28 < v1 - 0.2:
        vv = vg0 + 0.3 + k * 0.28
        D.brus('obolochka', BRUS, (GU1 - 0.1, vv, F2), (GU1 - 0.1, vv, F2 + 1.0), 0.045, 0.045, (1, 0, 0), 0.004)
        k += 1
    D.plita('obolochka', CHER, [(u1, vg0 - 0.2, EV - 0.05), (u1, v1 + 0.1, EV - 0.05), (GU1 + 0.3, v1 + 0.1, wv - 0.25),
                                (GU1 + 0.3, vg0 - 0.2, wv - 0.25)], 0.16)
    D.plita('obolochka', KRAS, [(u1 + 0.1, vg0 - 0.15, wv - 0.1), (GU1 + 0.25, vg0 - 0.15, wv - 0.3),
                                (GU1 + 0.25, vg0 - 0.95, wv - 0.75), (u1 + 0.1, vg0 - 0.95, wv - 0.55)], 0.02)


def _galereya_perednyaya(D, r, u0, u1, v0, P, F2, EV, g, dv_u0, dv_u1, tg):
    """Широкая двухъярусная галерея во весь фасад (Астра 28.09): внизу — крытое крыльцо зала, вверху — галерея комнат;
    столбы на каменных базах во всю высоту, настил на балках, перила с балясинами; кровля — продлённый передний скат."""
    vg = v0 - g
    D.kor('obolochka', MOSH, u0 - 0.15, u1 + 0.05, vg - 0.05, v0 + 0.02, 0.0, P, 0.01)
    a = sn(dv_u0 - 0.5)
    D.kor('obolochka', MOSH, a, dv_u1 + 0.5, vg - 0.55, vg - 0.03, 0.0, P * 0.5, 0.01)
    vp = vg + 0.13
    n = max(3, int(round((u1 - u0) / 2.3)) + 1)
    stolby = [u0 + 0.12 + (u1 - u0 - 0.24) * k / (n - 1) for k in range(n)]
    dc = (dv_u0 + dv_u1) / 2.0
    stolby = [x_ if not (dv_u0 - 0.25 < x_ < dv_u1 + 0.25) else (dv_u0 - 0.3 if x_ < dc else dv_u1 + 0.3) for x_ in stolby]
    w_verh = EV - (v0 - vp) * tg - 0.26                    # под плитой продлённого ската
    for i, x_ in enumerate(stolby):
        D.kor('obolochka', KAM, x_ - 0.2, x_ + 0.2, vp - 0.2, vp + 0.2, P, P + 0.38, 0.02)
        D.brus('obolochka', BRUS, (x_, vp, P + 0.38), (x_, vp, w_verh), 0.22, 0.22, (1, 0, 0))
        for zn in (-1, 1):                                  # подкосы под балкой настила и под обвязкой кровли
            if (i == 0 and zn < 0) or (i == len(stolby) - 1 and zn > 0):
                continue
            D.brus('obolochka', BRUS, (x_ + zn * 0.08, vp, F2 - 0.85), (x_ + zn * 0.6, vp, F2 - 0.3), 0.12, 0.12, (0, 1, 0))
            D.brus('obolochka', BRUS, (x_ + zn * 0.08, vp, w_verh - 0.5), (x_ + zn * 0.5, vp, w_verh - 0.05), 0.1, 0.1, (0, 1, 0))
    D.brus('obolochka', BRUS, (u0 - 0.1, vp, F2 - 0.2), (u1 + 0.1, vp, F2 - 0.2), 0.24, 0.26, (0, 1, 0))
    D.brus('obolochka', BRUS, (u0 - 0.15, vp, w_verh + 0.06), (u1 + 0.15, vp, w_verh + 0.06), 0.2, 0.14, (0, 1, 0))
    x_ = u0 + 0.3
    while x_ < u1 - 0.1:
        D.brus('obolochka', BRUS, (x_, v0 + 0.15, F2 - 0.16), (x_, vg - 0.06, F2 - 0.16), 0.14, 0.18, (1, 0, 0))
        x_ += 0.9
    D.kor('obolochka', DOSKI, u0 - 0.05, u1 + 0.05, vg - 0.08, v0, F2 - 0.07, F2, 0.005)
    vr = vg + 0.05
    for w in (F2 + 1.0, F2 + 0.45):
        D.brus('obolochka', BRUS, (u0 - 0.05, vr, w), (u1 + 0.05, vr, w), 0.09 if w > F2 + 0.5 else 0.07, 0.08, (0, 1, 0))
        for xe in (u0 - 0.02, u1 + 0.02):
            D.brus('obolochka', BRUS, (xe, vr, w), (xe, v0, w), 0.09, 0.08, (1, 0, 0))
    x_ = u0 + 0.22
    while x_ < u1 - 0.1:
        D.brus('obolochka', BRUS, (x_, vr, F2), (x_, vr, F2 + 1.0), 0.045, 0.045, (1, 0, 0), 0.004)
        x_ += 0.24
    for xe in (u0 - 0.02, u1 + 0.02):
        y_ = vr + 0.25
        while y_ < v0 - 0.1:
            D.brus('obolochka', BRUS, (xe, y_, F2), (xe, y_, F2 + 1.0), 0.045, 0.045, (0, 1, 0), 0.004)
            y_ += 0.24
    # мареновая ткань на перилах, горшки с травой на галерее, лавка у стены на крыльце
    for k in range(r.randint(1, 2)):
        x0 = u0 + 0.8 + r.uniform(0.0, max(0.1, u1 - u0 - 2.8))
        D.kor('obolochka', KRAS, x0, x0 + r.uniform(0.9, 1.3), vr - 0.08, vr - 0.04, F2 + 0.2, F2 + 1.04)
    for k in range(3):
        x0 = u0 + 0.6 + (u1 - u0 - 1.2) * (k + 0.5) / 3.0
        D.cil('melochi', BRUS, x0, vr + 0.3, F2, 0.18, 0.3, 10)
        D.sfera('melochi', TRAV, x0, vr + 0.3, F2 + 0.42, 0.22, (1.0, 1.0, 0.8), 3)
    D.kor('melochi', BRUS, u0 + 0.35, dv_u0 - 0.3, v0 - 0.5, v0 - 0.18, P + 0.42, P + 0.48, 0.008)
    for a_ in (u0 + 0.45, dv_u0 - 0.45):
        D.kor('melochi', BRUS, a_, a_ + 0.1, v0 - 0.45, v0 - 0.23, P, P + 0.42)


def _kuznya_prislon(D, u1, lp_w, vf, vb, Pk, Hw, tg_a):
    """Кузня у края (galereya): открытый навес у бока корпуса — помост, столбы на каменных базах, низкая каменная стенка
    сзади и сбоку, кровля — половина вальмы (`_prislon_krysha`)."""
    sv = 0.35
    uo = u1 + lp_w
    D.kor('obolochka', MOSH, u1, uo + 0.05, vf, vb, 0.0, Pk, 0.01)
    D.kor('obolochka', MOSH, u1 + 0.4, uo - 0.4, vf - 0.4, vf + 0.02, 0.0, Pk * 0.5, 0.01)
    He = _prislon_krysha(D, u1, lp_w + sv, vf - sv, vb + sv, Hw, tg_a)
    w_st = He + (sv + 0.15) * tg_a - 0.26
    for vv in (vf + 0.15, vb - 0.15):
        D.kor('obolochka', KAM, uo - 0.38, uo + 0.06, vv - 0.22, vv + 0.22, Pk, Pk + 0.45, 0.02)
        D.brus('obolochka', BRUS, (uo - 0.16, vv, Pk + 0.45), (uo - 0.16, vv, w_st), 0.22, 0.22, (1, 0, 0))
        D.brus('obolochka', BRUS, (uo - 0.16, vv + (0.1 if vv < vb - 1 else -0.1), w_st - 0.6),
               (uo - 0.16, vv + (0.55 if vv < vb - 1 else -0.55), w_st - 0.05), 0.12, 0.12, (1, 0, 0))
    D.brus('obolochka', BRUS, (uo - 0.16, vf - 0.1, w_st + 0.1), (uo - 0.16, vb + 0.1, w_st + 0.1), 0.2, 0.22, (1, 0, 0))
    D.kor('obolochka', KAM, u1, uo + 0.06, vb - 0.42, vb, Pk, Pk + 1.2, 0.02)
    D.kor('obolochka', KAM, uo - 0.38, uo + 0.06, vb - (vb - vf) * 0.45, vb - 0.42, Pk, Pk + 1.0, 0.02)


def _pristrojka(D, r, u1, v0, va0, va1, aw, ap, Pk, Hw, tg_a, KR):
    """Низкая боковая пристройка (Астра 28.09: «основной корпус с низкой боковой пристройкой, крыши образуют две
    ступени»): спереди — открытая кузня у стены корпуса, сзади за перегородкой — кладовая с дверью во двор; стены —
    камень внизу, известь выше; кровля — половина вальмы ниже карниза корпуса."""
    Ta = 0.45
    ua = u1 + aw
    sv = 0.45
    He = _prislon_krysha(D, u1, aw + sv, va0 - sv, va1 + sv, Hw, tg_a)
    Wt = He + sv * tg_a
    KRa = min(KR, Wt - 0.7)
    D.kor('obolochka', MOSH, u1, ua, va0 - 0.2, va1, 0.0, Pk, 0.01)
    D.kor('obolochka', MOSH, u1 + 0.4, ua - 0.5, va0 - 0.6, va0 - 0.18, 0.0, Pk * 0.5, 0.01)
    D.kor('obolochka', KAM, ua - 0.1, ua + 0.07, va0 - 0.07, va1 + 0.07, 0.0, 0.32, 0.02)          # цоколь-пояс
    D.kor('obolochka', KAM, u1 + 0.3, ua + 0.07, va1 - 0.1, va1 + 0.07, 0.0, 0.32, 0.02)
    if v0 - va0 > 0.3:
        D.kor('obolochka', KAM, u1 - 0.07, u1 + 0.1, va0 - 0.07, v0, 0.0, 0.32, 0.02)

    def stena_a(box, vy):
        D.stena('obolochka', KAM, [box[0], box[1], box[2], box[3], 0.0, KRa], vy)
        D.stena('obolochka', SHT, [box[0], box[1], box[2], box[3], KRa, Wt], vy)
    ok_v = sn((va0 + ap) / 2.0)
    stena_a([ua - Ta, ua, va0, va1], [[ua - Ta - 0.3, ua + 0.3, ok_v - 0.35, ok_v + 0.35, Pk + 1.0, Pk + 1.75]])
    stena_a([u1, ua - Ta, va1 - Ta, va1], [[ua - Ta - 1.25, ua - Ta - 0.25, va1 - Ta - 0.3, va1 + 0.3, Pk, Pk + 2.1]])
    if v0 - va0 > 0.3:
        stena_a([u1, u1 + Ta, va0, v0], [])
    D.okno('v', ok_v - 0.35, ok_v + 0.35, Pk + 1.0, Pk + 1.75, ua, 1, perepl=1, stavni=True, steklo=False, glub=0.25)
    D.kor('obolochka', KAM, ua - 0.55, ua + 0.05, va0 - 0.05, va0 + 0.5, 0.0, Wt, 0.02)          # столб-пилон угла
    D.brus('obolochka', BRUS, (u1 + (Ta if v0 - va0 > 0.3 else 0.0) - 0.1, va0 + 0.15, Wt - 0.17),
           (ua - 0.5, va0 + 0.15, Wt - 0.17), 0.3, 0.32, (1, 0, 0))                                  # прогон над проёмом
    D.stena('peregorodki', SHT, [u1, ua - Ta, ap, ap + TV, Pk, Wt], [[ua - Ta - 1.3, ua - Ta - 0.3, ap - 0.3, ap + TV + 0.3, Pk, Pk + 2.2]])
    # полотно задней двери приоткрыто, в кладовой — бочки и мешки
    D.brus('obolochka', BRUS, (ua - Ta - 0.3, va1 - Ta + 0.05, Pk + 1.05), (ua - Ta - 0.95, va1 - Ta - 0.65, Pk + 1.05), 2.05, 0.06, (0, 0, 1), 0.006)
    for k in range(2):
        D.cil('mebel', BRUS, u1 + 0.45 + k * 0.62, va1 - Ta - 0.45, Pk, 0.28, 0.75, 12)
    for k in range(3):
        D.sfera('mebel', TKAN, ua - Ta - 0.35, ap + TV + 0.45 + k * 0.45, Pk + 0.3, 0.3, (1.0, 1.0, 1.1), 3)
    # поленница у наружной стены
    for ryad in range(4):
        for j in range(5):
            vv = va1 - 0.5 - j * 0.15 - (0.07 if ryad % 2 else 0.0)
            D.cil_os('melochi', BRUS, (ua + 0.08, vv, 0.08 + ryad * 0.14), (ua + 0.48, vv, 0.08 + ryad * 0.14), 0.07, 7)


def _terrasa_ugol(D, r, u1, v0, tf_u0, gf, gs, vt1, F2, Pk):
    """Терраса верха поворачивает за угол (Астра 28.09: «галерея поворачивает за угол, кузня занимает угол дома»):
    передняя часть над кузней, короткое плечо вдоль бока к наружной лестнице; столбы на каменных базах, настил на
    балках, перила, мареновый полог на шестах. Под террасой — помост кузни."""
    ue, ve = u1 + gs, v0 - gf
    D.kor('obolochka', MOSH, tf_u0 - 0.1, ue + 0.1, ve - 0.15, v0 + 0.02, 0.0, Pk, 0.01)
    D.kor('obolochka', MOSH, tf_u0 + 0.5, ue - 0.5, ve - 0.55, ve - 0.13, 0.0, Pk * 0.5, 0.01)
    D.kor('obolochka', DOSKI, tf_u0, ue, ve, v0, F2 - 0.08, F2, 0.005)
    if vt1 > v0 + 0.05:
        D.kor('obolochka', DOSKI, u1, ue, v0, vt1, F2 - 0.08, F2, 0.005)
    stolby = []
    n = max(2, int(round((ue - tf_u0) / 2.9)) + 1)
    for k in range(n):
        stolby.append((tf_u0 + 0.15 + (ue - tf_u0 - 0.3) * k / (n - 1), ve + 0.15))
    if vt1 - ve > 2.6:
        stolby.append((ue - 0.15, (ve + vt1) / 2.0))
    stolby.append((ue - 0.15, vt1 - 0.15))
    for (x_, y_) in stolby:
        D.kor('obolochka', KAM, x_ - 0.25, x_ + 0.25, y_ - 0.25, y_ + 0.25, 0.0, Pk + 0.45, 0.02)
        D.brus('obolochka', BRUS, (x_, y_, Pk + 0.45), (x_, y_, F2 - 0.12), 0.26, 0.26, (1, 0, 0))
        D.brus('obolochka', BRUS, (x_, y_, F2), (x_, y_, F2 + 1.12), 0.14, 0.14, (1, 0, 0))
    D.brus('obolochka', BRUS, (tf_u0 - 0.05, ve + 0.15, F2 - 0.22), (ue + 0.05, ve + 0.15, F2 - 0.22), 0.26, 0.28, (0, 1, 0))
    D.brus('obolochka', BRUS, (ue - 0.15, ve, F2 - 0.22), (ue - 0.15, vt1, F2 - 0.22), 0.26, 0.28, (1, 0, 0))
    x_ = tf_u0 + 0.25
    while x_ < ue - 0.1:
        y0_ = v0 + 0.15 if x_ < u1 else vt1
        D.brus('obolochka', BRUS, (x_, y0_, F2 - 0.17), (x_, ve + 0.02, F2 - 0.17), 0.14, 0.18, (1, 0, 0))
        x_ += 0.8
    # парапет: сплошная доска по передней кромке, по боковой и по левому торцу, поручень сверху; у верха лестницы —
    # проход (Астра 28.09: «стойки и ограждения перегружают угол — упростить ритм»)
    vr, ur = ve + 0.06, ue - 0.06
    D.kor('obolochka', DOSKI, tf_u0, ue, vr - 0.03, vr + 0.03, F2, F2 + 0.92, 0.005)
    D.kor('obolochka', DOSKI, ur - 0.03, ur + 0.03, ve, vt1 - 0.1, F2, F2 + 0.92, 0.005)
    D.kor('obolochka', DOSKI, tf_u0 + 0.01, tf_u0 + 0.07, ve, v0, F2, F2 + 0.92, 0.005)
    D.brus('obolochka', BRUS, (tf_u0 - 0.04, vr, F2 + 0.97), (ue + 0.04, vr, F2 + 0.97), 0.12, 0.08, (0, 1, 0))
    D.brus('obolochka', BRUS, (ur, ve - 0.04, F2 + 0.97), (ur, vt1 - 0.1, F2 + 0.97), 0.12, 0.08, (1, 0, 0))
    D.brus('obolochka', BRUS, (tf_u0 + 0.04, ve, F2 + 0.97), (tf_u0 + 0.04, v0, F2 + 0.97), 0.12, 0.08, (1, 0, 0))
    # мареновый полог на шестах над углом террасы
    pu0, pu1 = max(tf_u0 + 0.4, u1 - 2.2), ue - 0.15
    for x_ in (pu0, pu1):
        D.cil_os('obolochka', BRUS, (x_, ve + 0.2, F2), (x_, ve + 0.2, F2 + 2.25), 0.04, 6)
    D.plita('obolochka', KRAS, [(pu0, ve + 0.1, F2 + 2.2), (pu1, ve + 0.1, F2 + 2.2), (pu1, v0 + 0.05, F2 + 2.55),
                                (pu0, v0 + 0.05, F2 + 2.55)], 0.02)
    for k in range(3):
        x0 = tf_u0 + 0.5 + (ue - tf_u0 - 1.0) * (k + 0.5) / 3.0
        D.cil('melochi', BRUS, x0, vr + 0.3, F2, 0.18, 0.3, 10)
        D.sfera('melochi', TRAV, x0, vr + 0.3, F2 + 0.42, 0.22, (1.0, 1.0, 0.8), 3)


def _kamen_zhivoj(D, r, u0, u1, v0, v1, KR, proemy):
    """Живой камень низа: угловые камни крупнее рядовых, неровный верхний ряд, отдельные камни выступают на 1–3 см
    (Астра: 3–5 размеров, выступ 1–3 см, повреждено не больше 5 % фасада)."""
    def v_proeme(st, a, w):
        for (s_, a0, a1, w0, w1, vid) in proemy:
            if s_ == st and a0 - 0.1 < a < a1 + 0.1 and w0 - 0.1 < w < w1 + 0.1:
                return True
        return False
    for (cu, cv, zu, zv) in ((u0, v0, 1, 1), (u1, v0, -1, 1), (u0, v1, 1, -1), (u1, v1, -1, -1)):
        w = 0.0
        k = 0
        while w < KR - 0.1:
            h = r.uniform(0.28, 0.38)                    # угловые камни крупнее и выступают заметно (Астра 28.09, вечер)
            dl_a, dl_b = (0.7, 0.36) if k % 2 == 0 else (0.36, 0.7)
            vy = r.uniform(0.04, 0.07)
            D.kor('obolochka', KAM, min(cu, cu + zu * dl_a) - (vy if zu < 0 else 0), max(cu, cu + zu * dl_a) + (vy if zu < 0 else 0),
                  min(cv, cv - zv * vy), max(cv, cv - zv * vy) + (0.02 if zv > 0 else 0), w, min(w + h, KR + 0.04), 0.012)
            D.kor('obolochka', KAM, min(cu, cu - zu * vy), max(cu, cu - zu * vy) + (0.02 if zu > 0 else 0),
                  min(cv, cv + zv * dl_b), max(cv, cv + zv * dl_b), w, min(w + h, KR + 0.04), 0.012)
            w += h
            k += 1
    for st in ('ul', 'zad', 'sev', 'jug'):
        a_nach, a_kon = (u0 + 0.6, u1 - 0.6) if st in ('ul', 'zad') else (v0 + 0.6, v1 - 0.6)
        a = a_nach
        while a < a_kon:
            dl = r.uniform(0.25, 0.6)
            h = r.uniform(0.18, 0.3)
            dw = r.uniform(-0.07, 0.08)                  # неровный верх каменного низа
            if not v_proeme(st, a + dl / 2, KR - 0.1):
                _kamen_na_stene(D, st, a, min(a + dl, a_kon), KR - h + dw, KR + dw, r.uniform(0.02, 0.045), u0, u1, v0, v1)
            a += dl + 0.01
        for _ in range(int((a_kon - a_nach) * 1.2)):
            a = r.uniform(a_nach, a_kon)
            w = r.uniform(0.35, KR - 0.4)
            if v_proeme(st, a, w):
                continue
            dl, h = r.uniform(0.2, 0.45), r.uniform(0.12, 0.24)
            _kamen_na_stene(D, st, a, a + dl, w, w + h, r.uniform(0.02, 0.05), u0, u1, v0, v1)


def _glyby_u_uglov(D, rr, u0, u1, v0, v1, zanyato=()):
    """Крупные камни, наполовину в земле, у углов дома (Астра 28.09, вечер: «отдельные крупные камни» — толщина
    архитектуры). zanyato — (u0, u1, v0, v1) мест, где камней не класть (крыльцо, лестница, навес)."""
    for (cu, cv, zu, zv) in ((u0, v0, -1, -1), (u1, v0, 1, -1), (u0, v1, -1, 1), (u1, v1, 1, 1)):
        for _ in range(rr.choice((1, 2))):
            ru = rr.uniform(0.22, 0.38)
            x = cu + zu * rr.uniform(0.1, 0.45)
            y = cv + zv * rr.uniform(0.1, 0.45)
            if any(b0 - 0.4 <= x <= b1 + 0.4 and c0 - 0.4 <= y <= c1 + 0.4 for (b0, b1, c0, c1) in zanyato):
                continue
            D.sfera('melochi', KAM, x, y, rr.uniform(-0.06, 0.03), ru,
                    (rr.uniform(1.15, 1.5), rr.uniform(0.9, 1.2), rr.uniform(0.45, 0.65)), 3)


def _kamen_na_stene(D, st, a0, a1, w0, w1, vy, u0, u1, v0, v1):
    if st == 'ul':
        D.kor('obolochka', KAM, a0, a1, v0 - vy, v0 + 0.05, w0, w1, 0.01)
    elif st == 'zad':
        D.kor('obolochka', KAM, a0, a1, v1 - 0.05, v1 + vy, w0, w1, 0.01)
    elif st == 'sev':
        D.kor('obolochka', KAM, u0 - vy, u0 + 0.05, a0, a1, w0, w1, 0.01)
    else:
        D.kor('obolochka', KAM, u1 - 0.05, u1 + vy, a0, a1, w0, w1, 0.01)


def _karkas_verha(D, r, u0, u1, v0, v1, F1, F2, EV, proemy_verh, bez_pered, bez_kronshtejnov_pered, stavni=True):
    """Тёмный брус верха: лежень, обвязка, стойки на углах и у окон (не поперёк окна и ставней), выпуски балок
    перекрытия 15–30 см, кронштейны под свесом. bez_pered — куски фасада, где выпусков нет (под галереей и террасой)."""
    def okna_stor(st):
        return [(a0, a1, vid) for (s_, a0, a1, w0, w1, vid) in proemy_verh if s_ == st and vid.startswith('okno')]
    for st, (a_nach, a_kon), lico, zn in (('ul', (u0, u1), v0, -1), ('zad', (u0, u1), v1, 1),
                                          ('sev', (v0, v1), u0, -1), ('jug', (v0, v1), u1, 1)):
        ok = okna_stor(st)
        dveri = [(a0, a1) for (s_, a0, a1, w0, w1, vid) in proemy_verh if s_ == st and vid.startswith('dver')]
        # верхняя обвязка идет сплошь, а нижний лежень (F2 + 0.08) прерывается у дверных проёмов
        _brus_vdol(D, st, a_nach - 0.04, a_kon + 0.04, lico + zn * 0.06, EV - 0.1, 0.18, 0.2)
        lezh_kuski = _svobodno(a_nach - 0.04, a_kon + 0.04, [(d0 - 0.02, d1 + 0.02) for d0, d1 in dveri]) if dveri else [(a_nach - 0.04, a_kon + 0.04)]
        for (ka, kb) in lezh_kuski:
            if kb - ka > 0.05:
                _brus_vdol(D, st, ka, kb, lico + zn * 0.06, F2 + 0.08, 0.18, 0.2)

        # Зоны проёмов, куда стойка каркаса попадать не должна (окна с распахнутыми ставнями и двери)
        zapret = []
        for (a0, a1, vid) in ok:
            w_sh = ((a1 - a0) / 2.0 + 0.02) if (stavni and vid == 'okno') else 0.02
            zapret.append((a0 - w_sh, a1 + w_sh))
        for (d0, d1) in dveri:
            zapret.append((d0 - 0.05, d1 + 0.05))

        # Стойки: обязательно угловые + обрамление оконных групп
        kandidaty = [a_nach + 0.08, a_kon - 0.08]
        for (a0, a1, vid) in ok:
            w_sh = ((a1 - a0) / 2.0 + 0.02) if (stavni and vid == 'okno') else 0.02
            # отступ 0.14 даёт аккуратный зазор ~6 см между распахнутой ставней и стойкой шириной 16 см
            kandidaty.append(round(a0 - w_sh - 0.14, 3))
            kandidaty.append(round(a1 + w_sh + 0.14, 3))

        itog_stoiki = []
        for a in sorted(kandidaty):
            if a < a_nach + 0.05 or a > a_kon - 0.05:
                continue
            # Полуширина стойки 0.08: стойка занимает [a - 0.08, a + 0.08]
            if any(z0 < a + 0.08 and a - 0.08 < z1 for z0, z1 in zapret):
                continue
            if any(abs(a - s) < 0.22 for s in itog_stoiki):
                continue
            itog_stoiki.append(a)

        for a in itog_stoiki:
            _stojka(D, st, a, lico + zn * 0.06, F2 + 0.15, EV - 0.18)
        if st in ('ul', 'zad'):
            vyp = r.uniform(*STIL['vypusk_balok'])
            a = a_nach + 0.45
            while a < a_kon - 0.3:
                if not (st == 'ul' and any(b0 < a < b1 for (b0, b1) in bez_pered)):
                    D.brus('obolochka', BRUS, (a, lico - zn * 0.2, F1 + 0.14), (a, lico + zn * vyp, F1 + 0.14), 0.16, 0.2, (1, 0, 0))
                a += r.uniform(0.95, 1.15)
            if st == 'ul' and bez_kronshtejnov_pered:
                continue
            a = a_nach + 0.3
            while a < a_kon:
                vv0 = lico
                D.profil('obolochka', BRUS, [(vv0, EV - 0.55), (vv0, EV - 0.02), (vv0 + zn * 0.6, EV - 0.02),
                                              (vv0 + zn * 0.6, EV - 0.12), (vv0 + zn * 0.2, EV - 0.5)], 'vw', a - 0.07, a + 0.07, 0.01)
                a += 1.1


def _brus_vdol(D, st, a0, a1, lico, w, shir, tol):
    if st in ('ul', 'zad'):
        D.brus('obolochka', BRUS, (a0, lico, w), (a1, lico, w), shir, tol, (0, 1, 0))
    else:
        D.brus('obolochka', BRUS, (lico, a0, w), (lico, a1, w), shir, tol, (1, 0, 0))


def _stojka(D, st, a, lico, w0, w1):
    if st in ('ul', 'zad'):
        D.brus('obolochka', BRUS, (a, lico, w0), (a, lico, w1), 0.16, 0.16, (1, 0, 0))
    else:
        D.brus('obolochka', BRUS, (lico, a, w0), (lico, a, w1), 0.16, 0.16, (0, 1, 0))


# ---------------------------------------------------------------------------------------------------- нутро

def _stol(D, r, os_, a0, a1, c, P, lavki=(-1, 1), posuda=True):
    """Стол от a0 до a1 вдоль оси os_ ('u' или 'v'), середина поперёк — c; лавки с сторон lavki; посуда группами."""
    def box(p0, p1, q0, q1, w0, w1, m=BRUS, fs=0.0):
        if os_ == 'u':
            D.kor('mebel', m, p0, p1, q0, q1, w0, w1, fs)
        else:
            D.kor('mebel', m, q0, q1, p0, p1, w0, w1, fs)

    def tochka(a, q):
        return (a, q) if os_ == 'u' else (q, a)
    box(a0, a1, c - 0.425, c + 0.425, P + 0.72, P + 0.8, BRUS, 0.01)
    for x_ in (a0 + 0.2, a1 - 0.35):
        box(x_, x_ + 0.15, c - 0.33, c + 0.33, P, P + 0.72, BRUS, 0.008)
    for s_ in lavki:
        q = c + s_ * (0.425 + 0.13 + 0.16)
        box(a0 + 0.1, a1 - 0.1, q - 0.16, q + 0.16, P + 0.42, P + 0.48, BRUS, 0.008)
        for x_ in (a0 + 0.25, a1 - 0.35):
            box(x_, x_ + 0.1, q - 0.11, q + 0.11, P, P + 0.42)
    if posuda:
        dl = a1 - a0
        n = max(3, int(dl / 0.5))
        for k in range(n):
            if k % 4 == 3:
                continue
            a = a0 + 0.3 + (dl - 0.6) * k / max(1, n - 1)
            q = c + (0.18 if k % 2 else -0.18)
            x_, y_ = tochka(a, q)
            if k % 4 == 1:
                D.cil('mebel', KAM, x_, y_, P + 0.8, 0.09, 0.28, 10, 0.06)               # кувшин
            else:
                D.cil('mebel', ZHEL if k % 2 else BRUS, x_, y_, P + 0.8, 0.07, 0.1, 8)     # миска, кружка
        x_, y_ = tochka((a0 + a1) / 2.0, c)
        D.cil('mebel', ZHEL, x_, y_, P + 0.8, 0.05, 0.22, 8)                              # подсвечник
        D.cil('mebel', TKAN, x_, y_, P + 1.02, 0.025, 0.1, 6)


def _mebel_zala(D, r, S, ca, ui0, ui1, vi0, vi1, L_sh, kb_u0, kb_v0, pov_u1, P, F1, dv_u0, dv_u1, kl_v_pr):
    """Зал (Астра 28.09: «должен сразу показывать столы, лавки и место встречи у очага»): место у огня — ковёр, лавка со
    спинкой лицом к огню, табуреты; общий стол — в глубине зала за лестницей, виден от двери; стойка хозяйки — вдоль
    перегородки поварни; столик у фасада, если есть место. → середина общего стола (u, v)."""
    # место встречи у огня
    S.kor(D, 'mebel', KRAS, ca - 1.1, ca + 1.1, 0.95, 2.1, P + 0.005, P + 0.02)
    S.kor(D, 'mebel', BRUS, ca - 0.8, ca + 0.8, 1.55, 1.9, P + 0.42, P + 0.49, 0.008)
    for a_ in (ca - 0.7, ca + 0.6):
        S.kor(D, 'mebel', BRUS, a_, a_ + 0.1, 1.6, 1.85, P, P + 0.42)
    S.kor(D, 'mebel', BRUS, ca - 0.8, ca + 0.8, 1.84, 1.91, P + 0.49, P + 0.95, 0.008)
    for s_ in (-1, 1):
        q = S.p(ca + s_ * 1.2, 1.2, 0.0)
        D.cil('mebel', BRUS, q[0], q[1], P, 0.2, 0.45, 10)
    ogon = S.box(ca - 1.45, ca + 1.45, 0.0, 2.25)
    # общий стол в глубине — вдоль v, лавки по обе стороны (если тесно — одна, со стороны лестницы)
    n_u0, n_u1 = ui0 + L_sh + 0.35, kb_u0 - TV / 2 - 0.12
    n_v0, n_v1 = kb_v0 - 1.1, vi1 - 0.75                 # сзади — обход (Астра: «выдвинуть в зал, сохранив обход»)
    shir_n = n_u1 - n_u0
    if shir_n >= 1.75:
        cu, lavki = min((n_u0 + n_u1) / 2.0 + 0.15, n_u1 - 0.875), (-1, 1)
    else:
        cu, lavki = n_u1 - 0.43, (-1,)
    dl = min(2.8, n_v1 - n_v0)
    _stol(D, r, 'v', n_v1 - dl, n_v1, cu, P, lavki)
    D.kor('mebel', TKAN, cu - 0.17, cu + 0.17, n_v1 - dl + 0.1, n_v1 - 0.1, P + 0.8, P + 0.806)       # дорожка на столе
    stol_c = (cu, n_v1 - dl / 2.0)
    _lampa(D, stol_c[0], stol_c[1], P + 2.25, F1)
    # стойка хозяйки вдоль перегородки поварни (со стороны зала) между дверями; на ней бочонки, над ней полка
    s_u0 = kb_u0 + 1.4
    s_u1 = (pov_u1 + 0.05) if not kl_v_pr else ui1 - 0.15
    if s_u1 - s_u0 >= 0.7:
        D.kor('mebel', BRUS, s_u0, s_u1, kb_v0 - TV / 2 - 0.58, kb_v0 - TV / 2, P, P + 1.02, 0.012)
        D.kor('mebel', BRUS, s_u0 - 0.04, s_u1 + 0.04, kb_v0 - TV / 2 - 0.64, kb_v0 - TV / 2, P + 1.02, P + 1.09, 0.008)
        nb = max(1, int((s_u1 - s_u0) / 0.55))
        for k in range(nb):
            x_ = s_u0 + (s_u1 - s_u0) * (k + 0.5) / nb
            D.cil_os('mebel', BRUS, (x_ - 0.2, kb_v0 - 0.4, P + 1.24), (x_ + 0.2, kb_v0 - 0.4, P + 1.24), 0.14, 10)
        D.kor('mebel', BRUS, s_u0, s_u1, kb_v0 - TV / 2 - 0.25, kb_v0 - TV / 2, P + 1.75, P + 1.8)
        for k in range(max(2, int((s_u1 - s_u0) / 0.25))):
            x_ = s_u0 + 0.12 + k * 0.25
            if x_ > s_u1 - 0.1:
                break
            D.cil('mebel', KAM if k % 2 else ZHEL, x_, kb_v0 - TV / 2 - 0.13, P + 1.8, 0.07, 0.18 if k % 2 else 0.08, 8)
    # столик у фасада между дверью и местом у огня (круглый, три табурета), если помещается
    zan = [ogon, (dv_u0 - 0.4, dv_u1 + 0.4, vi0, vi0 + 1.7), (kb_u0 + 0.2, ui1, kb_v0 - 1.15, vi1),
           (kb_u0 - 0.3, kb_u0 + 0.2, kb_v0 - 0.3, vi1), (ui0, ui0 + L_sh + 0.4, vi0, vi1)]
    for cv_ in (vi0 + 1.1, vi0 + 1.35, vi0 + 1.6):
        for cu_ in [dv_u1 + 1.0 + 0.25 * k for k in range(20)]:
            b = (cu_ - 0.82, cu_ + 0.82, cv_ - 0.82, cv_ + 0.82)
            if b[1] > ui1 - 0.2 or b[2] < vi0 + 0.1 or b[3] > kb_v0 - 0.2:
                continue
            if any(_peresek2(b, z) for z in zan):
                continue
            D.cil('mebel', BRUS, cu_, cv_, P, 0.12, 0.72, 10)
            D.cil('mebel', BRUS, cu_, cv_, P + 0.72, 0.45, 0.06, 16)
            D.cil('mebel', ZHEL, cu_ + 0.1, cv_, P + 0.78, 0.06, 0.1, 8)
            for k in range(3):
                ug = 0.5 + k * 2.1
                D.cil('mebel', BRUS, cu_ + 0.64 * math.cos(ug), cv_ + 0.64 * math.sin(ug), P, 0.17, 0.45, 8)
            return stol_c
    return stol_c


def _lampa(D, cu, cv, w, F1):
    """Висячий фонарь над общим столом: цепь от балки, железная рама, стекло, свет."""
    D.cil_os('mebel', ZHEL, (cu, cv, w + 0.32), (cu, cv, F1 - 0.12), 0.012, 4)
    D.kor('mebel', ZHEL, cu - 0.2, cu + 0.2, cv - 0.2, cv + 0.2, w + 0.3, w + 0.34)
    D.kor('mebel', ZHEL, cu - 0.16, cu + 0.16, cv - 0.16, cv + 0.16, w - 0.02, w + 0.02)
    for (a, b) in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
        D.cil_os('mebel', ZHEL, (cu + a * 0.15, cv + b * 0.15, w), (cu + a * 0.19, cv + b * 0.19, w + 0.32), 0.01, 4)
    D.kor('mebel', STEK, cu - 0.12, cu + 0.12, cv - 0.12, cv + 0.12, w + 0.02, w + 0.28)
    D.istochnik('stol', cu, cv, w + 0.12, 1.8, 330.0, (255, 196, 140), True)


def _peresek2(a, b):
    return min(a[1], b[1]) - max(a[0], b[0]) > 1e-3 and min(a[3], b[3]) - max(a[2], b[2]) > 1e-3


def _mebel_povarni(D, kb_u0, kb_v0, pov_u1, vi1, ui1, P, F1, kl_v_pr):
    """Поварня: печь с котлом у задней стены, разделочный стол, кадка; кладовая: закрома, мешки, бочки, сундук-казна."""
    pu1 = pov_u1 - TV / 2
    D.kor('mebel', KAM, pu1 - 1.1, pu1 - 0.05, vi1 - 0.8, vi1, P, P + 0.95, 0.02)
    D.kor('mebel', KAM, pu1 - 1.0, pu1 - 0.15, vi1 - 0.5, vi1, P + 0.95, F1, 0.012)
    D.cil('mebel', ZHEL, pu1 - 0.58, vi1 - 0.52, P + 0.95, 0.22, 0.28, 12, 0.18)
    D.kor('mebel', BRUS, kb_u0 + 0.2, kb_u0 + 1.05, kb_v0 + 0.55, kb_v0 + 1.1, P + 0.78, P + 0.85, 0.01)
    D.kor('mebel', BRUS, kb_u0 + 0.25, kb_u0 + 1.0, kb_v0 + 0.6, kb_v0 + 1.05, P, P + 0.78)
    D.cil('mebel', BRUS, kb_u0 + 0.4, vi1 - 0.4, P, 0.28, 0.6, 12)
    if kl_v_pr:
        return
    for k in range(2):
        D.cil('mebel', BRUS, pov_u1 + 0.45, kb_v0 + 0.55 + k * 0.62, P, 0.27, 0.75, 12)
    for k in range(3):
        D.sfera('mebel', TKAN, ui1 - 0.35, kb_v0 + 0.5 + k * 0.45, P + 0.3, 0.28, (1.0, 1.0, 1.1), 3)
    D.kor('mebel', BRUS, pov_u1 + 0.25, ui1 - 0.1, vi1 - 0.6, vi1 - 0.1, P, P + 0.5, 0.02)
    D.kor('mebel', ZHEL, pov_u1 + 0.23, ui1 - 0.08, vi1 - 0.62, vi1 - 0.08, P + 0.22, P + 0.26)


def _mebel_komnat(D, r, komn, F2, vi0, kor_v0, truba):
    """Комнаты (Астра 28.09: «кровать у стены, сундук у изножья, столик у окна; ночлежке — двухъярусная кровать»):
    группы встают в первое свободное место из списка — двери остаются открыты, высокие вещи не закрывают окна."""
    for k in komn:
        b0, b1, c0, c1 = k['b']
        dv = k['dver_kor']
        dveri = [(dv[0] - 0.05, dv[1] + 0.05, c1 - 0.95, c1)]
        if 'dver_pered' in k:
            dp = k['dver_pered']
            dveri.append((dp[0] - 0.05, dp[1] + 0.05, c0, c0 + 0.95))
        okna = [(o[0] - 0.1, o[1] + 0.1, c0, c0 + 0.55) for o in k.get('okna', [])]
        if 'okno_bok' in k:
            okna.append((b1 - 0.55, b1, k['okno_bok'][0] - 0.1, k['okno_bok'][1] + 0.1))
        zan = list(dveri) + ([truba] if _peresek2(truba, (b0, b1, c0, c1)) else [])
        wr = b1 - b0
        if k['id'] == 'nochlezhka':
            wn = 0.8
            kand = [(b0 + 0.1, b0 + 0.1 + wn, c0 + 0.12, c0 + 2.12), (b1 - 0.1 - wn, b1 - 0.1, c1 - 2.12, c1 - 0.12),
                    (b1 - 0.1 - wn, b1 - 0.1, c0 + 0.12, c0 + 2.12), (b0 + 0.1, b0 + 0.1 + wn, c1 - 2.12, c1 - 0.12)]
            postavleno = 0
            for bb in kand:
                if postavleno >= 2:
                    break
                if any(_peresek2(bb, z) for z in zan + okna):
                    continue
                _nary(D, bb, F2)
                zan.append(bb)
                postavleno += 1
            _sunduk(D, zan, [(b0 + 0.1, b0 + 0.9, c0 + 2.25, c0 + 2.75), (b1 - 0.9, b1 - 0.1, c1 - 2.75, c1 - 2.25),
                             (b1 - 0.9, b1 - 0.1, c0 + 2.25, c0 + 2.75)], F2)
            _kryuchki(D, r, b0, b1, c0, c1, zan + okna, F2)
            continue
        wb = max(0.75, min(0.9, wr - 1.15))
        L = 2.0
        kand = [((b1 - 0.1 - wb, b1 - 0.1, c1 - 0.1 - L, c1 - 0.1), 'zad', 'prav'),
                ((b0 + 0.1, b0 + 0.1 + wb, c1 - 0.1 - L, c1 - 0.1), 'zad', 'lev'),
                ((b1 - 0.1 - wb, b1 - 0.1, c0 + 0.1, c0 + 0.1 + L), 'pered', 'prav'),
                ((b0 + 0.1, b0 + 0.1 + wb, c0 + 0.1, c0 + 0.1 + L), 'pered', 'lev')]
        for (bb, golova, _) in kand:
            su = (bb[0] + 0.05, bb[1] - 0.05, bb[2] - 0.6, bb[2] - 0.08) if golova == 'zad' else \
                (bb[0] + 0.05, bb[1] - 0.05, bb[3] + 0.08, bb[3] + 0.6)
            if any(_peresek2(bb, z) or _peresek2(su, z) for z in zan):
                continue
            _krovat(D, bb, golova, F2, KRAS if k['id'] == 'hozyajskaya' else TKAN)
            zan.append(bb)
            obhod = (bb[0] - b0 >= 0.85) or (b1 - bb[1] >= 0.85)
            kand_su = [su] if obhod else []
            kand_su += [(b0 + 0.08, b0 + 0.58, c0 + 1.3, c0 + 2.1), (b1 - 0.58, b1 - 0.08, c0 + 1.3, c0 + 2.1),
                        (b0 + 0.08, b0 + 0.58, c1 - 1.9, c1 - 1.1)]
            _sunduk(D, zan, kand_su, F2)
            break
        # столик и табурет у окна
        for o in k.get('okna', []):
            xc = (o[0] + o[1]) / 2.0
            st = (xc - 0.35, xc + 0.35, c0 + 0.1, c0 + 0.58)
            tb = (xc + 0.0, xc + 0.36, c0 + 0.75, c0 + 1.11)
            if any(_peresek2(st, z) or _peresek2(tb, z) for z in zan):
                continue
            D.kor('mebel', BRUS, st[0], st[1], st[2], st[3], F2 + 0.72, F2 + 0.78, 0.008)
            for a_ in (st[0] + 0.05, st[1] - 0.12):
                D.kor('mebel', BRUS, a_, a_ + 0.07, st[2] + 0.06, st[3] - 0.06, F2, F2 + 0.72)
            D.cil('mebel', BRUS, xc + 0.18, c0 + 0.93, F2, 0.18, 0.45, 8)
            D.cil('mebel', KAM, xc - 0.15, c0 + 0.34, F2 + 0.78, 0.07, 0.2, 8, 0.05)
            D.cil('mebel', ZHEL, xc + 0.12, c0 + 0.3, F2 + 0.78, 0.04, 0.12, 6)
            zan += [st, tb]
            break
        # хозяйской — шкаф, гостевой — умывальник; всем — половик и крючки
        if k['id'] == 'hozyajskaya':
            for bb in ((b0 + 0.08, b0 + 0.68, c0 + 0.9, c0 + 2.0), (b1 - 0.68, b1 - 0.08, c0 + 0.9, c0 + 2.0),
                       (b0 + 0.08, b0 + 0.68, c0 + 2.1, c0 + 3.2)):
                if any(_peresek2(bb, z) for z in zan + okna):
                    continue
                D.kor('mebel', BRUS, bb[0], bb[1], bb[2], bb[3], F2, F2 + 1.9, 0.015)
                D.kor('mebel', ZHEL, bb[0] - 0.01, bb[1] + 0.01, (bb[2] + bb[3]) / 2 - 0.02, (bb[2] + bb[3]) / 2 + 0.02, F2 + 0.9, F2 + 1.2)
                zan.append(bb)
                break
        else:
            for bb in ((b0 + 0.08, b0 + 0.52, c0 + 1.2, c0 + 1.66), (b1 - 0.52, b1 - 0.08, c0 + 1.2, c0 + 1.66),
                       (b0 + 0.08, b0 + 0.52, c0 + 2.3, c0 + 2.76)):
                if any(_peresek2(bb, z) for z in zan):
                    continue
                cu_, cv_ = (bb[0] + bb[1]) / 2.0, (bb[2] + bb[3]) / 2.0
                D.cil('mebel', BRUS, cu_, cv_, F2, 0.05, 0.78, 6)
                D.cil('mebel', BRUS, cu_, cv_, F2 + 0.78, 0.22, 0.04, 12)
                D.cil('mebel', ZHEL, cu_, cv_, F2 + 0.82, 0.19, 0.08, 12, 0.14)
                zan.append(bb)
                break
        pol = (b0 + 0.3, b1 - 0.3, c0 + 1.0, c1 - 1.1)
        if pol[1] - pol[0] > 0.5 and pol[3] - pol[2] > 0.6:
            D.kor('mebel', KRAS if k['id'] == 'hozyajskaya' else TKAN, pol[0], pol[1], pol[2], pol[3], F2 + 0.003, F2 + 0.015)
        _kryuchki(D, r, b0, b1, c0, c1, zan + okna, F2)


def _koridor(D, ui0, ui1, vi1, L_sh, kor_v0, F2, EV, kz):
    """Коридор верха: дорожка вдоль, лавка у задней стены между окнами, фонарь на стене у верха лестницы."""
    a0, a1 = ui0 + L_sh + 0.35, ui1 - 0.3
    D.kor('mebel', KRAS, a0, a1, kor_v0 + TV / 2 + 0.3, vi1 - 0.3, F2 + 0.003, F2 + 0.014)
    lu0, lu1 = ui0 + 2.55, ui1 - 2.6
    if lu1 - lu0 >= 0.9:
        c = (lu0 + lu1) / 2.0
        lu0, lu1 = c - min(0.8, (lu1 - lu0) / 2.0), c + min(0.8, (lu1 - lu0) / 2.0)
        D.kor('mebel', BRUS, lu0, lu1, vi1 - 0.36, vi1 - 0.04, F2 + 0.42, F2 + 0.48, 0.008)
        for x_ in (lu0 + 0.1, lu1 - 0.2):
            D.kor('mebel', BRUS, x_, x_ + 0.1, vi1 - 0.32, vi1 - 0.08, F2, F2 + 0.42)
    fu = ui0 + L_sh + 0.5
    D.kor('mebel', ZHEL, fu - 0.12, fu + 0.12, vi1 - 0.2, vi1 - 0.02, F2 + 1.75, F2 + 2.05)
    D.kor('mebel', STEK, fu - 0.09, fu + 0.09, vi1 - 0.18, vi1 - 0.05, F2 + 1.78, F2 + 2.02)
    D.istochnik('koridor', fu, vi1 - 0.35, F2 + 1.9, 1.6, 420.0, (255, 200, 150), False)


def _krovat(D, bb, golova, F2, pokryvalo=KRAS):
    u0, u1, v0, v1 = bb
    D.kor('mebel', BRUS, u0, u1, v0, v1, F2, F2 + 0.42, 0.01)
    D.kor('mebel', TKAN, u0 + 0.04, u1 - 0.04, v0 + 0.04, v1 - 0.04, F2 + 0.42, F2 + 0.55, 0.03)
    if golova == 'zad':
        D.kor('mebel', TKAN, u0 + 0.1, u1 - 0.1, v1 - 0.45, v1 - 0.1, F2 + 0.55, F2 + 0.68, 0.04)
        D.kor('mebel', BRUS, u0, u1, v1 - 0.08, v1, F2, F2 + 0.95)
        D.kor('mebel', pokryvalo, u0 + 0.03, u1 - 0.03, v0 + 0.05, v0 + 0.75, F2 + 0.55, F2 + 0.58)
    else:
        D.kor('mebel', TKAN, u0 + 0.1, u1 - 0.1, v0 + 0.1, v0 + 0.45, F2 + 0.55, F2 + 0.68, 0.04)
        D.kor('mebel', BRUS, u0, u1, v0, v0 + 0.08, F2, F2 + 0.95)
        D.kor('mebel', pokryvalo, u0 + 0.03, u1 - 0.03, v1 - 0.75, v1 - 0.05, F2 + 0.55, F2 + 0.58)


def _nary(D, bb, F2):
    u0, u1, v0, v1 = bb
    for ur in (F2 + 0.35, F2 + 1.4):
        D.kor('mebel', BRUS, u0, u1, v0, v1, ur, ur + 0.12, 0.01)
        D.kor('mebel', TKAN, u0 + 0.05, u1 - 0.05, v0 + 0.05, v1 - 0.05, ur + 0.12, ur + 0.2, 0.02)
    for (a, b) in ((u0, v0), (u1 - 0.1, v0), (u0, v1 - 0.1), (u1 - 0.1, v1 - 0.1)):
        D.kor('mebel', BRUS, a, a + 0.1, b, b + 0.1, F2, F2 + 1.8)
    D.brus('mebel', BRUS, (u1 - 0.05, v1 - 0.4, F2 + 0.2), (u1 - 0.05, v1 - 0.4, F2 + 1.5), 0.06, 0.06, (0, 1, 0))   # лесенка


def _sunduk(D, zan, kandidaty, F2):
    for bb in kandidaty:
        if any(_peresek2(bb, z) for z in zan):
            continue
        D.kor('mebel', BRUS, bb[0], bb[1], bb[2], bb[3], F2, F2 + 0.48, 0.02)
        D.kor('mebel', ZHEL, bb[0] - 0.02, bb[1] + 0.02, bb[2] - 0.02, bb[3] + 0.02, F2 + 0.2, F2 + 0.24)
        zan.append(bb)
        return bb
    return None


def _kryuchki(D, r, b0, b1, c0, c1, zan, F2):
    """Крючки с одеждой на свободной боковой стене."""
    for (u_, zn) in ((b0 + 0.02, 1), (b1 - 0.02, -1)):
        for vv in (c0 + 1.3, c0 + 2.4, c1 - 1.5):
            bb = (min(u_, u_ + zn * 0.35), max(u_, u_ + zn * 0.35), vv - 0.5, vv + 0.5)
            if any(_peresek2(bb, z) for z in zan):
                continue
            D.kor('mebel', BRUS, min(u_, u_ + zn * 0.06), max(u_, u_ + zn * 0.06), vv - 0.5, vv + 0.5, F2 + 1.6, F2 + 1.68)
            for j in range(r.randint(1, 2)):
                y_ = vv - 0.3 + j * 0.45
                D.kor('mebel', KRAS if j else TKAN, min(u_, u_ + zn * 0.14), max(u_, u_ + zn * 0.14), y_ - 0.17, y_ + 0.17,
                      F2 + 0.75, F2 + 1.6, 0.02)
            return


def _melochi_ulicy(D, r, kz, kr_u0, kr_u1, v0, P, NV0, dv_u0, dv_u1):
    """Обжитость у входа: лавка на крыльце, кадки с цветами у ступеней, фонарь у двери."""
    if kz != 'galereya':
        a0 = kr_u0 + 0.35
        a1 = min(dv_u0 - 0.3, a0 + 1.5)
        if a1 - a0 > 0.8:
            D.kor('melochi', BRUS, a0, a1, v0 - 0.55, v0 - 0.2, P + 0.42, P + 0.48, 0.008)
            for a in (a0 + 0.1, a1 - 0.2):
                D.kor('melochi', BRUS, a, a + 0.1, v0 - 0.5, v0 - 0.25, P, P + 0.42)
    kv = NV0 - 0.15 if kz != 'galereya' else v0 - 1.9
    for uu in (dv_u0 - 0.95, dv_u1 + 0.95):
        D.cil('melochi', BRUS, uu, kv, 0.0, 0.26, 0.42, 12)
        D.sfera('melochi', TRAV, uu, kv, 0.58, 0.3, (1.0, 1.0, 0.7), 3)
        for k in range(5):
            D.sfera('melochi', CVET, uu + 0.16 * math.cos(k * 1.3), kv + 0.16 * math.sin(k * 1.3), 0.72, 0.07, (1, 1, 1), 2)
    fu = dv_u0 - 0.35
    D.kor('melochi', ZHEL, fu - 0.04, fu + 0.04, v0 - 0.35, v0 - 0.02, P + 2.35, P + 2.39)
    D.kor('melochi', ZHEL, fu - 0.14, fu + 0.14, v0 - 0.49, v0 - 0.21, P + 1.95, P + 2.3)
    D.kor('melochi', STEK, fu - 0.11, fu + 0.11, v0 - 0.46, v0 - 0.24, P + 1.98, P + 2.27)
