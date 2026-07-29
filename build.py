#!/usr/bin/env python3
"""Regenerates dist/index.html from data/<CC>.json, geo/ and templates/.

Usage:
    python3 build.py            # normal build
    python3 build.py --check    # validate the data without writing

The files in data/ are authoritative. Never edit dist/index.html by hand:
it is overwritten on every build.
"""
import json, math, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / 'tools'))
from projection import project, inside_path, rings

ROOT = pathlib.Path(__file__).resolve().parent
SCHEMA = json.loads((ROOT / 'schema.json').read_text())
GEO = json.loads((ROOT / 'geo' / 'europe.json').read_text())


# The base map draws Russia as a wedge closed by one straight chord running from
# the Arctic coast, (703.8, 54.5), to the Caspian, (948.3, 578.0). Every other
# segment of that outline is a real border or a real coast; this one is the cut
# made when the outlines were fitted to a European frame, and everything east of
# it was dropped. Twenty counted venues stand east of it — Kazan, Perm, Ufa,
# Samara, Vorkuta, Orenburg among them — and a marker on white ground reads as a
# mistake rather than as a theatre.
#
# So the chord is pushed out past the frame, and only the chord: no vertex that
# Natural Earth drew is touched, and geo/europe.json keeps the outlines exactly
# as it received them. This is deliberately not the true shape of Russia — it is
# the same honest cut, moved far enough east and north to hold the country's own
# theatres, and running off the top and right of the frame so that what a reader
# sees is a country continuing beyond the map, which is true, rather than one
# stopping in the middle of the Volga, which is not.
RU_CHORD = ((703.8, 54.5), (948.3, 578.0))
RU_BLEED = [(740.0, -400.0), (1500.0, -400.0), (1500.0, 650.0)]


def extend_russia(geo):
    """Replaces the Russian chord with a boundary that leaves the frame."""
    a, b = RU_CHORD
    rs = rings(geo['paths']['RU'])
    main = max(rs, key=len)
    near = lambda p, q: math.dist(p, q) < 0.5
    if not (near(main[0], b) and near(main[-1], a)):
        raise SystemExit('RU outline no longer ends on the chord it used to: '
                         'the base map changed and the extension must be refitted.')
    rs[rs.index(main)] = main + RU_BLEED
    geo['paths']['RU'] = ''.join(
        'M' + 'L'.join(f'{x:.1f},{y:.1f}' for x, y in r) + 'Z' for r in rs)
    return geo


GEO = extend_russia(GEO)
TPL = (ROOT / 'templates' / 'carte.html').read_text()

IDS = {i['id'] for i in SCHEMA['indicators']}
REQUIRED = ['population_M', 'venues', 'schools', 'dates', 'titles',
            'production_life', 'share_under_20', 'share_young_audience',
            'share_income_from_performing']
CONFIDENCES = set(SCHEMA['confidence'])
STATUSES = set(SCHEMA['status'])

SCHOOL_FIELDS = ('name', 'city', 'address', 'lat', 'lon', 'status', 'award',
                 'url', 'description', 'counted', 'source', 'checked_on')
SCHOOL_STATUSES = {'public', 'private', 'foundation'}
PERF_BASES = {'form', 'organisation'}
VENUE_UNITS = ('house', 'stage', 'unknown')
VENUE_FIELDS = ('name', 'city', 'address', 'lat', 'lon', 'unit', 'parent',
                'authority', 'registration', 'url', 'source', 'checked_on')


