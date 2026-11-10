import glob
 
import pandas as pd
 
LIMIT_M = 1000
BINS = [-1, 100, 1000, 5000, float("inf")]
LABELS = ["<=100 m", "100-1000 m", "1000-5000 m", ">5000 m"]
 
frames = [pd.read_parquet(f) for f in glob.glob("data/raw/gbif_*.parquet")]
df = pd.concat(frames, ignore_index=True)
df["datasetName"] = df["datasetName"].fillna("unknown")
 
unc = df["coordinateUncertaintyInMeters"]
df["unc_class"] = pd.cut(unc, bins=BINS, labels=LABELS)
df["unc_class"] = df["unc_class"].cat.add_categories("not stated").fillna("not stated")
 
print("Records per species and uncertainty class")
by_species = df.groupby(["scientificName", "unc_class"], observed=True).size()
print(by_species.unstack(fill_value=0).to_string())
 
kept = unc.isna() | (unc <= LIMIT_M)
summary = kept.groupby(df["scientificName"]).agg(kept="sum", total="size")
summary["pct_kept"] = (100 * summary["kept"] / summary["total"]).round(1)
print(f"\nRecords kept by the {LIMIT_M} m rule (stated or not stated)")
print(summary.to_string())
 
print("\nTop datasets and their uncertainty classes")
by_dataset = df.groupby(["datasetName", "unc_class"], observed=True).size()
table = by_dataset.unstack(fill_value=0)
table["total"] = table.sum(axis=1)
print(table.sort_values("total", ascending=False).head(10).to_string())