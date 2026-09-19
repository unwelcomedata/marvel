"""Generate notebooks/06-viz-social.ipynb for the marvel project.

Publication-ready charts (owner-confirmed framing from 04-viz):
  1. Treemap by Phase       (hero)          — legend off
  2. Treemap by Saga                        — legend off
  3. Average gross per film by Phase (1b)   — ranked bars
  4. Domestic vs international by Phase      — 100% stacked

Each chart renders TWO targets from the same data (two-target system):
  - SOCIAL: full chrome (title/subtitle/source/watermark), twitter_landscape → outputs/social/
  - WEB:    web_mode=True (no title/subtitle/source, watermark only), web preset → outputs/web/
"""
from __future__ import annotations
import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

nb = new_notebook()
cells = []

cells.append(new_markdown_cell(
    "# 06 — Social (publication charts)\n\n"
    "The owner reviewed `04-viz` and confirmed the framing, so this notebook renders the\n"
    "publication-ready set. Four charts, each in **two targets** from the same data:\n"
    "- **Social** — full chrome (title, subtitle, source, watermark), `twitter_landscape` (1600×900)\n"
    "  → `outputs/social/`. Optimized for Bluesky/X.\n"
    "- **Web** — `web_mode=True` (drops title/subtitle/source, keeps only the `@unwelcomedata`\n"
    "  watermark), `web` preset (1664×936) → `outputs/web/`. These get embedded on the Pages site,\n"
    "  which supplies its own headings.\n\n"
    "**The four charts (confirmed in `04-viz`):**\n"
    "1. **Treemap by Phase** (hero) — the MCU as a part-of-whole, tile area = worldwide gross,\n"
    "   colored by Phase. Legend OFF (the per-block Phase headers already name each group).\n"
    "2. **Treemap by Saga** — same tiles, two colors: Infinity Saga vs Multiverse Saga. Legend OFF.\n"
    "3. **Average gross per film by Phase** (chart 1b) — the fair comparison that controls for how\n"
    "   many films each Phase has; film counts shown in the labels.\n"
    "4. **Domestic vs international by Phase** — revenue-mix composition, 100% stacked.\n\n"
    "Titles are **descriptive** (house default), not conclusion headlines. Data cited from The\n"
    "Numbers, cross-checked against Box Office Mojo (see `SOURCES.md`). Read-only DuckDB; closed in\n"
    "the Cleanup cell."
))

cells.append(new_code_cell(
    "import sys, os\n"
    "from pathlib import Path\n\n"
    "PROJECT = Path.cwd()\n"
    "while not (PROJECT / 'config.yaml').exists() and PROJECT != PROJECT.parent:\n"
    "    PROJECT = PROJECT.parent\n"
    "os.chdir(PROJECT)\n"
    "sys.path.insert(0, str(PROJECT))\n"
    "sys.path.insert(0, str(PROJECT.parent.parent / 'shared'))\n\n"
    "import duckdb\n"
    "from IPython.display import display\n"
    "from src.ingest import load_config\n"
    "from colors import c\n"
    "from chart_templates import treemap, single_ranked_bars, stacked_100pct_bars\n"
    "from viz import PRESETS\n\n"
    "cfg = load_config('config.yaml')\n"
    "con = duckdb.connect(cfg['settings']['duckdb_file'], read_only=True)\n"
    "soc_w, soc_h, _ = PRESETS['twitter_landscape']\n"
    "web_w, web_h, _ = PRESETS['web']\n"
    "social_out = Path(cfg['paths']['outputs_social']); social_out.mkdir(parents=True, exist_ok=True)\n"
    "web_out = social_out.parent / 'web'; web_out.mkdir(parents=True, exist_ok=True)\n\n"
    "films = con.execute('SELECT * FROM mcu_box_office ORDER BY worldwide_gross DESC').df()\n"
    "billions = lambda v: f'${v/1e9:.2f}B'\n"
    "SRC = 'The Numbers (cross-checked vs Box Office Mojo), retrieved 2026-09-19'\n"
    "# Phase palette (cool = Infinity Saga P1\u20133; warm = Multiverse Saga P4\u20136).\n"
    "PHASE_COLORS = {'Phase 1': c('teal_light'), 'Phase 2': c('cyan'), 'Phase 3': c('teal_dark'),\n"
    "                'Phase 4': c('gold_light'), 'Phase 5': c('caramel'), 'Phase 6': c('brown_red')}\n"
    "SAGA_COLORS = {'Infinity Saga': c('teal'), 'Multiverse Saga': c('caramel')}\n"
    "print(len(films), 'films  |  $%.1fB total' % (films['worldwide_gross'].sum()/1e9))"
))

