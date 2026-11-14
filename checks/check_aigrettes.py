import geopandas as gpd
import pandas as pd

SITE_ID = "5054"
CELL_X, CELL_Y = 26, 8
UTM = "EPSG:32740"  # UTM zone 40S, in metres, covers Mauritius

pa = gpd.read_file("data/processed/protected_areas.gpkg")
poly = pa.loc[pa["SITE_ID"].astype(str) == SITE_ID, "geometry"].to_crs(UTM).iloc[0]

occ = pd.read_parquet(
    "data/processed/occurrences.parquet",
    columns=["species_key", "lon", "lat", "cell_x", "cell_y"],
)
occ = occ[(occ["cell_x"] == CELL_X) & (occ["cell_y"] == CELL_Y)]

points = gpd.GeoSeries(gpd.points_from_xy(occ["lon"], occ["lat"]), crs="EPSG:4326")
dist = points.to_crs(UTM).distance(poly)

labels = ["inside", "0-50 m", "50-100 m", "100-250 m", "250-500 m", "over 500 m"]
bins = pd.cut(dist, [-1, 0, 50, 100, 250, 500, 1e9], labels=labels)

print("records in the cell:", len(occ))
print("distance to the polygon:")
print(bins.value_counts().reindex(labels).to_string())
print("median distance (m):", round(float(dist.median())))
