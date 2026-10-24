"""Build the small, pre-aggregated tables the app serves.

Three wins at once (plan §8.2): performance, privacy (no individual row is ever
deployed), and deployment safety. Every output is a tidy Parquet in
data/processed/. The confidentiality threshold (§10) masks small crossed cells.
"""

from __future__ import annotations

import pandas as pd

from utils import constants as C
from utils import prep


def _accidents_by(acc: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    return acc.groupby(keys, observed=True).agg(
        accidents=("Num_Acc", "nunique")).reset_index()


def _people_by(usr: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    return usr.groupby(keys, observed=True).agg(
        killed=("killed", "sum"), victims=("victim", "sum")).reset_index()


def build_all(years: list[int] | None = None) -> dict[str, pd.DataFrame]:
    """Compute every aggregated table across all years. Returns a dict."""
    years = years or C.YEARS
    usr = pd.concat([prep.build_usager_level(y) for y in years], ignore_index=True)
    acc = pd.concat([prep.build_accident_level(y) for y in years], ignore_index=True)
    out: dict[str, pd.DataFrame] = {}

    # KPI base: year x metro x agg_label -> accidents, killed, victims.
    a = _accidents_by(acc, ["year", "metro", "agg_label"])
    p = _people_by(usr, ["year", "metro", "agg_label"])
    out["kpi"] = a.merge(p, on=["year", "metro", "agg_label"], how="outer")

    # By department (metro only for the choropleth).
    am = _accidents_by(acc[acc["metro"]], ["dep", "region", "year"])
    pm = _people_by(usr[usr["metro"]], ["dep", "region", "year"])
    dep = am.merge(pm, on=["dep", "region", "year"], how="outer").fillna(0)
    dep["gravity_index"] = (dep["killed"] / dep["accidents"] * 100).round(2)
    out["by_dep"] = dep

    # Hour x weekday (heatmap) -- metro.
    a = _accidents_by(acc[acc["metro"]], ["hour", "weekday", "year"])
    p = _people_by(usr[usr["metro"]], ["hour", "weekday", "year"])
    hd = a.merge(p, on=["hour", "weekday", "year"], how="outer").fillna(0)
    hd["gravity_index"] = (hd["killed"] / hd["accidents"].replace(0, pd.NA) * 100).round(2)
    out["by_hour_dow"] = hd.dropna(subset=["hour", "weekday"])

    # Month (seasonality).
    a = _accidents_by(acc[acc["metro"]], ["year", "month"])
    p = _people_by(usr[usr["metro"]], ["year", "month"])
    out["by_month"] = a.merge(p, on=["year", "month"], how="outer").fillna(0)

    # Mode of transport (victims vs killed share).
    out["by_mode"] = _people_by(usr[usr["metro"]], ["mode", "year"])

    # Age x sex of the killed (confidentiality mask on small cells).
    agesex = _people_by(usr[usr["metro"]], ["age_band", "sexe_label", "year"])
    agesex = agesex[agesex["sexe_label"].isin(["Male", "Female"])]
    agesex.loc[agesex["killed"] < C.CONFIDENTIALITY_MIN, "killed"] = pd.NA
    out["by_age_sex"] = agesex

    # Conditions (small multiples): lum, atm, catr, speed band.
    cond_frames = []
    vma = pd.to_numeric(acc["vma"], errors="coerce")
    acc = acc.assign(
        lum_lbl=pd.to_numeric(acc["lum"], errors="coerce").map(C.LUM_LABELS),
        atm_lbl=pd.to_numeric(acc["atm"], errors="coerce").map(C.ATM_LABELS),
        catr_lbl=pd.to_numeric(acc["catr"], errors="coerce").map(C.CATR_LABELS),
        vma_band=pd.cut(vma.where((vma > 0) & (vma <= 130)),
                        bins=[0, 30, 50, 80, 90, 110, 130],
                        labels=["≤30", "31-50", "51-80", "81-90", "91-110", "111-130"]),
    )
    for dim, col in [("Lighting", "lum_lbl"), ("Weather", "atm_lbl"),
                     ("Road type", "catr_lbl"), ("Speed limit (km/h)", "vma_band")]:
        g = acc[acc["metro"]].groupby(col, observed=True).agg(
            accidents=("Num_Acc", "nunique"), fatal=("is_fatal", "sum")).reset_index()
        g = g.rename(columns={col: "modality"})
        g["dimension"] = dim
        g["gravity_index"] = (g["fatal"] / g["accidents"] * 100).round(2)
        cond_frames.append(g.dropna(subset=["modality"]))
    out["by_condition"] = pd.concat(cond_frames, ignore_index=True)

    # Geolocation completeness (for the quality section).
    geo = acc.groupby("year").agg(
        accidents=("Num_Acc", "nunique"),
        geoloc=("lat", lambda s: s.notna().sum())).reset_index()
    geo["geoloc_pct"] = (geo["geoloc"] / geo["accidents"] * 100).round(1)
    out["geo_quality"] = geo

    # Missingness of key user variables (quality heatmap).
    miss_vars = {"sexe": "sexe", "age": "age", "mode": "mode", "grav": "grav"}
    miss = []
    for y in years:
        sub = usr[usr["year"] == y]
        for label, col in miss_vars.items():
            if col == "sexe":
                na = (pd.to_numeric(sub["sexe"], errors="coerce") == -1).mean()
            else:
                na = sub[col].isna().mean()
            miss.append({"year": y, "variable": label, "missing_pct": round(na * 100, 2)})
    out["missingness"] = pd.DataFrame(miss)

    # One-off quality metrics (duplicates, orphans, validation).
    dup = sum(prep.duplicate_accidents(y) for y in years)
    orphans = 0
    for y in years:
        car = prep.read_raw(y, "caracteristiques")
        usa = prep.read_raw(y, "usagers")
        orphans += int((~usa["Num_Acc"].isin(set(car["Num_Acc"]))).sum())
    killed_2024_metro = int(usr[(usr["year"] == C.LAST_YEAR) & (usr["metro"])]["killed"].sum())
    male_share = (
        usr[(usr["year"] == C.LAST_YEAR) & (usr["metro"]) & (usr["killed"] == 1)]
        ["sexe_label"].eq("Male").mean() * 100
    )
    out["quality_report"] = pd.DataFrame([
        {"metric": "Duplicate accident ids", "value": dup, "reference": "expected 0"},
        {"metric": "Orphan users (no accident)", "value": orphans, "reference": "expected 0"},
        {"metric": "Killed, metro 2024", "value": killed_2024_metro, "reference": "ONISR 3193"},
        {"metric": "Male share of killed 2024 (%)", "value": round(float(male_share), 1),
         "reference": "ONISR 77"},
    ])

    return out


def write_all(years: list[int] | None = None) -> None:
    C.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    tables = build_all(years)
    for name, df in tables.items():
        df.to_parquet(C.PROCESSED_DIR / f"{name}.parquet", index=False)
        print(f"  wrote {name:14} {df.shape}")