def check_venues(code, o):
    """Since the ruling of 2026-07-27 a counted venue may be a stage inside a
    larger organisation. Any value researched at source has to say how many of
    each it holds, so that the strict organisation-only reading stays
    recoverable. Opening estimates are exempt: they count nothing nameable."""
    if o.get('confidence') == 'estimated':
        return []
    u = o.get('units')
    if not isinstance(u, dict):
        return [f'{code}/venues: sourced value with no units split. Say how many are '
                f'house, stage or unknown, or the strict reading is lost.']
    bad = [k for k in u if k not in VENUE_UNITS]
    if bad:
        return [f'{code}/venues: unknown unit kind {bad}, expected {list(VENUE_UNITS)}']
    low = o.get('lower_bound', o.get('value'))
    total = sum(u.get(k, 0) for k in VENUE_UNITS)
    if total != low:
        return [f'{code}/venues: units sum to {total} but lower_bound = {low}']
    # A count taken from a statistical aggregate names nobody and cannot be listed.
    # Everything else must enumerate itself. A count may be partly of each: the
    # aggregate gives the total, and part of it has since been named one venue at
    # a time. What is named is validated like any other list; only the residue
    # under 'unknown' is exempt, because there is nothing to validate.
    named = sum(u.get(k, 0) for k in ('house', 'stage'))
    if u.get('unknown') and named == 0:
        return []
    err, lst = [], o.get('venues_list')
    if not isinstance(lst, list):
        return [f'{code}/venues: no venues_list. A count that cannot be enumerated '
                f'cannot be audited.']
    tally = {}
    for v in lst:
        where = v.get('name') or v.get('city') or '?'
        missing = [c for c in VENUE_FIELDS if c not in v]
        if missing:
            err.append(f'{code}/venues/{where}: missing fields {missing}')
            continue
        if v['unit'] not in ('house', 'stage'):
            err.append(f"{code}/venues/{where}: unit must be house or stage, not '{v['unit']}'")
        if v['unit'] == 'stage' and not v.get('parent'):
            err.append(f'{code}/venues/{where}: a stage must name the organisation it sits inside')
        # A venue absent from the gazetteer keeps its place in the count and
        # loses only its point on the map. Better an unmapped venue than an
        # invented coordinate.
        for c in ('lat', 'lon'):
            if v[c] is not None and not isinstance(v[c], (int, float)):
                err.append(f'{code}/venues/{where}: {c} is neither a number nor null')
        if (v['lat'] is None) != (v['lon'] is None):
            err.append(f'{code}/venues/{where}: half a coordinate is not a coordinate')
        if not v.get('source'):
            err.append(f'{code}/venues/{where}: no source')
        tally[v['unit']] = tally.get(v['unit'], 0) + 1
    if len(lst) != named:
        err.append(f'{code}/venues: {len(lst)} venue(s) listed but house + stage = {named}. '
                   f'A venue that is not named belongs under unknown, not in the list.')
    for k in ('house', 'stage'):
        if u.get(k, 0) != tally.get(k, 0):
            err.append(f'{code}/venues: units says {k}={u.get(k, 0)} but the list holds '
                       f'{tally.get(k, 0)}')
    return err


def check_by_venue(code, o):
    """The optional named list of producers behind a performances count."""
    lst = o.get('by_venue')
    if lst is None:
        return []
    err = []
    if not str(o.get('by_venue_covers', '')).strip():
        err.append(f'{code}/performances: by_venue with no by_venue_covers. A list of parts '
                   f'that does not say what fraction of the whole it holds invites a wrong sum.')
    total = 0
    for e in lst:
        where = e.get('name') or '?'
        for f in ('name', 'value', 'unit', 'venue'):
            if f not in e:
                err.append(f'{code}/performances/{where}: missing field {f}')
        if e.get('unit') not in ('performances', 'productions'):
            err.append(f"{code}/performances/{where}: unit must be performances or productions")
        if e.get('unit') == 'performances' and isinstance(e.get('value'), int):
            total += e['value']
    # Only comparable when the parts count the same thing as the headline.
    if all(e.get('unit') == 'performances' for e in lst) and total > o['value']:
        err.append(f'{code}/performances: the named producers sum to {total}, above the '
                   f"headline {o['value']}. The parts cannot exceed the whole.")
    return err


