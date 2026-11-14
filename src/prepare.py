from pathlib import Path

import pandas as pd
import yaml

from src.clean import add_grid, clean_records
from src.landcover import (
    CLASSES,
    WATER,
    clip_worldcover,
    far_from_land,
    sample_classes,
)

RENAME = {
    "gbifID": "gbif_id",
    "speciesKey": "species_key",
    "scientificName": "name_in_record",
    "decimalLatitude": "lat",
    "decimalLongitude": "lon",
    "coordinateUncertaintyInMeters": "uncertainty_m",
    "eventDate": "event_date",
    "basisOfRecord": "basis",
    "datasetKey": "dataset_key",
    "datasetName": "dataset_name",
    "establishmentMeans": "establishment",
}


def add_log_row(log, rule, before, after):
    row = pd.DataFrame([{"rule": rule, "removed": before - after, "remaining": after}])
    return pd.concat([log, row], ignore_index=True)


def main():
    with open("config/config.yml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    min_records = cfg["min_records_per_species"]
    water_buffer_m = cfg.get("water_buffer_m", 1000)

    res = pd.read_csv("data/processed/species_resolved.csv")
    res = res[res["n_records"] > 0].copy()
    res["speciesKey"] = res["speciesKey"].astype(int)

    raw = pd.concat(
        [pd.read_parquet(f"data/raw/gbif_{k}.parquet") for k in res["speciesKey"]],
        ignore_index=True,
    )
    raw = raw.dropna(subset=["speciesKey", "decimalLatitude", "decimalLongitude"])
    raw["speciesKey"] = raw["speciesKey"].astype(int)
    downloaded = raw["speciesKey"].value_counts()

    d, log = clean_records(raw, cfg)
    d = d.rename(columns=RENAME)

    path = clip_worldcover(cfg["bbox"])
    d["landcover_code"] = sample_classes(path, d["lon"], d["lat"])
    d["landcover"] = d["landcover_code"].map(CLASSES).fillna("Unknown or no data")

    # The island box is a rectangle, so it keeps open sea. Records on water
    # with no land within water_buffer_m are misplaced points, not coastal ones.
    before = len(d)
    on_water = (d["landcover_code"] == WATER).to_numpy()
    far = pd.Series(False, index=d.index)
    far[on_water] = far_from_land(
        path, d.loc[on_water, "lon"], d.loc[on_water, "lat"], water_buffer_m
    )
    d = d[~far].copy()
    log = add_log_row(log, f"open water, no land within {water_buffer_m} m", before, len(d))

    # The 20-record rule is applied last, because cleaning can remove most
    # records of a species (for example blurred coordinates).
    counts = d["species_key"].value_counts()
    enough = counts[counts >= min_records].index
    before = len(d)
    d = d[d["species_key"].isin(enough)].copy()
    log = add_log_row(log, f"species with fewer than {min_records} records", before, len(d))

    # Names looked up by hand on gbif.org for datasets that have no name in GBIF
    names_file = Path("config/datasets.csv")
    if names_file.exists():
        lookup = pd.read_csv(names_file).dropna(subset=["dataset_name"])
        mapping = dict(zip(lookup["dataset_key"], lookup["dataset_name"]))
        names = d["dataset_name"].astype(object)
        mapped = d["dataset_key"].map(mapping).astype(object)
        d["dataset_name"] = names.where(names.notna(), mapped)
    d["dataset_name"] = d["dataset_name"].fillna("dataset " + d["dataset_key"].str[:8])
    d = add_grid(d, cfg)

    Path("outputs").mkdir(exist_ok=True)
    d.to_parquet("data/processed/occurrences.parquet")
    log.to_csv("outputs/cleaning_log.csv", index=False)

    sp = res.rename(
        columns={
            "speciesKey": "species_key",
            "group": "taxon_group",
            "n_records": "n_records_gbif",
        }
    )
    # Records actually downloaded (the live GBIF count can grow after the download)
    sp["n_records_gbif"] = sp["species_key"].map(downloaded).fillna(0).astype(int)
    sp["n_records_clean"] = sp["species_key"].map(counts).fillna(0).astype(int)
    sp["analysed"] = sp["species_key"].isin(enough)
    cols = [
        "species_key",
        "scientific_name",
        "common_name",
        "taxon_group",
        "iucn_category",
        "n_records_gbif",
        "n_records_clean",
        "analysed",
    ]
    sp[cols].to_csv("data/processed/species_table.csv", index=False)
    sp[cols].to_csv("outputs/species_status.csv", index=False)

    print(log.to_string(index=False))
    print("\nfinal records:", len(d), "| species:", d["species_key"].nunique())
    print("\nrecords per species after cleaning:")
    shown = ["common_name", "n_records_gbif", "n_records_clean", "analysed"]
    print(sp[shown].to_string(index=False))
    print("\nland cover of records:")
    print(d["landcover"].value_counts())
    n_sea = d["landcover"].isin(["Water", "Unknown or no data"]).sum()
    print(f"\nrecords on water or no data: {n_sea} ({100 * n_sea / len(d):.1f}%)")
    print("\nrecords per dataset:")
    print(d["dataset_name"].value_counts().head(8))


if __name__ == "__main__":
    main()
