# mauritius-species-atlas

Open-data atlas of endemic animals of Mauritius: records, habitat and protected areas. Python, SQL (DuckDB) and GIS, with tests and CI.

**Status:** work in progress (release v1.0 planned). The pipeline up to the cleaned dataset is done. The database build, SQL results, figures and the findings on protection are still being added. See [`docs/PROJECT_PLAN.md`](docs/PROJECT_PLAN.md) for the plan, risks and current state.

This is a transparent, modest data analysis, not a scientific study.

## What it does

The project collects open occurrence records of endemic and threatened animals of Mauritius from GBIF, cleans them with documented rules, and links each record to land cover (ESA WorldCover 2021) and a 2 km grid. It then asks how many records exist, in which land cover they were made, and how many fall inside protected areas, compared with the share of the island's tree cover that is protected.

## Key findings so far

- Twelve candidate species were checked. Nine have enough records after cleaning (at least 20) and are analysed: eight birds and one gecko. The Mauritian flying fox, Telfair's skink and Guenther's day gecko are data-poor, because most of their open records have blurred or imprecise coordinates.
- Open data is very uneven: of 6,385 records downloaded, 4,644 remain after cleaning, and eBird supplies 82% of them. Eight GBIF datasets contribute in total.
- Intensive monitoring data is largely lost in cleaning: the SAFRING historical bird ringing records (2005 to 2009) fall from 799 records to 13, mostly because of duplicate records at the same place and date and coordinates outside the island.
- 89% of the cleaned records fall on tree cover. Tree cover covers a bit over half of the island's land in this layer, and it includes plantations and forest invaded by exotic plants, so it is not native forest.
- Protected share of records and of tree cover, and the hotspot cells: to be added.

## Quick start

Run everything from the project root.

```powershell
conda env create -f environment.yml
conda activate atlas-mauritius
python -m src.fetch_gbif
python -m src.prepare
# manual step: download the Mauritius WDPA shapefile into data/raw/wdpa/ (see below)
python -m src.protected
python -m src.build_db
python -m src.protected_share
python -m src.make_figures
python -m pytest -q
```

`protected_share` and `make_figures` are not implemented yet.

## Data and licences

| Source | Use | Licence and citation |
|--------|-----|----------------------|
| GBIF occurrence records | Species records, country MU, 2000 to 2025 | Records carry their own licences (CC0, CC BY, CC BY-NC). Cite GBIF.org, retrieved 2026-11-10, and the datasets below. |
| WDPA and WD-OECM (Protected Planet) | Protected area polygons, Nov 2026 release | UNEP-WCMC and IUCN, Protected Planet. Non-commercial use with attribution, no redistribution. Files are not in this repository: download them from Protected Planet. Check the current terms page. |
| ESA WorldCover 2021 v200 | 10 m land cover | CC BY 4.0, ESA WorldCover (Zanaga et al., 2022). |
| IUCN Red List | Categories typed by hand in `config/species.csv` | Cite the IUCN Red List and the date checked (to fill in). |

GBIF datasets in the cleaned data (4,644 records):

| Dataset | Publisher | Licence | Records |
|---------|-----------|---------|--------:|
| eBird | Cornell Lab of Ornithology | CC BY 4.0 | 3,802 |
| Observation.org Nature data from around the World | Observation.org | CC BY-NC 4.0 | 366 |
| iNaturalist research-grade observations | iNaturalist.org | CC BY-NC 4.0 (dataset level) | 255 |
| Birda - Global Observation Dataset | Birda | CC BY-NC 4.0 | 101 |
| Xeno-canto - Bird sounds from around the world | Vellinga W P, Planqué B | CC BY-NC 4.0 | 62 |
| NABU\|naturgucker | naturgucker.de | CC BY 4.0 | 23 |
| Macaulay Library Audio and Video Collection | Scholes III Ph.D.E | CC0 1.0 | 22 |
| SAFRING: Historical Bird Ringing Records (2005-2009) | Oschadleus D and Ranwashe F | CC BY 4.0 | 13 |

Four of these datasets are CC BY-NC (Observation.org, iNaturalist, Birda, Xeno-canto; 784 of the 4,644 records), and the protected area data are for non-commercial use. This project is therefore a non-commercial portfolio project, and all sources are credited. Results are aggregated, and raw records are not shared.

Raw data are never committed. The scripts download GBIF records and land cover; the WDPA download is the only manual step.

## Method

1. Resolve species names against the GBIF backbone and count records before downloading.
2. Download records per species and cache them.
3. Clean the records with the rules below and keep a log of what each rule removed.
4. Attach a 10 m land cover class and a 2 km grid cell to every record.
5. Load everything into DuckDB and answer the five questions with SQL files in `sql/`.
6. Compute how much tree cover lies inside protected areas with a raster calculation, and draw three figures.

Cleaning log (records removed per rule):

| Rule | Removed | Remaining |
|------|--------:|----------:|
| start | 0 | 6,385 |
| occurrence status is present or detected | 0 | 6,385 |
| no fossil or living (captive) specimens | 0 | 6,385 |
| year within study period | 0 | 6,385 |
| inside island bounding box | 466 | 5,919 |
| coordinate uncertainty within limit (1,000 m) | 599 | 5,320 |
| exact duplicates (species, place, date, dataset) | 657 | 4,663 |
| species with fewer than 20 records | 19 | 4,644 |

Records with no stated coordinate uncertainty are kept. All records removed by the uncertainty rule come from iNaturalist.

## Responsible data use

- Locations of threatened species can be misused (poaching, disturbance). No exact coordinates are published. Outputs are species-level summaries and aggregated 2 km cells with at least 3 records.
- Blurred coordinates (for example iNaturalist records of threatened species) are removed, never recovered.
- Raw GBIF downloads, WDPA files and the DuckDB database are not committed.

## Limitations

- Records are where observers went, not where animals are. A few datasets dominate, mostly eBird. Results describe recorded locations, not distribution.
- Coordinates can be generalised or imprecise. Records without stated uncertainty are kept, so many eBird points may be hotspot locations rather than exact sightings. 2.4% of cleaned records fall on water pixels.
- The duplicate rule counts the same species, place, date and dataset once. Counts are distinct combinations, not individual animals, and intensive monitoring data (for example ringing records at one site) is largely collapsed.
- Datasets cover different periods (for example the SAFRING ringing records only 2005 to 2009), so records from different years and sources are not comparable in effort.
- Tree cover is not native habitat: it includes plantations, gardens and invaded forest.
- Land cover is from 2021 while records span 2000 to 2025.
- Protected areas are the current Nov 2026 boundaries, which may be younger than some records. Protection on paper is not effectiveness. Fishing reserves, marine parks and other conservation measures (OECM) are excluded.
- Small numbers for rare species, and three species are too data-poor to analyse. No statistical inference is made.
- Reintroduced and managed populations are included.

## Project management

The plan, risk register and what actually happened are in [`docs/PROJECT_PLAN.md`](docs/PROJECT_PLAN.md). Risks that occurred so far: unmatched or outdated species names, a different WDPA file structure from the guide, blurred and imprecise coordinates, one dataset dominating, data licences that limit use to non-commercial, and formatting problems in copied config files.

## Repository structure

```
config/      settings, species list, dataset names and licences
docs/        project plan, one-page summary
src/         Python modules, run with python -m src.<name>
sql/         SQL queries run against DuckDB
outputs/     small result tables, cleaning log, figures
tests/       tests for the cleaning rules
checks/      diagnostic scripts used during the project
data/        raw and processed data (not committed)
```

## Licence

Code: MIT. Data keep the licences of their sources (see above).