def check_schools(code, o):
    """The schools indicator must be justifiable one establishment at a time."""
    err = []
    if not o.get('checked_on'):
        err.append(f'{code}/schools: checked_on missing, the collection date is mandatory')
    if 'establishments' not in o:
        err.append(f'{code}/schools: establishments list absent')
        return err
    counted = 0
    for e in o['establishments']:
        where = e.get('city') or '?'
        missing = [c for c in SCHOOL_FIELDS if c not in e]
        if missing:
            err.append(f'{code}/schools/{where}: missing fields {missing}')
            continue
        if e['status'] not in SCHOOL_STATUSES:
            err.append(f"{code}/schools/{where}: unknown status '{e['status']}'")
        if not isinstance(e['lat'], (int, float)) or not -90 <= e['lat'] <= 90:
            err.append(f'{code}/schools/{where}: invalid latitude')
        if not isinstance(e['lon'], (int, float)) or not -180 <= e['lon'] <= 180:
            err.append(f'{code}/schools/{where}: invalid longitude')
        if not str(e.get('description', '')).strip():
            err.append(f'{code}/schools/{where}: empty description')
        if e['counted']:
            counted += 1
            if not e.get('source'):
                err.append(f'{code}/schools/{where}: counted establishment with no source')
        elif not e.get('exclusion_reason'):
            err.append(f'{code}/schools/{where}: uncounted establishment with no exclusion_reason')
    low = o.get('lower_bound', o.get('value'))
    if counted != low:
        err.append(f'{code}/schools: {counted} counted establishment(s) but '
                   f'lower_bound = {low}. The count must be justified one by one.')
    return err


def load():
    countries, errors = {}, []
    for f in sorted((ROOT / 'data').glob('*.json')):
        d = json.loads(f.read_text())
        code = d['code']
        if code != f.stem:
            errors.append(f'{f.name}: the code field ({code}) does not match the file name')
        vals = {}
        for o in d['observations']:
            ind = o['indicator']
            if ind not in IDS:
                errors.append(f"{code}: unknown indicator '{ind}'")
                continue
            if o.get('confidence') not in CONFIDENCES:
                errors.append(f'{code}/{ind}: invalid confidence')
            if o.get('status') not in STATUSES:
                errors.append(f'{code}/{ind}: invalid status')
            if not str(o.get('reasoning', '')).strip():
                errors.append(f'{code}/{ind}: empty reasoning, value refused')
            if o.get('confidence') in ('sourced', 'declared') and not o.get('source'):
                errors.append(f"{code}/{ind}: confidence '{o['confidence']}' with no source")
            if ind == 'schools':
                errors += check_schools(code, o)
            if ind == 'venues':
                errors += check_venues(code, o)
            if ind == 'performances':
                errors += check_by_venue(code, o)
            if ind == 'performances' and o.get('basis') not in PERF_BASES:
                errors.append(f"{code}/performances: basis must be one of "
                              f"{sorted(PERF_BASES)}, a count of puppetry that does not "
                              f"say whether it counts a form or an institution is unreadable")
            vals[ind] = o
        missing = [r for r in REQUIRED if r not in vals]
        if missing:
            errors.append(f'{code}: missing indicators {missing}')
        if code not in GEO['paths']:
            errors.append(f'{code}: no geographic outline')
        countries[code] = {'name': d['name'], 'notes': d.get('notes', ''), 'obs': vals}
    orphans = [c for c in GEO['paths'] if c not in countries]
    if orphans:
        errors.append(f'outlines with no data file: {orphans}')
    return countries, errors


def west_of_the_urals(lon, lat):
    """The scope ruling of 2026-07-28 in three lines: Urals, Ural river, Caspian.

    Approximated by latitude band, which is enough to catch the error that
    matters — a Russian venue recorded east of the line, in a part of the
    federation this study does not cover.
    """
    if lat >= 66.0:      # the Polar Urals run east of Vorkuta
        return lon <= 66.0
    if lat >= 50.0:      # the range proper, keeping Perm, Ufa and Kirov inside
        return lon <= 60.5
    return lon <= 56.0   # the Ural river down to the Caspian


def locate(code, lon, lat):
    """Projects a school and pulls it back inside its country outline if needed.

    The coastline of the base map is generalised, so a port city often lands a
    few pixels offshore. In that case the point is moved towards the country
    centroid in 2% steps, up to 40% of the way. Returns (x, y, shift_in_px), or
    None if the point stays outside, which signals a wrong coordinate rather
    than a roughly cut coastline.

    Russia carries one check the others do not need. Its outline is the extended
    one, which reaches past the frame and would happily swallow a venue recorded
    in Yekaterinburg or Omsk, so the scope ruling of 2026-07-28 is enforced on
    the coordinate itself before the outline is consulted at all.
    """
    if code == 'RU' and not west_of_the_urals(lon, lat):
        return None
    x, y = project(lon, lat)
    outline = GEO['paths'].get(code)
    if outline is None or inside_path(outline, x, y):
        return x, y, 0.0
    cx, cy = GEO['centroids'][code]
    for i in range(1, 21):
        t = i * 0.02
        nx, ny = x + (cx - x) * t, y + (cy - y) * t
        if inside_path(outline, nx, ny):
            return nx, ny, math.hypot(nx - x, ny - y)
    return None


