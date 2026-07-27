#!/usr/bin/env python3
"""Seeds data/<CC>.json from the opening estimates.

To be run once only. After that the files in data/ are authoritative and are
edited by hand or through Claude Code, one country at a time.

Kept for the record: it documents where the numbers came from. It writes the
current English field names, but it does NOT write the schools layer, which
since the July 2026 pass carries checked_on and a named establishments list.
Re-running it would wipe that and the build would refuse the result.
"""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / 'data'

# code: [name, pop_M, venues_min, venues_max, schools_min, schools_max, note]
INST = json.loads((ROOT / 'tools' / 'seed_inst.json').read_text())
# code: [dates, titles, life, share_under_20, share_ya, share_income]
JOB = json.loads((ROOT / 'tools' / 'seed_job.json').read_text())

R_EST = ("Opening estimate, produced with no source and no research. It exists "
         "to be falsified, not to be used as data.")
R_DATES = (
    "DISPUTED. First value produced as a mean conditioned on artists who actually "
    "tour, which drops from the denominator the makers who do not perform. Method "
    "error identified: a fee is not a performance. For France the true median "
    "probably sits between 10 and 20, over a bimodal distribution. For countries "
    "with permanent companies, recomputed from the top: 250 to 400 performances a "
    "year, casts of 3 to 5, a company of about twenty, so on the order of 50 to "
    "90. To be redone in full once the denominator is settled."
)


def obs(ind, val, conf='estimated', status='open', reasoning=R_EST, lo=None, hi=None):
    o = {'indicator': ind, 'value': val, 'year': None, 'source': None,
         'confidence': conf, 'status': status, 'reasoning': reasoning}
    if lo is not None:
        o['lower_bound'], o['upper_bound'] = lo, hi
    return o


for code, (name, pop, lmin, lmax, emin, emax, note) in INST.items():
    j = JOB[code]
    doc = {
        'code': code,
        'name': name,
        'observations': [
            obs('population_M', pop),
            obs('venues', (lmin + lmax) / 2, lo=lmin, hi=lmax),
            obs('schools', (emin + emax) / 2, lo=emin, hi=emax),
            obs('dates', j[0], status='disputed', reasoning=R_DATES),
            obs('titles', j[1]),
            obs('production_life', j[2]),
            obs('share_under_20', j[3], status='disputed', reasoning=R_DATES),
            obs('share_young_audience', j[4]),
            obs('share_income_from_performing', j[5]),
        ],
        'notes': note,
        'to_check': [
            "Settle the denominator of the dates indicator before collecting anything.",
            "Find the annual report of at least one organisation in the country.",
        ],
    }
    (OUT / f'{code}.json').write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n')

print(f'{len(INST)} files written to {OUT}')