# ── Chart 1: treemap by Phase ────────────────────────────────────────────────
cells.append(new_markdown_cell(
    "## Chart 1 (hero) — MCU worldwide box office by film, grouped by Phase\n\n"
    "Tile area = lifetime worldwide gross; color = Phase. Legend off. Social keeps the title/\n"
    "subtitle/source; the web version drops them (the page supplies the heading)."
))
cells.append(new_code_cell(
    "img = treemap(df=films, value_col='worldwide_gross', label_col='title',\n"
    "    group_col='phase', group_colors=PHASE_COLORS, value_fmt=billions, legend=False,\n"
    "    title='Marvel Cinematic Universe \u2014 worldwide box office by film',\n"
    "    subtitle='Tile area = lifetime worldwide gross; color = Phase (cool = Infinity Saga, warm = Multiverse Saga)',\n"
    "    source=SRC, img_width=soc_w, img_height=soc_h)\n"
    "img.save(social_out / '01_mcu_treemap_by_phase.png'); display(img)\n"
    "imgw = treemap(df=films, value_col='worldwide_gross', label_col='title',\n"
    "    group_col='phase', group_colors=PHASE_COLORS, value_fmt=billions, legend=False,\n"
    "    title='', subtitle=None, source=None, web_mode=True, img_width=web_w, img_height=web_h)\n"
    "imgw.save(web_out / '01_mcu_treemap_by_phase.png')\n"
    "print('saved 01 (social + web)')"
))

# ── Chart 2: treemap by Saga ─────────────────────────────────────────────────
cells.append(new_markdown_cell(
    "## Chart 2 — MCU worldwide box office by film, grouped by Saga\n\n"
    "Same tiles, collapsed to two color blocks: the finished Infinity Saga (Phases 1–3) vs the\n"
    "ongoing Multiverse Saga (Phases 4–6). Legend off — the two block headers name the Sagas."
))
cells.append(new_code_cell(
    "img = treemap(df=films, value_col='worldwide_gross', label_col='title',\n"
    "    group_col='saga', group_colors=SAGA_COLORS, value_fmt=billions, legend=False,\n"
    "    title='Marvel Cinematic Universe \u2014 worldwide box office by Saga',\n"
    "    subtitle='Infinity Saga (Phases 1\u20133) vs Multiverse Saga (Phases 4\u20136); tile area = worldwide gross',\n"
    "    source=SRC, img_width=soc_w, img_height=soc_h)\n"
    "img.save(social_out / '02_mcu_treemap_by_saga.png'); display(img)\n"
    "imgw = treemap(df=films, value_col='worldwide_gross', label_col='title',\n"
    "    group_col='saga', group_colors=SAGA_COLORS, value_fmt=billions, legend=False,\n"
    "    title='', subtitle=None, source=None, web_mode=True, img_width=web_w, img_height=web_h)\n"
    "imgw.save(web_out / '02_mcu_treemap_by_saga.png')\n"
    "print('saved 02 (social + web)')"
))