def school_points(countries):
    """[x, y, name, city, address, counted, reason, award, url, description] per
    country, plus the log of the points that had to be shifted."""
    pts, shifted, lost = {}, [], []
    for code, p in countries.items():
        lst = []
        for e in p['obs']['schools'].get('establishments', []):
            r = locate(code, e['lon'], e['lat'])
            if r is None:
                lost.append(f"{code}/{e['city']}")
                continue
            x, y, d = r
            if d > 0:
                shifted.append(f"{code}/{e['city']} {d:.1f}px")
            lst.append([round(x, 1), round(y, 1), e['name'], e['city'],
                        e.get('address') or '', 1 if e['counted'] else 0,
                        e.get('exclusion_reason') or '', e.get('award') or '',
                        e.get('url') or '', e.get('description') or ''])
        if lst:
            pts[code] = lst
    return pts, shifted, lost


def venue_points(countries):
    """[x, y, name, city, address, unit, parent, authority, url, output] per country.
    A venue with no coordinate keeps its place in the count and simply does not
    appear on the map. A venue that had to be pulled inland is reported: the
    shift was silent here until 2026-07-29, and thirteen Russian venues were
    being dragged up to 40% of the way to the country's centroid without saying
    so, which is a marker in the wrong town rather than a marker missing."""
    pts, lost, shifted = {}, [], []
    for code, p in countries.items():
        lst = []
        out = ((p['obs'].get('performances') or {}).get('by_venue') or [])
        out = {e['venue']: e['value'] for e in out
               if e.get('venue') and e['unit'] == 'performances'}
        for e in p['obs']['venues'].get('venues_list', []):
            if e['lat'] is None:
                continue
            r = locate(code, e['lon'], e['lat'])
            if r is None:
                lost.append(f"{code}/{e['name']}")
                continue
            x, y, d = r
            if d > 0:
                shifted.append(f"{code}/{e.get('city') or e['name']} {d:.1f}px")
            lst.append([round(x, 1), round(y, 1), e['name'], e.get('city') or '',
                        e.get('address') or '', e['unit'], e.get('parent') or '',
                        e.get('authority') or '', e.get('url') or '',
                        out.get(e['name'], 0)])
        if lst:
            pts[code] = lst
    return pts, lost, shifted


def frame(*point_sets):
    """The SVG viewBox: the drawn outlines, plus whatever falls outside them.

    The base map was cut to the countries it draws, and eastern European Russia
    is not one of them: Vorkuta lands above the top edge and Orenburg past the
    right one. Rather than drop those venues or invent a Russian coastline for
    them, the frame simply opens far enough to hold every point it has to show.
    The space that appears to the north-east is empty on purpose — it is the part
    of the continent this base map never drew.
    """
    xs = [p[0] for s in point_sets for lst in s.values() for p in lst]
    ys = [p[1] for s in point_sets for lst in s.values() for p in lst]
    # Wide enough that a marker at the extreme point keeps its ring, now that the
    # frame clips instead of letting the drawing spill onto the page.
    pad = 10.0
    x0, y0 = min([0.0] + xs) - pad, min([0.0] + ys) - pad
    x1, y1 = max([GEO['w']] + xs) + pad, max([GEO['h']] + ys) + pad
    return [round(x0, 1), round(y0, 1), round(x1 - x0, 1), round(y1 - y0, 1)]


