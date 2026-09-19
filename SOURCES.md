# Data Sources — marvel

Source standards are **tiered**:
- **Serious tier** (methodology invites scrutiny): use official government or
  authoritative primary sources only. Crowd-edited references (Wikipedia, etc.)
  are NOT used — credibility is the product.
- **Fun tier** (low-stakes pop-culture): crowd-sourced references (fan wikis,
  SuperSummary, etc.) and owner-as-primary (hand-collected counts from a book or
  broadcast) are fine — just cite them plainly below.

Document every data source here before ingesting it. Include enough detail
that someone else could independently locate and verify the original data.

---

## Source Template

Copy and fill in for each source. The **How the source collects the data**,
**How the source defines the data**, and **Methodology changes / series breaks**
sections are required — they are what keep our analysis honest and prevent
apples-to-oranges comparisons. Do not leave them blank; if something is genuinely
not applicable or unknown, write "N/A" or "unknown" so it's clear it was considered.

### [Source Name]
- **Publisher:** [Agency, organization, or author]
- **URL:** [Direct link to the file or page]
- **Format:** [CSV | JSON | HTML table | ZIP | PDF | hand-curated]
- **License:** [Public domain | CC0 | CC-BY | proprietary | etc.]
- **Fields used:** [Column names or description of what was extracted]
- **Coverage:** [Geographic scope, date range, or other relevant bounds]
- **How the source collects the data:** [How does the publisher actually gather it?
  Survey / administrative records / registration / model estimate / scraped, etc.
  For surveys: sampling frame, sample size, response rate. For counts: the universe
  and denominator. Who is included and who is excluded from the raw collection?]
- **How the source defines the data:** [How is the thing being measured *defined*?
  Spell out the judgment calls in what counts. Example: a "COVID death" can mean died
  *from* COVID (underlying cause) vs. died *with* COVID (contributing/any mention) —
  very different counts. Note the exact definition this source uses.]
- **Methodology changes / series breaks:** [Dates when the definition or collection
  method changed, and which time periods are therefore NOT directly comparable.
  If the whole series is consistent, say so explicitly. This is the flag that stops
  us from charting a pre-change number next to a post-change number as if they match.]
