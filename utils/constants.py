"""Central registry of codes, labels, groupings and colours.

Everything that maps an Eurostat code to something a non-specialist reader can
understand lives here, so the rest of the app never has to know about SEC 2010
vocabulary. See README (section "Method") for why each choice was made.
"""

from __future__ import annotations

# --- Dataset identity ------------------------------------------------------
DATASET_CODE = "gov_10a_taxag"
DATASET_DOI = "10.2908/gov_10a_taxag"
DATASET_TITLE = "Main national accounts tax aggregates"

# --- Core analytical choices (validated in Phase 1, see README) ------------
# Sector S13_S212 (general government + EU institutions) is the one that
# reproduces the official Eurostat headline figures (FR 2024 = 45.3 %,
# EU 2023 = 39.9 %). We keep it fixed for every country and never mix it with
# S13 alone.
SECTOR_MAIN = "S13_S212"

# Subsectors for the "who collects?" section.
SUBSECTORS = {
    "S1311": "Central government",
    "S1313": "Local government",
    "S1314": "Social security funds",
}

# Total tax burden (taxes + net social contributions, minus uncollectable):
# this is the "tax-to-GDP ratio" headline indicator.
NA_TOTAL = "D2_D5_D91_D61_M_D995"
# Taxes only (no social contributions) -- used for the "taxes alone" comparison.
NA_TAXES_ONLY = "D2_D5_D91"

# --- Reference unit --------------------------------------------------------
UNIT_PC_GDP = "PC_GDP"
UNIT_MIO = "MIO_EUR"

# --- Category grouping (4 buckets a citizen can reason about) --------------
# Each bucket maps to a single Eurostat na_item code. D995 (amounts assessed
# but unlikely to be collected) is subtracted from the total, not shown as a
# category. The four categories + the D995 correction sum to NA_TOTAL
# (checked in tests/test_prep.py).
CATEGORY_CODES = {
    "D2": "Taxes on production & imports",
    "D5": "Current taxes on income & wealth",
    "D91": "Capital taxes",
    "D61": "Net social contributions",
}
CATEGORY_ORDER = [
    "Taxes on production & imports",
    "Current taxes on income & wealth",
    "Capital taxes",
    "Net social contributions",
]
NA_UNCOLLECTABLE = "D995"  # subtracted to reconcile the sum with the total

# na_item codes we pull from Eurostat (keeps the snapshot small).
NA_ITEMS_USED = [NA_TOTAL, NA_TAXES_ONLY, *CATEGORY_CODES, NA_UNCOLLECTABLE]

# --- Geography -------------------------------------------------------------
EU_AGGREGATE = "EU27_2020"  # stable 27-member definition over the whole series
EU_LABEL = "EU27"

# The 27 EU member states (Eurostat geo codes; note EL = Greece).
EU27_MEMBERS = [
    "BE", "BG", "CZ", "DK", "DE", "EE", "IE", "EL", "ES", "FR",
    "HR", "IT", "CY", "LV", "LT", "LU", "HU", "MT", "NL", "AT",
    "PL", "PT", "RO", "SI", "SK", "FI", "SE",
]
NON_EU = ["IS", "NO", "CH"]  # shown only when the user opts in

# Eurostat geo code -> ISO-3166 alpha-3 (for Plotly choropleth).
# The single irregular case is EL -> GRC (Eurostat uses EL for Greece).
EUROSTAT_TO_ISO3 = {
    "BE": "BEL", "BG": "BGR", "CZ": "CZE", "DK": "DNK", "DE": "DEU",
    "EE": "EST", "IE": "IRL", "EL": "GRC", "ES": "ESP", "FR": "FRA",
    "HR": "HRV", "IT": "ITA", "CY": "CYP", "LV": "LVA", "LT": "LTU",
    "LU": "LUX", "HU": "HUN", "MT": "MLT", "NL": "NLD", "AT": "AUT",
    "PL": "POL", "PT": "PRT", "RO": "ROU", "SI": "SVN", "SK": "SVK",
    "FI": "FIN", "SE": "SWE", "IS": "ISL", "NO": "NOR", "CH": "CHE",
}

# Human-readable country names.
COUNTRY_NAMES = {
    "BE": "Belgium", "BG": "Bulgaria", "CZ": "Czechia", "DK": "Denmark",
    "DE": "Germany", "EE": "Estonia", "IE": "Ireland", "EL": "Greece",
    "ES": "Spain", "FR": "France", "HR": "Croatia", "IT": "Italy",
    "CY": "Cyprus", "LV": "Latvia", "LT": "Lithuania", "LU": "Luxembourg",
    "HU": "Hungary", "MT": "Malta", "NL": "Netherlands", "AT": "Austria",
    "PL": "Poland", "PT": "Portugal", "RO": "Romania", "SI": "Slovenia",
    "SK": "Slovakia", "FI": "Finland", "SE": "Sweden",
    "IS": "Iceland", "NO": "Norway", "CH": "Switzerland",
    EU_AGGREGATE: "EU27",
}

FOCAL_DEFAULT = "FR"
COMPARE_DEFAULT = ["FR", "DE", "IT", "ES", "SE"]

# --- Colours (colourblind-safe) --------------------------------------------
# Okabe-Ito qualitative palette for country lines; information is never carried
# by colour alone (direct labels + reference lines everywhere).
OKABE_ITO = [
    "#0072B2", "#E69F00", "#009E73", "#D55E00",
    "#CC79A7", "#56B4E9", "#F0E442", "#000000",
]
COLOR_FOCAL = "#D55E00"   # France / focal country: warm, high-contrast
COLOR_EU = "#0072B2"      # EU reference: blue
COLOR_OTHER = "#999999"   # de-emphasised comparison countries

# Diverging colours for the category grouping (stable across the app).
CATEGORY_COLORS = {
    "Taxes on production & imports": "#0072B2",
    "Current taxes on income & wealth": "#E69F00",
    "Capital taxes": "#CC79A7",
    "Net social contributions": "#009E73",
}

# Crisis bands annotated on time series (denominator effect, see README).
CRISIS_EVENTS = [
    (2008, 2009, "Financial crisis"),
    (2020, 2020, "COVID-19"),
]

# Last fully complete year (2025 is partial: 22/34 geographies as of snapshot).
LAST_COMPLETE_YEAR = 2024
