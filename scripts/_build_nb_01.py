"""Generate notebooks/01-ingest.ipynb for the marvel project.

Run once with the project venv:
    .venv/bin/python scripts/_build_nb_01.py
Then execute the notebook. This builder is a dev convenience — the notebook is
the canonical artifact.
"""
from __future__ import annotations
import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

nb = new_notebook()
cells = []

cells.append(new_markdown_cell(
    "# 01 — Ingest\n\n"
    "**Project:** *marvel* — the Marvel Cinematic Universe as a part-of-whole box-office picture.\n\n"
    "This notebook fetches the raw per-film box-office data and builds the small Phase/Saga\n"
    "reference table, then loads everything into DuckDB with source provenance. Nothing is\n"
    "transformed here — raw HTML lands in `data/raw/` untouched; cleaning happens in `02-clean`.\n\n"
    "**Sources (see `SOURCES.md` for full attribution):**\n"
    "- **The Numbers — MCU franchise page** (`tnumbers_mcu`, PRIMARY). One HTML table carrying,\n"
    "  per film: release date, production budget, opening weekend, **domestic** and **worldwide**\n"
    "  lifetime gross (nominal $). This is the only single-page source with worldwide-per-film,\n"
    "  which the treemap needs for tile sizing.\n"
    "- **Box Office Mojo — MCU franchise page** (`bom_mcu`, CROSS-CHECK). Domestic lifetime gross\n"
    "  per film + distributor + release date. Used in `02-clean` to sanity-check The Numbers'\n"
    "  domestic figures and confirm the roster.\n"
    "- **MCU Phase / Saga groupings** — a small factual lookup (title → phase → saga) built inline\n"
    "  below from Marvel Studios' official Phase designations (verified against Wikipedia). Not\n"
    "  scraped; it's reference data.\n\n"
    "**Scope decision (theatrical MCU only):** released theatrical feature films in Marvel\n"
    "Studios' Phase 1–6 canon, including the Sony-distributed Tom Holland *Spider-Man* films\n"
    "(MCU-canon). Excluded: unreleased/future films, TV specials (e.g. *Werewolf by Night*), and\n"
    "Disney+ series. The filtering itself happens in `02-clean`; here we just capture the raw tables."
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
    "from src.ingest import load_config, ingest_source\n"
    "from src.clean_quality import get_connection, load_to_duckdb, register_source, run_sql\n\n"
    "cfg = load_config('config.yaml')\n"
    "con = get_connection(cfg)\n"
    "print(f'Project: {cfg[\"project_name\"]}')"
))

# The Numbers primary source
cells.append(new_markdown_cell(
    "## Source 1 — The Numbers MCU franchise page (PRIMARY)\n\n"
    "Fetches `https://www.the-numbers.com/movies/franchise/Marvel-Cinematic-Universe`. The page's\n"
    "first `<table>` is the full franchise box-office history. `ingest_source()` saves the raw HTML\n"
    "to `data/raw/tnumbers_mcu.html` and returns the parsed table.\n\n"
    "The raw table includes announced-but-unreleased films (shown with `$0` grosses) and one TV\n"
    "special — we keep them in the raw table as-is and filter them out in `02-clean` so the raw\n"
    "capture stays faithful to the source."
))
cells.append(new_code_cell(
    "df_tn = ingest_source('tnumbers_mcu', cfg, rate_limit_seconds=1.5)\n"
    "print('raw shape:', df_tn.shape)\n"
    "print('columns:', list(df_tn.columns))\n"
    "df_tn.head(10)"
))

cells.append(new_markdown_cell(
    "Load the raw table into DuckDB as `tnumbers_mcu_raw` (verbatim — no cleaning) and register\n"
    "its provenance in the `_sources` metadata table."
))
cells.append(new_code_cell(
    "load_to_duckdb(df_tn, 'tnumbers_mcu_raw', con)\n"
    "register_source(\n"
    "    con,\n"
    "    table='tnumbers_mcu_raw',\n"
    "    name='The Numbers — Marvel Cinematic Universe franchise box office',\n"
    "    url='https://www.the-numbers.com/movies/franchise/Marvel-Cinematic-Universe',\n"
    "    license='Proprietary (industry aggregator); cited reference for a fun-tier project',\n"
    "    notes=('Per-film release date, production budget, opening weekend, domestic and worldwide '\n"
    "           'lifetime gross. Primary source (only single page with worldwide-per-film). '\n"
    "           'Unreleased films appear with $0 and are filtered in 02-clean; Werewolf by Night '\n"
    "           '(TV special) also dropped. Theatrical released-only universe.'),\n"
    "    retrieved='2026-09-19',\n"
    "    methodology=('Aggregates studio-reported/tracked theatrical receipts. Domestic = U.S. & '\n"
    "                 'Canada; worldwide = domestic + international. Budgets = production cost.'),\n"
    "    series_breaks=('NOMINAL year-of-release dollars across all years — not inflation-adjusted, '\n"
    "                   'so raw cross-era gross comparisons overstate later films. Recent films\\' '\n"
    "                   'worldwide totals may still be settling; FX-sensitive.'),\n"
    ")\n"
    "print('registered tnumbers_mcu_raw')"
))

