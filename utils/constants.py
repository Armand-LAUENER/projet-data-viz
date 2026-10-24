"""BAAC code labels, groupings, geography and colours.

Everything that turns an ONISR/BAAC numeric code into something a non-specialist
reader understands lives here, so no SEC-like jargon ever reaches the UI.
Codes follow the ONISR "Description des bases de données annuelles" (2019+ format).
"""

from __future__ import annotations

from pathlib import Path

# --- Dataset identity ------------------------------------------------------
DATASET_ID = "53698f4ca3a729239d2036df"
DATASET_TITLE = "Bases de données annuelles des accidents corporels (BAAC)"
PRODUCER = "ONISR"
LICENCE = "Licence Ouverte / Etalab 2.0"
DATASET_URL = (
    "https://www.data.gouv.fr/datasets/bases-de-donnees-annuelles-des-accidents-"
    "corporels-de-la-circulation-routiere-annees-de-2005-a-2024"
)

# --- Perimeter -------------------------------------------------------------
YEARS = list(range(2019, 2025))   # homogeneous 2019+ format
LAST_YEAR = 2024                  # last complete published year
TABLES = ["caracteristiques", "lieux", "vehicules", "usagers"]
CONFIDENTIALITY_MIN = 5           # mask crossed cells with fewer than N killed

# --- Paths -----------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
GEOJSON = ROOT / "assets" / "departements.geojson"

# --- Code labels (plain language) ------------------------------------------
GRAV_LABELS = {1: "Unharmed", 2: "Killed", 3: "Hospitalised", 4: "Slight injury"}
SEXE_LABELS = {1: "Male", 2: "Female", -1: "Unknown"}
AGG_LABELS = {1: "Outside built-up area", 2: "Built-up area"}
LUM_LABELS = {
    1: "Daylight", 2: "Dawn/dusk", 3: "Night, no lighting",
    4: "Night, lighting off", 5: "Night, lighting on",
}
ATM_LABELS = {
    -1: "Unknown", 1: "Normal", 2: "Light rain", 3: "Heavy rain", 4: "Snow/hail",
    5: "Fog/smoke", 6: "Strong wind", 7: "Dazzling", 8: "Overcast", 9: "Other",
}
CATU_LABELS = {1: "Driver", 2: "Passenger", 3: "Pedestrian"}
CATR_LABELS = {
    1: "Motorway", 2: "National road", 3: "Departmental road", 4: "Local road",
    5: "Off public network", 6: "Car park", 7: "Urban metropolis road", 9: "Other",
}

# --- Mode of transport (grouping of catv + pedestrians) --------------------
# Pedestrians are detected from catu==3 before catv is read.
CATV_TO_MODE = {
    1: "Bicycle", 80: "Bicycle",                         # incl. e-bike
    50: "E-scooter / PMD", 60: "E-scooter / PMD",
    2: "Powered two-wheeler", 30: "Powered two-wheeler", 31: "Powered two-wheeler",
    32: "Powered two-wheeler", 33: "Powered two-wheeler", 34: "Powered two-wheeler",
    41: "Powered two-wheeler", 42: "Powered two-wheeler", 43: "Powered two-wheeler",
    3: "Car", 7: "Car", 8: "Car", 9: "Car",
    10: "Light goods vehicle", 11: "Light goods vehicle", 12: "Light goods vehicle",
    13: "Heavy goods vehicle", 14: "Heavy goods vehicle", 15: "Heavy goods vehicle",
    16: "Heavy goods vehicle", 17: "Heavy goods vehicle",
    37: "Bus/coach", 38: "Bus/coach",
    35: "Quad/other", 36: "Quad/other", 39: "Quad/other", 40: "Quad/other",
}
MODE_PEDESTRIAN = "Pedestrian"
MODE_ORDER = [
    "Pedestrian", "Bicycle", "E-scooter / PMD", "Powered two-wheeler",
    "Car", "Light goods vehicle", "Heavy goods vehicle", "Bus/coach", "Quad/other",
]
# Vulnerable road users (highlighted in the "who" section).
VULNERABLE_MODES = ["Pedestrian", "Bicycle", "E-scooter / PMD", "Powered two-wheeler"]

# --- Age bins --------------------------------------------------------------
AGE_BINS = [0, 14, 18, 25, 35, 45, 55, 65, 75, 200]
AGE_LABELS = ["0-13", "14-17", "18-24", "25-34", "35-44", "45-54", "55-64", "65-74", "75+"]

# --- Missing-value sentinels ----------------------------------------------
MISSING_CODES = {-1, "-1", "", " "}

# --- Geography -------------------------------------------------------------
def is_metropolitan(dep: str) -> bool:
    """Metropolitan departments are 2-char codes (01-95, 2A, 2B); overseas are 3-digit."""
    return isinstance(dep, str) and len(dep) == 2

# 96 metropolitan departments -> 13 regions.
DEP_TO_REGION = {
    # Auvergne-Rhône-Alpes
    **{d: "Auvergne-Rhône-Alpes" for d in
       ["01", "03", "07", "15", "26", "38", "42", "43", "63", "69", "73", "74"]},
    # Bourgogne-Franche-Comté
    **{d: "Bourgogne-Franche-Comté" for d in
       ["21", "25", "39", "58", "70", "71", "89", "90"]},
    # Bretagne
    **{d: "Bretagne" for d in ["22", "29", "35", "56"]},
    # Centre-Val de Loire
    **{d: "Centre-Val de Loire" for d in ["18", "28", "36", "37", "41", "45"]},
    # Corse
    **{d: "Corse" for d in ["2A", "2B"]},
    # Grand Est
    **{d: "Grand Est" for d in
       ["08", "10", "51", "52", "54", "55", "57", "67", "68", "88"]},
    # Hauts-de-France
    **{d: "Hauts-de-France" for d in ["02", "59", "60", "62", "80"]},
    # Île-de-France
    **{d: "Île-de-France" for d in ["75", "77", "78", "91", "92", "93", "94", "95"]},
    # Normandie
    **{d: "Normandie" for d in ["14", "27", "50", "61", "76"]},
    # Nouvelle-Aquitaine
    **{d: "Nouvelle-Aquitaine" for d in
       ["16", "17", "19", "23", "24", "33", "40", "47", "64", "79", "86", "87"]},
    # Occitanie
    **{d: "Occitanie" for d in
       ["09", "11", "12", "30", "31", "32", "34", "46", "48", "65", "66", "81", "82"]},
    # Pays de la Loire
    **{d: "Pays de la Loire" for d in ["44", "49", "53", "72", "85"]},
    # Provence-Alpes-Côte d'Azur
    **{d: "Provence-Alpes-Côte d'Azur" for d in ["04", "05", "06", "13", "83", "84"]},
}
REGIONS = sorted(set(DEP_TO_REGION.values()))

# --- Colours (colourblind-safe, sober tone for a sensitive topic) ----------
SEQ_SCALE = "Cividis"          # maps and heatmaps
COLOR_KILLED = "#B22222"       # deaths: restrained dark red
COLOR_ACCIDENTS = "#0072B2"    # accident counts: blue
COLOR_GRAVITY = "#D55E00"      # gravity index: orange
COLOR_REF = "#888888"
OKABE_ITO = ["#0072B2", "#E69F00", "#009E73", "#D55E00",
             "#CC79A7", "#56B4E9", "#F0E442", "#000000", "#999999"]
MODE_COLORS = dict(zip(MODE_ORDER, OKABE_ITO))

# Crisis / break annotations on time series.
COVID_YEAR = 2020
