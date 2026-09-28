# -*- coding: utf-8 -*-
"""Дом генератора без движка → glTF (GLB): те же детали, что собирает в Unreal `ue/dom_detali.py`, — тела сетками numpy,
по группам (оболочка, перегородки, полы, кровля, мебель, мелочи — узлы GLB: их можно прятать, снять крышу и заглянуть
внутрь), материалы — цветами облика земли. Чтобы генератор можно было показать и попробовать без Unreal: браузер
(`prosmotr/index.html`), Blender, любой просмотрщик glTF.

    python -m generator_domov.eksport_glb traktir <зерно> [--kompoz=naves|galereya|ugol|pristrojka] [--krysha=valma|dvuskat]
        [--vyhod=файл.glb]
    python -m generator_domov.eksport_glb dom-dvor <зерно> [--chast=sad|masterskaya|krylco] [--sad=sev|jug]
        [--stil=mangala|kolybel] [--vyhod=файл.glb]

Оси: u, v, w генератора (w — вверх, метры) → glTF x = u, y = w, z = v. Оси Unreal левые, glTF — правые: одна
перестановка осей даёт тот же вид без зеркала.
"""
import json
import math
import os
import random
import re
import sys

import numpy as np
import trimesh

from .detali import GRUPPY

# места материалов (stil_mangala: 0 камень, 1 известь, 2 тёмный брус, 3 черепица/камыш, 4 стекло, 5 мареновая ткань,
# 6 железо, 7 травы, 8 цветы, 9 доски, 10 мешки, 11 мощение, 12 угли) → (RGBA 0..1, шероховатость, металл, свечение)
_OBSHCHEE = {4: ((0.66, 0.76, 0.82, 0.35), 0.1, 0.0, 0.0), 5: ((0.56, 0.12, 0.10, 1), 0.8, 0.0, 0.0),
             6: ((0.18, 0.18, 0.20, 1), 0.45, 0.8, 0.0), 7: ((0.36, 0.46, 0.22, 1), 0.9, 0.0, 0.0),
             8: ((0.82, 0.38, 0.52, 1), 0.8, 0.0, 0.0), 9: ((0.52, 0.38, 0.24, 1), 0.8, 0.0, 0.0),
             10: ((0.74, 0.64, 0.46, 1), 0.95, 0.0, 0.0), 11: ((0.62, 0.57, 0.52, 1), 0.85, 0.0, 0.0),
             12: ((1.00, 0.45, 0.12, 1), 0.6, 0.0, 1.0)}
PALITRA = {
    'mangala': {**_OBSHCHEE, **{0: ((0.56, 0.30, 0.22, 1), 0.9, 0.0, 0.0), 1: ((0.88, 0.84, 0.76, 1), 0.85, 0.0, 0.0),
                                  2: ((0.27, 0.18, 0.12, 1), 0.75, 0.0, 0.0), 3: ((0.68, 0.35, 0.22, 1), 0.7, 0.0, 0.0)}},
    'kolybel': {**_OBSHCHEE, **{0: ((0.58, 0.55, 0.48, 1), 0.9, 0.0, 0.0), 1: ((0.86, 0.78, 0.60, 1), 0.9, 0.0, 0.0),
                                  2: ((0.24, 0.16, 0.10, 1), 0.75, 0.0, 0.0), 3: ((0.60, 0.50, 0.30, 1), 0.95, 0.0, 0.0)}},
}
BRUS, STEK, KRAS, ZHEL, CHER = 2, 4, 5, 6, 3
CVETA_MESTA = {'kamen': 0, 'steny': 1, 'brus': 2, 'krysha': 3, 'stavni': 5}   # цвета облика с картинки → места


def palitra(stil='mangala', cveta=None):
    """Палитра облика; cveta — {'steny': '#rrggbb', …} с картинки (obraz.py) поверх неё."""
    pal = dict(PALITRA.get(stil, PALITRA['mangala']))
    for k, hx in (cveta or {}).items():
        m = CVETA_MESTA.get(k)
        if m is None or not isinstance(hx, str) or not re.fullmatch(r'#?[0-9a-fA-F]{6}', hx.strip()):
            continue                                   # ИИ ошибся в цвете — место остаётся с цветом облика
        hx = hx.strip()
        h = hx.lstrip('#')
        rgb = tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
        _, sher, met, sv = pal[m]
        pal[m] = ((rgb[0], rgb[1], rgb[2], 1.0), sher, met, sv)
    return pal

