# Project Plan: Endemic Species and Habitat Atlas for Mauritius

Owner: István Attila Filutás | Started: 2026-11-10 | Release v1.0: _to fill in_ | Planned effort: about 6 working days of focused work

## 1. Goal

Map where threatened and endemic animals of Mauritius have been recorded in open biodiversity data, in which land cover class they were found, and how many of the records and how much of the remaining tree cover lie inside protected areas, using only open data and a fully reproducible Python, SQL and GIS pipeline.

The project answers five questions and nothing more:

1. **Data coverage:** how many open records exist for each chosen species, from which years, datasets and record types?
2. **Habitat:** in which land cover classes were the records made?
3. **Protection:** what share of each species' records lies inside protected areas?
4. **Habitat protection:** what share of the island's tree cover lies inside protected areas, compared with the share of records?
5. **Hotspots:** where on the island (2 km cells) are most species recorded?

This is a transparent, modest data analysis, not a scientific study.

## 2. Scope

- **Species (12 candidates, 9 analysed after cleaning):** endemic or threatened animals of Mauritius (birds, a bat, reptiles). The candidate list with IUCN categories is in `config/species.csv`.
- **Region:** Mauritius main island, bounding box in `config/config.yml`.
- **Period:** records from 2000-01-01 to 2025-12-31.
- **Records:** GBIF occurrence records with coordinates, country MU.
- **Land cover:** ESA WorldCover 2021 v200 (10 m), read as a small window of tile S21E057.
- **Protected areas:** current WDPA polygons, formally designated protected areas only (terrestrial and coastal). Other conservation measures (OECM), marine areas, fishing reserves and the marine park are excluded.
- **Grid:** 2 km cells (0.02 degrees) for hotspot mapping, cells with fewer than 3 records hidden.
- **Tools:** Python 3.11, DuckDB with spatial extension, GitHub Actions.
- **Deliverables:** public GitHub repository, DuckDB build script, five SQL files with result tables in `outputs/`, three figures, cleaning log, tests, CI, README with findings, limitations and licences, one-page summary (`docs/ONE_PAGER.md`), release v1.0.

## 3. Out of scope

- No other islands (Rodrigues, Réunion, Seychelles): possible extension.
- No forest loss over time, species distribution models or population trends.
- No separation of native from exotic forest (the data cannot do it).
- No marine species or marine protected areas.
- No claim about how well protected areas work.
- No publication of exact species coordinates.

## 4. Milestones

| ID | Milestone | Status |
|----|-----------|--------|
| M1 | Day 1: repository, environment, plan, species list, record counts, go or no-go decision | [x] |
| M2 | Day 2: all records downloaded and cached, WDPA and land cover obtained | [x] |
| M3 | Day 3: cleaned dataset with land cover and grid cells, cleaning log | [x] |
| M4 | Day 4: DuckDB database and SQL results, tree cover protected share | [ ] |
| M5 | Day 5: three figures and tests | [ ] |
| M6 | Day 6: README, one-pager, CI green, release v1.0 | [ ] |

## 5. Risks

| # | Risk | Likelihood | Impact | Mitigation | Occurred? / What I did |
|---|------|-----------|--------|-----------|------------------------|
| R1 | Too few records for rare species | High | Medium | Count first, drop species under about 20 records, report them as data-poor | Occurred: Phelsuma guentheri has only 9 records. After the 1,000 m uncertainty rule, Pteropus niger (13 of 221 kept) and Leiolopisma telfairii (7 of 59) are also data-poor. After all cleaning rules: Pteropus niger 13, Leiolopisma telfairii 6, Phelsuma guentheri 0. All three are kept in `species.csv` and reported as data-poor. |
| R2 | Names do not match the GBIF backbone (taxonomy changes) | Medium | Medium | Always resolve names with the species match service and read the match type | Occurred: Terpsiphone desolata did not match (HIGHERRANK), so the row was changed to Terpsiphone bourbonnensis. Lalage typica is a SYNONYM in the GBIF backbone, speciesKey 2486753 used. Records are published under several names (for example Columba mayeri, Coracina typica, subspecies); each downloaded file was checked to contain exactly one speciesKey. |
| R3 | WDPA file structure differs from what the guide says | Medium | Medium | Print the columns before using them | Occurred: the Nov 2026 release differs from the guide. MARINE is replaced by REALM, WDPAID by SITE_ID, and the file merges protected areas with other conservation measures (OECM). Adapted the script; all 35 polygons are PA. |
| R4 | Sampling bias: records cluster near roads, trails and well-known sites, and a few datasets dominate | High | High | Report records per dataset, word results as recorded locations, not distribution | Occurred: before cleaning, eBird supplies 3,932 of 6,385 records (62%); after cleaning it supplies 3,802 of 4,644 (82%). The SAFRING historical bird ringing records (dataset b4ae1720, 2005 to 2009 only) fall from 799 records to 13 because of the bounding box and duplicate rules. Results are worded as recorded locations. |
| R5 | Coordinates imprecise or generalised | High | Medium | Filter by uncertainty, keep the 2 km grid, state the limitation | Occurred: stated uncertainty is rare (eBird states none). Where stated, it is often above 5,000 m (595 of 873 iNaturalist records), probably blurred coordinates of threatened taxa. All 599 records removed by the 1,000 m rule are iNaturalist records. Records without stated uncertainty are kept. Coordinates are not "un-blurred". 448 kestrel records of the SAFRING ringing dataset lay outside the island box and were removed. 110 final records (2.4%) fall on water pixels and are reported, not moved. |
| R6 | Land cover is not native habitat: tree cover includes plantations and invaded forest | High | High | Call it tree cover, never native forest | Occurred: tree cover is about half of the island's land in WorldCover, far more than any native forest, confirming that this layer must be called tree cover only. |
| R7 | Misleading conclusions or sensitive data exposed | Medium | High | Cautious wording, aggregated maps only, no exact coordinates in the repository | Not occurred so far. `data/` is git-ignored and blurred coordinates are removed, not recovered. |
| R8 | Time and tooling problems | Medium | Medium | Fixed scope, caching, fallback to scripts instead of notebooks | Occurred: `environment.yml`, `config.yml` and `species.csv` copied from the PDF lost their formatting and had to be rewritten. A duplicate-rule test in the brief removed its own test record, so the test data was corrected. A pandas string-type error in `prepare.py` was fixed. |
| R9 | Data licences restrict use (added during the project) | Medium | Medium | Look up the licence of every dataset, cite all sources, publish only aggregated results | Occurred: four datasets are CC BY-NC (Observation.org, iNaturalist, Xeno-canto, Birda; 784 of 4,644 cleaned records, 17%), and the WDPA terms allow non-commercial use only. The project is stated as non-commercial, with attribution; raw records and WDPA files are not redistributed. |

