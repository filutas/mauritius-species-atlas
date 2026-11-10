import argparse
from pathlib import Path

import pandas as pd
import yaml

from src import gbif


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count-only", action="store_true")
    args = parser.parse_args()

    with open("config/config.yml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    sp = pd.read_csv("config/species.csv")

    rows = []
    for name in sp["scientific_name"]:
        m = gbif.match_species(name)
        key = m["speciesKey"]
        n = 0
        if key:
            n = gbif.count_records(
                key, cfg["country"], cfg["year_min"], cfg["year_max"]
            )
        m["n_records"] = n
        rows.append(m)

    res = sp.merge(pd.DataFrame(rows), left_on="scientific_name", right_on="query")

    Path("data/processed").mkdir(parents=True, exist_ok=True)
    res.to_csv("data/processed/species_resolved.csv", index=False)

    cols = ["scientific_name", "matched", "status", "matchType", "speciesKey", "n_records"]
    print(res[cols].to_string(index=False))

    if args.count_only:
        return

    for key in res.loc[res["n_records"] > 0, "speciesKey"].astype(int):
        df = gbif.fetch_species(key, cfg["country"], cfg["year_min"], cfg["year_max"])
        print("downloaded", key, len(df))


if __name__ == "__main__":
    main()
