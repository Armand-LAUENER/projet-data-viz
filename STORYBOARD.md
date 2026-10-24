# Storyboard — The French tax exception?

> Produced before the code. Each panel = one insight sentence, one visual, one
> interaction, and the one question it answers. A chart that answers no question
> is cut. Insight sentences are written from what Phase 1 actually showed.

**Audience:** curious non-specialist who has heard "France is Europe's tax
champion". **Question:** is France a real tax outlier, and what is the gap made of?

---

### Panel 0 — Intro (Hook + Context)
- **Insight:** "In 2024 France raised 45.3 % of GDP in taxes & contributions,
  ~+5 points above the EU27 average."
- **Visual:** KPI header (focal ratio, EU27 avg, gap, rank) + accroche text +
  a collapsible **Definition** box.
- **Interaction:** none (sets the frame).
- **Answers:** Why does this matter? What exactly is measured?

### Panel 1 — Where does each country stand?
- **Insight:** "France has the 2nd highest ratio in the EU27."
- **Visual:** choropleth of Europe (Cividis) **+** horizontal ranking bars with
  the EU27 average as a reference line; France highlighted.
- **Interaction:** reference-year slider; metric switch (total ↔ one category);
  include non-EU toggle.
- **Answers:** What is each country's relative level?

### Panel 2 — How did we get here?
- **Insight:** "The France–EU27 gap is structural, visible since 1995" (exact
  verb — widened / narrowed / stable — set from the data for the chosen period).
- **Visual:** multi-country line chart (France vs EU27 vs selected) **+** a
  dedicated gap line (country − EU), zero line, extremes annotated. Crisis bands
  mark 2008–09 and 2020.
- **Interaction:** country multiselect; period slider.
- **Answers:** Is the gap recent or long-standing?

### Panel 3 — What is the gap made of?
- **Insight:** "Most of the gap comes from production taxes **and** social
  contributions — not from income & wealth taxes (below EU average)."
- **Visual:** stacked bars by category (FR vs EU vs selected) **+** small
  multiples, one panel per category, shared Y scale **+** a decomposition table.
- **Interaction:** countries compared; reference year.
- **Answers:** Which component explains the gap?

### Panel 4 — Who collects? *(bonus)*
- **Insight:** "In France, social security funds collect ~54 % of all receipts."
- **Visual:** 100 %-stacked bars by subsector (central / local / social security).
- **Interaction:** countries compared; reference year.
- **Answers:** Who actually receives the money?

### Panel 5 — Can we trust these numbers?
- **Insight:** "The series is ~99 % complete; known definition caveats are shown."
- **Visual:** completeness heatmap (country × year) + duplicate / sum-coherence
  metrics + a validation table reproducing official figures.
- **Interaction:** none.
- **Answers:** How reliable are these figures?

### Panel 6 — What to take away
- **Insight:** the three findings restated + what the data cannot say.
- **Visual:** text recap of key numbers.
- **Interaction:** none.
- **Answers:** What should the reader remember — and not over-conclude?

---

**Control → effect map** (every control changes something useful):

| Control | Affects |
|---|---|
| Period slider | lines, gap line, KPI "since start" delta |
| Reference-year slider | map, ranking, composition, KPIs, subsectors |
| Focal country | KPIs, gap line, decomposition, conclusions |
| Countries compared | lines, stacked bars, small multiples, subsectors |
| Metric (total/category) | map, ranking |
| Include non-EU toggle | map, ranking |
