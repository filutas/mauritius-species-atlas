from pathlib import Path

import duckdb

DB = "data/atlas.duckdb"


def main():
    Path("outputs").mkdir(exist_ok=True)
    con = duckdb.connect(DB)
    # The first run downloads the spatial extension, so it needs a connection.
    con.execute("INSTALL spatial")
    con.execute("LOAD spatial")

    con.execute(
        """CREATE OR REPLACE TABLE species AS
           SELECT * FROM read_csv_auto('data/processed/species_table.csv')"""
    )
    con.execute(
        """CREATE OR REPLACE TABLE occurrences AS
           SELECT * FROM read_parquet('data/processed/occurrences.parquet')"""
    )
    con.execute(
        """CREATE OR REPLACE TABLE protected_areas AS
           SELECT * FROM ST_Read('data/processed/protected_areas.gpkg')"""
    )
    # ST_Point takes longitude first, then latitude.
    con.execute(
        """CREATE OR REPLACE TABLE occurrences_pa AS
           SELECT o.*,
                  EXISTS (SELECT 1 FROM protected_areas p
                          WHERE ST_Within(ST_Point(o.lon, o.lat), p.geom)) AS in_pa
           FROM occurrences o"""
    )

    n_pa = con.execute("SELECT COUNT(*) FROM protected_areas").fetchone()[0]
    n_occ, n_in = con.execute(
        """SELECT COUNT(*), SUM(CASE WHEN in_pa THEN 1 ELSE 0 END)
           FROM occurrences_pa"""
    ).fetchone()
    print(f"protected areas: {n_pa} | records: {n_occ} | inside protected areas: {n_in}")

    for f in sorted(Path("sql").glob("*.sql")):
        df = con.execute(f.read_text(encoding="utf-8")).df()
        df.to_csv(f"outputs/{f.stem}.csv", index=False)
        print("---", f.name, len(df), "rows")
        print(df.head(15).to_string(index=False))
    con.close()


if __name__ == "__main__":
    main()