- **Known controversies / debates:** [Any contested measurement choices worth a
  footnote or caveat in a published chart. Optional but encouraged. "None known" is
  a valid answer once you've checked.]
- **Notes:** [Anything else — data-quality quirks, suppression rules, imputation, etc.]
- **Retrieved:** [YYYY-MM-DD]

---

## Sources

### The Numbers — Marvel Cinematic Universe franchise box office (PRIMARY)
- **Publisher:** The Numbers (Nash Information Services, LLC)
- **URL:** https://www.the-numbers.com/movies/franchise/Marvel-Cinematic-Universe
- **Format:** HTML table
- **License:** Proprietary (industry data aggregator). Used here as a cited
  reference for a fun-tier pop-culture project; figures are publicly displayed
  box-office totals, not redistributed as a licensed dataset.
- **Fields used:** release date, title, production budget, opening weekend,
  domestic box office, worldwide box office (one row per film).
- **Coverage:** every film The Numbers assigns to the MCU franchise, from
  *Iron Man* (2008) forward, including announced/unreleased titles (listed with
  $0 grosses) and one TV special.
- **How the source collects the data:** The Numbers aggregates studio-reported
  and tracked theatrical box-office receipts (domestic = U.S. & Canada;
  worldwide = domestic + international). Budgets are reported/estimated
  production costs, not marketing.
- **How the source defines the data:** "Domestic" = U.S. and Canada theatrical
  gross. "Worldwide" = domestic + all international theatrical gross, in NOMINAL
  (year-of-release, unadjusted) U.S. dollars. Lifetime totals (include any
  re-release runs folded into the film's total by the aggregator).
- **Methodology changes / series breaks:** Nominal dollars across all years — a
  2008 dollar and a 2026 dollar are NOT inflation-equivalent, so cross-era
  comparisons of raw gross overstate later films. No inflation adjustment is
  applied (this project's story is share-of-franchise, not cross-era ranking).
  International grosses shift with exchange rates and late-reporting territories;
  recent films' worldwide totals may still be settling. Figures are a snapshot
  as of the retrieval date.
- **Known controversies / debates:** box-office aggregators (The Numbers, Box
  Office Mojo) occasionally differ by a few million on a given film due to
  reporting cutoffs and re-release accounting; see cross-check note below.
- **Notes:** unreleased films (*Blade*, *Avengers: Doomsday*, *Avengers: Secret
  Wars*, *Nova*, *Ghost Rider*) appear with $0 and are dropped in cleaning; the
  *Werewolf by Night* TV special (no theatrical gross) is also dropped. Universe
  = released theatrical features only.
- **Retrieved:** 2026-09-19

### Box Office Mojo — Marvel Cinematic Universe franchise page (CROSS-CHECK)
- **Publisher:** Box Office Mojo (IMDbPro / Amazon)
- **URL:** https://www.boxofficemojo.com/franchise/fr541495045/
- **Format:** HTML table
- **License:** Proprietary. Cited reference, same fun-tier basis as above.
- **Fields used:** title, lifetime (domestic) gross, max theaters, opening,
  release date, distributor.
- **Coverage:** MCU franchise films, domestic (U.S. & Canada) only. Includes
  separate rows for re-releases and a "Columbia 100th Anniversary Series" entry.
- **How the source collects the data:** tracked/reported U.S. & Canada
  theatrical receipts.
- **How the source defines the data:** "Lifetime Gross" = domestic (U.S. &
  Canada) theatrical, NOMINAL dollars. This page does NOT carry worldwide
  per-film — hence The Numbers is the primary source for the treemap's
  worldwide sizing.
- **Methodology changes / series breaks:** nominal dollars; re-release runs are
  listed as their own rows (not folded into the original film) — these are
  excluded so each film is counted once at its original run.
- **Known controversies / debates:** minor per-film discrepancies vs The Numbers
  (reporting cutoffs). Cross-check documented in `02-clean`.
- **Notes:** used to confirm the film roster and distributors, and to sanity-check
  domestic figures against The Numbers. Re-release and anniversary-series rows are
  filtered in cleaning.
- **Retrieved:** 2026-09-19

### MCU Phase / Saga groupings (factual reference — hand-built)
- **Publisher:** Marvel Studios' official Phase/Saga designations, cross-checked
  against the Wikipedia "List of Marvel Cinematic Universe films" and per-Phase
  articles (fun-tier; crowd-edited reference acceptable and cited plainly).
- **URL:** https://en.wikipedia.org/wiki/List_of_Marvel_Cinematic_Universe_films
- **Format:** hand-curated lookup table built in `01-ingest` (title → phase → saga).
- **License:** factual groupings (not copyrightable); Wikipedia text CC-BY-SA,
  used only to verify the assignments.
- **Fields used:** film title → Phase (1–6) → Saga (Infinity / Multiverse).
- **Boundaries used (authoritative as of 2026-09):**
  - **Infinity Saga** — Phase 1 (2008–2012), Phase 2 (2013–2015), Phase 3 (2016–2019)
  - **Multiverse Saga** — Phase 4 (2021–2022), Phase 5 (2023–2025), Phase 6 (2025– )
  - Phase 4 begins with *Black Widow* (2021), ends with *Black Panther: Wakanda
    Forever* (2022). Phase 5 begins with *Ant-Man and the Wasp: Quantumania*
    (2023), ends with *Thunderbolts\** (2025). Phase 6 begins with *The Fantastic
    Four: First Steps* (2025); *Spider-Man: Brand New Day* (2026) is Phase 6.
- **Notes / boundary decision:** scope is **theatrical MCU feature films only**.
  The Sony-distributed Tom Holland *Spider-Man* films (*Homecoming*, *Far From
  Home*, *No Way Home*, *Brand New Day*) ARE MCU-canon and are included; both The
  Numbers and Box Office Mojo already file them under the MCU franchise. Excluded:
  Disney+ series and TV specials (no theatrical gross), unreleased/future films,
  and non-MCU Marvel films (Fox X-Men, pre-MCU Sony Spider-Man, etc.).
- **Retrieved:** 2026-09-19

---

## Notes on Data Quality

- All source files are saved verbatim to `data/raw/` and never modified.
- Discrepancies between sources should be noted here and resolved explicitly.
- **Series breaks:** whenever a source changed its definition or method mid-series,
  document the break date under that source and treat pre/post as separate series —
  never chart or aggregate across a break without a visible caveat.
- **Definitions drive comparisons:** before comparing two numbers (across years,
  places, or sources), confirm they are defined the same way. If not, say so in the
  chart, the codebook, and any social copy.

---

## Source Provenance in DuckDB

Every table in `data/project.duckdb` has a corresponding entry in the
`_sources` metadata table:

```sql
SELECT * FROM _sources;
```
