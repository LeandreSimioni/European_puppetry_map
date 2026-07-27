#!/usr/bin/env python3
"""Projection from (lon, lat) to the SVG coordinates of geo/europe.json.

The base map uses a conic projection whose parameters are not documented.
Rather than guessing them, we fit a degree-2 polynomial transform on the area
centroids of the country outlines, which absorbs any conic over the European
extent.

The coefficients below are produced by `python3 tools/projection.py` and
validated by containment: every school must fall inside the outline of its own
country. Do not edit them by hand.
"""
import json, math, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Fitted on 38 countries: rms 4.7 px, worst case 12.5 px, on the order of 13 km
# at the scale of this base map. Good enough to place a city, not a street:
# school coordinates are locality-level.
COEF_X = [102.2654964, 31.2464312, 0.5270365, -0.0046501, -0.3267308, 0.0368594]
COEF_Y = [1650.1710413, 4.2118725, -23.3485799, -0.1004455, -0.0326683, 0.0109518]


def project(lon, lat):
    """(lon, lat) in degrees -> (x, y) in the 1000 x 862.8 SVG frame."""
    t = [1.0, lon, lat, lon * lon, lon * lat, lat * lat]
    return (sum(c * v for c, v in zip(COEF_X, t)),
            sum(c * v for c, v in zip(COEF_Y, t)))


# --------------------------------------------------------------------------
# tooling: fitting and validation. Not used by build.py.
# --------------------------------------------------------------------------

def rings(d):
    """Splits an SVG 'd' attribute into lists of points."""
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


def inside_path(d, x, y):
    """Does the point fall inside any ring of the outline?"""
    for p in rings(d):
        inside = False
        for i in range(len(p)):
            x0, y0 = p[i]
            x1, y1 = p[(i - 1) % len(p)]
            if (y0 > y) != (y1 > y) and x < (x1 - x0) * (y - y0) / (y1 - y0) + x0:
                inside = not inside
        if inside:
            return True
    return False


def _area_centroid(d):
    best = None
    for p in rings(d):
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


def _solve(M, v):
    """Gaussian elimination with partial pivoting."""
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


# Approximate geographic centres. _area_centroid keeps only the largest ring of
# an outline, so for archipelago or island states the reference is the centre of
# the main landmass (mainland Portugal, Great Britain, Jutland, mainland
# Greece), not that of the whole territory.
# Covering the full extent is essential: a polynomial fit extrapolates badly,
# and a reference set confined to central Europe sent Lisbon off the canvas.
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
            c = _area_centroid(G['paths'][cc])
            if c:
                pts.append((lo, la, c[0], c[1]))
    base = lambda lo, la: [1.0, lo, la, lo * lo, lo * la, la * la]
    for name, idx in (('COEF_X', 2), ('COEF_Y', 3)):
        M = [[sum(base(p[0], p[1])[i] * base(p[0], p[1])[j] for p in pts)
              for j in range(6)] for i in range(6)]
        v = [sum(base(p[0], p[1])[i] * p[idx] for p in pts) for i in range(6)]
        print(f'{name} = {[round(c, 7) for c in _solve(M, v)]}')
    err = [math.hypot(project(p[0], p[1])[0] - p[2],
                      project(p[0], p[1])[1] - p[3]) for p in pts]
    print(f'\n{len(pts)} points, rms {math.sqrt(sum(e*e for e in err)/len(err)):.2f} px, '
          f'worst {max(err):.1f} px')


if __name__ == '__main__':
    _fit()
