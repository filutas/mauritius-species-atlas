import glob

import geopandas as gpd
import pandas as pd

files = glob.glob("data/raw/wdpa/**/*polygons.shp", recursive=True)
everything = pd.concat([gpd.read_file(f) for f in files], ignore_index=True)
everything = gpd.GeoDataFrame(everything)
kept = gpd.read_file("data/processed/protected_areas.gpkg")

dropped = everything[~everything["SITE_ID"].isin(kept["SITE_ID"])].copy()
point = dropped.geometry.representative_point()
dropped["lon"] = point.x.round(2)
dropped["lat"] = point.y.round(2)

cols = ["SITE_ID", "NAME_ENG", "DESIG_ENG", "REALM", "GIS_AREA", "lon", "lat"]
print(len(dropped), "polygons are not in the final set of", len(kept))
print(dropped[cols].sort_values(["REALM", "NAME_ENG"]).to_string(index=False))