# BOM cross-check source
cells.append(new_markdown_cell(
    "## Source 2 — Box Office Mojo MCU franchise page (CROSS-CHECK)\n\n"
    "Fetches `https://www.boxofficemojo.com/franchise/fr541495045/`. BOM's franchise table is\n"
    "**domestic only** (no worldwide per film), so it isn't the primary source — but it's a good\n"
    "independent check on The Numbers' domestic figures and confirms distributors and the roster.\n"
    "The raw table also contains re-release rows and a \"Columbia 100th Anniversary Series\" entry,\n"
    "which we leave in the raw capture and filter in `02-clean`."
))
cells.append(new_code_cell(
    "df_bom = ingest_source('bom_mcu', cfg, rate_limit_seconds=1.5)\n"
    "print('raw shape:', df_bom.shape)\n"
    "print('columns:', list(df_bom.columns))\n"
    "df_bom.head(10)"
))
cells.append(new_code_cell(
    "load_to_duckdb(df_bom, 'bom_mcu_raw', con)\n"
    "register_source(\n"
    "    con,\n"
    "    table='bom_mcu_raw',\n"
    "    name='Box Office Mojo — Marvel Cinematic Universe franchise page',\n"
    "    url='https://www.boxofficemojo.com/franchise/fr541495045/',\n"
    "    license='Proprietary (IMDbPro); cited reference for a fun-tier project',\n"
    "    notes=('Domestic (U.S. & Canada) lifetime gross per film + max theaters, opening, release '\n"
    "           'date, distributor. Cross-check on The Numbers domestic figures and roster. '\n"
    "           'Re-release + Columbia-anniversary rows filtered in 02-clean.'),\n"
    "    retrieved='2026-09-19',\n"
    "    methodology='Tracked/reported U.S. & Canada theatrical receipts. Domestic only; nominal $.',\n"
    "    series_breaks='Nominal dollars; re-release runs listed as separate rows (excluded in cleaning).',\n"
    ")\n"
    "print('registered bom_mcu_raw')"
))

