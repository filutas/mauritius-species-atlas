from pathlib import Path

import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
import yaml
from matplotlib.patches import Patch

matplotlib.use("Agg")

FIG = Path("outputs/figures")
COLORS = {"bird": "tab:blue", "mammal": "tab:orange", "reptile": "tab:green"}
TREE_COVER = 10


def figure_records_per_species():
    rec = pd.read_csv("outputs/01_records_per_species.csv").sort_values("records")
    colors = [COLORS.get(g, "grey") for g in rec["taxon_group"]]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(rec["common_name"], rec["records"], color=colors)
    for y, n in enumerate(rec["records"]):
        ax.text(n, y, f" {n}", va="center", fontsize=8)
    ax.margins(x=0.1)
    handles = [Patch(color=COLORS.get(g, "grey"), label=g) for g in rec["taxon_group"].unique()]
    ax.legend(handles=handles, loc="lower right")
    ax.set_xlabel("Open records in Mauritius, 2000 to 2025 (after cleaning)")
    ax.set_title("How much open data exists for each species")
    fig.tight_layout()
    fig.savefig(FIG / "fig1_records_per_species.png", dpi=150)
    plt.close(fig)


def figure_protected_share():
    sp = pd.read_csv("outputs/02_protected_share.csv")
    sp = sp.sort_values("pct_in_protected_area")
    lc = pd.read_csv("outputs/landcover_protected_share.csv")
    tree = lc.loc[lc["landcover"] == "Tree cover", "pct_protected"].iloc[0]
    land = lc.loc[lc["landcover"] == "All land", "pct_protected"].iloc[0]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(sp["common_name"], sp["pct_in_protected_area"], color="tab:blue")
    for y, v in enumerate(sp["pct_in_protected_area"]):
        ax.text(v, y, f" {v:.0f}%", va="center", fontsize=8)
    ax.axvline(
        tree,
        color="black",
        linestyle="--",
        label=f"Island tree cover that is protected ({tree:.1f}%)",
    )
    ax.axvline(
        land,
        color="grey",
        linestyle=":",
        label=f"All island land that is protected ({land:.1f}%)",
    )
    ax.set_xlim(0, 100)
    ax.set_xlabel("Share of records inside protected areas (%)")
    ax.set_title("Where records fall relative to protected areas")
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "fig2_protected_share.png", dpi=150)
    plt.close(fig)


def figure_richness_map(cfg):
    b, size = cfg["bbox"], cfg["grid_deg"]
    nx = round((b["east"] - b["west"]) / size) + 1
    ny = round((b["north"] - b["south"]) / size) + 1
    grid = np.full((ny, nx), np.nan)
    for r in pd.read_csv("outputs/04_grid_richness.csv").itertuples():
        if r.cell_y < ny and r.cell_x < nx:
            grid[r.cell_y, r.cell_x] = r.species_richness

    with rasterio.open("data/raw/worldcover_mauritius.tif") as src:
        lcm = src.read(1)[::20, ::20]
        bd = src.bounds
    tree_layer = np.where(lcm == TREE_COVER, 1.0, np.nan)

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.imshow(
        tree_layer,
        extent=[bd.left, bd.right, bd.bottom, bd.top],
        cmap="Greens",
        vmin=0,
        vmax=2,
        alpha=0.6,
    )
    im = ax.imshow(
        grid,
        origin="lower",
        extent=[b["west"], b["west"] + nx * size, b["south"], b["south"] + ny * size],
        cmap="viridis",
        alpha=0.85,
    )
    pa = gpd.read_file("data/processed/protected_areas.gpkg")
    pa.boundary.plot(ax=ax, color="black", linewidth=0.6)
    ax.set_xlim(b["west"], b["east"])
    ax.set_ylim(b["south"], b["north"])
    ax.set_aspect(1 / np.cos(np.radians(20.2)))
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Recorded species richness per 2 km cell (cells with 3 or more records)")
    plt.colorbar(im, ax=ax, shrink=0.7, label="Species recorded")
    fig.tight_layout()
    fig.savefig(FIG / "fig3_richness_map.png", dpi=150)
    plt.close(fig)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    with open("config/config.yml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    figure_records_per_species()
    figure_protected_share()
    figure_richness_map(cfg)
    print("figures saved in", FIG)


if __name__ == "__main__":
    main()
