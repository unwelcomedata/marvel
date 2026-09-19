# marvel — Dataset Codebook
Generated: 2026-09-19

## Columns

### `title`
- **Type**: `object`
- **Non-null**: 38 / 38 (100.0%)
- **Description**: Film title (Marvel Cinematic Universe theatrical feature).

### `phase_num`
- **Type**: `int64`
- **Non-null**: 38 / 38 (100.0%)
- **Description**: MCU Phase as an integer 1-6.

### `phase`
- **Type**: `object`
- **Non-null**: 38 / 38 (100.0%)
- **Description**: MCU Phase label ("Phase 1" ... "Phase 6"). Marvel Studios' official release grouping.

### `saga`
- **Type**: `object`
- **Non-null**: 38 / 38 (100.0%)
- **Description**: Over-arching story arc: "Infinity Saga" (Phases 1-3) or "Multiverse Saga" (Phases 4-6).

### `release_date`
- **Type**: `datetime64[us]`
- **Non-null**: 38 / 38 (100.0%)
- **Description**: U.S. theatrical release date.

### `release_year`
- **Type**: `int32`
- **Non-null**: 38 / 38 (100.0%)
- **Description**: Year of U.S. theatrical release.

### `worldwide_gross`
- **Type**: `int64`
- **Non-null**: 38 / 38 (100.0%)
- **Description**: Lifetime worldwide theatrical box-office gross, in nominal (year-of-release) US dollars. Domestic + international.

### `domestic_gross`
- **Type**: `int64`
- **Non-null**: 38 / 38 (100.0%)
- **Description**: Lifetime U.S. & Canada theatrical gross, nominal US dollars.

### `international_gross`
- **Type**: `int64`
- **Non-null**: 38 / 38 (100.0%)
- **Description**: Lifetime gross outside the U.S. & Canada (worldwide minus domestic), nominal US dollars.

### `domestic_share`
- **Type**: `float64`
- **Non-null**: 38 / 38 (100.0%)
- **Description**: Domestic gross as a fraction of worldwide (0-1).

### `intl_share`
- **Type**: `float64`
- **Non-null**: 38 / 38 (100.0%)
- **Description**: International gross as a fraction of worldwide (0-1); equals 1 - domestic_share.

### `share_of_franchise`
- **Type**: `float64`
- **Non-null**: 38 / 38 (100.0%)
- **Description**: This film's worldwide gross as a fraction of the ENTIRE MCU worldwide total (0-1). Sums to 1 across all films.

### `share_of_saga`
- **Type**: `float64`
- **Non-null**: 38 / 38 (100.0%)
- **Description**: This film's worldwide gross as a fraction of its Saga total (0-1). Sums to 1 within each saga.

### `share_of_phase`
- **Type**: `float64`
- **Non-null**: 38 / 38 (100.0%)
- **Description**: This film's worldwide gross as a fraction of its Phase total (0-1). Sums to 1 within each phase.

### `opening_weekend`
- **Type**: `int64`
- **Non-null**: 38 / 38 (100.0%)
- **Description**: U.S. opening-weekend gross, nominal US dollars.

### `production_budget`
- **Type**: `int64`
- **Non-null**: 38 / 38 (100.0%)
- **Description**: Reported/estimated production budget, nominal US dollars (excludes marketing).

### `profit_multiple`
- **Type**: `float64`
- **Non-null**: 38 / 38 (100.0%)
- **Description**: Worldwide gross divided by production budget. Box-office-only ratio; ignores marketing spend and studio/exhibitor revenue splits, so it is NOT true profit.

## Notes

Source: The Numbers (the-numbers.com) Marvel Cinematic Universe franchise page, per-film
box office; cross-checked against Box Office Mojo (domestic figures agree to within ~1.4%).
Retrieved 2026-09-19.

Scope: released THEATRICAL MCU feature films only (Marvel Studios Phase 1-6 canon, including
the Sony-distributed Tom Holland Spider-Man films). Excludes unreleased/future films, TV
specials, and Disney+ series.

All dollar figures are NOMINAL (year-of-release) and NOT inflation-adjusted; cross-era raw
gross comparisons therefore understate older films. This dataset's purpose is share-of-
franchise composition, not cross-era ranking. License: box-office figures are cited from an
industry aggregator for a non-commercial pop-culture project; see SOURCES.md.
