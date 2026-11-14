import duckdb

WEST, SOUTH, SIZE = 57.2, -20.6, 0.02

con = duckdb.connect("data/atlas.duckdb", read_only=True)

cells = con.execute(
    """SELECT cell_x, cell_y, COUNT(*) AS records,
              SUM(CASE WHEN landcover = 'Water' THEN 1 ELSE 0 END) AS on_water,
              COUNT(DISTINCT species_key) AS species,
              COUNT(DISTINCT dataset_name) AS datasets
       FROM occurrences_pa
       GROUP BY cell_x, cell_y
       HAVING COUNT(*) >= 3
          AND 2 * SUM(CASE WHEN landcover = 'Water' THEN 1 ELSE 0 END) > COUNT(*)
       ORDER BY cell_x, cell_y"""
).df()
cells["lon_from"] = (WEST + cells["cell_x"] * SIZE).round(2)
cells["lat_from"] = (SOUTH + cells["cell_y"] * SIZE).round(2)
print("cells with 3 or more records where most records are on water pixels")
print(cells.to_string(index=False))

detail_sql = """SELECT s.common_name, o.dataset_name, COUNT(*) AS records,
                       MIN(o.year) AS first_year, MAX(o.year) AS last_year,
                       SUM(CASE WHEN o.uncertainty_m IS NULL THEN 1 ELSE 0 END)
                           AS no_uncertainty_stated,
                       COUNT(*) - COUNT(DISTINCT o.lat || ',' || o.lon)
                           AS repeated_points
                FROM occurrences_pa o
                JOIN species s USING (species_key)
                WHERE o.cell_x = ? AND o.cell_y = ?
                GROUP BY 1, 2
                ORDER BY records DESC"""
for c in cells.itertuples():
    print(f"\ncell {c.cell_x}_{c.cell_y} (lon from {c.lon_from}, lat from {c.lat_from})")
    print(con.execute(detail_sql, [c.cell_x, c.cell_y]).df().to_string(index=False))
con.close()
