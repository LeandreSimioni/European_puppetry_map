#!/usr/bin/env python3
"""Regenere dist/index.html a partir de data/<CC>.json, geo/ et templates/.

Usage :
    python3 build.py            # build normal
    python3 build.py --check    # valide les donnees sans ecrire

Les fichiers data/ font foi. Ne jamais editer dist/index.html a la main :
il est ecrase a chaque build.
"""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent
SCHEMA = json.loads((ROOT / 'schema.json').read_text())
GEO = json.loads((ROOT / 'geo' / 'europe.json').read_text())
TPL = (ROOT / 'templates' / 'carte.html').read_text()

IDS = {i['id'] for i in SCHEMA['indicateurs']}
REQUIS = ['population_M', 'lieux', 'ecoles', 'dates', 'titres',
          'vie_production', 'part_sous_20', 'part_jeune_public', 'part_revenu_jeu']
CONFIANCES = set(SCHEMA['confiance'])
STATUTS = set(SCHEMA['statut'])


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
    return {'geo': GEO, 'data': data, 'metier': metier, 'confiance': conf}


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
    if '--check' in sys.argv:
        return
    out = ROOT / 'dist' / 'index.html'
    out.parent.mkdir(exist_ok=True)
    out.write_text(TPL.replace('__PAYLOAD__', json.dumps(payload(pays), separators=(',', ':'))))
    print(f'ecrit {out} ({out.stat().st_size // 1024} Ko)')


if __name__ == '__main__':
    main()
