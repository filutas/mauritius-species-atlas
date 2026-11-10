import numpy as np
import pandas as pd

EXCLUDED_BASIS = ["FOSSIL_SPECIMEN", "LIVING_SPECIMEN"]
ACCEPTED_STATUS = ["PRESENT", "DETECTED"]
DEDUP_COLUMNS = [
    "speciesKey",
    "decimalLatitude",
    "decimalLongitude",
    "eventDate",
    "datasetKey",
]


def clean_records(df, cfg):
    b = cfg["bbox"]
    d = df.copy()
    log = [{"rule": "start", "removed": 0, "remaining": len(d)}]

    def step(name, keep):
        nonlocal d
        before = len(d)
        d = d[keep(d)]
        log.append({"rule": name, "removed": before - len(d), "remaining": len(d)})

    step(
        "occurrence status is present or detected",
        lambda x: x["occurrenceStatus"]
        .fillna("PRESENT")
        .str.upper()
        .isin(ACCEPTED_STATUS),
    )
    step(
        "no fossil or living (captive) specimens",
        lambda x: ~x["basisOfRecord"].isin(EXCLUDED_BASIS),
    )
    step(
        "year within study period",
        lambda x: x["year"].between(cfg["year_min"], cfg["year_max"]),
    )
    step(
        "inside island bounding box",
        lambda x: x["decimalLongitude"].between(b["west"], b["east"])
        & x["decimalLatitude"].between(b["south"], b["north"]),
    )
    step(
        "coordinate uncertainty within limit",
        lambda x: x["coordinateUncertaintyInMeters"].isna()
        | (x["coordinateUncertaintyInMeters"] <= cfg["max_uncertainty_m"]),
    )

    before = len(d)
    d = d.drop_duplicates(subset=DEDUP_COLUMNS)
    log.append(
        {
            "rule": "exact duplicates (species, place, date, dataset)",
            "removed": before - len(d),
            "remaining": len(d),
        }
    )
    return d, pd.DataFrame(log)


def add_grid(df, cfg):
    b, size = cfg["bbox"], cfg["grid_deg"]
    d = df.copy()
    d["cell_x"] = np.floor((d["lon"] - b["west"]) / size).astype(int)
    d["cell_y"] = np.floor((d["lat"] - b["south"]) / size).astype(int)
    d["cell_id"] = d["cell_x"].astype(str) + "_" + d["cell_y"].astype(str)
    return d