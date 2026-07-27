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

**Closed on 2026-07-27. Do not reopen it to document zeros.**

Counted by establishment, never by programme: an academy carrying four puppetry
degrees counts 1.

Every `schools` observation carries `checked_on` and an `establishments` list.
The build fails when the number of entries with `counted: true` does not equal
`lower_bound`. A country at zero carries no obligation to list what was examined:
the search was made, the absence is the finding, and an absence does not have to
be proved twice. Establishments already recorded stay — they cost nothing and
several of them are useful — but sixteen empty lists are not a backlog.

Coordinates are locality-level and are validated by containment: the build
refuses a point falling outside its own country outline. If a newly added
establishment is rejected, the coordinate is wrong; do not widen the tolerance.

## After any change

```bash
python3 build.py --check   # must exit without error
python3 build.py           # regenerates the map
```

## Talking to GitHub

Use the authenticated GitHub tooling for anything on the remote: run status,
branches, pull requests, comments. Do not call `api.github.com` with an
anonymous `curl`.

The reason is not style. Anonymous calls are rate-limited and are refused
outright through the agent proxy, and the refusal does not look like a
refusal: the JSON that comes back has no `status` or `conclusion` field, so a
polling loop waiting on one spins silently until it hits its timeout. That
cost five minutes on 2026-07-27 while a workflow run had in fact already
finished, in success, twenty-five seconds after the push.

Do not poll a workflow run, and do not check one after every push. Push the
whole batch, then look once at the end, and read one thing: did it pass or
fail. The run details are only worth opening when it failed — which is the only
case where the logs say anything you did not already know.

Two practical reasons to keep it to one look. The authenticated call returns
the full repository object with every run, tens of thousands of characters for
a single yes-or-no answer. And the answer is almost always yes: the build
validates the data locally before the commit is even made, so a red run means
something the local check cannot see, not a data error.

## What not to do

- Do not propose qualitative or categorical indicators. They were ruled out
  explicitly: production regime, employment status, traditions, figures. Only
  what is quantifiable and comparable between countries is kept.
- Do not reason from the number of venues or schools to infer a volume of
  activity. That is the bias this repository exists to correct.
- Do not treat an institutional datum as an indicator of vitality.
