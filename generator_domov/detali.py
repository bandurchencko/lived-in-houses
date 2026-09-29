# -*- coding: utf-8 -*-
"""Детали дома — описание без движка: что и где поставить общими деталями `ue/dom_detali.py`.

Каждая деталь — словарь с видом 't', местом материала 'm' (номера — `stil_mangala.py`) и группой 'g' (своя сетка в
Unreal: оболочка, перегородки, полы и потолки, кровля, мебель, мелочи — так держит свет Lumen). Оси дома — u, v, w в
метрах (см. `__init__.py`).
"""
import math

GRUPPY = ('obolochka', 'peregorodki', 'poly', 'krysha', 'mebel', 'melochi')


class Detali:
    def __init__(self):
        self.spisok = []
        self.svet = []
        self.proemy = []          # проёмы наружных стен — для проверок (балка не поперёк окна и т. п.)

    def _d(self, g, **kw):
        assert g in GRUPPY, g
        kw['g'] = g
        self.spisok.append(kw)
        return kw

    # --- простые тела ---
    def kor(self, g, m, u0, u1, v0, v1, w0, w1, fs=0.0):
        if u1 - u0 < 1e-3 or v1 - v0 < 1e-3 or w1 - w0 < 1e-3:
            return None
        return self._d(g, t='kor', m=m, b=[round(u0, 4), round(u1, 4), round(v0, 4), round(v1, 4), round(w0, 4),
                                           round(w1, 4)], fs=fs)

    def stena(self, g, m, box, vyrezy, fs=0.0):
        """Короб с вырезами проёмов (двери, окна) — вырезы в тех же осях, насквозь."""
        vyr = [[round(x, 4) for x in b] for b in vyrezy if _peresek(box, b)]
        return self._d(g, t='stena', m=m, b=[round(x, 4) for x in box], vyr=vyr, fs=fs)

    def brus(self, g, m, p1, p2, shir, tol, os_=(0, 0, 1), fs=0.015):
        return self._d(g, t='brus', m=m, p1=[round(x, 4) for x in p1], p2=[round(x, 4) for x in p2], sh=shir, tol=tol,
                       os=list(os_), fs=fs)

    def plita(self, g, m, tochki, tol=0.14, uv_v=None):
        """uv_v — сдвиг развёртки вдоль ската (м): у граней одного ската рисунок идёт сплошь через переломы."""
        if uv_v is None:
            return self._d(g, t='plita', m=m, pts=[[round(x, 4) for x in p] for p in tochki], tol=tol)
        return self._d(g, t='plita', m=m, pts=[[round(x, 4) for x in p] for p in tochki], tol=tol, uv_v=round(uv_v, 4))

    def profil(self, g, m, tochki, plan, a0, a1, fs=0.0):
        return self._d(g, t='profil', m=m, pts=[[round(x, 4) for x in p] for p in tochki], plan=plan, a0=round(a0, 4),
                       a1=round(a1, 4), fs=fs)

    def cil(self, g, m, cu, cv, w0, r, h, n=10, r2=None):
        return self._d(g, t='cil', m=m, c=[round(cu, 4), round(cv, 4)], w0=round(w0, 4), r=r, h=h, n=n, r2=r2)

    def cil_os(self, g, m, p1, p2, r, n=10, r2=None):
        return self._d(g, t='cil_os', m=m, p1=[round(x, 4) for x in p1], p2=[round(x, 4) for x in p2], r=r, n=n, r2=r2)

    def sfera(self, g, m, cu, cv, cw, r, masht=(1.0, 1.0, 1.0), shagi=3):
        return self._d(g, t='sfera', m=m, c=[round(cu, 4), round(cv, 4), round(cw, 4)], r=r, masht=list(masht),
                       shagi=shagi)

    def okno(self, os_, a0, a1, w0, w1, lico, znak, perepl=1, stavni=False, steklo=True, glub=0.2, otliv=True):
        """Окно в проёме наружной стены (коробка рамы, стекло, переплёт, отлив, ставни — `dom_detali.okno`)."""
        return self._d('obolochka', t='okno', os=os_, a0=round(a0, 4), a1=round(a1, 4), w0=round(w0, 4),
                       w1=round(w1, 4), lico=round(lico, 4), znak=znak, perepl=perepl, stavni=bool(stavni), steklo=bool(steklo), glub=glub, otliv=bool(otliv))

    def cherepica(self, uk, wk, ex, ez, nx, nz, v_ot, v_do, ryadov=4, os_karniza='u'):
        """Ряды настоящей черепицы у карниза одного ската (`dom_detali.cherepica_karniz`)."""
        return self._d('krysha', t='cherepica', uk=round(uk, 4), wk=round(wk, 4), ex=ex, ez=ez, nx=nx, nz=nz,
                       v_ot=round(v_ot, 4), v_do=round(v_do, 4), ryadov=ryadov, os_karniza=os_karniza)

    def istochnik(self, imya, u, v, w, sila, rad, cvet, ten=True):
        self.svet.append({'imya': imya, 'p': [round(u, 3), round(v, 3), round(w, 3)], 'sila': sila, 'rad': rad,
                          'cvet': list(cvet), 'ten': ten})

    def po_gruppam(self):
        out = {g: 0 for g in GRUPPY}
        for d in self.spisok:
            out[d['g']] += 1
        return out

    def v_json(self):
        return {'detali': self.spisok, 'svet': self.svet, 'po_gruppam': self.po_gruppam()}


def _peresek(a, b):
    return all(min(a[2 * i + 1], b[2 * i + 1]) - max(a[2 * i], b[2 * i]) > 1e-4 for i in range(3))


def zerkalo_detalej(spisok, svet, SU):
    """Отражение всего дома по u (u → SU − u): лестница и галерея на другую сторону. Меняет порядок пределов."""
    def mu(x):
        return round(SU - x, 4)
    for d in spisok:
        t = d['t']
        if t in ('kor', 'stena'):
            b = d['b']
            b[0], b[1] = mu(b[1]), mu(b[0])
            if t == 'stena':
                for c in d['vyr']:
                    c[0], c[1] = mu(c[1]), mu(c[0])
        elif t in ('brus', 'cil_os'):
            d['p1'][0], d['p2'][0] = mu(d['p1'][0]), mu(d['p2'][0])
        elif t == 'plita':
            d['pts'] = [[mu(p[0]), p[1], p[2]] for p in reversed(d['pts'])]
        elif t == 'profil':
            if d['plan'] == 'uw':
                d['pts'] = [[mu(p[0]), p[1]] for p in reversed(d['pts'])]
            elif d['plan'] == 'uv':
                d['pts'] = [[mu(p[0]), p[1]] for p in reversed(d['pts'])]
            else:                                   # 'vw' — выдавлено по u
                d['a0'], d['a1'] = mu(d['a1']), mu(d['a0'])
        elif t in ('cil', 'sfera'):
            d['c'][0] = mu(d['c'][0])
        elif t == 'okno':
            if d['os'] == 'u':
                d['a0'], d['a1'] = mu(d['a1']), mu(d['a0'])
            else:
                d['lico'] = mu(d['lico'])
                d['znak'] = -d['znak']
        elif t == 'cherepica':
            if d['os_karniza'] == 'u':
                d['v_ot'], d['v_do'] = mu(d['v_do']), mu(d['v_ot'])
            else:
                d['uk'] = mu(d['uk'])
                d['ex'] = -d['ex']
                d['nx'] = -d['nx']
    for s in svet:
        s['p'][0] = mu(s['p'][0])


def ugol(gr):
    return math.radians(gr)
