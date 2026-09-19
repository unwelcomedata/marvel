"""Generate notebooks/04-viz.ipynb for the marvel project (exploration)."""
from __future__ import annotations
import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

nb = new_notebook()
cells = []

cells.append(new_markdown_cell(
    "# 04 — Visual exploration\n\n"
    "This is where we settle **what the story is** and **which charts tell it**, before any\n"
    "publication rendering in `06-viz-social`. Everything here is exploratory and rendered inline.\n\n"
    "The project's headline chart is the **treemap** (the kit's new hierarchical template): the MCU\n"
    "as a part-of-whole, every film a tile sized by worldwide gross, colored by Phase. Below we\n"
    "render it a few ways and look at the supporting cuts (Phase roll-up, Saga split, domestic vs\n"
    "international) so we can pick the framing.\n\n"
    "All charts read from the processed table `mcu_box_office` (built in `03-prepare`). DuckDB is\n"
    "opened **read-only** here and closed in the Cleanup cell.\n\n"
    "> Charts are rendered with the shared Pillow factory/templates (`shared/`) rather than\n"
    "> matplotlib, because the treemap only exists there — and exploring it in its real form is the\n"
    "> point. These are drafts WITH chrome (title/subtitle/source) so we can read them standalone;\n"
    "> the web/social split happens later."
))

cells.append(new_code_cell(
    "import sys, os\n"
    "from pathlib import Path\n\n"
    "PROJECT = Path.cwd()\n"
    "while not (PROJECT / 'config.yaml').exists() and PROJECT != PROJECT.parent:\n"
    "    PROJECT = PROJECT.parent\n"
    "os.chdir(PROJECT)\n"
    "sys.path.insert(0, str(PROJECT))\n"
    "sys.path.insert(0, str(PROJECT.parent.parent / 'shared'))  # workspace/shared\n\n"
    "import duckdb, pandas as pd\n"
    "from IPython.display import display\n"
    "from colors import c\n"
    "from chart_templates import treemap, single_ranked_bars, stacked_100pct_bars\n\n"
    "con = duckdb.connect('data/project.duckdb', read_only=True)\n"
    "films = con.execute('SELECT * FROM mcu_box_office ORDER BY worldwide_gross DESC').df()\n"
    "print(len(films), 'films  |  total worldwide $%.1fB' % (films['worldwide_gross'].sum()/1e9))\n"
    "films[['title','phase','saga','worldwide_gross','share_of_franchise']].head()"
))

cells.append(new_markdown_cell(
    "## Phase color scheme\n\n"
    "Six Phases need six colors. Phases are **ordered and nested in two Sagas**, so instead of six\n"
    "arbitrary hues I use two brand families that make the Saga split legible in the treemap itself:\n"
    "- **Infinity Saga** (Phases 1–3) → the cool **teal** family, light → dark.\n"
    "- **Multiverse Saga** (Phases 4–6) → the warm **gold/red** family, light → dark.\n\n"
    "So warm tiles = the newer, unfinished Saga; cool tiles = the original arc. (We'll also try a\n"
    "flat per-Phase categorical scheme to compare.)"
))
cells.append(new_code_cell(
    "PHASE_COLORS = {\n"
    "    'Phase 1': c('teal_light'),\n"
    "    'Phase 2': c('cyan'),\n"
    "    'Phase 3': c('teal_dark'),\n"
    "    'Phase 4': c('gold_light'),\n"
    "    'Phase 5': c('caramel'),\n"
    "    'Phase 6': c('brown_red'),\n"
    "}\n"
    "SAGA_COLORS = {'Infinity Saga': c('teal'), 'Multiverse Saga': c('caramel')}\n"
    "billions = lambda v: f'${v/1e9:.2f}B'\n"
    "millions = lambda v: f'${v/1e6:,.0f}M'\n"
    "PHASE_COLORS"
))

cells.append(new_markdown_cell(
    "## Treemap A — the lead chart: MCU worldwide box office by film, grouped by Phase\n\n"
    "Tile area = lifetime worldwide gross; color = Phase (cool = Infinity Saga, warm = Multiverse\n"
    "Saga). This is the whole premise in one image: the giant *Endgame* / *Brand New Day* /\n"
    "*Infinity War* / *No Way Home* tiles, the dense Phase 3 block, and Phase 4's fragmentation\n"
    "into many small tiles."
))
cells.append(new_code_cell(
    "img = treemap(\n"
    "    df=films, value_col='worldwide_gross', label_col='title',\n"
    "    group_col='phase', group_colors=PHASE_COLORS, value_fmt=billions,\n"
    "    title='Marvel Cinematic Universe \u2014 worldwide box office by film',\n"
    "    subtitle='Tile area = lifetime worldwide gross; color = Phase (cool = Infinity Saga, warm = Multiverse Saga)',\n"
    "    source='The Numbers, retrieved 2026-09-19',\n"
    "    img_width=1600, img_height=900,\n"
    ")\n"
    "display(img)"
))

cells.append(new_markdown_cell(
    "## Treemap B — same tiles, colored only by Saga\n\n"
    "Collapsing the color to just two categories asks a simpler question: *how much of the whole is\n"
    "the original Infinity Saga vs everything since?* The answer is stark — the finished 3-phase arc\n"
    "still outweighs the entire ongoing Multiverse Saga."
))
cells.append(new_code_cell(
    "img = treemap(\n"
    "    df=films, value_col='worldwide_gross', label_col='title',\n"
    "    group_col='saga', group_colors=SAGA_COLORS, value_fmt=billions,\n"
    "    title='Marvel Cinematic Universe \u2014 worldwide box office by Saga',\n"
    "    subtitle='Infinity Saga (Phases 1\u20133) vs Multiverse Saga (Phases 4\u20136); tile area = worldwide gross',\n"
    "    source='The Numbers, retrieved 2026-09-19',\n"
    "    img_width=1600, img_height=900,\n"
    ")\n"
    "display(img)"
))

