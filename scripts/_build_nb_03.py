"""Generate notebooks/03-prepare.ipynb for the marvel project."""
from __future__ import annotations
import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

nb = new_notebook()
cells = []

cells.append(new_markdown_cell(
    "# 03 — Prepare & Export\n\n"
    "Add the share-of-whole columns the treemap story is built on, then package the analysis-ready\n"
    "dataset (CSV + Excel + Parquet + codebook).\n\n"
    "**Derived columns (all computed in DuckDB from `mcu_films_clean`):**\n"
    "- `share_of_franchise` — a film's worldwide gross as a fraction of the **whole MCU** total.\n"
    "  This is the treemap's tile size: it answers \"how much of the franchise is this one film?\"\n"
    "- `share_of_saga` — worldwide gross as a fraction of the film's **Saga** total (Infinity vs\n"
    "  Multiverse).\n"
    "- `share_of_phase` — worldwide gross as a fraction of the film's **Phase** total.\n"
    "- `intl_share` — international (non-U.S./Canada) gross as a fraction of worldwide, i.e.\n"
    "  `1 - domestic_share`. How much of the film's take came from outside North America.\n"
    "- `profit_multiple` — worldwide gross ÷ production budget (a rough \"how many times its budget\n"
    "  did it earn at the box office\" — box-office only, ignores marketing and studio splits).\n\n"
    "The dataset is one row per released theatrical MCU film."
))

cells.append(new_code_cell(
    "import sys, os\n"
    "from pathlib import Path\n\n"
    "PROJECT = Path.cwd()\n"
    "while not (PROJECT / 'config.yaml').exists() and PROJECT != PROJECT.parent:\n"
    "    PROJECT = PROJECT.parent\n"
    "os.chdir(PROJECT)\n"
    "sys.path.insert(0, str(PROJECT))\n\n"
    "import pandas as pd\n"
    "from src.ingest import load_config\n"
    "from src.clean_quality import get_connection, run_sql, load_to_duckdb, save_processed\n"
    "from src.prepare import package_dataset\n\n"
    "cfg = load_config('config.yaml')\n"
    "con = get_connection(cfg)"
))

cells.append(new_markdown_cell(
    "## Compute share-of-whole columns\n\n"
    "Window functions give each film its share of the franchise, its saga, and its phase in one\n"
    "pass. Shares are rounded to 4 decimals (0.0001 = 0.01%)."
))
cells.append(new_code_cell(
    "SQL = '''\n"
    "SELECT\n"
    "    title,\n"
    "    phase_num,\n"
    "    phase,\n"
    "    saga,\n"
    "    release_date,\n"
    "    release_year,\n"
    "    worldwide_gross,\n"
    "    domestic_gross,\n"
    "    international_gross,\n"
    "    domestic_share,\n"
    "    ROUND(1 - domestic_share, 4)                                              AS intl_share,\n"
    "    ROUND(worldwide_gross::DOUBLE / SUM(worldwide_gross) OVER (), 4)           AS share_of_franchise,\n"
    "    ROUND(worldwide_gross::DOUBLE / SUM(worldwide_gross) OVER (PARTITION BY saga), 4)  AS share_of_saga,\n"
    "    ROUND(worldwide_gross::DOUBLE / SUM(worldwide_gross) OVER (PARTITION BY phase), 4) AS share_of_phase,\n"
    "    opening_weekend,\n"
    "    production_budget,\n"
    "    ROUND(worldwide_gross::DOUBLE / production_budget, 2)                      AS profit_multiple\n"
    "FROM mcu_films_clean\n"
    "ORDER BY worldwide_gross DESC\n"
    "'''\n"
    "df = run_sql(SQL, con)\n"
    "print(len(df), 'films')\n"
    "df[['title','phase','saga','worldwide_gross','share_of_franchise','share_of_phase','intl_share','profit_multiple']].head(12)"
))

cells.append(new_markdown_cell(
    "Sanity checks: shares must sum to 1 at each level of aggregation (whole franchise = 1.0; each\n"
    "saga's films sum to 1.0; each phase's films sum to 1.0)."
))
cells.append(new_code_cell(
    "print('sum share_of_franchise:', round(df['share_of_franchise'].sum(), 3))\n"
    "print('sum share_of_saga by saga:')\n"
    "print(df.groupby('saga')['share_of_saga'].sum().round(3).to_string())\n"
    "print('sum share_of_phase by phase:')\n"
    "print(df.groupby('phase', sort=False)['share_of_phase'].sum().round(3).to_string())\n"
    "assert abs(df['share_of_franchise'].sum() - 1.0) < 0.01\n"
    "assert (df.groupby('saga')['share_of_saga'].sum().round(2) == 1.0).all()\n"
    "assert (df.groupby('phase')['share_of_phase'].sum().round(2) == 1.0).all()\n"
    "print('\\nshare columns reconcile to 1.0 at every level')"
))

