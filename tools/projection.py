#!/usr/bin/env python3
"""Projection (lon, lat) -> coordonnees SVG de geo/europe.json.

Le fond de carte est dans une projection conique dont les parametres ne sont
pas documentes. Plutot que de les deviner, on ajuste une transformation
polynomiale de degre 2 sur les centres d'aire des traces de pays, ce qui
absorbe n'importe quelle conique sur l'emprise europeenne.

Les coefficients ci-dessous sont produits par `python3 tools/projection.py --fit`
et valides par appartenance : chaque ecole doit tomber dans le trace de son
pays. Ne pas les editer a la main.
"""
import json, math, re, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Ajustes sur 28 pays compacts : rms 3.79 px, ecart maximal 11.9 px, soit de
# l'ordre de 13 km a l'echelle du fond. Suffisant pour situer une ville, pas
# pour situer une rue : les coordonnees des ecoles sont de niveau localite.
COEF_X = [102.2654964, 31.2464312, 0.5270365, -0.0046501, -0.3267308, 0.0368594]
COEF_Y = [1650.1710413, 4.2118725, -23.3485799, -0.1004455, -0.0326683, 0.0109518]


def project(lon, lat):
    """(lon, lat) en degres -> (x, y) dans le repere SVG 1000 x 862.8."""
    t = [1.0, lon, lat, lon * lon, lon * lat, lat * lat]
    return (sum(c * v for c, v in zip(COEF_X, t)),
            sum(c * v for c, v in zip(COEF_Y, t)))


# --------------------------------------------------------------------------
# outillage : ajustement et validation. Non utilise par build.py.
# --------------------------------------------------------------------------

def anneaux(d):
    """Decoupe un attribut SVG 'd' en listes de points."""
    out, cur = [], []
    for m in re.finditer(r'([MLZ])([-\d.]*),?([-\d.]*)', d):
        c, a, b = m.group(1), m.group(2), m.group(3)
        if c == 'Z':
            if len(cur) > 2:
                out.append(cur)
            cur = []
        else:
            cur.append((float(a), float(b)))
    if len(cur) > 2:
        out.append(cur)
    return out


def dans_trace(d, x, y):
    """Le point tombe-t-il dans l'un des anneaux du trace ?"""
    for p in anneaux(d):
        dedans = False
        for i in range(len(p)):
            x0, y0 = p[i]
            x1, y1 = p[(i - 1) % len(p)]
            if (y0 > y) != (y1 > y) and x < (x1 - x0) * (y - y0) / (y1 - y0) + x0:
                dedans = not dedans
        if dedans:
            return True
    return False


def _centre_aire(d):
    best = None
    for p in anneaux(d):
        A = cx = cy = 0.0
        for i in range(len(p)):
            x0, y0 = p[i]
            x1, y1 = p[(i + 1) % len(p)]
            cr = x0 * y1 - x1 * y0
            A += cr
            cx += (x0 + x1) * cr
            cy += (y0 + y1) * cr
        if abs(A) < 1e-9:
            continue
        A *= 0.5
        if best is None or abs(A) > best[0]:
            best = (abs(A), (cx / (6 * A), cy / (6 * A)))
    return best[1] if best else None


def _resoudre(M, v):
    """Elimination de Gauss avec pivot partiel."""
    n = len(v)
    A = [row[:] + [v[i]] for i, row in enumerate(M)]
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(A[r][i]))
        A[i], A[p] = A[p], A[i]
        for r in range(i + 1, n):
            f = A[r][i] / A[i][i]
            for c in range(i, n + 1):
                A[r][c] -= f * A[i][c]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = (A[i][n] - sum(A[i][c] * x[c] for c in range(i + 1, n))) / A[i][i]
    return x


# Centres geographiques approximatifs. _centre_aire ne retient que l'anneau le
# plus grand d'un trace : pour les Etats a archipel ou a iles, la reference est
# donc le centre de la masse principale (Portugal continental, Grande-Bretagne,
# Jutland, Grece continentale), pas celui du territoire entier.
# Couvrir toute l'emprise est indispensable : un ajustement polynomial
# extrapole tres mal, et une reference bornee a l'Europe centrale envoyait
# Lisbonne hors du cadre.
REF = {
    'PT': (39.60, -8.00), 'ES': (40.00, -3.60), 'GB': (54.30, -2.30),
    'IE': (53.20, -8.00), 'IS': (64.90, -18.60), 'NO': (64.50, 11.00),
    'SE': (62.80, 16.50), 'FI': (64.50, 26.30), 'DK': (56.30, 9.30),
    'GR': (39.50, 21.80),
    'AL': (41.15, 20.17), 'AT': (47.68, 13.35), 'BA': (44.17, 17.79),
    'BE': (50.64, 4.66), 'BG': (42.77, 25.22), 'BY': (53.54, 28.03),
    'CH': (46.80, 8.21), 'CZ': (49.74, 15.34), 'DE': (51.11, 10.39),
    'EE': (58.67, 25.55), 'FR': (46.56, 2.46), 'HR': (45.08, 16.40),
    'HU': (47.16, 19.39), 'IT': (42.80, 12.50), 'LT': (55.33, 23.89),
    'LU': (49.77, 6.09), 'LV': (56.86, 24.91), 'MD': (47.20, 28.46),
    'ME': (42.79, 19.24), 'MK': (41.60, 21.70), 'NL': (52.10, 5.28),
    'PL': (52.13, 19.39), 'RO': (45.85, 24.97), 'RS': (44.03, 20.79),
    'SI': (46.12, 14.81), 'SK': (48.71, 19.48), 'UA': (48.97, 31.35),
    'XK': (42.57, 20.87),
}


def _fit():
    G = json.loads((ROOT / 'geo' / 'europe.json').read_text())
    pts = []
    for cc, (la, lo) in REF.items():
        if cc in G['paths']:
            c = _centre_aire(G['paths'][cc])
            if c:
                pts.append((lo, la, c[0], c[1]))
    base = lambda lo, la: [1.0, lo, la, lo * lo, lo * la, la * la]
    for nom, idx in (('COEF_X', 2), ('COEF_Y', 3)):
        M = [[sum(base(p[0], p[1])[i] * base(p[0], p[1])[j] for p in pts)
              for j in range(6)] for i in range(6)]
        v = [sum(base(p[0], p[1])[i] * p[idx] for p in pts) for i in range(6)]
        print(f'{nom} = {[round(c, 7) for c in _resoudre(M, v)]}')
    err = [math.hypot(project(p[0], p[1])[0] - p[2],
                      project(p[0], p[1])[1] - p[3]) for p in pts]
    print(f'\n{len(pts)} points, rms {math.sqrt(sum(e*e for e in err)/len(err)):.2f} px, '
          f'max {max(err):.1f} px')


if __name__ == '__main__':
    _fit()
