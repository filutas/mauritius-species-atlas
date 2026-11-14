from pathlib import Path

import numpy as np
import rasterio
import yaml
from rasterio.windows import Window, from_bounds

URL = (
    "https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/"
    "ESA_WorldCover_10m_2021_v200_S21E057_Map.tif"
)
OUT = Path("data/raw/worldcover_mauritius.tif")
NO_DATA = 0
WATER = 80

CLASSES = {
    10: "Tree cover",
    20: "Shrubland",
    30: "Grassland",
    40: "Cropland",
    50: "Built-up",
    60: "Bare or sparse",
    70: "Snow and ice",
    80: "Water",
    90: "Herbaceous wetland",
    95: "Mangroves",
    100: "Moss and lichen",
}


def clip_worldcover(bbox):
    if OUT.exists():
        return OUT
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(URL) as src:
        w = from_bounds(
            bbox["west"], bbox["south"], bbox["east"], bbox["north"], src.transform
        )
        w = Window(round(w.col_off), round(w.row_off), round(w.width), round(w.height))
        arr = src.read(1, window=w)
        profile = {
            "driver": "GTiff",
            "height": arr.shape[0],
            "width": arr.shape[1],
            "count": 1,
            "dtype": arr.dtype,
            "crs": src.crs,
            "transform": src.window_transform(w),
            "compress": "deflate",
            "nodata": 0,
        }
    with rasterio.open(OUT, "w", **profile) as dst:
        dst.write(arr, 1)
    return OUT


def sample_classes(path, lons, lats):
    with rasterio.open(path) as src:
        return np.array([v[0] for v in src.sample(zip(lons, lats))])


def far_from_land(path, lons, lats, radius_m):
    """For each point, True if there is no land pixel within radius_m metres.

    Land is any pixel that is neither water (80) nor no data (0).
    """
    far = []
    with rasterio.open(path) as src:
        height_m = abs(src.transform.e) * 110_570
        for lon, lat in zip(lons, lats):
            width_m = abs(src.transform.a) * 111_320 * np.cos(np.radians(lat))
            rows_r = int(np.ceil(radius_m / height_m))
            cols_r = int(np.ceil(radius_m / width_m))
            row, col = src.index(lon, lat)
            r0, r1 = max(row - rows_r, 0), min(row + rows_r + 1, src.height)
            c0, c1 = max(col - cols_r, 0), min(col + cols_r + 1, src.width)
            block = src.read(1, window=Window(c0, r0, c1 - c0, r1 - r0))
            dy = (np.arange(r0, r1) - row)[:, None] * height_m
            dx = (np.arange(c0, c1) - col)[None, :] * width_m
            inside = dx**2 + dy**2 <= radius_m**2
            land = (block != WATER) & (block != NO_DATA)
            far.append(not np.any(land & inside))
    return np.array(far, dtype=bool)


if __name__ == "__main__":
    with open("config/config.yml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    path = clip_worldcover(cfg["bbox"])
    with rasterio.open(path) as src:
        arr = src.read(1)
        print("file:", path, "| size (rows, cols):", arr.shape)
        print("bounds:", src.bounds)
    codes, counts = np.unique(arr, return_counts=True)
    for code, n in zip(codes, counts):
        print(f"{int(code):>4} {CLASSES.get(int(code), '?'):<20} {100 * n / arr.size:5.1f}%")