cells.append(new_markdown_cell(
    "### Phase- and saga-level roll-up (the treemap's group totals)\n\n"
    "Quick look at the aggregates the treemap groups by — worldwide gross and franchise share per\n"
    "Phase, which is where the \"*Endgame*-era Phase 3 carries the franchise; Phase 4 fragments into\n"
    "many smaller films\" story shows up."
))
cells.append(new_code_cell(
    "rollup = run_sql('''\n"
    "SELECT saga, phase,\n"
    "       COUNT(*)                AS films,\n"
    "       SUM(worldwide_gross)    AS worldwide_gross,\n"
    "       ROUND(SUM(worldwide_gross)::DOUBLE / (SELECT SUM(worldwide_gross) FROM mcu_films_clean), 4) AS share_of_franchise,\n"
    "       ROUND(AVG(worldwide_gross))  AS avg_film_gross\n"
    "FROM mcu_films_clean\n"
    "GROUP BY saga, phase, phase_num\n"
    "ORDER BY phase_num\n"
    "''', con)\n"
    "rollup"
))

cells.append(new_markdown_cell(
    "## Save processed + package export\n\n"
    "Write the film-level table to `data/processed/`, then package `mcu_box_office_v1` to\n"
    "`export/` in all three formats with a plain-English codebook and a source/license note."
))
cells.append(new_code_cell(
    "load_to_duckdb(df, 'mcu_box_office', con)\n"
    "save_processed(df, cfg, 'mcu_box_office.parquet')"
))
cells.append(new_code_cell(
    "codebook = {\n"
    "    'title':              'Film title (Marvel Cinematic Universe theatrical feature).',\n"
    "    'phase_num':          'MCU Phase as an integer 1-6.',\n"
    "    'phase':              'MCU Phase label (\"Phase 1\" ... \"Phase 6\"). Marvel Studios\\' official release grouping.',\n"
    "    'saga':               'Over-arching story arc: \"Infinity Saga\" (Phases 1-3) or \"Multiverse Saga\" (Phases 4-6).',\n"
    "    'release_date':       'U.S. theatrical release date.',\n"
    "    'release_year':       'Year of U.S. theatrical release.',\n"
    "    'worldwide_gross':    'Lifetime worldwide theatrical box-office gross, in nominal (year-of-release) US dollars. Domestic + international.',\n"
    "    'domestic_gross':     'Lifetime U.S. & Canada theatrical gross, nominal US dollars.',\n"
    "    'international_gross': 'Lifetime gross outside the U.S. & Canada (worldwide minus domestic), nominal US dollars.',\n"
    "    'domestic_share':     'Domestic gross as a fraction of worldwide (0-1).',\n"
    "    'intl_share':         'International gross as a fraction of worldwide (0-1); equals 1 - domestic_share.',\n"
    "    'share_of_franchise': 'This film\\'s worldwide gross as a fraction of the ENTIRE MCU worldwide total (0-1). Sums to 1 across all films.',\n"
    "    'share_of_saga':      'This film\\'s worldwide gross as a fraction of its Saga total (0-1). Sums to 1 within each saga.',\n"
    "    'share_of_phase':     'This film\\'s worldwide gross as a fraction of its Phase total (0-1). Sums to 1 within each phase.',\n"
    "    'opening_weekend':    'U.S. opening-weekend gross, nominal US dollars.',\n"
    "    'production_budget':  'Reported/estimated production budget, nominal US dollars (excludes marketing).',\n"
    "    'profit_multiple':    'Worldwide gross divided by production budget. Box-office-only ratio; ignores marketing spend and studio/exhibitor revenue splits, so it is NOT true profit.',\n"
    "}\n"
    "notes = '''\n"
    "Source: The Numbers (the-numbers.com) Marvel Cinematic Universe franchise page, per-film\n"
    "box office; cross-checked against Box Office Mojo (domestic figures agree to within ~1.4%).\n"
    "Retrieved 2026-09-19.\n\n"
    "Scope: released THEATRICAL MCU feature films only (Marvel Studios Phase 1-6 canon, including\n"
    "the Sony-distributed Tom Holland Spider-Man films). Excludes unreleased/future films, TV\n"
    "specials, and Disney+ series.\n\n"
    "All dollar figures are NOMINAL (year-of-release) and NOT inflation-adjusted; cross-era raw\n"
    "gross comparisons therefore understate older films. This dataset\\'s purpose is share-of-\n"
    "franchise composition, not cross-era ranking. License: box-office figures are cited from an\n"
    "industry aggregator for a non-commercial pop-culture project; see SOURCES.md.\n"
    "'''\n"
    "written = package_dataset(df, cfg, name='mcu_box_office_v1', codebook=codebook, notes=notes)\n"
    "list(written.items())"
))

cells.append(new_markdown_cell(
    "---\n**Next:** `04-viz.ipynb` — explore the treemap and share-of-whole cuts (matplotlib) to\n"
    "settle the story before building publication charts in `06-viz-social`."
))
cells.append(new_markdown_cell(
    "---\n## Cleanup\nClose the DuckDB connection so the single-writer lock is released."
))
cells.append(new_code_cell("con.close()\nprint('connection closed')"))

nb['cells'] = cells
nb['metadata'] = {
    'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
    'language_info': {'name': 'python', 'version': '3.14'},
}
nbf.write(nb, 'notebooks/03-prepare.ipynb')
print('wrote notebooks/03-prepare.ipynb')