cells.append(new_markdown_cell(
    "## Supporting cut 1 — Phase roll-up (ranked bars)\n\n"
    "The treemap shows composition; a plain ranked bar answers \"how big is each Phase\" precisely.\n"
    "Phase 3 alone is ~38% of the entire franchise — more than Phases 1, 2 combined, and it's the\n"
    "clearest single fact in the data."
))
cells.append(new_code_cell(
    "phase_rollup = con.execute('''\n"
    "    SELECT phase,\n"
    "           SUM(worldwide_gross) AS worldwide_gross,\n"
    "           ROUND(100*SUM(worldwide_gross)::DOUBLE/(SELECT SUM(worldwide_gross) FROM mcu_box_office),1) AS pct,\n"
    "           COUNT(*) AS films\n"
    "    FROM mcu_box_office GROUP BY phase, phase_num ORDER BY phase_num\n"
    "''').df()\n"
    "phase_rollup['label'] = phase_rollup.apply(lambda r: f\"${r.worldwide_gross/1e9:.1f}B  ({r.pct:.0f}%, {int(r.films)} films)\", axis=1)\n"
    "phase_rollup['color'] = phase_rollup['phase'].map(PHASE_COLORS)\n"
    "display(phase_rollup[['phase','worldwide_gross','pct','films']])\n"
    "img = single_ranked_bars(\n"
    "    df=phase_rollup, category_col='phase', value_col='worldwide_gross',\n"
    "    total_label_col='label', color_col='color',\n"
    "    title='MCU worldwide box office by Phase',\n"
    "    subtitle='Lifetime worldwide gross, nominal $; Phase 3 carries the franchise',\n"
    "    source='The Numbers, retrieved 2026-09-19',\n"
    "    img_width=1600, img_height=900,\n"
    ")\n"
    "display(img)"
))

cells.append(new_markdown_cell(
    "## Supporting cut 2 — domestic vs international split, by Phase\n\n"
    "A different angle worth checking before we commit: has the MCU's revenue mix shifted abroad\n"
    "over time? 100%-stacked bars per Phase compare *composition* (domestic vs international share),\n"
    "not size. If the international share is climbing Phase to Phase, that's a second story the\n"
    "treemap can't tell."
))
cells.append(new_code_cell(
    "split = con.execute('''\n"
    "    SELECT phase,\n"
    "           SUM(domestic_gross)      AS domestic_gross,\n"
    "           SUM(international_gross)  AS intl_gross\n"
    "    FROM mcu_box_office GROUP BY phase, phase_num ORDER BY phase_num\n"
    "''').df()\n"
    "# stacked_100pct_bars expects each segment column to be a PERCENT that sums\n"
    "# to 100 per row, so normalize the dollar sums to shares of worldwide.\n"
    "tot = split['domestic_gross'] + split['intl_gross']\n"
    "split['domestic_pct'] = (100 * split['domestic_gross'] / tot).round(1)\n"
    "split['intl_pct']     = (100 * split['intl_gross'] / tot).round(1)\n"
    "display(split)\n"
    "segments = [\n"
    "    {'col': 'domestic_pct', 'label': 'Domestic (US & Canada)', 'color': c('teal_dark')},\n"
    "    {'col': 'intl_pct',     'label': 'International',           'color': c('gold')},\n"
    "]\n"
    "img = stacked_100pct_bars(\n"
    "    df=split, group_col='phase', segments=segments,\n"
    "    title='MCU revenue mix by Phase \u2014 domestic vs international',\n"
    "    subtitle='Share of worldwide gross; each Phase normalized to 100%',\n"
    "    source='The Numbers, retrieved 2026-09-19',\n"
    "    img_width=1600, img_height=900,\n"
    ")\n"
    "display(img)"
))

cells.append(new_markdown_cell(
    "## What the exploration says\n\n"
    "- **The treemap (colored by Phase) is the lead.** It carries the whole premise in one image and\n"
    "  is the reason the project exists (it's the kit's first hierarchical chart). Treemap A is the\n"
    "  candidate hero.\n"
    "- **Two clean headline facts** the treemap makes visual and the bars make precise:\n"
    "  1. **Phase 3 ≈ 38% of the entire franchise** — one Phase, 11 films, more than a third of $34.8B.\n"
    "  2. **The finished Infinity Saga (64.5%) still outweighs the entire ongoing Multiverse Saga\n"
    "     (35.5%)** — Treemap B / the Saga split.\n"
    "- **Secondary angle:** the domestic/international mix by Phase (is the MCU leaning more on\n"
    "  overseas box office over time?). Worth keeping as a possible second chart, not the hero.\n"
    "- **Descriptive titles** kept per house style (\"MCU — worldwide box office by film\"), not\n"
    "  conclusion headlines.\n\n"
    "**Open question for the owner (before `06-viz-social`):**\n"
    "1. Hero = **Treemap A** (colored by all 6 Phases) or the simpler **Treemap B** (2-color Saga)?\n"
    "2. Do we publish a second chart (Phase roll-up bars, or the domestic/intl split), or lead with\n"
    "   the treemap alone?\n"
    "3. Any tile-labeling tweaks (e.g. force-label a few mid-size films, or drop the value line)?\n\n"
    "_Per the workflow, `06-viz-social` is NOT built until this framing is confirmed._"
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
nbf.write(nb, 'notebooks/04-viz.ipynb')
print('wrote notebooks/04-viz.ipynb')
