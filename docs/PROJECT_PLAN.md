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
- **Region:** Mauritius main island, bounding box in `config/config.yml`. The box also contains some small offshore islets near the main island, and open sea.
- **Period:** records from 2000-01-01 to 2025-12-31.
- **Records:** GBIF occurrence records with coordinates, country MU.
- **Land cover:** ESA WorldCover 2021 v200 (10 m), read as a small window of tile S21E057.
- **Protected areas:** current WDPA polygons, formally designated protected areas only (terrestrial and coastal, plus small islet Nature Reserves that WDPA labels as marine). Other conservation measures (OECM), marine areas, fishing reserves and the marine park are excluded.
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
| M4 | Day 4: DuckDB database and SQL results, tree cover protected share | [x] |
| M5 | Day 5: three figures and tests | [x] |
| M6 | Day 6: README, one-pager, CI green, release v1.0 | [ ] |

## 5. Risks

| # | Risk | Likelihood | Impact | Mitigation | Occurred? / What I did |
|---|------|-----------|--------|-----------|------------------------|
| R1 | Too few records for rare species | High | Medium | Count first, drop species under about 20 records, report them as data-poor | Occurred: Phelsuma guentheri has only 9 records. After the 1,000 m uncertainty rule, Pteropus niger (13 of 221 kept) and Leiolopisma telfairii (7 of 59) are also data-poor. After all cleaning rules: Pteropus niger 13, Leiolopisma telfairii 6, Phelsuma guentheri 0. All three are kept in `species.csv` and reported as data-poor. |
| R2 | Names do not match the GBIF backbone (taxonomy changes) | Medium | Medium | Always resolve names with the species match service and read the match type | Occurred: Terpsiphone desolata did not match (HIGHERRANK), so the row was changed to Terpsiphone bourbonnensis. Lalage typica is a SYNONYM of Coracina typica (Hartlaub, 1865) in the GBIF backbone, speciesKey 2486753 used. Records are published under several names (for example Columba mayeri, Coracina typica, subspecies); each downloaded file was checked to contain exactly one speciesKey. IUCN uses different names for some species (for example Alexandrinus eques). |
| R3 | WDPA file structure differs from what the guide says | Medium | Medium | Print the columns before using them | Occurred: the Nov 2026 release differs from the guide. MARINE is replaced by REALM, WDPAID by SITE_ID, and the file merges protected areas with other conservation measures (OECM). Adapted the script; all 35 polygons are PA. In addition, WDPA labels three small islet Nature Reserves (Île aux Aigrettes, Coin de Mire, Île aux Serpents) as realm Marine, so the realm filter from the guide excluded them. Found while checking why a heavily recorded hotspot cell had almost no records inside protected areas. Fixed by keeping Nature Reserve designations whatever the realm label says. The fix did not change any result: no record falls inside these polygons. |
| R4 | Sampling bias: records cluster near roads, trails and well-known sites, and a few datasets dominate | High | High | Report records per dataset, word results as recorded locations, not distribution | Occurred: before cleaning, eBird supplies 3,932 of 6,385 records (62%); after cleaning it supplies 3,799 of 4,626 (82%). The SAFRING historical bird ringing records (dataset b4ae1720, 2005 to 2009 only) fall from 799 records to 13 because of the bounding box and duplicate rules. One coordinate holds 589 of the 4,626 cleaned records (12.7%); it lies in a 2 km cell with 735 records (632 of them eBird), of which only 4 are inside a protected area. Results are worded as recorded locations, and the sensitivity to that cell is reported. |
| R5 | Coordinates imprecise or generalised | High | Medium | Filter by uncertainty, keep the 2 km grid, state the limitation | Occurred: stated uncertainty is rare (eBird states none). Where stated, it is often above 5,000 m (595 of 873 iNaturalist records), probably blurred coordinates of threatened taxa. All 599 records removed by the 1,000 m rule are iNaturalist records. Records without stated uncertainty are kept. Coordinates are not "un-blurred". 448 kestrel records of the SAFRING ringing dataset lay outside the island box and were removed. The hotspot map (Figure 3) showed three 2 km cells over open sea, 5 to 13 km off the west coast: 14 records, all from the Macaulay Library audio and video collection (2009 and 2010, no stated uncertainty). The box is a rectangle, so it keeps open sea. A new cleaning rule removes records on water pixels with no land within 1 km: 18 records (15 Macaulay Library, 3 eBird). 92 final records (2.0%) remain on water pixels, mostly coastal points, and are reported, not moved. |
| R6 | Land cover is not native habitat: tree cover includes plantations and invaded forest | High | High | Call it tree cover, never native forest | Occurred: tree cover is 999 km², 54% of the island's land in WorldCover, far more than any native forest, confirming that this layer must be called tree cover only. |
| R7 | Misleading conclusions or sensitive data exposed | Medium | High | Cautious wording, aggregated maps only, no exact coordinates in the repository | Not occurred so far. `data/` is git-ignored, blurred coordinates are removed and not recovered, and the hotspot map shows aggregated 2 km cells without species names. Diagnostic scripts print counts only. |
| R8 | Time and tooling problems | Medium | Medium | Fixed scope, caching, fallback to scripts instead of notebooks | Occurred: `environment.yml`, `config.yml` and `species.csv` copied from the PDF lost their formatting and had to be rewritten. A duplicate-rule test in the brief removed its own test record, so the test data was corrected. A pandas string-type error in `prepare.py` was fixed. The cleaning rule in the brief would have removed all eBird records (status DETECTED), see Data facts. `make_figures` failed once with an OSError while saving a PNG (probably because the file was open in another program); a rerun worked. |
| R9 | Data licences restrict use (added during the project) | Medium | Medium | Look up the licence of every dataset, cite all sources, publish only aggregated results | Occurred: four datasets are CC BY-NC (Observation.org, iNaturalist, Xeno-canto, Birda; 784 of 4,626 cleaned records, 17%), and the WDPA terms allow non-commercial use only. The project is stated as non-commercial, with attribution; raw records and WDPA files are not redistributed. |
| R10 | GBIF changes after the download, so a rerun gives slightly different data (added during the project) | Medium | Low | Document the retrieval date, use the cached download for the reported numbers, state that a rerun can differ | Occurred: the live counts rose after the download on 2026-11-10 (222 instead of 221 for the flying fox, 255 instead of 254 for the ornate day gecko, 62 instead of 59 for Telfair's skink). The reported numbers use the cached download. |

## 6. Definition of done

- [ ] One documented command sequence recreates all outputs from raw downloads (the WDPA download is the only manual data step).
- [x] At least 6 species with enough records are analysed, or the plan explains why not. (9 species)
- [x] Cleaning rules and a cleaning log are included.
- [x] Five SQL files run against the DuckDB database and their results are saved.
- [x] Three figures, a README with findings, limitations and licences, and a one-page summary exist.
- [ ] Tests pass and CI is green. Tagged release v1.0.
- [ ] No exact species coordinates and no raw WDPA files in the repository.
- [ ] PROJECT_PLAN.md lists risks that actually occurred and what was done about them.

## 7. Data facts

_Fill in as the project progresses. This section feeds the README._

### Species

- **Species decision rule:** keep species with at least 20 records after cleaning (`min_records_per_species`). If fewer than 6 species or fewer than about 300 records in total remain, add species or discuss an extension.
- **Go or no-go decision and record counts per species:** Go. Counts checked on 2026-11-10 (GBIF, country MU, 2000 to 2025, before cleaning): Nesoenas mayeri 1419, Falco punctatus 876, Foudia rubra 847, Hypsipetes olivaceus 802, Psittacula eques 648, Zosterops chloronothos 460, Terpsiphone bourbonnensis 454, Lalage typica 336, Phelsuma ornata 254, Pteropus niger 221, Leiolopisma telfairii 59, Phelsuma guentheri 9. Total 6,385 records. Live counts rose slightly after the download (see R10).
- **Records after cleaning (analysed species):** Nesoenas mayeri 927, Hypsipetes olivaceus 709, Foudia rubra 698, Psittacula eques 589, Terpsiphone bourbonnensis 418, Zosterops chloronothos 396, Falco punctatus 375, Lalage typica 289, Phelsuma ornata 225. Total 4,626 records, 9 species.
- **Species dropped as data-poor:** Pteropus niger (13 records after cleaning), Leiolopisma telfairii (6), Phelsuma guentheri (0). Most of their records have coordinate uncertainty above 5,000 m (all 9 Guenther's gecko records), consistent with blurred coordinates of threatened taxa; some also lie on islets outside the main-island box.
- **Name changes (matchType, status SYNONYM):** Terpsiphone desolata did not match (HIGHERRANK); GBIF treats desolata as a subspecies of Terpsiphone bourbonnensis, so the row was changed. Lalage typica is a SYNONYM of Coracina typica (Hartlaub, 1865) in the GBIF backbone (accepted name Coracina typica), speciesKey 2486753 used; records under both names are included. IUCN lists Psittacula eques as Alexandrinus eques. IUCN common names: Pteropus niger is Greater Mascarene Flying Fox, Phelsuma guentheri is Round Island Day Gecko.
- **IUCN Red List categories (checked on 2026-11-10, Red List version 2026-1):** Falco punctatus CR, Zosterops chloronothos CR, Nesoenas mayeri VU, Psittacula eques VU, Hypsipetes olivaceus VU, Leiolopisma telfairii VU, Foudia rubra EN, Lalage typica EN, Pteropus niger EN, Terpsiphone bourbonnensis LC, Phelsuma ornata LC, Phelsuma guentheri VU.

### GBIF records

- **GBIF retrieval date:** 2026-11-10
- **Occurrence status and basis of record (before cleaning):** all 6,385 records have status DETECTED, so the cleaning rule accepts PRESENT and DETECTED (the rule in the brief accepted only PRESENT and would have removed everything). 6,265 human observations and 120 machine observations; machine observations are kept. No fossil or living specimens and no record without a year.
- **Cleaning decisions:** absent and not-detected records, fossil and living specimens, years outside 2000 to 2025, points outside the island box, coordinate uncertainty above 1,000 m, exact duplicates and records in open water (no land within 1 km) are removed. Records with no stated coordinate uncertainty are kept. The duplicate rule treats the same species, place, date and dataset as one record, so counts are distinct species-place-date-dataset combinations, not individual animals or observers.
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
| open water, no land within 1000 m | 18 | 4,645 |
| species with fewer than 20 records | 19 | 4,626 |

- **Which records each rule removed:** bounding box 466 (448 SAFRING ringing records, 16 iNaturalist, 2 eBird; 449 of them are kestrel records); uncertainty 599 (all iNaturalist); duplicates 657 (SAFRING 338, eBird 128, Macaulay Library 98, Xeno-canto 84, others 9); open water 18 (15 Macaulay Library, 3 eBird).
- **Datasets (records before and after cleaning):** 1,580 records had no dataset name in GBIF; they come from six datasets, named by hand in `config/datasets.csv`.

| Dataset | Key (start) | Publisher | Licence | Before | After |
|---------|-------------|-----------|---------|-------:|------:|
| eBird (EOD – eBird Observation Dataset) | 4fa7b334 | Cornell Lab of Ornithology | CC BY 4.0 | 3,932 | 3,799 |
| iNaturalist research-grade observations | 50c9509d | iNaturalist.org | CC BY-NC 4.0 (dataset level) | 873 | 255 |
| SAFRING: Historical Bird Ringing Records (2005-2009) | b4ae1720 | Oschadleus D and Ranwashe F | CC BY 4.0 | 799 | 13 |
| Observation.org Nature data from around the World | 8a863029 | Observation.org | CC BY-NC 4.0 | 376 | 366 |
| Birda - Global Observation Dataset | 6ff8b3b0 | Birda | CC BY-NC 4.0 | 101 | 101 |
| Xeno-canto - Bird sounds from around the world | b1047888 | Vellinga W P, Planqué B | CC BY-NC 4.0 | 146 | 62 |
| NABU\|naturgucker | 6ac3f774 | naturgucker.de | CC BY 4.0 | 37 | 23 |
| Macaulay Library Audio and Video Collection | 7f6dd0f7 | Scholes III Ph.D.E | CC0 1.0 | 120 | 7 |

- **Licence notes:** four datasets are CC BY-NC (Observation.org, iNaturalist, Birda, Xeno-canto), together 784 of the 4,626 cleaned records (17%), so the project is non-commercial, with attribution to every dataset. The licence column shows the dataset-level licence from GBIF; iNaturalist records can carry a less restrictive licence of their own, which was not downloaded. The 120 Macaulay Library records match the 120 machine observations.
- **Datasets in the final tables (from `05_data_sources`, records, species, years):** eBird 3,799 records, 8 species, 2001 to 2025; Observation.org 366, 9 species, 2004 to 2025; iNaturalist 255, only 3 species, 2003 to 2025; Birda 101, 8 species, 2022 to 2025; Xeno-canto 62, 8 species, 2007 to 2025; naturgucker 23, 8 species, 2010 to 2025; SAFRING 13, 5 species, 2007 to 2009; Macaulay Library 7 (machine observations), 3 species, 2009 to 2010.

### Land cover

- **Land cover raster (ESA WorldCover 2021 v200, clipped to the bounding box):** 8,400 × 8,400 pixels. Share of the box: water 66.8%, tree cover 17.7%, cropland 6.8%, grassland 5.5%, built-up 2.3%, no data 0.6%. Tree cover here includes plantations, gardens and invaded forest, so it is not native forest.
- **Land cover counts of final records (4,626):** tree cover 4,121 (89.1%), built-up 188 (4.1%), bare or sparse 113 (2.4%), grassland 93 (2.0%), water 92 (2.0%), cropland 12 (0.3%), mangroves 7 (0.2%).
- **Records on water or no data:** 92 (2.0%) on water pixels, none on no-data pixels, after the open-water rule removed 18 more. They are mostly coastal points and are reported, not moved.

### Protected areas (WDPA)

- **WDPA:** release Nov 2026 (merged WDPA and WD-OECM), downloaded on 2026-11-10. 35 polygons (14 terrestrial, 12 coastal, 9 marine), all PA and Designated.
- **Filter steps:** 29 polygons after the realm filter (terrestrial and coastal, plus 3 Nature Reserves labelled Marine and kept by exception: Île aux Aigrettes, Coin de Mire (Gunner's Quoin) and Île aux Serpents); 24 after excluding 5 marine-purpose areas (fishing reserves and the marine park); 20 after the bounding box (Île aux Serpents lies north of the box).
- **Largest areas (GIS_AREA, km²):** Black River Gorges National Park 56.2 and Black River Gorges Bel Ombre Biosphere Reserve 49.6 (these two overlap), Bras d'Eau National Park 4.9, Vallée d'Osterlog Endemic Garden 2.7, Ile d'Ambre 1.7.
- **Records per protected area (`06`, overlapping areas count a record twice):** Black River Gorges National Park 1,875, Black River Gorges Bel Ombre Biosphere Reserve 1,749, Bras d'Eau National Park 65, Rivulet Terre Rouge Estuary Bird Sanctuary 10, Pointe d'Esny Wetland 4, Ile d'Ambre 1, Vallée d'Osterlog Endemic Garden 1. Only 7 of the 20 polygons contain any record.

### Protection results

- **Records inside protected areas:** 2,152 of 4,626 (46.5%). By species: Mauritius cuckooshrike 85.1% (246 of 289), echo parakeet 76.6% (451 of 589), Mauritius bulbul 58.1% (412 of 709), pink pigeon 48.1% (446 of 927), Mascarene paradise flycatcher 43.5% (182 of 418), Mauritius kestrel 37.3% (140 of 375), Mauritius fody 26.4% (184 of 698), Mauritius olive white-eye 18.2% (72 of 396), ornate day gecko 8.4% (19 of 225).
- **Total land area computed (sanity check against about 1,860 km²):** 1,844.5 km².
- **Tree cover protection (`outputs/landcover_protected_share.csv`):** tree cover 999.1 km² (54.2% of land), 76.6 km² protected (7.7%); grassland 311.2 km², 0.4%; cropland 385.8 km², 0%; built-up 131.6 km², 0%; mangroves 3.0 km², 17.5%; all land 78.7 km² protected (4.3%).
- **Concentration in one place:** a 2 km cell has 735 records (93 distinct points, 589 records at a single point, 632 from eBird, 716 on tree cover) and only 4 of them inside a protected area; none of its records lies within 250 m of the Île aux Aigrettes polygon (686 are more than 500 m away), so they are not on that islet. Without that cell, the share of records inside protected areas is 55.2% (2,148 of 3,891) instead of 46.5%; pink pigeon 63.5% instead of 48.1%, fody 40.9% instead of 26.4%, olive white-eye 35.3% instead of 18.2%.
- **Hotspots (`04`):** 92 cells with at least 3 records. The richest cells have 9 species each (one with 1,037 records, one with 442).

### Fresh-start test
- **Date and setup:** 2026-11-15. The repository was cloned into a new folder, a new conda environment was created from `environment.yml`, and only `data/raw/wdpa` was copied. GBIF records and land cover were downloaded again.
- **Result:** the full run order completed. All outputs were recreated.
- **Difference from the reported numbers:** GBIF had grown since the download of 2026-11-10: 6,390 records instead of 6,385, and 4,627 cleaned records instead of 4,626 (one more ornate day gecko record). Species (9), shares of records inside protected areas (46.5%), tree cover protection (7.7%) and the number of hotspot cells (92) are unchanged. The reported numbers stay those of the 2026-11-10 download.

## 8. Results notes

_Word everything as recorded locations, not distribution, and say tree cover, never native forest._

- Data coverage and unevenness: 4,626 cleaned records of 9 species; eBird supplies 82%; three of twelve candidate species are data-poor. One coordinate supplies 12.7% of the records.
- Land cover of records: 89% of records fall on tree cover, 2.0% on water pixels.
- Share of records versus share of tree cover inside protected areas: 46.5% of cleaned records lie inside protected areas, against 7.7% of the island's tree cover and 4.3% of all land. Shares by species run from 8% (ornate day gecko) to 85% (Mauritius cuckooshrike). Most records inside protected areas are in the Black River Gorges area. This cannot show whether the species live there or observers go there.
- Hotspot cells: 92 cells of 2 km have at least 3 records. They show where observers go, not where animals are.
- Statements apply to these species, these open datasets and this land cover layer only, as downloaded on 2026-11-10.
