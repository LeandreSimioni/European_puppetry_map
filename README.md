# The Europe of Puppet Booths

A cartographic pre-study of the European puppetry ecosystem.

Everything here started as memory: values produced without research, to serve as
hypotheses to be confirmed or refuted country by country. That is the point of
the exercise — a preview precise enough to be refutable.

**Two indicators have since been checked.** `schools` has been verified against
sources for all 45 countries and carries the named list of the establishments
behind each count. `population_M` is sourced for 44 of 45. Every other indicator
is still an estimate and must not leave this repository.

## The population layer

Sourced on 2026-07-27 from Eurostat's `demo_pjan`, population on 1 January,
read through the dissemination API. Thirty-seven countries carry the 2025
figure. The remaining eight are each a separate case, and the exceptions are
the useful part:

| | |
|---|---|
| **GB** | ONS mid-2025. Eurostat's UK row stops at 2020, after the departure from the Union. The reference differs from the rest of the series — a mid-year estimate against a 1 January stock — and the file says so rather than smoothing it over. |
| **AD, BY** | Eurostat, 1 January 2019. No later row exists there. Sourced, and seven years old. |
| **XK** | Eurostat, 1 January 2022. Same situation. |
| **UA** | Eurostat, 1 January 2022 — weeks before the full-scale invasion. `disputed`: the figure is read correctly, the *denominator* is not settled. Residents, the de jure population including those displaced abroad, and the population of government-controlled territory are three different numbers, and "total population" does not choose between them. |
| **BA** | The 2013 census, read on the front page of the national statistics agency, Eurostat publishing no row at all. `disputed` on its age. |
| **TR** | Eurostat 2025, whole country. Read and refused earlier in the day under the old denominator, recorded once the transcontinental ruling removed the requirement. |
| **RU** | World Bank `SP.POP.TOTL`, 2025. The only country Eurostat does not serve — its last Russian row is 1 January 2014. Rosstat answered 503 twice and is what should carry this value; the World Bank is a compilation, citable but not primary. |
| **SM** | **No value.** The Bollettino demografico exists and was not opened. A figure that has not been read is not a source. |

One country therefore keeps an unsourced estimate, on purpose. The working rule
is that a figure which has not been read produces a report, not a number.

### The transcontinental ruling, 2026-07-27

The denominator used to ask for the European part alone of Russia and Turkey.
It no longer does: splitting a country along a continental line cost more
precision than it bought, and producing those figures meant constructing a
number — Eastern Thrace out of provincial tables with Istanbul cut across the
Bosphorus — rather than reading one.

**This deliberately breaks the scope match between two indicators.**
`population_M` now covers the whole country; `schools` still counts European
establishments only, which is why Anadolu Üniversitesi stays outside Turkey's
count. Any ratio built from the two is inconsistent for those two countries:
nil effect for Turkey, which counts zero schools either way, and an inflated
denominator for Russia, whose one counted school is in Saint Petersburg while the
population now includes Siberia. Both indicators carry the warning in
`schema.json` so neither can be read without meeting it.

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
and set aside, each with an `exclusion_reason` — `closed`,
`not_degree_granting`, `outside_scope`, `outside_denominator`, `unconfirmed`.
That is frequently the most useful information in the record. The United Kingdom
reads as zero because Central closed its puppetry BA to new entrants in 2018;
Turkey reads as zero because its one qualifying course sits in Anatolia, outside
the European scope this record uses.

### The two rulings, settled 2026-07-27

Both questions the pass had left open are now answered, and the denominator was
rewritten to carry the answers rather than a note.

- **Object theatre counts.** A specialism in object, figure or material theatre
  enters on the same footing as one whose title carries the word puppet. Latvia
  had been excluded on nothing but the absence of that word in a course title,
  while the specialism itself was built with the national puppet theatre. Latvia
  moves to 1.
- **The award decides, not the owner.** "Backed by a state institution"
  conflated two different things — who owns the walls, and who recognises the
  qualification. Only the second is a fact about the training. Public, private
  and foundation-run institutions are now treated alike. Hungary's dispute is
  lifted.

The second ruling withdrew `private` as an exclusion reason, so the three
establishments that carried it were re-read on their award instead: Bochum and
Florence stay out for awarding nothing the State recognises, Perugia became
`unconfirmed` because what it awards could not be read. Austria and Germany
each had a sentence removed that excluded unopened private provision by
construction — that provision is now unexamined rather than excluded.

The distinction that decides cases is now **specialism against subject**.
Latvia counts because object theatre is a named specialisation inside an acting
degree; Spain's Dantzerti does not, because puppetry there is a module inside
one.

Twenty schools across 18 countries. One record stays `disputed`: Belarus, where
no accessible source reaches stream level.

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
2. Settle the Ukrainian denominator — residents, de jure population, or
   government-controlled territory — then source against a body that publishes
   on that basis. Fetch the Bosnian annual estimate in place of the 2013
   census. Open the San Marino bulletin. Replace the Russian figure with
   Rosstat when it answers.
3. Finish what the ownership ruling reopened. Four Italian files are unexamined
   (Perugia, Animateria, Cesenatico, plus the academies of fine arts), Austria's
   private provision has never been opened, and Cyprus's private drama schools
   were skipped when private still meant excluded.
4. Reach a first-party or state source for Hungary. Two passes have failed:
   szfe.hu and felveteli.szfe.hu answer 403, felvi.hu answered 503. The value
   rests on an encyclopaedic entry, which is why it stays `estimated`.
5. Record the candidates examined in the 16 countries whose `establishments`
   list is still empty (AD, AL, BA, CY, DK, GR, IE, IS, LI, LU, MD, ME, MK, MT,
   SM, XK). A zero with nothing behind it cannot be audited or reused.
6. Re-open Belarus and North Macedonia, the two weakest files in the schools
   pass: neither rests on a real finding.
7. Show confidence per cell rather than per layer: the payload already carries
   `confidence[country][indicator]`, the template does not use it yet.
8. Add the indicators listed under `indicators_to_add` in the schema. Note that
   **performances per 100,000 inhabitants does not wait on the `dates` ruling**:
   that ruling blocks per-performer measures, not per-country ones. It needs a
   volume of performances and a population, both of which national culture
   statistics and step 2 can supply.
