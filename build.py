#!/usr/bin/env python3
"""Regenere dist/index.html a partir de data/<CC>.json, geo/ et templates/.

Usage :
    python3 build.py            # build normal
    python3 build.py --check    # valide les donnees sans ecrire

Les fichiers data/ font foi. Ne jamais editer dist/index.html a la main :
il est ecrase a chaque build.
"""
import json, math, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / 'tools'))
from projection import project, dans_trace

ROOT = pathlib.Path(__file__).resolve().parent
SCHEMA = json.loads((ROOT / 'schema.json').read_text())
GEO = json.loads((ROOT / 'geo' / 'europe.json').read_text())
TPL = (ROOT / 'templates' / 'carte.html').read_text()

IDS = {i['id'] for i in SCHEMA['indicateurs']}
REQUIS = ['population_M', 'lieux', 'ecoles', 'dates', 'titres',
          'vie_production', 'part_sous_20', 'part_jeune_public', 'part_revenu_jeu']
CONFIANCES = set(SCHEMA['confiance'])
STATUTS = set(SCHEMA['statut'])


CHAMPS_ECOLE = ('nom', 'ville', 'adresse', 'lat', 'lon', 'statut', 'diplome',
                'compte', 'source', 'verifie_le')
STATUTS_ECOLE = {'public', 'prive', 'fondation'}


def verifier_ecoles(code, o):
    """L'indicateur ecoles doit pouvoir se justifier etablissement par etablissement."""
    err = []
    if not o.get('verifie_le'):
        err.append(f'{code}/ecoles : verifie_le manquant, la date de collecte est obligatoire')
    if 'etablissements' not in o:
        err.append(f'{code}/ecoles : liste etablissements absente')
        return err
    comptes = 0
    for e in o['etablissements']:
        ou = e.get('ville') or '?'
        manque = [c for c in CHAMPS_ECOLE if c not in e]
        if manque:
            err.append(f'{code}/ecoles/{ou} : champs manquants {manque}')
            continue
        if e['statut'] not in STATUTS_ECOLE:
            err.append(f"{code}/ecoles/{ou} : statut '{e['statut']}' inconnu")
        if not isinstance(e['lat'], (int, float)) or not -90 <= e['lat'] <= 90:
            err.append(f'{code}/ecoles/{ou} : latitude invalide')
        if not isinstance(e['lon'], (int, float)) or not -180 <= e['lon'] <= 180:
            err.append(f'{code}/ecoles/{ou} : longitude invalide')
        if e['compte']:
            comptes += 1
            if not e.get('source'):
                err.append(f'{code}/ecoles/{ou} : etablissement compte sans source')
        elif not e.get('motif_exclusion'):
            err.append(f'{code}/ecoles/{ou} : etablissement non compte sans motif_exclusion')
    bb = o.get('borne_basse', o.get('valeur'))
    if comptes != bb:
        err.append(f'{code}/ecoles : {comptes} etablissement(s) compte(s) mais '
                   f'borne_basse = {bb}. Le compte doit se justifier un par un.')
    return err


def charger():
    pays, erreurs = {}, []
    for f in sorted((ROOT / 'data').glob('*.json')):
        d = json.loads(f.read_text())
        code = d['code']
        if code != f.stem:
            erreurs.append(f"{f.name} : le champ code ({code}) ne correspond pas au nom de fichier")
        vals = {}
        for o in d['observations']:
            ind = o['indicateur']
            if ind not in IDS:
                erreurs.append(f"{code} : indicateur inconnu '{ind}'")
                continue
            if o.get('confiance') not in CONFIANCES:
                erreurs.append(f"{code}/{ind} : confiance invalide")
            if o.get('statut') not in STATUTS:
                erreurs.append(f"{code}/{ind} : statut invalide")
            if not str(o.get('raisonnement', '')).strip():
                erreurs.append(f"{code}/{ind} : raisonnement vide, valeur refusee")
            if o.get('confiance') in ('sourced', 'declare') and not o.get('source'):
                erreurs.append(f"{code}/{ind} : confiance '{o['confiance']}' sans source")
            if ind == 'ecoles':
                erreurs += verifier_ecoles(code, o)
            vals[ind] = o
        manquants = [r for r in REQUIS if r not in vals]
        if manquants:
            erreurs.append(f"{code} : indicateurs manquants {manquants}")
        if code not in GEO['paths']:
            erreurs.append(f"{code} : aucun trace geographique")
        pays[code] = {'nom': d['nom'], 'notes': d.get('notes', ''), 'obs': vals}
    orphelins = [c for c in GEO['paths'] if c not in pays]
    if orphelins:
        erreurs.append(f"traces sans fichier de donnees : {orphelins}")
    return pays, erreurs


