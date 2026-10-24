# Storyboard — When does a road accident turn deadly?

> Produced before the code. Each panel = one insight sentence, one visual, one
> interaction, one question. A chart that answers no question is cut. Insight
> sentences were finalised after Phase 1 exploration, from what the data showed.

**Audience:** general public, esp. young drivers & vulnerable users.
**Question:** when, where and for whom does an accident turn deadly?
**Thread:** frequency ≠ severity (gravity index = killed per 100 accidents).

---

### Panel 0 — Intro (Hook + Context)
- **Insight:** "In 2024, 3 193 people were killed on metropolitan roads — ~9 a day."
- **Visual:** KPI header (accidents, killed, gravity index, % deaths outside town) +
  collapsible **Definitions** box.
- **Interaction:** global filters (years).
- **Answers:** why it matters; how to read the numbers.

### Panel 1 — When?
- **Insight:** "Accidents peak at rush hour, but a night accident is far deadlier
  (≈9.8 vs 5.7 killed/100)."
- **Visual:** hour × weekday **heatmap** + monthly **seasonality** curve.
- **Interaction:** metric toggle (Accidents / Killed / Gravity index); years.
- **Answers:** when is the risk highest?

### Panel 2 — Where?
- **Insight:** "The map inverts: the departments with the most accidents are the
  least deadly per accident (corr −0.58)."
- **Visual:** department **choropleth** + built-up-vs-outside **share bars**.
- **Interaction:** metric toggle; region multiselect; years.
- **Answers:** where are accidents most deadly?

### Panel 3 — Who?
- **Insight:** "Powered two-wheelers are ~22 % of deaths; e-scooters the mirror
  image; deaths peak at 18–24 and 75+."
- **Visual:** **dumbbell** (share of victims vs share of deaths by mode) + **age
  pyramid** of the killed by sex.
- **Interaction:** mode multiselect; years.
- **Answers:** who pays the heaviest toll?

### Panel 4 — In what conditions? *(bonus)*
- **Insight:** "Night, open roads and higher speed limits all raise the share that kill."
- **Visual:** **small multiples** of the gravity index by lighting, weather, road type,
  speed limit.
- **Interaction:** none (whole-period view).
- **Answers:** what conditions aggravate accidents?

### Panel 5 — Can we trust these numbers?
- **Insight:** "Pipeline reproduces the ONISR figures exactly; known fragilities shown."
- **Visual:** validation table + missingness heatmap + quality KPIs; **ethics** note.
- **Interaction:** none.
- **Answers:** how reliable, and handled how responsibly?

### Panel 6 — What to take away
- **Insight:** the three findings restated + what the data cannot say.
- **Visual:** text recap.
- **Answers:** what to remember — and not over-conclude.

---

**Control → effect map** (every control changes something):

| Control | Affects |
|---|---|
| Years slider | every chart and KPI |
| Metric (Accidents / Killed / Gravity index) | heatmap + choropleth |
| Regions multiselect | choropleth + department-based KPIs |
| Modes multiselect | mode dumbbell |
