# When does a road accident turn deadly? — a data story on French road safety

An interactive Streamlit data story on the French road-accident database (BAAC,
ONISR). It follows one thread: **where and when accidents are most *frequent* is
not where and when they are most *deadly*.** The reader explores that contrast
across time, geography and road-user profiles.

- **Repository:** https://github.com/Armand-LAUENER/projet-data-viz
- **Live app:** https://projet-data-viz-fqbofjrosdu4xcvokeyvsb.streamlit.app/
- **Demo video (2–4 min):** _<add link>_
- **Storyboard:** [`STORYBOARD.md`](STORYBOARD.md)

> The app is **descriptive**: it compares and decomposes. It makes **no causal
> claim**, evaluates **no policy**, and — having no exposure data (km travelled) —
> **never ranks modes by risk per trip**. Only aggregates are deployed (ethics).

---

## 1. Question & audience

- **Central question:** when, where and for whom does a road accident turn deadly?
- **Thread:** the contrast between **frequency** and **severity**, measured by the
  **gravity index** = *people killed per 100 injury accidents* (a single-source metric
  that needs no population or distance denominator).
- **Audience:** a general audience, especially **young drivers and vulnerable road
  users**. Plain language, definitions in tooltips, no BAAC codes on screen.

## 2. What the data show (metropolitan France, 2024)

Hypotheses were tested, not assumed — and the data reshaped the story:

- **Frequency ≠ severity (the spine).** Only **37 % of accidents** happen outside
  built-up areas, but **68 % of deaths** do. Across departments, accident count and
  gravity index are **negatively correlated (−0.58)**: dense urban departments (Paris
  0.7 killed/100) have many minor accidents; sparse rural ones (Dordogne, Jura ≈ 21)
  have few but deadly ones. **The map inverts.**
- **Night is the deadly multiplier.** Gravity index at night (22h–6h) is **9.8** vs
  **5.7** in daytime — nearly double, for far fewer accidents.
- **Who dies is not who you'd guess.** Powered two-wheelers are **22 % of deaths**
  (far above their traffic share); e-scooters are the mirror image (many injuries, few
  deaths); deaths peak twice by age — **18–24** (521) and **75+** (551).

## 3. Data

| | |
|---|---|
| Dataset | ONISR — *Bases de données annuelles des accidents corporels (BAAC)* |
| Portal | **data.gouv.fr** (dataset id `53698f4ca3a729239d2036df`) |
| Producer | ONISR (Observatoire national interministériel de la sécurité routière) |
| Structure | 4 tables (caractéristiques, lieux, véhicules, usagers) joined on the accident id |
| Perimeter | **2019–2024, metropolitan France** (homogeneous format) |
| Licence | **Licence Ouverte / Etalab 2.0** |

**Citation**

```
Source: ONISR — Bases de données annuelles des accidents corporels de la circulation
routière, années 2005 à 2024, data.gouv.fr, Licence Ouverte / Etalab 2.0, accessed 2026-10-24.
Reprocessed by the author: harmonisation, joins, aggregation.
```

## 4. Method

- **Perimeter 2019–2024, metropolitan France** (overseas excluded for comparability).
  Metropolitan = 2-char department code (incl. Corsica `2A`/`2B`).
- **Four tables joined** on the accident id. Two traps handled (all tested):
  - the accident key is **`Accident_Id` in caract 2022**, `Num_Acc` elsewhere → harmonised;
  - **`lieux` has several rows per accident** in some years → de-duplicated so the
    users×context join never inflates counts;
  - users↔vehicles joined on the **vehicle key** (not on the accident id alone).
- **Gravity index** = killed / 100 injury accidents — the frequency-vs-severity metric.
- **Derived**: weekday, hour, season, age band, **mode of transport** (grouping of
  `catv` + pedestrians), metropolitan flag, region.
- **Deaths only for comparisons** (the 30-day indicator); hospitalised-injury counts
  broke in 2018 and are never used for trends.

See [`utils/prep.py`](utils/prep.py) (joins & features), [`utils/aggregate.py`](utils/aggregate.py)
(aggregated tables) and [`utils/constants.py`](utils/constants.py) (every code → label).

## 5. Run the project

```bash
git clone https://github.com/Armand-LAUENER/projet-data-viz.git
cd projet-data-viz

uv sync --extra dev        # or: make install
make data                  # optional: re-download the raw CSVs (data/processed is committed)
make tables                # optional: rebuild the aggregates
make run                   # streamlit run app.py
make test                  # 7 targeted tests
```

The app reads the **committed aggregated tables** in `data/processed/` (~60 kB) — no
network, no individual records, same figures in the demo and at grading.

## 6. Code structure

```
app.py                 entry point: sidebar, KPI header, sections
sections/              intro · when · where · who · conditions · quality · conclusions
utils/
  io.py                load aggregated tables + basemap (st.cache_data)
  prep.py              pure, tested: read → harmonise → join → derive features
  aggregate.py         build the pre-aggregated Parquet tables
  viz.py               unified Plotly chart factory
  constants.py         BAAC code labels, mode grouping, dep→region, palette
scripts/
  download_data.py     data.gouv API → data/raw/ + MANIFEST (dated snapshot)
  build_tables.py      data/raw → data/processed (aggregates) + validation
data/processed/        committed aggregates (the only data the app serves)
assets/departements.geojson   departments basemap (see §9)
tests/test_prep.py     key uniqueness, no join inflation, ONISR reproduction, labels
```

## 7. Data quality & validation

Shown in-app (section 5):

- **Reproduces ONISR 2024 exactly**: killed metropolitan = **3193** (ref 3193),
  metro+overseas = 3432, male share of the killed = 77 % (ref 77 %).
- **0 duplicate accident ids**, **0 orphan users**; gravity index within a sane range.
- **Honest artefacts**: age/sex missingness rises from 2021 (hit-and-run offenders
  added); injury counts are *not* reproducible (ONISR corrects them separately); not all
  accidents are geolocated (department totals used, no point map); 2020 COVID distortion.

## 8. Ethics & privacy

Deaths involve real people. Safeguards (section 5 + here): **only aggregates deployed**;
**no point map** of fatal accidents with date/age/sex; **suppression threshold** (cells
with < 5 deaths masked in age × sex); sober tone; reminder that the victim mix also
reflects exposure, which is unknown here.

## 9. Licences & the basemap

- **Code:** MIT (see [`LICENSE`](LICENSE)).
- **Data:** ONISR / BAAC — **Licence Ouverte / Etalab 2.0** (distinct from the code).
- **Basemap:** `assets/departements.geojson` (simplified departments, from the
  open `france-geojson` project) is a **map background, not analytical data** — all
  values come from the BAAC. A 100 % single-source alternative (density map from the
  BAAC coordinates) is possible if an external basemap is not accepted.

## Notes for the demo / grading

Streamlit Community Cloud apps hibernate — open the app a few minutes before the demo or
grading so it is awake.