def placer(code, lon, lat):
    """Projette une ecole et la ramene dans le trace de son pays si besoin.

    Le trait de cote du fond est simplifie : une ville portuaire tombe souvent
    quelques pixels au large. On rapproche alors le point du centroide du pays
    par pas de 2 %, jusqu'a 40 % du chemin. Renvoie (x, y, recale_de_px) ou
    None si le point reste hors du trace, ce qui signale une coordonnee fausse
    et non une cote mal decoupee.
    """
    x, y = project(lon, lat)
    trace = GEO['paths'].get(code)
    if trace is None or dans_trace(trace, x, y):
        return x, y, 0.0
    cx, cy = GEO['centroids'][code]
    for i in range(1, 21):
        t = i * 0.02
        nx, ny = x + (cx - x) * t, y + (cy - y) * t
        if dans_trace(trace, nx, ny):
            return nx, ny, math.hypot(nx - x, ny - y)
    return None


def points_ecoles(pays):
    """[x, y, nom, ville, adresse, compte, motif, diplome] par pays, plus le
    journal des recalages."""
    pts, recales, perdus = {}, [], []
    for code, p in pays.items():
        lst = []
        for e in p['obs']['ecoles'].get('etablissements', []):
            r = placer(code, e['lon'], e['lat'])
            if r is None:
                perdus.append(f"{code}/{e['ville']}")
                continue
            x, y, d = r
            if d > 0:
                recales.append(f"{code}/{e['ville']} {d:.1f}px")
            lst.append([round(x, 1), round(y, 1), e['nom'], e['ville'],
                        e.get('adresse') or '', 1 if e['compte'] else 0,
                        e.get('motif_exclusion') or '', e.get('diplome') or ''])
        if lst:
            pts[code] = lst
    return pts, recales, perdus


def payload(pays):
    """Pivote le format long vers la structure attendue par le gabarit."""
    data, metier, conf = {}, {}, {}
    for code, p in pays.items():
        o = p['obs']
        g = lambda k, c: o[k].get(c, o[k]['valeur'])
        data[code] = [p['nom'], o['population_M']['valeur'],
                      g('lieux', 'borne_basse'), g('lieux', 'borne_haute'),
                      g('ecoles', 'borne_basse'), g('ecoles', 'borne_haute'),
                      p['notes']]
        metier[code] = [o['dates']['valeur'], o['titres']['valeur'],
                        o['vie_production']['valeur'], o['part_sous_20']['valeur'],
                        o['part_jeune_public']['valeur'], o['part_revenu_jeu']['valeur']]
        conf[code] = {k: [v['confiance'], v['statut']] for k, v in o.items()}
    pts, _, _ = points_ecoles(pays)
    verif = {c: p['obs']['ecoles'].get('verifie_le') for c, p in pays.items()
             if p['obs']['ecoles'].get('verifie_le')}
    return {'geo': GEO, 'data': data, 'metier': metier, 'confiance': conf,
            'ecoles_pts': pts, 'verifie_le': verif}


def resume(pays):
    n = c = s = 0
    for p in pays.values():
        for o in p['obs'].values():
            n += 1
            c += o['confiance'] != 'estime'
            s += o['statut'] == 'conteste'
    return n, c, s


def main():
    pays, erreurs = charger()
    if erreurs:
        print('DONNEES INVALIDES', file=sys.stderr)
        for e in erreurs:
            print('  ' + e, file=sys.stderr)
        sys.exit(1)
    n, c, s = resume(pays)
    print(f'{len(pays)} pays, {n} observations, {c} sourcees ou declarees, {s} contestees')
    pts, recales, perdus = points_ecoles(pays)
    tot = sum(len(v) for v in pts.values())
    print(f'{tot} etablissements localises sur {len(pts)} pays')
    if recales:
        print(f'  recales vers l interieur des terres (cote simplifiee) : {", ".join(recales)}')
    if perdus:
        print('DONNEES INVALIDES', file=sys.stderr)
        print(f'  hors du trace de leur pays meme apres recalage : {", ".join(perdus)}',
              file=sys.stderr)
        sys.exit(1)
    if '--check' in sys.argv:
        return
    out = ROOT / 'dist' / 'index.html'
    out.parent.mkdir(exist_ok=True)
    out.write_text(TPL.replace('__PAYLOAD__', json.dumps(payload(pays), separators=(',', ':'))))
    print(f'ecrit {out} ({out.stat().st_size // 1024} Ko)')


if __name__ == '__main__':
    main()
