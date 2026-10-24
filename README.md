# The French tax exception? — a data story on tax-to-GDP in Europe

An interactive Streamlit data story that asks a question many people think they
already know the answer to: **is France really a tax outlier in Europe — and
what is the gap actually made of?** It uses Eurostat's national-accounts tax
aggregates (1995–2025, ~30 countries) and lets the reader explore the answer
rather than take it on faith.

- **Repository:** https://github.com/Armand-LAUENER/projet-data-viz
- **Live app:** _<add Streamlit Community Cloud URL after deployment>_
- **Demo video (2–4 min):** _<add link>_
- **Storyboard:** [`STORYBOARD.md`](STORYBOARD.md)

> The app is **descriptive**: it compares and decomposes. It makes **no causal
> claim** and no political judgement, and it says explicitly what the data
> cannot tell us.

---

## 1. Question & audience

- **Central question:** Is France a genuine tax exception in Europe, and which
  components explain the gap with the EU average?
- **Audience:** a curious, non-specialist reader (citizen or student) who has
  heard *"France is Europe's tax champion"* and wants to know what that means.
  Hence: plain vocabulary, definitions in tooltips, no visible SEC 2010 jargon.
- **Narrative arc:** Hook → Context (definition) → Insights (rank, trend,
  composition) → Implications (what we can and cannot conclude).

## 2. What the data show (headline findings, 2024)

The analysis was driven by the data, not the other way around. The working
hypothesis was that the French gap comes *mainly* from social contributions.
**The data only partly confirm it** — which makes for a more honest story:

- France raises **45.3 % of GDP** in taxes + social contributions, **rank 2 of
  27** (behind Denmark 45.5, ahead of Belgium 45.2) — matching Eurostat's
  official top three.
- The gap with the EU27 average (40.2 %) is **+5.1 points**, and it is
  **structural**: visible across the whole 1995– period, not a recent spike.
- **The gap is two blocs, not one.** Decomposed by category (FR − EU27, 2024):

  | Category | FR − EU27 gap |
  |---|---|
  | Taxes on production & imports | **+2.8 pts** |
  | Net social contributions | **+2.6 pts** |
  | Capital taxes | +0.4 pts |
  | Current taxes on income & wealth | **−0.7 pts** |

  So the "tax champion" label is really about **how social spending is
  financed** (social contributions *and* production taxes), while French income
  & wealth taxes sit **at or below** the EU average.

## 3. Data

| | |
|---|---|
| Dataset | Eurostat — *Main national accounts tax aggregates* |
| Code / DOI | `gov_10a_taxag` · DOI [`10.2908/gov_10a_taxag`](https://doi.org/10.2908/gov_10a_taxag) |
| Coverage | 1995–2025, EU27 + aggregates + IS/NO/CH, annual |
| Unit used | **% of GDP** (`PC_GDP`); € million (`MIO_EUR`) for the "who collects" shares |
| Licence | **CC BY 4.0** (Eurostat reuse policy) |
| Snapshot | see the dated file in [`data/`](data/) |

**Citation**

```
Source: Eurostat, Main national accounts tax aggregates (gov_10a_taxag),
DOI 10.2908/gov_10a_taxag, accessed 2026-10-24.
Modified data: filtering, category grouping and derived calculations by the author.
```

## 4. Method

Every analytical choice is documented so the numbers are reproducible.

- **Sector = `S13_S212`** (general government + EU institutions). Chosen because
  it reproduces the official headline figures exactly (FR 2024 = 45.3 %,
  EU 2023 = 39.9 %); the alternative `S13` under-reports by ~0.2–0.3 pt. The
  sector is **fixed for every country** — comparisons are always like-for-like.
- **Headline indicator = `D2_D5_D91_D61_M_D995`** (taxes + net social
  contributions − uncollectable amounts) = the tax-to-GDP ratio.
- **Four reader-friendly categories**, each one Eurostat `na_item`:
  `D2` production & imports, `D5` income & wealth, `D91` capital,
  `D61` net social contributions. `D995` (uncollectable) is subtracted, not
  shown. The four categories − `D995` reconcile with the total (tested).
- **EU reference = `EU27_2020`** over the whole series (stable 27-member
  definition, UK excluded from 1995) so composition never changes mid-series.
- **Derived variables:** `gap_vs_eu` (country − EU, pts), `rank` (within EU27),
  `share_of_total` (category share), subsector shares, `is_provisional`.
- **One source only.** INSEE's "compulsory levies" figure differs by scope; we
  never mix INSEE and Eurostat in the same chart.

See [`utils/prep.py`](utils/prep.py) for the exact transformations and
[`utils/constants.py`](utils/constants.py) for every code → label mapping.

## 5. Run the project

```bash
git clone https://github.com/Armand-LAUENER/projet-data-viz.git
cd projet-data-viz

# with uv (recommended)
uv sync --extra dev        # or: make install
make data                  # optional: refresh the Eurostat snapshot
make run                   # streamlit run app.py
make test                  # 5 targeted tests

# without uv
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The app reads the **local snapshot** in `data/`, never the network, so the demo
and the grading run always show the same figures.

## 6. Code structure

```
app.py                 entry point: page config, sidebar, KPI header, sections
sections/              one module per narrative step (intro → conclusions)
utils/
  io.py                load the snapshot (st.cache_data lives here)
  prep.py              pure, tested pandas transformations
  viz.py               unified Plotly chart factory
  constants.py         codes, category/ISO mappings, accessible palette
scripts/download_data.py   Eurostat → dated Parquet snapshot
data/                  committed, filtered snapshot (a few hundred kB)
tests/test_prep.py     duplicates, sum coherence, official-figure reproduction, ISO map
```

## 7. Data quality & limitations

Shown transparently inside the app (section 5):

- **Completeness** ~99 %; the most recent year (2025) is only partly reported
  (22/34 geographies) and flagged provisional.
- **0 duplicates** on the natural key; category sums reconcile to within 0.2 pt.
- **Denominator effect:** a ratio can rise because GDP falls (2009, 2020) with
  no tax increase — crisis years are shaded on the time series.
- **Revisions:** EU27 2024 reads 40.2 % here vs. 40.4 % in Eurostat's Oct-2025
  release — a revision between that release and this snapshot, documented, not
  hidden.
- **Scope:** a % of GDP is not a personal tax rate and says nothing about
  whether public money is well spent.

## 8. Accessibility

Colourblind-safe palettes (Cividis map, Okabe-Ito lines); information is never
carried by colour alone (direct labels + reference lines); every axis has a unit;
each chart has a one-sentence `st.caption` alt text; charts render with
`theme="streamlit"` so they adapt to light and dark.

## 9. Possible extensions

Break `D2` down (VAT vs. other production taxes); add a household-level view from
a different dataset; extend beyond the EU with OECD data (different definitions).

## 10. Licences

- **Code:** MIT (see [`LICENSE`](LICENSE)).
- **Data:** © European Union, Eurostat — **CC BY 4.0**. The two are distinct.

## Notes for the demo / grading

Streamlit Community Cloud apps **hibernate** after inactivity — open the app once
a few minutes before the demo or grading so it is awake.
