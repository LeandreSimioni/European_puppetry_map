# The Europe of Puppet Booths

A cartographic pre-study of the European puppetry ecosystem.

Everything here started as memory: values produced without research, to serve as
hypotheses to be confirmed or refuted country by country. That is the point of
the exercise — a preview precise enough to be refutable.

**Two indicators have since been checked.** `schools` has been verified against
sources for all 45 countries and carries the named list of the establishments
behind each count; that layer is now closed. `population_M` is sourced for all
45. `venues` and `performances` are being collected, five countries at a time.
Every other indicator is still an estimate and must not leave this repository.

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
| **SM** | The national statistics office's `Bollettino di Statistica`, I trimestre 2026, table 1.1 — 34 172 residents on 1 January 2026. A first pass had reported it unreachable, which was true of the route and not of the document: the front page is a hub and the figure sits in a quarterly PDF two levels down. |

**All 45 countries are sourced.** Two remain `disputed` — Ukraine and Bosnia —
and the dispute is about the denominator, not the reading.

Where a source offered a choice, the file records which was taken and why. San
Marino's bulletin also gives a fresher 31 March figure, not used: 1 January is
the stock convention the Eurostat countries follow, and a third reference date
for one country costs more than three months of freshness are worth. The same
bulletin distinguishes `popolazione residente` from `popolazione presente`,
which adds people staying without residence and reaches 35 589; the resident
concept is the one recorded, being what `demo_pjan` measures.

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
dist/index.html           generated map, never to be edited by hand
docs/                     verification protocol, and the initial table from memory
```

## Usage

```bash
python3 build.py --check   # validates the data, writes nothing
python3 build.py           # regenerates dist/index.html
```

No dependencies, standard Python 3 is enough. Open `dist/index.html` in a
browser.

## The venues ruling, 2026-07-27

`venues` counts **the permanent puppetry unit, not the legal person.** A named
puppet stage or ensemble counts whether or not it has its own legal personality.
What stays out is a programming strand or an occasional co-production
maintaining no permanent ensemble.

The old wording asked for a "permanent organisation with a building of its own",
and three countries stalled on it in two batches — Czechia between 8 and 10,
Hungary between 12 and 13, Croatia between 4 and 5. Three findings decided it:

- **Output.** In Czechia the integrated stages are the same size as the
  freestanding houses. Divadlo rozmanitostí in Most plays 276 puppet
  performances against Alfa's 248 in Plzeň. The distinction separated nothing.
- **Applicability.** The obvious alternative — a majority-of-repertoire test —
  needs a performance count per venue. Of the ten countries collected, only
  Czechia and Croatia publish any puppetry figure at all.
- **Consistency**, which decided it. `performances` counted by form already
  includes puppetry made inside drama houses. Excluding those houses from
  `venues` assigns their output to no venue and breaks every ratio built from
  the two columns: 479 performances belonging nowhere in Czechia alone.

The old wording also failed in practice. Its own author applied it wrongly
within a day, counting Czechia at 8 by missing that Divadlo Lampion sits inside
Divadla Kladno. The strict count was 7.

Every researched value carries a `units` split, and the build refuses one that
does not:

| | |
|---|---|
| `house` | Freestanding organisation whose vocation is puppetry. **This is the strict pre-ruling count, recoverable for ever.** |
| `stage` | Named puppet stage or ensemble inside a larger organisation. |
| `unknown` | The source is a statistical aggregate naming no establishment, so the split cannot be read. |

Two cases fell out on **vocation** rather than structure, and they are the ones
that show where the cursor sits: Hungary's Kolibri and Croatia's Osijek are both
public children's theatres that play puppetry with a single mixed company and no
puppet unit named anywhere. A mixed company playing some puppetry is not a
permanent puppetry unit; a named stage inside a bigger house is.

**Expect the counts to rise in the west.** Germany's Sparten and France's
labelled structures have not been read under the new wording yet, and the
east-west gap will narrow when they are. That is a correction: counting legal
persons rewarded systems whose puppetry was organised into separate
institutions — the socialist state-theatre legacy above all — and penalised
those where it lives inside larger houses.

## The activity layer

`performances` is the newest indicator and the first that counts work rather
than containers. It does not wait on the `dates` ruling: that ruling blocks
per-performer measures, not per-country ones.

It is also **the first indicator a country is allowed not to have.** Where the
national statistics isolate no puppetry, the country carries no observation at
all — not a zero, not an estimate. The map colours it as no-data and says so.
An estimate here would be indistinguishable from a measurement of a small
country, and a zero would be a lie about a whole statistical apparatus.

Every observation declares a `basis`, and the build refuses one that does not:

| | |
|---|---|
| `form` | The source counts performances by genre of production. A puppetry production staged by a drama theatre is inside; a puppet theatre's straight play is outside. This is the denominator met exactly. |
| `organisation` | The source counts the output of named puppet theatres, whatever they staged. A proxy: it drops puppetry made elsewhere and picks up non-puppetry made in the right building. |

The distinction is not academic. Czechia counts by form, and its table shows
puppet performances played by 33 different theatres — two drama houses account
for 479 of them between them. An organisation-based count throws those away.

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

### The layer is closed, 2026-07-27

Sixteen countries carry a zero with an empty `establishments` list, and that is
where they stay. The search was made in each of them; recording the candidates
examined and set aside would document an absence a second time without changing
a single value. The same ruling closes the follow-ups the ownership decision had
reopened — the unexamined Italian files, Austrian and Cypriot private provision,
a first-party Hungarian source, Belarus and North Macedonia. Any of them could
move a count by one. None of them is worth a session while seven indicators out
of nine have never been researched at all.

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

Twelve measures across three layers. The institutions layer counts containers;
the activity layer counts performances actually played; the trade layer posits
volumes of work. As soon as a trade measure is active, a
diagonal hatch covers the map. Inverted-reading measures switch to a cold ramp.

School markers sit at the real coordinates of each establishment, not at the
country centroid. Hovering one gives its city, award, status and check date; the
detail panel lists every establishment with its address, its description and a
link to its website.

## Next steps

1. **Source `venues` and `performances`, five countries at a time.** In progress,
   Baltic states first. These are the two indicators a desk can reach: national
   culture statistics count both, and neither waits on the `dates` ruling.
2. Settle the denominator of `dates`. It blocks 90 observations — `dates` and
   `share_under_20` for all 45 countries.
3. Settle the Ukrainian denominator — residents, de jure population, or
   government-controlled territory — then source against a body that publishes
   on that basis. Fetch the Bosnian annual estimate in place of the 2013
   census. Replace the Russian figure with Rosstat when it answers.
4. Collect the four remaining trade indicators by declarative survey. No
   published source gives them; they come from professionals or not at all.
