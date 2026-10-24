"""Pure data transformations: raw BAAC CSVs -> tidy analysis frames.

No Streamlit, no network. Reads one year's four tables, harmonises them, joins
them correctly (the join that must NOT duplicate rows is usagers x vehicules on
the vehicle key, not on Num_Acc alone), and derives the features the story needs.
Unit-tested in tests/test_prep.py.
"""

from __future__ import annotations

import pandas as pd

from utils import constants as C


# --- Robust reading --------------------------------------------------------
def read_raw(year: int, table: str) -> pd.DataFrame:
    """Read one raw BAAC CSV (';'-separated, latin-1, dep kept as string)."""
    path = C.RAW_DIR / f"{table}_{year}.csv"
    df = pd.read_csv(path, sep=";", encoding="latin-1", low_memory=False,
                     dtype={"dep": str, "com": str})
    df.columns = [c.strip() for c in df.columns]
    # The accident key is named 'Accident_Id' in some years (e.g. caract 2022).
    df = df.rename(columns={"Accident_Id": "Num_Acc"})
    return df


def _to_float(series: pd.Series) -> pd.Series:
    """French decimals use a comma; convert to float."""
    return pd.to_numeric(
        series.astype(str).str.replace(",", ".", regex=False).replace({"nan": None}),
        errors="coerce",
    )


def _hour(hrmn: pd.Series) -> pd.Series:
    """Extract the hour (0-23) from an 'hh:mm' string."""
    s = hrmn.astype(str).str.extract(r"^(\d{1,2})")[0]
    return pd.to_numeric(s, errors="coerce").astype("Int64")


def _mode(catu: pd.Series, catv: pd.Series) -> pd.Series:
    """Map each road user to a plain-language transport mode."""
    cv = pd.to_numeric(catv, errors="coerce")
    mode = cv.map(C.CATV_TO_MODE).fillna("Quad/other")
    mode = mode.where(catu != 3, C.MODE_PEDESTRIAN)  # catu==3 -> pedestrian
    return mode


# --- Usager-level frame (victims & deaths) ---------------------------------
def build_usager_level(year: int) -> pd.DataFrame:
    """One enriched row per road user, carrying accident context.

    Columns: Num_Acc, year, month, weekday, hour, lum, atm, catr, vma, dep,
    region, metro, agg_label, mode, grav, killed, victim, sexe_label, age, age_band.
    """
    car = read_raw(year, "caracteristiques")
    # lieux can carry several rows per accident in some years; keep one (catr/vma
    # are accident-level attributes) so the join never duplicates users.
    lie = read_raw(year, "lieux").drop_duplicates("Num_Acc")
    veh = read_raw(year, "vehicules")
    usa = read_raw(year, "usagers")

    # Accident context: caracteristiques (+ lieux for road type / speed limit).
    car = car.rename(columns={"long": "lon"})
    ctx = car[["Num_Acc", "jour", "mois", "an", "hrmn", "lum", "dep", "agg", "atm"]].copy()
    ctx = ctx.merge(lie[["Num_Acc", "catr", "vma"]], on="Num_Acc", how="left")

    # Users + vehicle category (join on the VEHICLE key -> no row duplication).
    rows_before = len(usa)
    usa = usa.merge(veh[["Num_Acc", "id_vehicule", "catv"]],
                    on=["Num_Acc", "id_vehicule"], how="left")
    assert len(usa) == rows_before, "usagers x vehicules join duplicated rows"

    df = usa.merge(ctx, on="Num_Acc", how="left")

    # Derived features.
    df["year"] = pd.to_numeric(df["an"], errors="coerce").astype("Int64")
    df["month"] = pd.to_numeric(df["mois"], errors="coerce").astype("Int64")
    dt = pd.to_datetime(
        dict(year=df["year"], month=df["month"],
             day=pd.to_numeric(df["jour"], errors="coerce")),
        errors="coerce",
    )
    df["weekday"] = dt.dt.dayofweek            # 0 = Monday
    df["hour"] = _hour(df["hrmn"])
    df["metro"] = df["dep"].map(C.is_metropolitan)
    df["region"] = df["dep"].map(C.DEP_TO_REGION)
    df["agg_label"] = pd.to_numeric(df["agg"], errors="coerce").map(C.AGG_LABELS)
    df["mode"] = _mode(df["catu"], df["catv"])
    df["grav"] = pd.to_numeric(df["grav"], errors="coerce")
    df["killed"] = (df["grav"] == 2).astype(int)
    df["victim"] = df["grav"].isin([2, 3, 4]).astype(int)   # excludes "unharmed"
    df["sexe_label"] = pd.to_numeric(df["sexe"], errors="coerce").map(C.SEXE_LABELS)

    age = df["year"] - pd.to_numeric(df["an_nais"], errors="coerce")
    df["age"] = age.where((age >= 0) & (age <= 110))
    df["age_band"] = pd.cut(df["age"], bins=C.AGE_BINS, labels=C.AGE_LABELS, right=False)
    return df


def build_accident_level(year: int) -> pd.DataFrame:
    """One row per accident, with context + a fatal flag (>=1 killed)."""
    car = read_raw(year, "caracteristiques").rename(columns={"long": "lon"})
    lie = read_raw(year, "lieux").drop_duplicates("Num_Acc")
    usa = read_raw(year, "usagers")

    killed = (pd.to_numeric(usa["grav"], errors="coerce")
              .eq(2).groupby(usa["Num_Acc"]).max())

    df = car[["Num_Acc", "jour", "mois", "an", "hrmn", "lum", "dep", "agg", "atm",
              "lat", "lon"]].copy()
    df = df.merge(lie[["Num_Acc", "catr", "vma"]], on="Num_Acc", how="left")
    df["year"] = pd.to_numeric(df["an"], errors="coerce").astype("Int64")
    df["month"] = pd.to_numeric(df["mois"], errors="coerce").astype("Int64")
    dt = pd.to_datetime(
        dict(year=df["year"], month=df["month"],
             day=pd.to_numeric(df["jour"], errors="coerce")), errors="coerce")
    df["weekday"] = dt.dt.dayofweek
    df["hour"] = _hour(df["hrmn"])
    df["metro"] = df["dep"].map(C.is_metropolitan)
    df["region"] = df["dep"].map(C.DEP_TO_REGION)
    df["agg_label"] = pd.to_numeric(df["agg"], errors="coerce").map(C.AGG_LABELS)
    df["lat"] = _to_float(df["lat"])
    df["lon"] = _to_float(df["lon"])
    df["is_fatal"] = df["Num_Acc"].map(killed).fillna(False).astype(int)
    return df


# --- Validation helpers (used by app + tests) ------------------------------
def duplicate_accidents(year: int) -> int:
    car = read_raw(year, "caracteristiques")
    return int(car["Num_Acc"].duplicated().sum())


def killed_count(df_usager: pd.DataFrame, metro_only: bool = True) -> int:
    d = df_usager[df_usager["metro"]] if metro_only else df_usager
    return int(d["killed"].sum())
