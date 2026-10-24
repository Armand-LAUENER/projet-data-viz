"""Download the BAAC raw CSVs from data.gouv.fr into data/raw/ + a MANIFEST.

Why a dated snapshot (not a live read at app start): ONISR revises and republishes
the open data; a frozen snapshot keeps the demo and the grading run identical, and
the app never depends on the network.

Resource titles are inconsistent across years (e.g. 'Caract_2024.csv',
'caract-2023.csv', and the typo 'carcteristiques-2021.csv'); we resolve each of
the four tables x six years from the dataset's resource list.

Run:  python scripts/download_data.py   (or: make data)
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import constants as C

API = f"https://www.data.gouv.fr/api/1/datasets/{C.DATASET_ID}/"


def _table_of(title: str) -> str | None:
    t = title.lower()
    if "immatricul" in t:
        return None
    if re.match(r"(caract|carcteristiques)", t):   # handles the 2021/2022 typo
        return "caracteristiques"
    for name in ("lieux", "usagers", "vehicules"):
        if t.startswith(name[:6]):
            return name
    return None


def resolve_urls() -> dict[int, dict[str, str]]:
    """Map each (year, table) in the perimeter to its download URL."""
    meta = json.loads(urllib.request.urlopen(API, timeout=60).read())
    sel: dict[int, dict[str, str]] = {y: {} for y in C.YEARS}
    for r in meta.get("resources", []):
        title = r.get("title") or ""
        table = _table_of(title)
        m = re.search(r"20(19|20|21|22|23|24)", title)
        if table and m and int(m.group(0)) in sel:
            sel[int(m.group(0))][table] = r["url"]
    missing = {y: [t for t in C.TABLES if t not in sel[y]] for y in C.YEARS}
    missing = {y: v for y, v in missing.items() if v}
    if missing:
        raise RuntimeError(f"Could not resolve every file: {missing}")
    return sel


def main() -> None:
    C.RAW_DIR.mkdir(parents=True, exist_ok=True)
    sel = resolve_urls()
    manifest: dict[str, dict] = {}
    t0 = time.time()
    for year, tables in sel.items():
        for table, url in tables.items():
            data = urllib.request.urlopen(url, timeout=180).read()
            fn = f"{table}_{year}.csv"
            (C.RAW_DIR / fn).write_bytes(data)
            manifest[fn] = {"url": url, "bytes": len(data),
                            "sha256": hashlib.sha256(data).hexdigest()}
            print(f"  {fn:28} {len(data) / 1e6:6.2f} MB")
    manifest["_downloaded"] = time.strftime("%Y-%m-%d")
    manifest["_dataset"] = C.DATASET_URL
    (C.RAW_DIR / "MANIFEST.json").write_text(json.dumps(manifest, indent=2))
    print(f"Done: {len(manifest) - 2} files in {time.time() - t0:.0f}s "
          f"-> {C.RAW_DIR}")


if __name__ == "__main__":
    main()
