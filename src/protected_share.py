from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio import features

from src.landcover import CLASSES

NO_DATA = 0
WATER = 80


def main():
    with rasterio.open("data/raw/worldcover_mauritius.tif") as src:
        lc = src.read(1)
        transform, crs = src.transform, src.crs

    pa = gpd.read_file("data/processed/protected_areas.gpkg").to_crs(crs)
    mask = features.rasterize(
        ((g, 1) for g in pa.geometry),
        out_shape=lc.shape,
        transform=transform,
        fill=0,
        dtype="uint8",
    ).astype(bool)

    # Pixel area in km2 for each row: pixels get narrower away from the equator.
    lat = transform.f + transform.e * (np.arange(lc.shape[0]) + 0.5)
    width_km = abs(transform.a) * 111.32 * np.cos(np.radians(lat))
    height_km = abs(transform.e) * 110.57
    row_km2 = width_km * height_km

    def area_km2(sel):
        # Count selected pixels per row, then weight each row by its pixel area.
        return float((sel.sum(axis=1) * row_km2).sum())

    rows = []
    for code, name in CLASSES.items():
        sel = lc == code
        total = area_km2(sel)
        if total == 0:
            continue
        prot = area_km2(sel & mask)
        rows.append(
            {
                "landcover": name,
                "area_km2": round(total, 1),
                "protected_km2": round(prot, 1),
                "pct_protected": round(100 * prot / total, 1),
            }
        )

    land = (lc != WATER) & (lc != NO_DATA)
    land_total = area_km2(land)
    land_prot = area_km2(land & mask)
    rows.append(
        {
            "landcover": "All land",
            "area_km2": round(land_total, 1),
            "protected_km2": round(land_prot, 1),
            "pct_protected": round(100 * land_prot / land_total, 1),
        }
    )

    out = pd.DataFrame(rows)
    Path("outputs").mkdir(exist_ok=True)
    out.to_csv("outputs/landcover_protected_share.csv", index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
