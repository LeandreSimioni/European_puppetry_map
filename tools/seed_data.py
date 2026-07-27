#!/usr/bin/env python3
"""Amorce data/<CC>.json a partir des estimations de depart.

A n'executer qu'une fois. Ensuite, les fichiers data/ font foi et se
modifient a la main ou via Claude Code, un pays a la fois.
"""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / 'data'

# code: [nom, pop_M, lieux_min, lieux_max, ecoles_min, ecoles_max, note]
INST = json.loads((ROOT / 'tools' / 'seed_inst.json').read_text())
# code: [dates, titres, vie, part_sous_20, part_jp, part_revenu_jeu]
JOB = json.loads((ROOT / 'tools' / 'seed_job.json').read_text())

R_EST = "Estimation de depart, produite sans source ni recherche. Sert d'hypothese a falsifier, pas de donnee."
R_DATES = (
    "CONTESTE. Premiere valeur produite comme moyenne conditionnee aux artistes qui tournent, "
    "en excluant du denominateur les createurs qui ne jouent pas. Erreur de methode identifiee : "
    "confusion entre cachet et date jouee. Pour la France, la mediane reelle est probablement dans "
    "la fourchette 10 a 20, avec une distribution bimodale. Pour les pays a troupes permanentes, "
    "recalcul par le haut : 250 a 400 representations annuelles, distributions de 3 a 5, troupe "
    "d'une vingtaine, soit de l'ordre de 50 a 90. Valeur a reprendre integralement une fois le "
    "denominateur tranche."
)

def obs(ind, val, conf='estime', statut='ouvert', raison=R_EST, lo=None, hi=None):
    o = {'indicateur': ind, 'valeur': val, 'annee': None, 'source': None,
         'confiance': conf, 'statut': statut, 'raisonnement': raison}
    if lo is not None:
        o['borne_basse'], o['borne_haute'] = lo, hi
    return o

for code, (nom, pop, lmin, lmax, emin, emax, note) in INST.items():
    j = JOB[code]
    doc = {
        'code': code,
        'nom': nom,
        'observations': [
            obs('population_M', pop),
            obs('lieux', (lmin + lmax) / 2, lo=lmin, hi=lmax),
            obs('ecoles', (emin + emax) / 2, lo=emin, hi=emax),
            obs('dates', j[0], statut='conteste', raison=R_DATES),
            obs('titres', j[1]),
            obs('vie_production', j[2]),
            obs('part_sous_20', j[3], statut='conteste', raison=R_DATES),
            obs('part_jeune_public', j[4]),
            obs('part_revenu_jeu', j[5]),
        ],
        'notes': note,
        'a_verifier': [
            "Trancher le denominateur de l'indicateur dates avant toute collecte.",
            "Trouver le rapport annuel d'au moins une structure du pays.",
        ],
    }
    (OUT / f'{code}.json').write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n')

print(f'{len(INST)} fichiers ecrits dans {OUT}')
