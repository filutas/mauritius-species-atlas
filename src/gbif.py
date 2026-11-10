import time
from pathlib import Path

import pandas as pd
import requests

API = "https://api.gbif.org/v1"
RAW = Path("data/raw")

FIELDS = [
    "gbifID",
    "speciesKey",
    "scientificName",
    "decimalLatitude",
    "decimalLongitude",
    "coordinateUncertaintyInMeters",
    "year",
    "month",
    "eventDate",
    "basisOfRecord",
    "datasetKey",
    "datasetName",
    "occurrenceStatus",
    "establishmentMeans",
    "issues",
]


def _get(url, params):
    for attempt in range(3):
        try:
            r = requests.get(url, params=params, timeout=60)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as err:
            print("retry", attempt + 1, err)
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"GBIF request failed: {url}")


def match_species(name):
    j = _get(f"{API}/species/match", {"name": name, "kingdom": "Animalia"})
    return {
        "query": name,
        "matched": j.get("scientificName"),
        "status": j.get("status"),
        "matchType": j.get("matchType"),
        "speciesKey": j.get("speciesKey"),
    }


def _query(key, country, year_min, year_max):
    return {
        "taxonKey": key,
        "country": country,
        "hasCoordinate": "true",
        "hasGeospatialIssue": "false",
        "year": f"{year_min},{year_max}",
    }


def count_records(key, country, year_min, year_max):
    params = _query(key, country, year_min, year_max)
    params["limit"] = 0
    return _get(f"{API}/occurrence/search", params)["count"]


def fetch_species(key, country, year_min, year_max):
    RAW.mkdir(parents=True, exist_ok=True)
    out = RAW / f"gbif_{key}.parquet"
    if out.exists():
        return pd.read_parquet(out)

    rows, offset = [], 0
    while True:
        params = _query(key, country, year_min, year_max)
        params.update({"limit": 300, "offset": offset})
        j = _get(f"{API}/occurrence/search", params)
        rows += j["results"]
        if j["endOfRecords"]:
            break
        offset += 300
        time.sleep(0.5)

    df = pd.DataFrame(rows).reindex(columns=FIELDS)
    df["issues"] = df["issues"].apply(
        lambda x: ",".join(x) if isinstance(x, list) else ""
    )
    df.to_parquet(out)
    return df