# Phase / Saga reference table
cells.append(new_markdown_cell(
    "## Source 3 — MCU Phase / Saga reference table (factual lookup)\n\n"
    "The Phase and Saga each film belongs to is **not** in the box-office data — it's a factual\n"
    "grouping from Marvel Studios' official Phase announcements. We build it inline as a small\n"
    "lookup (`film` → `phase` → `saga`), verified against the Wikipedia *List of Marvel Cinematic\n"
    "Universe films* and per-Phase articles (fun-tier; crowd-edited reference is acceptable and is\n"
    "cited plainly in `SOURCES.md`).\n\n"
    "**Boundaries used (authoritative as of 2026-09):**\n"
    "- **Infinity Saga** — Phase 1 (2008–2012), Phase 2 (2013–2015), Phase 3 (2016–2019)\n"
    "- **Multiverse Saga** — Phase 4 (2021–2022), Phase 5 (2023–2025), Phase 6 (2025– )\n\n"
    "Titles below are written to match The Numbers' spellings so they join cleanly in `02-clean`\n"
    "(any residual mismatches are reconciled there). This is the authoritative roster of the\n"
    "**released** theatrical MCU films."
))
cells.append(new_code_cell(
    "# film title (matching The Numbers) -> (phase, saga)\n"
    "PHASE_MAP = [\n"
    "    # ── Infinity Saga · Phase 1 (2008-2012) ──\n"
    "    ('Iron Man', 1),\n"
    "    ('The Incredible Hulk', 1),\n"
    "    ('Iron Man 2', 1),\n"
    "    ('Thor', 1),\n"
    "    ('Captain America: The First Avenger', 1),\n"
    "    ('The Avengers', 1),\n"
    "    # ── Infinity Saga · Phase 2 (2013-2015) ──\n"
    "    ('Iron Man 3', 2),\n"
    "    ('Thor: The Dark World', 2),\n"
    "    ('Captain America: The Winter Soldier', 2),\n"
    "    ('Guardians of the Galaxy', 2),\n"
    "    ('Avengers: Age of Ultron', 2),\n"
    "    ('Ant-Man', 2),\n"
    "    # ── Infinity Saga · Phase 3 (2016-2019) ──\n"
    "    ('Captain America: Civil War', 3),\n"
    "    ('Doctor Strange', 3),\n"
    "    ('Guardians of the Galaxy Vol 2', 3),\n"
    "    ('Spider-Man: Homecoming', 3),\n"
    "    ('Thor: Ragnarok', 3),\n"
    "    ('Black Panther', 3),\n"
    "    ('Avengers: Infinity War', 3),\n"
    "    ('Ant-Man and the Wasp', 3),\n"
    "    ('Captain Marvel', 3),\n"
    "    ('Avengers: Endgame', 3),\n"
    "    ('Spider-Man: Far From Home', 3),\n"
    "    # ── Multiverse Saga · Phase 4 (2021-2022) ──\n"
    "    ('Black Widow', 4),\n"
    "    ('Shang-Chi and the Legend of the Ten Rings', 4),\n"
    "    ('Eternals', 4),\n"
    "    ('Spider-Man: No Way Home', 4),\n"
    "    ('Doctor Strange in the Multiverse of Madness', 4),\n"
    "    ('Thor: Love and Thunder', 4),\n"
    "    ('Black Panther: Wakanda Forever', 4),\n"
    "    # ── Multiverse Saga · Phase 5 (2023-2025) ──\n"
    "    ('Ant-Man and the Wasp: Quantumania', 5),\n"
    "    ('Guardians of the Galaxy Vol 3', 5),\n"
    "    ('The Marvels', 5),\n"
    "    ('Deadpool & Wolverine', 5),\n"
    "    ('Captain America: Brave New World', 5),\n"
    "    ('Thunderbolts*', 5),\n"
    "    # ── Multiverse Saga · Phase 6 (2025- ) ──\n"
    "    ('The Fantastic Four: First Steps', 6),\n"
    "    ('Spider-Man: Brand New Day', 6),\n"
    "]\n\n"
    "def saga_for(phase: int) -> str:\n"
    "    return 'Infinity Saga' if phase <= 3 else 'Multiverse Saga'\n\n"
    "df_phase = pd.DataFrame(\n"
    "    [(film, phase, f'Phase {phase}', saga_for(phase)) for film, phase in PHASE_MAP],\n"
    "    columns=['film', 'phase_num', 'phase', 'saga'],\n"
    ")\n"
    "print('phase rows:', len(df_phase))\n"
    "df_phase.groupby(['saga', 'phase'], sort=False).size().rename('films')"
))
cells.append(new_code_cell(
    "load_to_duckdb(df_phase, 'phase_map', con)\n"
    "register_source(\n"
    "    con,\n"
    "    table='phase_map',\n"
    "    name='MCU Phase / Saga groupings (hand-built factual lookup)',\n"
    "    url='https://en.wikipedia.org/wiki/List_of_Marvel_Cinematic_Universe_films',\n"
    "    license='Factual groupings (not copyrightable); verified against Wikipedia (CC-BY-SA)',\n"
    "    notes=('title -> phase (1-6) -> saga (Infinity=P1-3, Multiverse=P4-6). Authoritative '\n"
    "           'roster of released theatrical MCU films; Sony Tom Holland Spider-Man films '\n"
    "           'included as MCU-canon.'),\n"
    "    retrieved='2026-09-19',\n"
    "    methodology='Marvel Studios official Phase announcements, cross-checked against Wikipedia.',\n"
    "    series_breaks='N/A (factual reference, not a measured time series).',\n"
    ")\n"
    "print('registered phase_map')"
))

cells.append(new_markdown_cell(
    "## Provenance check\n\n"
    "All three raw tables are now in DuckDB with `_sources` entries."
))
cells.append(new_code_cell(
    "run_sql('SELECT duckdb_table, source_name, retrieved FROM _sources ORDER BY duckdb_table', con)"
))

cells.append(new_markdown_cell(
    "---\n**Next:** `02-clean.ipynb` — parse the dollar/date strings, filter to released theatrical\n"
    "films, join the Phase/Saga map, cross-check domestic against BOM, and save interim Parquet."
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
nbf.write(nb, 'notebooks/01-ingest.ipynb')
print('wrote notebooks/01-ingest.ipynb')
