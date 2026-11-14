import duckdb

# Cell to inspect: cell_x and cell_y from outputs/04_grid_richness.csv
CELL_X, CELL_Y = 26, 8
WEST, SOUTH, SIZE = 57.2, -20.6, 0.02
PARAMS = [CELL_X, CELL_Y]

con = duckdb.connect("data/atlas.duckdb", read_only=True)


def show(title, sql):
    print(f"\n{title}")
    print(con.execute(sql, PARAMS).df().to_string(index=False))


lon0, lat0 = WEST + CELL_X * SIZE, SOUTH + CELL_Y * SIZE
print(f"cell {CELL_X}_{CELL_Y}: lon {lon0:.2f} to {lon0 + SIZE:.2f}, "
      f"lat {lat0:.2f} to {lat0 + SIZE:.2f}")

show(
    "species and protection",
    """SELECT s.common_name, COUNT(*) AS records,
              CAST(SUM(CASE WHEN o.in_pa THEN 1 ELSE 0 END) AS INTEGER)
                  AS in_protected_area
       FROM occurrences_pa o JOIN species s USING (species_key)
       WHERE o.cell_x = ? AND o.cell_y = ?
       GROUP BY 1 ORDER BY records DESC""",
)
show(
    "datasets",
    """SELECT dataset_name, COUNT(*) AS records,
              MIN(year) AS first_year, MAX(year) AS last_year
       FROM occurrences_pa o
       WHERE o.cell_x = ? AND o.cell_y = ?
       GROUP BY 1 ORDER BY records DESC""",
)
show(
    "land cover",
    """SELECT landcover, COUNT(*) AS records
       FROM occurrences_pa o
       WHERE o.cell_x = ? AND o.cell_y = ?
       GROUP BY 1 ORDER BY records DESC""",
)
show(
    "how many different points the records come from",
    """SELECT COUNT(*) AS distinct_points, MAX(n) AS most_records_at_one_point
       FROM (SELECT lat, lon, COUNT(*) AS n
             FROM occurrences_pa o
             WHERE o.cell_x = ? AND o.cell_y = ?
             GROUP BY lat, lon)""",
)
con.close()
