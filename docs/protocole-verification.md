# Verification protocol, country by country

## Suggested order of work

Start with the countries where the data already exists somewhere, to calibrate
the method before tackling the hard cases.

1. **Poland, Czechia, Romania, Croatia, Hungary.** State theatres there are
   accountable for a volume of activity and publish an annual report with
   numbers of performances and spectators. That is the most direct source.
2. **Germany.** Municipal theatres publish accounts, and there are aggregated
   sector statistics for the performing arts.
3. **France.** Paradoxically the hardest case: the information is scattered and
   heterogeneous. Go through the presenter side, or through performing-arts
   payroll data, which gives declared days worked.
4. **Italy, Spain, United Kingdom.** Little aggregation, many companies.
   Probably a declarative survey.
5. **The rest**, by direct professional contact.

## For each country, in order

1. Read `data/<CC>.json` and the `to_check` list.
2. Identify an organisation or body that publishes a volume of activity.
3. Fill the institutional indicators first: they are easier and act as a
   reliability test on the source.
4. Only move to the trade indicators once the denominator has been settled.
5. Update `confidence`, `status`, `source`, `year`, `checked_on` and `reasoning`.
6. Run `python3 build.py --check`, then commit.

## Model of acceptable reasoning

> 2024 annual report of organisation X: 312 performances, a company of 19
> permanent performers, casts of 3 to 5 depending on the title. Taking an
> average cast of 4 gives roughly 66 performances per performer. Denominator:
> performers on permanent contracts. Holds only for state theatres, not for the
> independent sector of the same country.

## Model of unacceptable reasoning

> About 100 performances, which matches what one observes in countries with
> permanent companies.

The difference: the first can be refuted, the second believes itself.

## Searching in the right language

Query in the country's own language, using the domestic term for the field:
*loutkové divadlo*, *bábkarská tvorba*, *teatru de păpuși*, *lutkarstvo*,
*кукольный театр*, *lėlių teatras*, *Figurentheater*, *teatro di figura*. An
English query returns the field's international literature, not the country's
institutions.

Beware of what a search engine asserts in summary. In this repository's schools
pass, summaries wrongly gave GITIS in Moscow a puppetry faculty, placed a German
college in Austria, and reported a Belarusian course as active. All three
collapsed on reading the actual page. Only a page opened and read counts as a
source.

## The trap to watch for at all times

An estimated value left in place long enough ends up being quoted as data. That
is the reason for the `confidence` field and for the hatching on the map. If an
estimated value leaves the repository, it comes back as an unofficial figure and
becomes impossible to correct.