# ── Chart 3: avg gross per film by Phase ─────────────────────────────────────
cells.append(new_markdown_cell(
    "## Chart 3 — average box office per film, by Phase\n\n"
    "The fair comparison: mean worldwide gross per film, which controls for how many films each\n"
    "Phase has (Phase 3 has 11; Phase 6 only 2). Film counts are shown in each label so the average\n"
    "is honestly contextualized. Same Phase colors as the treemap."
))
cells.append(new_code_cell(
    "phase_avg = con.execute('''\n"
    "    SELECT phase, ROUND(AVG(worldwide_gross)) AS avg_worldwide, COUNT(*) AS films\n"
    "    FROM mcu_box_office GROUP BY phase, phase_num ORDER BY phase_num\n"
    "''').df()\n"
    "phase_avg['label'] = phase_avg.apply(lambda r: f\"${r.avg_worldwide/1e9:.2f}B avg  ({int(r.films)} films)\", axis=1)\n"
    "phase_avg['color'] = phase_avg['phase'].map(PHASE_COLORS)\n"
    "img = single_ranked_bars(df=phase_avg, category_col='phase', value_col='avg_worldwide',\n"
    "    total_label_col='label', color_col='color',\n"
    "    title='MCU average box office per film, by Phase',\n"
    "    subtitle='Mean lifetime worldwide gross per film, nominal $; controls for the number of films per Phase',\n"
    "    source=SRC, img_width=soc_w, img_height=soc_h)\n"
    "img.save(social_out / '03_mcu_avg_gross_per_film_by_phase.png'); display(img)\n"
    "imgw = single_ranked_bars(df=phase_avg, category_col='phase', value_col='avg_worldwide',\n"
    "    total_label_col='label', color_col='color',\n"
    "    title='', subtitle=None, source=None, web_mode=True, img_width=web_w, img_height=web_h)\n"
    "imgw.save(web_out / '03_mcu_avg_gross_per_film_by_phase.png')\n"
    "print('saved 03 (social + web)')"
))

# ── Chart 4: domestic vs international split ──────────────────────────────────
cells.append(new_markdown_cell(
    "## Chart 4 — revenue mix by Phase: domestic vs international\n\n"
    "Share of each Phase's worldwide gross that came from the U.S. & Canada vs the rest of the world\n"
    "(each Phase normalized to 100%). Segment columns are pre-normalized to percentages."
))
cells.append(new_code_cell(
    "split = con.execute('''\n"
    "    SELECT phase, SUM(domestic_gross) AS dom, SUM(international_gross) AS intl\n"
    "    FROM mcu_box_office GROUP BY phase, phase_num ORDER BY phase_num\n"
    "''').df()\n"
    "tot = split['dom'] + split['intl']\n"
    "split['domestic_pct'] = (100*split['dom']/tot).round(1)\n"
    "split['intl_pct']     = (100*split['intl']/tot).round(1)\n"
    "segments = [{'col':'domestic_pct','label':'Domestic (US & Canada)','color':c('teal_dark')},\n"
    "            {'col':'intl_pct','label':'International','color':c('gold')}]\n"
    "img = stacked_100pct_bars(df=split, group_col='phase', segments=segments,\n"
    "    title='MCU revenue mix by Phase \u2014 domestic vs international',\n"
    "    subtitle='Share of worldwide gross; each Phase normalized to 100%',\n"
    "    source=SRC, img_width=soc_w, img_height=soc_h)\n"
    "img.save(social_out / '04_mcu_domestic_vs_international_by_phase.png'); display(img)\n"
    "imgw = stacked_100pct_bars(df=split, group_col='phase', segments=segments,\n"
    "    title='', subtitle=None, source=None, web_mode=True, img_width=web_w, img_height=web_h)\n"
    "imgw.save(web_out / '04_mcu_domestic_vs_international_by_phase.png')\n"
    "print('saved 04 (social + web)')"
))

cells.append(new_markdown_cell(
    "---\n**Next:** run `scripts/validate_charts.py` (must exit 0) — it re-derives every chart's facts\n"
    "from DuckDB and checks the export matches. Then the project is ready for the independent\n"
    "validation pass and release curation (`public-release.md`)."
))
cells.append(new_markdown_cell(
    "---\n## Cleanup\nClose the read-only DuckDB connection."
))
cells.append(new_code_cell("con.close()\nprint('connection closed')"))

nb['cells'] = cells
nb['metadata'] = {
    'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
    'language_info': {'name': 'python', 'version': '3.14'},
}
nbf.write(nb, 'notebooks/06-viz-social.ipynb')
print('wrote notebooks/06-viz-social.ipynb')
