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

- **Species (12 candidates, 9 expected to be analysed after cleaning):** endemic or threatened animals of Mauritius (birds, a bat, reptiles). The candidate list with IUCN categories is in `config/species.csv`.
- **Region:** Mauritius main island, bounding box in `config/config.yml`.
- **Period:** records from 2000-01-01 to 2025-12-31.
- **Records:** GBIF occurrence records with coordinates, country MU.
- **Land cover:** ESA WorldCover 2021 v200 (10 m), read as a small window of tile S21E057.
- **Protected areas:** current WDPA polygons (terrestrial and coastal, formally designated).
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
| M2 | Day 2: all records downloaded and cached, WDPA and land cover obtained | [ ] |
| M3 | Day 3: cleaned dataset with land cover and grid cells, cleaning log | [ ] |
| M4 | Day 4: DuckDB database and SQL results, tree cover protected share | [ ] |
| M5 | Day 5: three figures and tests | [ ] |
| M6 | Day 6: README, one-pager, CI green, release v1.0 | [ ] |

## 5. Risks

| # | Risk | Likelihood | Impact | Mitigation | Occurred? / What I did |
|---|------|-----------|--------|-----------|------------------------|
| R1 | Too few records for rare species | High | Medium | Count first, drop species under about 20 records, report them as data-poor | Occurred: Phelsuma guentheri has only 9 records. After the 1,000 m uncertainty rule, Pteropus niger (13 of 221 kept) and Leiolopisma telfairii (7 of 59) are also data-poor. All three are kept in `species.csv` and reported as data-poor. |
| R2 | Names do not match the GBIF backbone (taxonomy changes) | Medium | Medium | Always resolve names with the species match service and read the match type | Occurred: Terpsiphone desolata did not match (HIGHERRANK), so the row was changed to Terpsiphone bourbonnensis. Lalage typica is a SYNONYM in the GBIF backbone, speciesKey 2486753 used. Records are published under several names (for example Columba mayeri, Coracina typica, subspecies); each downloaded file was checked to contain exactly one speciesKey. |
| R3 | WDPA file structure differs from what the guide says | Medium | Medium | Print the columns before using them | |
| R4 | Sampling bias: records cluster near roads, trails and well-known sites, and a few datasets dominate | High | High | Report records per dataset, word results as recorded locations, not distribution | Occurred: before cleaning, eBird supplies 3,932 of 6,385 records (62%), iNaturalist research-grade 873, and 1,580 records have no dataset name (several datasets). Results are worded as recorded locations. |
| R5 | Coordinates imprecise or generalised | High | Medium | Filter by uncertainty, keep the 2 km grid, state the limitation | Occurred: stated uncertainty is rare (eBird states none). Where stated, it is often above 5,000 m (595 of 873 iNaturalist records), probably blurred coordinates of threatened taxa. Records above 1,000 m are removed, records without stated uncertainty are kept. Coordinates are not "un-blurred". |
| R6 | Land cover is not native habitat: tree cover includes plantations and invaded forest | High | High | Call it tree cover, never native forest | |
| R7 | Misleading conclusions or sensitive data exposed | Medium | High | Cautious wording, aggregated maps only, no exact coordinates in the repository | |
| R8 | Time and tooling problems | Medium | Medium | Fixed scope, caching, fallback to scripts instead of notebooks | Occurred: `environment.yml` copied from the PDF lost its formatting and conda could not parse it, so it was rewritten. A duplicate-rule test in the brief removed its own test record, so the test data was corrected. |

## 6. Definition of done

- [ ] One documented command sequence recreates all outputs from raw downloads (the WDPA download is the only manual data step).
- [ ] At least 6 species with enough records are analysed, or the plan explains why not.
- [ ] Cleaning rules and a cleaning log are included.
- [ ] Five SQL files run against the DuckDB database and their results are saved.
- [ ] Three figures, a README with findings, limitations and licences, and a one-page summary exist.
- [ ] Tests pass and CI is green. Tagged release v1.0.
- [ ] No exact species coordinates and no raw WDPA files in the repository.
- [ ] PROJECT_PLAN.md lists risks that actually occurred and what was done about them.

