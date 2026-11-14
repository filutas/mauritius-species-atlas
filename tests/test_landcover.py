import numpy as np
import rasterio
from affine import Affine

from src.landcover import far_from_land

PIXEL = 0.0000833  # degrees, about 9 m
WEST, NORTH = 57.2, -20.0


def make_raster(path):
    # All water, with a strip of land in the top 50 rows
    arr = np.full((300, 300), 80, dtype="uint8")
    arr[:50, :] = 10
    profile = {
        "driver": "GTiff",
        "height": 300,
        "width": 300,
        "count": 1,
        "dtype": "uint8",
        "crs": "EPSG:4326",
        "transform": Affine(PIXEL, 0, WEST, 0, -PIXEL, NORTH),
        "nodata": 0,
    }
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(arr, 1)


def point(row, col):
    return WEST + (col + 0.5) * PIXEL, NORTH - (row + 0.5) * PIXEL


def test_far_from_land_flags_only_distant_water(tmp_path):
    path = tmp_path / "wc.tif"
    make_raster(path)
    near = point(80, 150)  # about 270 m from the land strip
    far = point(250, 150)  # about 1.8 km from the land strip
    on_land = point(10, 150)
    lons = [near[0], far[0], on_land[0]]
    lats = [near[1], far[1], on_land[1]]
    result = far_from_land(path, lons, lats, 1000)
    assert result.tolist() == [False, True, False]
