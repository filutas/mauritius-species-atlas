import glob
from pathlib import Path

import geopandas as gpd
import pandas as pd
import yaml

OK_STATUS = ["Designated", "Established", "Inscribed"]
LAND_REALMS = ["terrestrial", "coastal"]
# The merged WDPA/WDOECM release holds protected areas (PA) and other
# effective area-based conservation measures (OECM). We keep PA only.
KEEP_SITE_TYPES = ["PA"]
# Coastal polygons that exist to protect fish and marine habitat. They say
# nothing about land habitat, so they are left out of the land analysis.
EXCLUDE_DESIGNATIONS = ["Fishing Reserve", "Marine Park"]
# Small islet reserves are sometimes labelled Marine in WDPA although they are
# land habitat. These designations are kept whatever the realm label says.
KEEP_ANY_REALM = ["Nature Reserve"]
PATTERN = "data/raw/wdpa/**/*polygons.shp"


def _check(gdf, step):
    if len(gdf) == 0:
        raise ValueError(f"No polygons left after: {step}. Check the printed values.")


def _is_land(gdf):
    # Newer releases use REALM (Terrestrial, Coastal, Marine),
    # older releases use MARINE (0 terrestrial, 1 coastal, 2 marine).
    if "REALM" in gdf.columns:
        realm = gdf["REALM"].astype(str).str.strip().str.lower()
        return realm.isin(LAND_REALMS)
    marine = pd.to_numeric(gdf["MARINE"], errors="coerce")
    return marine.isin([0, 1])


def load_protected(bbox):
    files = glob.glob(PATTERN, recursive=True)
    if not files:
        raise FileNotFoundError(
            "No WDPA polygon shapefile found in data/raw/wdpa (see step 9)."
        )
    print("shapefiles found:", len(files))
    gdf = gpd.GeoDataFrame(
        pd.concat([gpd.read_file(f) for f in files], ignore_index=True)
    )
    if "SITE_PID" in gdf.columns:
        gdf = gdf.drop_duplicates(subset="SITE_PID")
    print("polygons before filtering:", len(gdf))

    for col in ["SITE_TYPE", "STATUS", "REALM", "MARINE"]:
        if col in gdf.columns:
            counts = gdf[col].value_counts(dropna=False).to_string()
            print(f"\n{col}:\n{counts}")

    if "SITE_TYPE" in gdf.columns:
        gdf = gdf[gdf["SITE_TYPE"].isin(KEEP_SITE_TYPES)]
        _check(gdf, "site type")
    gdf = gdf[gdf["STATUS"].isin(OK_STATUS)]
    _check(gdf, "status")
    rescued = ~_is_land(gdf) & gdf["DESIG_ENG"].isin(KEEP_ANY_REALM)
    if rescued.any():
        print("\nkept despite a Marine realm label:")
        shown = ["SITE_ID", "NAME_ENG", "DESIG_ENG", "REALM", "GIS_AREA"]
        print(gdf.loc[rescued, shown].to_string(index=False))
    gdf = gdf[_is_land(gdf) | rescued]
    _check(gdf, "realm (terrestrial and coastal only)")
    n_land_realm = len(gdf)
    gdf = gdf[~gdf["DESIG_ENG"].isin(EXCLUDE_DESIGNATIONS)]
    _check(gdf, "designation (marine-purpose areas excluded)")
    print(f"\nmarine-purpose areas excluded: {n_land_realm - len(gdf)}")
    gdf = gdf.cx[bbox["west"] : bbox["east"], bbox["south"] : bbox["north"]].copy()
    _check(gdf, "bounding box")
    gdf["geometry"] = gdf.geometry.buffer(0)
    return gdf


if __name__ == "__main__":
    with open("config/config.yml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    pa = load_protected(cfg["bbox"])
    candidates = [
        "SITE_ID",
        "WDPAID",
        "NAME_ENG",
        "NAME",
        "DESIG_ENG",
        "IUCN_CAT",
        "STATUS",
        "STATUS_YR",
        "REALM",
        "MARINE",
        "SITE_TYPE",
        "GIS_AREA",
    ]
    show = [c for c in candidates if c in pa.columns]
    print(f"\n{len(pa)} polygons after filtering")
    print(pa[show].to_string(index=False))
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    pa.to_file("data/processed/protected_areas.gpkg", driver="GPKG")
