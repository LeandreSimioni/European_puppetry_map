# Working rules for this repository

## What this project is

A cartographic pre-study of the European puppetry ecosystem. Most values are
estimates produced without sources. The work consists of replacing them one by
one with verified values, not of defending them.

The working language of this repository is English: data, field names, code,
documentation, commit messages and the map itself.

## Non-negotiable rules

1. **One session, one country.** Never modify several country records in the
   same pass. Verifying Croatia must not touch the France row.
   *Exception, and only this one:* a transversal pass over a single indicator
   across all countries is allowed when it is asked for explicitly. Even then,
   each country is researched on its own, in its own language, and no value is
   ever derived from a neighbour.
2. **Never a value without reasoning.** The `reasoning` field is mandatory and
   the build fails when it is empty. Write the method that produced the value in
   it, not a paraphrase of the value.
3. **Never invent a source.** If no source is found, the value stays at
   `confidence: "estimated"` with `source: null`. An approximate source, or one
   reconstructed from memory, is worse than no source at all. A search-engine
   summary is not a source: only a page actually opened and read counts.
4. **Never edit `dist/index.html`.** It is overwritten on every build.
5. **Median, not mean**, for every indicator about the trade. The distributions
   are bimodal and the mean describes nobody.
6. **A fee is not a performance.** Rehearsals, residencies, workshops and
   outreach all generate fees with no show. Any value that conflates the two is
   wrong.
7. **One commit per value changed**, with the reasoning in the message.

## Before changing a value

Read `schema.json`, in particular the `denominator` field of the indicator
concerned and its `known_bias`. If the denominator carries the note
`TO BE SETTLED`, do not produce a value: report the missing ruling instead.

## The schools indicator specifically

Counted by establishment, never by programme: an academy carrying four puppetry
degrees counts 1.

Every `schools` observation carries `checked_on` and an `establishments` list.
The build fails when the number of entries with `counted: true` does not equal
`lower_bound`. A country at zero still records the candidates examined and set
aside, each with an `exclusion_reason`.

Coordinates are locality-level and are validated by containment: the build
refuses a point falling outside its own country outline. If a newly added
establishment is rejected, the coordinate is wrong; do not widen the tolerance.

## After any change

```bash
python3 build.py --check   # must exit without error
python3 build.py           # regenerates the map
```

## What not to do

- Do not propose qualitative or categorical indicators. They were ruled out
  explicitly: production regime, employment status, traditions, figures. Only
  what is quantifiable and comparable between countries is kept.
- Do not reason from the number of venues or schools to infer a volume of
  activity. That is the bias this repository exists to correct.
- Do not treat an institutional datum as an indicator of vitality.