_KOR_F = np.array([[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7], [0, 1, 5], [0, 5, 4],
                   [1, 2, 6], [1, 6, 5], [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7]])


def _norm(a):
    a = np.asarray(a, float)
    n = np.linalg.norm(a)
    return a / n if n > 1e-9 else a


def _naruzhu(V, F):
    """Обход граней — наружу (правило правой руки в осях u, v, w): знак объёма тела."""
    V, F = np.asarray(V, float), np.asarray(F, int)
    a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    if np.einsum('ij,ij->i', a, np.cross(b, c)).sum() < 0:
        F = F[:, ::-1]
    return V, F


def _ushi(pts):
    """Треугольники простого многоугольника (срезание ушей); pts — [(x, y)], обход любой."""
    P = [tuple(p) for p in pts]
    if len(P) >= 2 and np.allclose(P[0], P[-1]):
        P = P[:-1]
    idx = list(range(len(P)))
    pl = sum(P[i][0] * P[i - 1][1] - P[i - 1][0] * P[i][1] for i in range(len(P)))
    if pl > 0:                                          # приводим к обходу против часовой
        idx.reverse()

    def ccw(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    def vnutri(p, a, b, c):
        d1, d2, d3 = ccw(a, b, p), ccw(b, c, p), ccw(c, a, p)
        return d1 >= -1e-12 and d2 >= -1e-12 and d3 >= -1e-12
    tri = []
    ohrana = 0
    while len(idx) > 3 and ohrana < 10000:
        ohrana += 1
        n = len(idx)
        for k in range(n):
            i0, i1, i2 = idx[k - 1], idx[k], idx[(k + 1) % n]
            a, b, c = P[i0], P[i1], P[i2]
            if ccw(a, b, c) <= 1e-12:
                continue
            if any(vnutri(P[j], a, b, c) for j in idx if j not in (i0, i1, i2)):
                continue
            tri.append((i0, i1, i2))
            idx.pop(k)
            break
        else:                                           # вырожденный остаток — веером
            break
    if len(idx) >= 3:
        for k in range(1, len(idx) - 1):
            tri.append((idx[0], idx[k], idx[k + 1]))
    return tri


class Sborka:
    """Тела по (группа, место материала); в конце — сетки и сцена GLB."""

    def __init__(self, zerno=27):
        self.kuski = {}
        self.rnd = random.Random(zerno)

    def dob(self, g, m, V, F):
        V, F = _naruzhu(V, F)
        self.kuski.setdefault((g, int(m)), []).append((V, F))

    # — тела —
    def kor(self, g, m, u0, u1, v0, v1, w0, w1):
        u0, u1 = sorted((u0, u1))
        v0, v1 = sorted((v0, v1))
        w0, w1 = sorted((w0, w1))
        if u1 - u0 < 1e-4 or v1 - v0 < 1e-4 or w1 - w0 < 1e-4:
            return
        V = [[u0, v0, w0], [u1, v0, w0], [u1, v1, w0], [u0, v1, w0], [u0, v0, w1], [u1, v0, w1], [u1, v1, w1], [u0, v1, w1]]
        self.dob(g, m, V, _KOR_F)

    def obox(self, g, m, c, ex, ey, ez, hx, hy, hz):
        """Повёрнутый короб: центр c, оси ex, ey, ez, полуразмеры."""
        c, ex, ey, ez = (np.asarray(x, float) for x in (c, ex, ey, ez))
        V = [c + sx * hx * ex + sy * hy * ey + sz * hz * ez
             for sz in (-1, 1) for (sx, sy) in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        self.dob(g, m, V, _KOR_F)

    def stena(self, g, m, b, vyr):
        """Короб с проёмами насквозь: клетки по рёбрам проёмов, проёмы вынуты, столбики клеток слиты по высоте."""
        u0, u1, v0, v1, w0, w1 = b
        tonkaya_u = abs(u1 - u0) <= abs(v1 - v0)
        L0, L1 = (v0, v1) if tonkaya_u else (u0, u1)
        L0, L1 = sorted((L0, L1))
        w0, w1 = sorted((w0, w1))
        vyr_ = []
        for c in vyr:
            a0, a1 = sorted((c[2], c[3]) if tonkaya_u else (c[0], c[1]))
            q0, q1 = sorted((c[4], c[5]))
            vyr_.append((max(a0, L0), min(a1, L1), max(q0, w0), min(q1, w1)))
        xs = sorted({L0, L1} | {x for c in vyr_ for x in (c[0], c[1]) if L0 < x < L1})
        ws = sorted({w0, w1} | {x for c in vyr_ for x in (c[2], c[3]) if w0 < x < w1})
        for a, b_ in zip(xs, xs[1:]):
            lc = (a + b_) / 2
            ryad = None
            for q, r in zip(ws, ws[1:]):
                qc = (q + r) / 2
                dyra = any(c[0] < lc < c[1] and c[2] < qc < c[3] for c in vyr_)
                if dyra:
                    if ryad:
                        self._stena_kusok(g, m, tonkaya_u, b, a, b_, ryad[0], ryad[1])
                    ryad = None
                else:
                    ryad = (ryad[0], r) if ryad else (q, r)
            if ryad:
                self._stena_kusok(g, m, tonkaya_u, b, a, b_, ryad[0], ryad[1])

    def _stena_kusok(self, g, m, tonkaya_u, b, a, b_, q, r):
        if tonkaya_u:
            self.kor(g, m, b[0], b[1], a, b_, q, r)
        else:
            self.kor(g, m, a, b_, b[2], b[3], q, r)

    def brus(self, g, m, p1, p2, sh, tol, os_=(0, 0, 1)):
        p1, p2 = np.asarray(p1, float), np.asarray(p2, float)
        d = p2 - p1
        L = np.linalg.norm(d)
        if L < 0.01:
            return
        ex = d / L
        ey = np.asarray(os_, float) - np.dot(os_, ex) * ex
        if np.linalg.norm(ey) < 1e-6:
            alt = np.array([1.0, 0, 0]) if abs(ex[0]) < 0.9 else np.array([0, 1.0, 0])
            ey = alt - np.dot(alt, ex) * ex
        ey = _norm(ey)
        ez = np.cross(ex, ey)
        self.obox(g, m, (p1 + p2) / 2, ex, ey, ez, L / 2, sh / 2, tol / 2)

    def prizma(self, g, m, niz, verh):
        """Призма из двух многоугольников (одинаковый порядок точек): крышки срезанием ушей, бока квадами."""
        n = len(niz)
        V = [list(p) for p in niz] + [list(p) for p in verh]
        a = np.asarray(verh, float)
        nrm = _norm(np.cross(a[1] - a[0], a[2] - a[0]))
        e1 = _norm(a[1] - a[0])
        e2 = np.cross(nrm, e1)
        loc = [(float(np.dot(p - a[0], e1)), float(np.dot(p - a[0], e2))) for p in a]
        F = []
        for i, j, k in _ushi(loc):
            F.append([i + n, j + n, k + n])
            F.append([k, j, i])
        for i in range(n):
            j = (i + 1) % n
            F.append([i, j, j + n])
            F.append([i, j + n, i + n])
        self.dob(g, m, V, F)

    def plita(self, g, m, pts, tol):
        a = np.asarray(pts, float)
        nrm = _norm(np.cross(a[1] - a[0], a[2] - a[0]))
        if nrm[2] < 0:
            nrm = -nrm
        self.prizma(g, m, a - nrm * tol, a)

    def profil(self, g, m, pts, plan, a0, a1):
        def t(p, q, s):
            return (p, s, q) if plan == 'uw' else ((s, p, q) if plan == 'vw' else (p, q, s))
        self.prizma(g, m, [t(p, q, a0) for p, q in pts], [t(p, q, a1) for p, q in pts])

    def cil_os(self, g, m, p1, p2, r, n=10, r2=None):
        p1, p2 = np.asarray(p1, float), np.asarray(p2, float)
        d = p2 - p1
        if np.linalg.norm(d) < 1e-4:
            return
        ez = _norm(d)
        alt = np.array([1.0, 0, 0]) if abs(ez[0]) < 0.9 else np.array([0, 1.0, 0])
        ex = _norm(alt - np.dot(alt, ez) * ez)
        ey = np.cross(ez, ex)
        r2 = r if r2 is None else r2
        n = max(3, int(n))
        kr = [(math.cos(2 * math.pi * k / n), math.sin(2 * math.pi * k / n)) for k in range(n)]
        self.prizma(g, m, [p1 + r * (c * ex + s * ey) for c, s in kr], [p2 + r2 * (c * ex + s * ey) for c, s in kr])

    def cil(self, g, m, cu, cv, w0, r, h, n=10, r2=None):
        self.cil_os(g, m, (cu, cv, w0), (cu, cv, w0 + h), r, n, r2)

    def sfera(self, g, m, c, r, masht=(1, 1, 1), shagi=3):
        s = trimesh.creation.icosphere(subdivisions=1 if shagi <= 3 else 2, radius=r)
        V = s.vertices * np.asarray(masht, float) + np.asarray(c, float)
        self.dob(g, m, V, s.faces)

    def okno(self, os_, a0, a1, w0, w1, lico, znak, perepl=1, stavni=False, gorbylek=True, steklo=True, glub=0.2):
        """Как `ue/dom_detali.okno`: рама, стекло, переплёт, отлив, ставни к стене."""
        g = 'obolochka'

        def k(mid, p0, p1, d0, d1, q0, q1):
            g0, g1 = lico + znak * d0, lico + znak * d1
            if os_ == 'u':
                self.kor(g, mid, p0, p1, g0, g1, q0, q1)
            else:
                self.kor(g, mid, g0, g1, p0, p1, q0, q1)
        g0, g1 = -(glub + 0.04), -(glub - 0.04)
        k(BRUS, a0, a1, g0, g1, w0, w0 + 0.06)
        k(BRUS, a0, a1, g0, g1, w1 - 0.06, w1)
        k(BRUS, a0, a0 + 0.06, g0, g1, w0, w1)
        k(BRUS, a1 - 0.06, a1, g0, g1, w0, w1)
        if steklo:
            k(STEK, a0 + 0.05, a1 - 0.05, -(glub + 0.01), -(glub - 0.01), w0 + 0.05, w1 - 0.05)
        shag = (a1 - a0) / (perepl + 1)
        for j in range(1, perepl + 1 if steklo else 1):
            pj = a0 + j * shag
            k(BRUS, pj - 0.035, pj + 0.035, -glub, -(glub - 0.05), w0 + 0.05, w1 - 0.05)
        if gorbylek and steklo:
            k(BRUS, a0 + 0.05, a1 - 0.05, -glub, -(glub - 0.05), w0 + (w1 - w0) * 0.62, w0 + (w1 - w0) * 0.62 + 0.05)
        k(BRUS, a0 - 0.06, a1 + 0.06, -0.02, 0.07, w0 - 0.06, w0)
        if stavni:
            for p0, p1 in ((a0 - (a1 - a0) / 2 - 0.02, a0 - 0.02), (a1 + 0.02, a1 + (a1 - a0) / 2 + 0.02)):
                k(KRAS, p0, p1, 0.02, 0.06, w0, w1)
                for dz in (0.2, (w1 - w0) - 0.2):
                    k(ZHEL, p0, p1, 0.06, 0.075, w0 + dz - 0.02, w0 + dz + 0.02)

    def cherepica(self, uk, wk, ex, ez, nx, nz, v_ot, v_do, ryadov=4, dl_ch=0.3, shir_ch=0.21, tol_ch=0.018,
                  zazor=0.015, nad=0.012, os_karniza='v'):
        """Как `ue/dom_detali.cherepica_karniz`: ряды черепицы у карниза с нахлёстом и сдвигом через ряд."""
        rnd = self.rnd
        shag_ryada = dl_ch * 0.66
        for ryad in range(ryadov):
            s_ = 0.02 + ryad * shag_ryada
            smesh = (shir_ch + zazor) / 2.0 if ryad % 2 else 0.0
            vv = v_ot + shir_ch / 2 + smesh
            while vv < v_do - shir_ch / 2:
                dl = dl_ch + rnd.uniform(-0.02, 0.02)
                cu = uk + ex * (s_ + dl / 2) + nx * (nad + 0.006 * ryad)
                cw = wk + ez * (s_ + dl / 2) + nz * (nad + 0.006 * ryad)
                if os_karniza == 'v':
                    d, bok, c = np.array([ex, 0, ez]), np.array([0, 1.0, 0]), (cu, vv, cw)
                else:
                    d, bok, c = np.array([0, ex, ez]), np.array([1.0, 0, 0]), (vv, cu, cw)
                d = _norm(d + np.array([rnd.uniform(-0.02, 0.02) for _ in range(3)]))
                nn = _norm(np.cross(d, bok))
                bok = np.cross(nn, d)
                self.obox('krysha', CHER, c, d, bok, nn, dl / 2, shir_ch / 2, tol_ch / 2)
                vv += shir_ch + zazor

    # — детали генератора —
    def detal(self, d):
        t, m, g = d['t'], d.get('m'), d.get('g', 'obolochka')
        if t == 'kor':
            self.kor(g, m, *d['b'])
        elif t == 'stena':
            self.stena(g, m, d['b'], d['vyr'])
        elif t == 'brus':
            self.brus(g, m, d['p1'], d['p2'], d['sh'], d['tol'], d.get('os', (0, 0, 1)))
        elif t == 'plita':
            self.plita(g, m, d['pts'], d['tol'])
        elif t == 'profil':
            self.profil(g, m, d['pts'], d['plan'], d['a0'], d['a1'])
        elif t == 'cil':
            self.cil(g, m, d['c'][0], d['c'][1], d['w0'], d['r'], d['h'], d.get('n', 10), d.get('r2'))
        elif t == 'cil_os':
            self.cil_os(g, m, d['p1'], d['p2'], d['r'], d.get('n', 10), d.get('r2'))
        elif t == 'sfera':
            self.sfera(g, m, d['c'], d['r'], d.get('masht', (1, 1, 1)), d.get('shagi', 3))
        elif t == 'okno':
            self.okno(d['os'], d['a0'], d['a1'], d['w0'], d['w1'], d['lico'], d['znak'], d.get('perepl', 1),
                      d.get('stavni', False), steklo=d.get('steklo', True), glub=d.get('glub', 0.2))
        elif t == 'cherepica':
            self.cherepica(d['uk'], d['wk'], d['ex'], d['ez'], d['nx'], d['nz'], d['v_ot'], d['v_do'],
                           ryadov=d['ryadov'], os_karniza=d['os_karniza'])
        else:
            raise ValueError('неизвестная деталь %s' % t)

    def scena(self, stil='mangala', zemlya=None, cveta=None):
        """→ trimesh.Scene: узел на группу, внутри — сетка на место материала; zemlya — (u0, u1, v0, v1) плиты земли;
        cveta — цвета облика с картинки поверх палитры."""
        pal = palitra(stil, cveta)
        sc = trimesh.Scene()
        if zemlya:
            u0, u1, v0, v1 = zemlya
            self.kor('zemlya', -1, u0, u1, v0, v1, -0.3, -0.02)
        for g in list(GRUPPY) + ['zelen', 'zemlya']:
            kl = [k for k in self.kuski if k[0] == g]
            if not kl:
                continue
            sc.graph.update(frame_from=sc.graph.base_frame, frame_to=g)
            for (g_, m) in sorted(kl, key=lambda k: k[1]):
                Vs, Fs, o = [], [], 0
                for V, F in self.kuski[(g_, m)]:
                    Vs.append(V)
                    Fs.append(F + o)
                    o += len(V)
                V = np.vstack(Vs)
                F = np.vstack(Fs)
                V = V[:, [0, 2, 1]]                        # (u, v, w) → (x = u, y = w, z = v)
                F = F[:, ::-1]                             # перестановка осей переворачивает обход
                Vf = V[F].reshape(-1, 3)                   # грани плоские: у каждой свои вершины (без сглаживания углов)
                Ff = np.arange(len(Vf)).reshape(-1, 3)
                uv = razvertka(Vf, Ff)
                if m < 0:
                    cvet, sher, met, sv = (0.42, 0.40, 0.30, 1), 1.0, 0.0, 0.0
                else:
                    cvet, sher, met, sv = pal.get(m, ((0.7, 0.7, 0.7, 1), 0.8, 0.0, 0.0))
                mat = trimesh.visual.material.PBRMaterial(
                    name='m%02d' % m if m >= 0 else 'zemlya',
                    baseColorFactor=[int(round(255 * x)) for x in cvet], roughnessFactor=sher, metallicFactor=met,
                    emissiveFactor=[cvet[0] * sv, cvet[1] * sv, cvet[2] * sv] if sv else None,
                    alphaMode='BLEND' if cvet[3] < 1 else 'OPAQUE', doubleSided=cvet[3] < 1)
                mesh = trimesh.Trimesh(Vf, Ff, process=False)
                mesh.visual = trimesh.visual.TextureVisuals(uv=uv, material=mat)
                sc.add_geometry(mesh, node_name='%s__m%02d' % (g, max(m, 0)), geom_name='%s__m%02d' % (g, max(m, 0)),
                                parent_node_name=g)
        return sc


def razvertka(V, F):
    """Развёртка в метрах в плоскости каждой грани (glTF: y — вверх): первая ось — горизонталь грани, вторая — вверх
    по ней (черепица идёт вдоль карниза, кладка — рядами); у лежачих граней — оси x и z. Фактуру кладёт просмотр
    (шаг плитки — у набора фактур)."""
    a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    n = np.cross(b - a, c - a)
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    vverh = np.array([0.0, 1.0, 0.0])
    t = np.cross(vverh, n)
    lezh = np.linalg.norm(t, axis=1) < 0.25                 # почти лежачая грань — оси x и z
    t[lezh] = np.array([1.0, 0.0, 0.0])
    t /= np.maximum(np.linalg.norm(t, axis=1, keepdims=True), 1e-12)
    bb = np.cross(n, t)
    bb[lezh] = np.array([0.0, 0.0, 1.0])
    T, B = np.repeat(t, 3, axis=0), np.repeat(bb, 3, axis=0)
    P = V[F].reshape(-1, 3)
    return np.stack([np.einsum('ij,ij->i', P, T), np.einsum('ij,ij->i', P, B)], axis=1)


def dom_v_glb(D, put, stil='mangala', zemlya=None, zerno=27, plan=None, cveta=None):
    """Детали генератора (Detali или список словарей) → GLB. → сводка (треугольники по группам). plan — план дома:
    его садовые деревья (u, v, высота, масштаб, поворот) — стволом и кроной в группу «зелень» (в Unreal их ставит зелень
    двора настоящими растениями)."""
    S = Sborka(zerno)
    for d in getattr(D, 'spisok', D):
        S.detal(d)
    for (u, v, hz, masht, yaw) in (plan or {}).get('derevya', []):
        h = 2.4 * masht
        S.cil_os('zelen', BRUS, (u, v, hz), (u, v, hz + h), 0.13 * masht, 8, 0.09 * masht)
        S.sfera('zelen', 7, (u, v, hz + h + 0.4 * masht), 1.5 * masht, (1.0, 1.0, 0.85), 3)
    if zemlya is True:                                   # плита земли — по рамке дома с запасом 3 м
        V = np.vstack([V for kuski in S.kuski.values() for V, _ in kuski])
        zemlya = (V[:, 0].min() - 3.0, V[:, 0].max() + 3.0, V[:, 1].min() - 3.0, V[:, 1].max() + 3.0)
    sc = S.scena(stil, zemlya, cveta)
    os.makedirs(os.path.dirname(os.path.abspath(put)), exist_ok=True)
    sc.export(put)
    svodka = {}
    for (g, m), kuski in S.kuski.items():
        svodka[g] = svodka.get(g, 0) + sum(len(F) for _, F in kuski)
    return svodka


def main(a):
    from . import dom_dvor, traktir
    opc = dict(x[2:].split('=', 1) for x in a if x.startswith('--') and '=' in x)
    poz = [x for x in a if not x.startswith('--')]
    semejstvo, zerno = poz[0], int(poz[1])
    if semejstvo == 'traktir':
        pas, plan, D = traktir.sobrat(zerno, opc.get('kompoz'), krysha=opc.get('krysha'))
        stil = 'mangala'
        imya = 'traktir-%d-%s' % (zerno, pas['kompoz']) + ('-dvuskat' if opc.get('krysha') == 'dvuskat' else '')
    elif semejstvo == 'dom-dvor':
        stil = opc.get('stil', 'mangala')
        chast, sad = opc.get('chast', 'sad'), opc.get('sad')
        if chast == 'sad' and not sad:
            sad = 'jug'
        pas, plan, D = dom_dvor.sobrat(zerno, chast, [], None, sad if chast != 'krylco' else None, stil)
        imya = 'dom-dvor-%s-%s-%s-%d' % (stil, chast, sad or 'x', zerno)
    else:
        sys.exit('семейство: traktir | dom-dvor')
    put = opc.get('vyhod', os.path.join('rab', 'generator-glb', imya + '.glb'))
    svodka = dom_v_glb(D, put, stil, True, plan=plan)
    print('%s → %s: треугольников %d %s; %.1f МБ' % (imya, put, sum(svodka.values()), json.dumps(svodka, ensure_ascii=False),
                                                    os.path.getsize(put) / 1e6))
    return put


if __name__ == '__main__':
    main(sys.argv[1:])