## 6. Definition of done

- [ ] One documented command sequence recreates all outputs from raw downloads (the WDPA download is the only manual data step).
- [x] At least 6 species with enough records are analysed, or the plan explains why not. (9 species)
- [x] Cleaning rules and a cleaning log are included.
- [ ] Five SQL files run against the DuckDB database and their results are saved.
- [ ] Three figures, a README with findings, limitations and licences, and a one-page summary exist.
- [ ] Tests pass and CI is green. Tagged release v1.0.
- [ ] No exact species coordinates and no raw WDPA files in the repository.
- [ ] PROJECT_PLAN.md lists risks that actually occurred and what was done about them.

## 7. Data facts

_Fill in as the project progresses. This section feeds the README._

### Species

- **Species decision rule:** keep species with at least 20 records after cleaning (`min_records_per_species`). If fewer than 6 species or fewer than about 300 records in total remain, add species or discuss an extension.
- **Go or no-go decision and record counts per species:** Go. Counts checked on 2026-11-10 (GBIF, country MU, 2000 to 2025, before cleaning): Nesoenas mayeri 1419, Falco punctatus 876, Foudia rubra 847, Hypsipetes olivaceus 802, Psittacula eques 648, Zosterops chloronothos 460, Terpsiphone bourbonnensis 454, Lalage typica 336, Phelsuma ornata 254, Pteropus niger 221, Leiolopisma telfairii 59, Phelsuma guentheri 9. Total 6,385 records.
- **Records after cleaning (analysed species):** Nesoenas mayeri 930, Mauritius bulbul (Hypsipetes olivaceus) 712, Foudia rubra 698, Psittacula eques 591, Terpsiphone bourbonnensis 422, Zosterops chloronothos 396, Falco punctatus 379, Lalage typica 291, Phelsuma ornata 225. Total 4,644 records, 9 species.
- **Species dropped as data-poor:** Pteropus niger (13 records after cleaning), Leiolopisma telfairii (6), Phelsuma guentheri (0). Most of their records have coordinate uncertainty above 5,000 m (all 9 Guenther's gecko records), consistent with blurred coordinates of threatened taxa; some also lie on islets outside the main-island box.
- **Name changes (matchType, status SYNONYM):** Terpsiphone desolata did not match (HIGHERRANK); GBIF treats desolata as a subspecies of Terpsiphone bourbonnensis, so the row was changed. Lalage typica is a SYNONYM in the GBIF backbone (accepted name: _fill in_), speciesKey 2486753 used.
- **IUCN Red List categories checked on:** _to fill in_

### GBIF records

- **GBIF retrieval date:** 2026-11-10
- **Occurrence status and basis of record (before cleaning):** all 6,385 records have status DETECTED, so the cleaning rule accepts PRESENT and DETECTED (the rule in the brief accepted only PRESENT and would have removed everything). 6,265 human observations and 120 machine observations; machine observations are kept. No fossil or living specimens and no record without a year.
- **Cleaning decisions:** absent and not-detected records, fossil and living specimens, years outside 2000 to 2025, points outside the island box, coordinate uncertainty above 1,000 m and exact duplicates are removed. Records with no stated coordinate uncertainty are kept. The duplicate rule treats the same species, place, date and dataset as one record, so counts are distinct species-place-date-dataset combinations, not individual animals or observers.
- **Cleaning log (records removed per rule):**

| Rule | Removed | Remaining |
|------|--------:|----------:|
| start | 0 | 6,385 |
| occurrence status is present or detected | 0 | 6,385 |
| no fossil or living (captive) specimens | 0 | 6,385 |
| year within study period | 0 | 6,385 |
| inside island bounding box | 466 | 5,919 |
| coordinate uncertainty within limit | 599 | 5,320 |
| exact duplicates (species, place, date, dataset) | 657 | 4,663 |
| species with fewer than 20 records | 19 | 4,644 |

- **Which records each rule removed:** bounding box 466 (448 SAFRING ringing records, 16 iNaturalist, 2 eBird; 449 of them are kestrel records); uncertainty 599 (all iNaturalist); duplicates 657 (SAFRING 338, eBird 128, Macaulay Library 98, Xeno-canto 84, others 9).
- **Datasets (records before and after cleaning):** 1,580 records had no dataset name in GBIF; they come from six datasets, named by hand in `config/datasets.csv`.

| Dataset | Key (start) | Publisher | Licence | Before | After |
|---------|-------------|-----------|---------|-------:|------:|
| eBird (EOD – eBird Observation Dataset) | 4fa7b334 | Cornell Lab of Ornithology | CC BY 4.0 | 3,932 | 3,802 |
| iNaturalist research-grade observations | 50c9509d | iNaturalist.org | CC BY-NC 4.0 (dataset level) | 873 | 255 |
| SAFRING: Historical Bird Ringing Records (2005-2009) | b4ae1720 | Oschadleus D and Ranwashe F | CC BY 4.0 | 799 | 13 |
| Observation.org Nature data from around the World | 8a863029 | Observation.org | CC BY-NC 4.0 | 376 | 366 |
| Birda - Global Observation Dataset | 6ff8b3b0 | Birda | CC BY-NC 4.0 | 101 | 101 |
| Xeno-canto - Bird sounds from around the world | b1047888 | Vellinga W P, Planqué B | CC BY-NC 4.0 | 146 | 62 |
| NABU\|naturgucker | 6ac3f774 | naturgucker.de | CC BY 4.0 | 37 | 23 |
| Macaulay Library Audio and Video Collection | 7f6dd0f7 | Scholes III Ph.D.E | CC0 1.0 | 120 | 22 |

- **Licence notes:** four datasets are CC BY-NC (Observation.org, iNaturalist, Birda, Xeno-canto), together 784 of the 4,644 cleaned records (17%), so the project is non-commercial, with attribution to every dataset. The licence column shows the dataset-level licence from GBIF; iNaturalist records can carry a less restrictive licence of their own, which was not downloaded. The 120 Macaulay Library records match the 120 machine observations.
- **Dominant datasets in the final tables (from `05_data_sources`):** _to fill in_

### Land cover

- **Land cover raster (ESA WorldCover 2021 v200, clipped to the bounding box):** 8,400 × 8,400 pixels. Share of the box: water 66.8%, tree cover 17.7%, cropland 6.8%, grassland 5.5%, built-up 2.3%, no data 0.6%. Land is about 32.6% of the box, so tree cover is a bit over half of the land. Tree cover here includes plantations, gardens and invaded forest, so it is not native forest.
- **Land cover counts of final records (4,644):** tree cover 4,121 (88.7%), built-up 188 (4.0%), bare or sparse 113 (2.4%), water 110 (2.4%), grassland 93 (2.0%), cropland 12 (0.3%), mangroves 7 (0.2%).
- **Records on water or no data (likely generalised coordinates or coastal points):** 110 (2.4%) on water, none on no-data pixels. Reported, not moved.

### Protected areas (WDPA)

- **WDPA:** release Nov 2026 (merged WDPA and WD-OECM), downloaded on _date_. 35 polygons (14 terrestrial, 12 coastal, 9 marine), all PA and Designated. Marine polygons and polygons outside the bounding box removed (23 left), then fishing reserves and the marine park excluded, which should leave 18 polygons (confirm with the script output).
- **Largest areas (GIS_AREA, km²):** Black River Gorges National Park 56.2 and Black River Gorges Bel Ombre Biosphere Reserve 49.6 (these two overlap), Bras d'Eau National Park 4.9, Vallée d'Osterlog Endemic Garden 2.7, Ile d'Ambre 1.7.
- **Total land area computed (sanity check against about 1,860 km²):** _to fill in_

## 8. Results notes

_To fill in after M4 and M5. Word everything as recorded locations, not distribution, and say tree cover, never native forest._

- Data coverage and unevenness: 4,644 cleaned records of 9 species; eBird supplies 82%; three of twelve candidate species are data-poor.
- Land cover of records: 89% of records fall on tree cover, 2.4% on water pixels.
- Share of records versus share of tree cover inside protected areas: _to fill in_
- Hotspot cells: _to fill in_
- Statements apply to these species, these open datasets and this land cover layer only.
