import glob

import pandas as pd
import yaml

with open("config/config.yml", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)
b = cfg["bbox"]

files = glob.glob("data/raw/gbif_*.parquet")
df = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
df = df.dropna(subset=["speciesKey", "decimalLatitude", "decimalLongitude"])
df["speciesKey"] = df["speciesKey"].astype(int)
df["datasetName"] = df["datasetName"].fillna("dataset " + df["datasetKey"].str[:8])

sp = pd.read_csv("data/processed/species_table.csv")
names = dict(zip(sp["species_key"], sp["common_name"]))
df["species"] = df["speciesKey"].map(names)

lon, lat = df["decimalLongitude"], df["decimalLatitude"]
inside = lon.between(b["west"], b["east"]) & lat.between(b["south"], b["north"])
unc = df["coordinateUncertaintyInMeters"]
precise = unc.isna() | (unc <= cfg["max_uncertainty_m"])

# Same order as the cleaning rules: box, uncertainty, duplicates
df["fate"] = "kept"
df.loc[~inside, "fate"] = "outside box"
df.loc[inside & ~precise, "fate"] = "imprecise"
alive = df[df["fate"] == "kept"]
dup_cols = ["speciesKey", "decimalLatitude", "decimalLongitude", "eventDate", "datasetKey"]
dups = alive.duplicated(subset=dup_cols)
df.loc[dups[dups].index, "fate"] = "duplicate"

order = ["kept", "outside box", "imprecise", "duplicate"]

print("Fate of records per species")
by_species = pd.crosstab(df["species"], df["fate"], margins=True)
print(by_species[[c for c in order if c in by_species.columns] + ["All"]].to_string())

print("\nFate of records per dataset (top 8)")
by_dataset = pd.crosstab(df["datasetName"], df["fate"], margins=True)
by_dataset = by_dataset.sort_values("All", ascending=False).head(9)
print(by_dataset[[c for c in order if c in by_dataset.columns] + ["All"]].to_string())

print("\nWhere the outside-box records are (rounded to 0.5 degrees)")
out = df[df["fate"] == "outside box"]
rounded = pd.DataFrame(
    {
        "lat": (out["decimalLatitude"] * 2).round() / 2,
        "lon": (out["decimalLongitude"] * 2).round() / 2,
    }
)
print(rounded.value_counts().head(8).to_string())
