# The Europe of Puppet Booths

A cartographic pre-study of the European puppetry ecosystem.

Everything here started as memory: values produced without research, to serve as
hypotheses to be confirmed or refuted country by country. That is the point of
the exercise — a preview precise enough to be refutable.

**One layer has since been checked.** The `schools` indicator has been verified
against sources for all 45 countries, and carries the named list of the
establishments behind each count. Every other indicator is still an estimate and
must not leave this repository.

## What the repository holds

```
schema.json               definitions, denominators, collection rules
data/<CC>.json            one record per country, long format, 45 countries
geo/europe.json           projected outlines (Natural Earth 1:50 M, public domain)
templates/carte.html      the map template, without data
build.py                  validates the data and regenerates dist/index.html
tools/projection.py       (lon, lat) -> SVG frame, fitted on the base map
tools/seed_data.py        initial seeding, no longer to be run
dist/index.html           generated map, never to be edited by hand
docs/                     method note, protocol, initial table
```

## Usage

```bash
python3 build.py --check   # validates the data, writes nothing
python3 build.py           # regenerates dist/index.html
```

No dependencies, standard Python 3 is enough. Open `dist/index.html` in a
browser.

## The long format, and why

A wide table mixes sourced figures and invented ones on the same row, with no
way to tell them apart. Here every observation is a standalone object carrying
its value, its year, its source, its confidence level, its status and the
reasoning that produced it.

```json
{
  "indicator": "dates",
  "value": 35,
  "year": null,
  "source": null,
  "confidence": "estimated",
  "status": "disputed",
  "reasoning": "..."
}
```

The `reasoning` field is mandatory and the build fails when it is empty. This is
not a formality: the first `dates` value for France was refuted in one sentence
as soon as the reasoning was written out, because it exposed a truncated
denominator.

## The three confidence levels

| Level | Meaning | Citable |
|---|---|---|
| `estimated` | Produced by reasoning, with no source | Never, in any form |
| `declared` | Given by a professional in the country, unpublished | With an explicit caveat |
| `sourced` | Published by an identified, citable source | Yes |

The build refuses a `declared` or `sourced` observation with no `source` field.

## The schools layer

`schools` is the only indicator that has to justify itself one establishment at
a time. Each observation carries `checked_on` and an `establishments` list, and
the build fails when the number of entries with `counted: true` does not equal
`lower_bound`.

Countries at zero still carry establishments: those are the candidates examined
and set aside, each with an `exclusion_reason` — `private`, `closed`,
`not_degree_granting`, `outside_scope`, `outside_denominator`, `unconfirmed`.
That is frequently the most useful information in the record. The United Kingdom
reads as zero because Central closed its puppetry BA to new entrants in 2018;
Turkey reads as zero because its one qualifying course sits in Anatolia, outside
the European scope this record uses.

Two rulings are still open and are flagged in the data:

- **Does object theatre count as puppetry?** Latvia runs a Physical and Object
  Theatre specialism built with the national puppet theatre, but no course title
  contains the word puppet. Excluded for now. If the ruling goes the other way,
  Latvia moves to 1 and other countries need re-examining.
- **Does "backed by a state institution" mean public ownership, or state
  recognition of the award?** Hungary's national theatre university was
  transferred to a private foundation in 2020. Counted for now, status
  `disputed`.

## The ruling that blocks everything else

The denominator of the `dates` indicator is not settled. Three incompatible
options:

- anyone declaring themselves a professional puppeteer
- anyone who performed at least once during the year
- any performer on a permanent contract or equivalent

Comparing French self-declared performers with Croatian salaried ones compares
two different populations. Until that choice is made, the `dates` and
`share_under_20` columns stay at status `disputed`, and the map shows them as
such.

## What the map already does

Ten measures across two layers. The institutions layer counts containers; the
trade layer posits volumes of work. As soon as a trade measure is active, a
diagonal hatch covers the map. Inverted-reading measures switch to a cold ramp.

School markers sit at the real coordinates of each establishment, not at the
country centroid. Hovering one gives its city, award, status and check date; the
detail panel lists every establishment with its address, its description and a
link to its website.

## Next steps

1. Settle the denominator of `dates`.
2. Rule on object theatre, and on foundation-run universities.
3. Re-open Belarus and North Macedonia, the two weakest files in the schools
   pass: neither rests on a real finding.
4. Show confidence per cell rather than per layer: the payload already carries
   `confidence[country][indicator]`, the template does not use it yet.
5. Replace an estimated value with a sourced one, one country at a time,
   starting with those whose organisations publish annual reports.
6. Add the indicators listed under `indicators_to_add` in the schema, starting
   with public subsidy per performance played.
