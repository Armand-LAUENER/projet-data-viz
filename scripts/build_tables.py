"""Build the aggregated Parquet tables from the raw snapshot, then validate.

raw CSVs (data/raw/) -> aggregated tables (data/processed/). Also reproduces the
ONISR headline figure as a sanity check (killed in metropolitan France, 2024).

Run:  python scripts/build_tables.py   (or: make tables)
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import (
    aggregate,
    prep,
)
from utils import constants as C


def validate() -> None:
    usr = prep.build_usager_level(C.LAST_YEAR)
    killed_metro = prep.killed_count(usr, metro_only=True)
    killed_all = prep.killed_count(usr, metro_only=False)
    print(f"Validation {C.LAST_YEAR}: killed metro = {killed_metro} "
          f"(ONISR ref 3193) | metro+overseas = {killed_all} (ref 3432)")


def _write_snapshot_meta() -> None:
    """Persist the snapshot date into processed/ so it ships with the app."""
    import json
    manifest = C.RAW_DIR / "MANIFEST.json"
    date = "n/a"
    if manifest.exists():
        date = json.loads(manifest.read_text()).get("_downloaded", "n/a")
    (C.PROCESSED_DIR / "snapshot.txt").write_text(date + "\n")


def main() -> None:
    print("Building aggregated tables...")
    aggregate.write_all()
    _write_snapshot_meta()
    validate()
    total = sum(p.stat().st_size for p in C.PROCESSED_DIR.glob("*.parquet"))
    print(f"processed/ total size: {total / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