## 7. Data facts

_Fill in as the project progresses. This section feeds the README._

- **Species decision rule:** keep species with at least 20 records (`min_records_per_species`). If fewer than 6 species or fewer than about 300 records in total remain, add species or discuss an extension.
- **Go or no-go decision and record counts per species:** Go. Counts checked on 2026-11-10 (GBIF, country MU, 2000 to 2025, before cleaning): Nesoenas mayeri 1419, Falco punctatus 876, Foudia rubra 847, Hypsipetes olivaceus 802, Psittacula eques 648, Zosterops chloronothos 460, Terpsiphone bourbonnensis 454, Lalage typica 336, Phelsuma ornata 254, Pteropus niger 221, Leiolopisma telfairii 59, Phelsuma guentheri 9. Total 6,385 records. 11 species pass the 20-record rule before cleaning.
- **Records kept by the 1,000 m uncertainty rule (before duplicate and bounding box rules):** Nesoenas mayeri 1,284, Falco punctatus 854, Foudia rubra 774, Hypsipetes olivaceus 752, Psittacula eques 640, Terpsiphone bourbonnensis 447, Zosterops chloronothos 444, Lalage typica 327, Phelsuma ornata 232, Pteropus niger 13, Leiolopisma telfairii 7, Phelsuma guentheri 0. Nine species stay above 20 records (about 5,750 records).
- **Species dropped as data-poor:** Phelsuma guentheri, Pteropus niger and Leiolopisma telfairii. The final check happens after cleaning in `prepare.py`.
- **Name changes (matchType, status SYNONYM):** Terpsiphone desolata did not match (HIGHERRANK); GBIF treats desolata as a subspecies of Terpsiphone bourbonnensis, so the row was changed. Lalage typica is a SYNONYM in the GBIF backbone (accepted name: _fill in_), speciesKey 2486753 used.
- **GBIF retrieval date:** 2026-11-10
- **Datasets before cleaning:** eBird 3,932 records (no uncertainty stated), no dataset name 1,580 (top dataset keys b4ae1720 with 799, 8a863029 with 376, b1047888 with 146, names to look up), iNaturalist research-grade observations 873.
- **Dominant datasets after cleaning (from `05_data_sources`):** _to fill in_
- **Occurrence status and basis of record (before cleaning):** all 6,385 records have status DETECTED, so the cleaning rule accepts PRESENT and DETECTED (the rule in the brief accepted only PRESENT and would have removed everything). 6,265 human observations and 120 machine observations; machine observations are kept. No fossil or living specimens and no record without a year.
- **Cleaning decisions:** absent and not-detected records, fossil and living specimens, years outside 2000 to 2025, points outside the island box, coordinate uncertainty above 1,000 m and exact duplicates are removed. Records with no stated coordinate uncertainty are kept; records without a year would be dropped by the year rule.
- **Cleaning log (records removed per rule):** _to fill in_
- **Final number of records and species:** _to fill in_
- **Land cover counts of final records:** _to fill in_
- **Records in Water or Unknown or no data (likely generalised coordinates):** _to fill in_
- **WDPA download date and release month:** _to fill in_
- **WDPA polygons after filtering and largest areas:** _to fill in_
- **Total land area computed (sanity check against about 1,860 km²):** _to fill in_
- **IUCN Red List categories checked on:** _to fill in_

## 8. Results notes

_To fill in after M4 and M5. Word everything as recorded locations, not distribution, and say tree cover, never native forest._

- Data coverage and unevenness: _to fill in_
- Land cover of records: _to fill in_
- Share of records versus share of tree cover inside protected areas: _to fill in_
- Hotspot cells: _to fill in_
- Statements apply to these species, these open datasets and this land cover layer only.