def payload(countries):
    """Pivots the long format into the structure the template expects."""
    data, job, conf = {}, {}, {}
    for code, p in countries.items():
        o = p['obs']
        g = lambda k, c: o[k].get(c, o[k]['value'])
        data[code] = [p['name'], o['population_M']['value'],
                      g('venues', 'lower_bound'), g('venues', 'upper_bound'),
                      g('schools', 'lower_bound'), g('schools', 'upper_bound'),
                      p['notes']]
        job[code] = [o['dates']['value'], o['titles']['value'],
                     o['production_life']['value'], o['share_under_20']['value'],
                     o['share_young_audience']['value'],
                     o['share_income_from_performing']['value']]
        conf[code] = {k: [v['confidence'], v['status']] for k, v in o.items()}
    # performances is the one optional indicator: a country whose statistics do not
    # isolate puppetry carries no observation at all, and the map must show that as
    # an absence rather than as a zero.
    act = {code: [p['obs']['performances']['value'],
                  p['obs']['performances'].get('basis')]
           for code, p in countries.items() if 'performances' in p['obs']}
    # The house/stage split, so a reader can recompute the strict
    # organisation-only count the ruling of 2026-07-27 replaced.
    units = {code: p['obs']['venues']['units']
             for code, p in countries.items() if p['obs']['venues'].get('units')}
    pts, _, _ = school_points(countries)
    # Output per named venue, for the marker size. Only where the parts count the
    # same thing as the headline: productions and performances do not share a scale.
    vout = {}
    for code, p in countries.items():
        o = p['obs'].get('performances') or {}
        m = {e['venue']: e['value'] for e in o.get('by_venue', [])
             if e.get('venue') and e['unit'] == 'performances'}
        if m:
            vout[code] = m
    vpts, _, _ = venue_points(countries)
    vlist = {code: [{k: e[k] for k in ('name', 'city', 'address', 'unit', 'parent',
                                       'authority', 'registration', 'url')}
                    for e in p['obs']['venues'].get('venues_list', [])]
             for code, p in countries.items() if p['obs']['venues'].get('venues_list')}
    checked = {c: p['obs']['schools'].get('checked_on') for c, p in countries.items()
               if p['obs']['schools'].get('checked_on')}
    return {'geo': dict(GEO, frame=frame(pts, vpts)), 'data': data, 'job': job,
            'act': act, 'units': units,
            'confidence': conf, 'school_pts': pts, 'venue_pts': vpts, 'venue_list': vlist,
            'by_venue': {c: (p['obs'].get('performances') or {}).get('by_venue')
                         for c, p in countries.items()
                         if (p['obs'].get('performances') or {}).get('by_venue')},
            'checked_on': checked}


def tally(countries):
    n = c = s = 0
    for p in countries.values():
        for o in p['obs'].values():
            n += 1
            c += o['confidence'] != 'estimated'
            s += o['status'] == 'disputed'
    return n, c, s


def main():
    countries, errors = load()
    if errors:
        print('INVALID DATA', file=sys.stderr)
        for e in errors:
            print('  ' + e, file=sys.stderr)
        sys.exit(1)
    n, c, s = tally(countries)
    print(f'{len(countries)} countries, {n} observations, {c} sourced or declared, {s} disputed')
    pts, shifted, lost = school_points(countries)
    tot = sum(len(v) for v in pts.values())
    print(f'{tot} establishments located across {len(pts)} countries')
    vpts, vlost, vshifted = venue_points(countries)
    vtot = sum(len(v) for v in vpts.values())
    nlist = sum(len(p['obs']['venues'].get('venues_list', [])) for p in countries.values())
    print(f'{vtot} venues located of {nlist} listed, across {len(vpts)} countries')
    lost += vlost
    shifted += vshifted
    if shifted:
        print(f'  pulled inland (generalised coastline): {", ".join(shifted)}')
    if lost:
        print('INVALID DATA', file=sys.stderr)
        print(f'  outside their country outline even after shifting: {", ".join(lost)}',
              file=sys.stderr)
        sys.exit(1)
    if '--check' in sys.argv:
        return
    out = ROOT / 'dist' / 'index.html'
    out.parent.mkdir(exist_ok=True)
    out.write_text(TPL.replace('__PAYLOAD__', json.dumps(payload(countries), separators=(',', ':'))))
    print(f'wrote {out} ({out.stat().st_size // 1024} kB)')


if __name__ == '__main__':
    main()
