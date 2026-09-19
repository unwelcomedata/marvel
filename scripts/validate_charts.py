#!/usr/bin/env python3
"""Pre-publish validation — re-check the MCU chart data before anything goes public.

Run this BEFORE curating the release branch / flipping the repo public. It
re-derives what each of the four published charts should show, straight from the
DuckDB source table (mcu_box_office), and confirms:

  1. The published export CSV (export/mcu_box_office_v1.csv) matches the DuckDB
     source table on the key columns (no drift between the DB and what ships).
  2. The headline chart facts are still true (totals, per-Phase figures, the top
     film, the Saga split), so a silent data change can't slip out unnoticed.
  3. Structural invariants hold (worldwide = domestic + international per film;
     share columns reconcile to 1.0; expected row/film counts).
  4. Social vs web chart parity — the two rendered sets cover the same filenames
     and the web charts are the wider web canvas.

The four published charts:
  1. treemap by Phase           (worldwide gross per film, colored by Phase)
  2. treemap by Saga            (same tiles, Infinity vs Multiverse)
  3. average gross per film by Phase   (ranked bars, controls for film count)
  4. domestic vs international by Phase (100% stacked)

Exit code 0 = all checks passed, safe to publish. Non-zero = do NOT publish.

Usage:
    .venv/bin/python scripts/validate_charts.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import duckdb
import pandas as pd

PROJECT = Path(__file__).resolve().parent
while not (PROJECT / "config.yaml").exists() and PROJECT != PROJECT.parent:
    PROJECT = PROJECT.parent
sys.path.insert(0, str(PROJECT))
from src.ingest import load_config  # noqa: E402

failures: list[str] = []
checks: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        checks.append(f"  PASS  {name}")
    else:
        failures.append(f"  FAIL  {name}" + (f" — {detail}" if detail else ""))


def approx(a: float, b: float, tol: float = 0.005) -> bool:
    if b == 0:
        return a == 0
    return abs(a - b) / abs(b) <= tol


def main() -> int:
    cfg = load_config("config.yaml")
    db = str(PROJECT / cfg["settings"]["duckdb_file"])
    export_dir = PROJECT / cfg["paths"]["export"]
    con = duckdb.connect(db, read_only=True)

    films = con.execute("SELECT * FROM mcu_box_office ORDER BY worldwide_gross DESC").df()

    # ── Universe / totals ─────────────────────────────────────────────────
    check("universe: 38 released theatrical films", len(films) == 38, f"got {len(films)}")
    total_ww = int(films["worldwide_gross"].sum())
    check(
        "totals: franchise worldwide gross == $34,828,989,052",
        total_ww == 34_828_989_052,
        f"got {total_ww:,}",
    )

    # ── Structural invariants ─────────────────────────────────────────────
    bad_split = films[(films.domestic_gross + films.international_gross - films.worldwide_gross).abs() > 1]
    check(
        "structure: worldwide == domestic + international (all films)",
        len(bad_split) == 0,
        f"{len(bad_split)} films violate the split",
    )
    check(
        "structure: share_of_franchise sums to ~1.0",
        approx(float(films["share_of_franchise"].sum()), 1.0, tol=0.01),
        f"sum={films['share_of_franchise'].sum():.4f}",
    )
    phase_share_sums = films.groupby("phase")["share_of_phase"].sum().round(2)
    check(
        "structure: share_of_phase sums to 1.0 within every Phase",
        bool((phase_share_sums == 1.0).all()),
        f"{phase_share_sums.to_dict()}",
    )
    check(
        "structure: no null phase / saga / worldwide_gross",
        not films[["phase", "saga", "worldwide_gross"]].isna().any().any(),
        "found nulls in a key column",
    )

    # ── Chart 1 (treemap by Phase) — top film + Phase totals ──────────────
    top = films.iloc[0]
    check(
        "chart1: top film is Avengers: Endgame @ $2,717,503,922",
        top.title == "Avengers: Endgame" and int(top.worldwide_gross) == 2_717_503_922,
        f"got {top.title!r} @ {int(top.worldwide_gross):,}",
    )
    phase_tot = (con.execute(
        "SELECT phase, SUM(worldwide_gross) tot FROM mcu_box_office "
        "GROUP BY phase ORDER BY tot DESC").df())
    check(
        "chart1: Phase 3 is the top Phase by total gross",
        phase_tot.iloc[0].phase == "Phase 3",
        f"got {phase_tot.iloc[0].phase!r}",
    )
    p3_share = float(phase_tot.iloc[0].tot) / total_ww
    check(
        "chart1: Phase 3 is ~38.5% of the franchise",
        approx(p3_share, 0.3851, tol=0.01),
        f"got {p3_share:.4f}",
    )

    # ── Chart 2 (treemap by Saga) — Infinity vs Multiverse split ──────────
    saga = con.execute(
        "SELECT saga, SUM(worldwide_gross) tot, COUNT(*) films "
        "FROM mcu_box_office GROUP BY saga").df().set_index("saga")
    inf_share = float(saga.loc["Infinity Saga", "tot"]) / total_ww
    mul_share = float(saga.loc["Multiverse Saga", "tot"]) / total_ww
    check("chart2: Infinity Saga == 23 films", int(saga.loc["Infinity Saga", "films"]) == 23,
          f"got {int(saga.loc['Infinity Saga','films'])}")
    check("chart2: Multiverse Saga == 15 films", int(saga.loc["Multiverse Saga", "films"]) == 15,
          f"got {int(saga.loc['Multiverse Saga','films'])}")
    check("chart2: Infinity Saga ~= 64.5% of franchise", approx(inf_share, 0.6453, tol=0.01),
          f"got {inf_share:.4f}")
    check("chart2: Multiverse Saga ~= 35.5% of franchise", approx(mul_share, 0.3547, tol=0.01),
          f"got {mul_share:.4f}")
    check("chart2: the two Sagas partition all 38 films",
          int(saga["films"].sum()) == 38, f"got {int(saga['films'].sum())}")

    # ── Chart 3 (avg gross per film by Phase) — the metric the chart shows ─
    avg = con.execute(
        "SELECT phase, ROUND(AVG(worldwide_gross)) avg_ww, COUNT(*) films "
        "FROM mcu_box_office GROUP BY phase, phase_num ORDER BY phase_num").df()
    avg_by_phase = {r.phase: (float(r.avg_ww), int(r.films)) for _, r in avg.iterrows()}
    expected_avg_b = {  # avg worldwide per film, in $B, rounded to 2dp (what the labels show)
        "Phase 1": 0.63, "Phase 2": 0.88, "Phase 3": 1.22,
        "Phase 4": 0.82, "Phase 5": 0.61, "Phase 6": 1.49,
    }
    for ph, exp_b in expected_avg_b.items():
        got_b = round(avg_by_phase[ph][0] / 1e9, 2)
        check(f"chart3: {ph} avg/film == ${exp_b:.2f}B", got_b == exp_b, f"got ${got_b:.2f}B")
    expected_films = {"Phase 1": 6, "Phase 2": 6, "Phase 3": 11, "Phase 4": 7, "Phase 5": 6, "Phase 6": 2}
    check("chart3: film counts per Phase match labels",
          {p: avg_by_phase[p][1] for p in expected_films} == expected_films,
          f"got {{p: avg_by_phase[p][1] for p in expected_films}}")
    # The chart's point: Phase 6 has the highest per-film average, Phase 3 second.
    ranked = sorted(avg_by_phase.items(), key=lambda kv: kv[1][0], reverse=True)
    check("chart3: Phase 6 has the highest avg/film", ranked[0][0] == "Phase 6", f"got {ranked[0][0]}")
    check("chart3: Phase 3 has the second-highest avg/film", ranked[1][0] == "Phase 3", f"got {ranked[1][0]}")

    # ── Chart 4 (domestic vs international by Phase) — percentages sum to 100 ─
    split = con.execute(
        "SELECT phase, SUM(domestic_gross) dom, SUM(international_gross) intl "
        "FROM mcu_box_office GROUP BY phase, phase_num ORDER BY phase_num").df()
    split["dom_pct"] = (100 * split.dom / (split.dom + split.intl)).round(1)
    split["intl_pct"] = (100 * split.intl / (split.dom + split.intl)).round(1)
    check("chart4: each Phase's domestic% + international% == 100",
          bool((((split.dom_pct + split.intl_pct) - 100.0).abs() <= 0.1).all()),
          "a Phase's two shares do not sum to 100")
    # Spot-check one Phase's split (Phase 3 ~ 37% domestic).
    p3 = split[split.phase == "Phase 3"].iloc[0]
    check("chart4: Phase 3 domestic share ~= 37%", approx(float(p3.dom_pct), 37.0, tol=0.05),
          f"got {p3.dom_pct}%")

    # ── Published CSV matches the DuckDB source (no drift) ────────────────
    cols = ["title", "phase", "saga", "worldwide_gross", "domestic_gross",
            "international_gross", "share_of_franchise"]
    path = export_dir / "mcu_box_office_v1.csv"
    if not path.exists():
        check("export: mcu_box_office_v1.csv exists", False, "missing export file")
    else:
        df_csv = pd.read_csv(path)
        try:
            a = films[cols].sort_values("title").reset_index(drop=True)
            b = df_csv[cols].sort_values("title").reset_index(drop=True)
            same = a.shape == b.shape
            detail = "" if same else f"row count {a.shape[0]} vs {b.shape[0]}"
            if same:
                for col in cols:
                    if pd.api.types.is_numeric_dtype(a[col]):
                        diff = (a[col].astype("float64") - b[col].astype("float64")).abs()
                        # dollar cols exact-to-1; share col to 1e-4
                        tol = 1.0 if a[col].abs().max() > 10 else 1e-4
                        col_ok = bool(((diff <= tol) | (a[col].isna() & b[col].isna())).all())
                    else:
                        col_ok = bool((a[col].fillna("\x00").astype(str) ==
                                       b[col].fillna("\x00").astype(str)).all())
                    if not col_ok:
                        same = False
                        detail = f"column {col!r} differs"
                        break
            check("export: mcu_box_office_v1.csv matches DuckDB on key columns", same,
                  (detail + " — regenerate 03-prepare") if detail else "")
        except KeyError as e:
            check(f"export: CSV has expected columns {cols}", False, str(e))

    con.close()

    # ── Social vs web chart parity ────────────────────────────────────────
    social_dir = PROJECT / "outputs" / "social"
    web_dir = PROJECT / "outputs" / "web"
    social = sorted(social_dir.glob("*.png")) if social_dir.exists() else []
    if social and web_dir.exists():
        s_names = {p.name for p in social}
        w_names = {p.name for p in web_dir.glob("*.png")}
        check("parity: social and web sets cover the same filenames", s_names == w_names,
              f"only social: {sorted(s_names - w_names)}; only web: {sorted(w_names - s_names)}")
        check("parity: exactly 4 published charts", len(s_names) == 4, f"got {len(s_names)}")
        try:
            from PIL import Image
            s_dims = {Image.open(p).size for p in social}
            w_dims = {Image.open(p).size for p in web_dir.glob("*.png")}
            check("parity: every social chart is 1600x900", s_dims == {(1600, 900)}, f"got {sorted(s_dims)}")
            check("parity: every web chart is 1664x936", w_dims == {(1664, 936)}, f"got {sorted(w_dims)}")
        except ImportError:
            pass
    else:
        checks.append("  SKIP  chart parity (outputs/ not rendered on this checkout)")

    # ── Report ────────────────────────────────────────────────────────────
    print("Pre-publish chart-data validation — marvel (MCU box office)")
    print("=" * 60)
    for line in checks:
        print(line)
    for line in failures:
        print(line)
    print("=" * 60)
    if failures:
        print(f"RESULT: {len(failures)} FAILURE(S) — DO NOT PUBLISH.")
        return 1
    print(f"RESULT: all {len([c for c in checks if 'PASS' in c])} checks passed — safe to publish.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
