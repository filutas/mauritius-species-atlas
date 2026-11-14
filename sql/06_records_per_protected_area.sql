SELECT p.NAME_ENG AS protected_area, p.DESIG_ENG AS designation,
       COUNT(DISTINCT o.gbif_id) AS records,
       COUNT(DISTINCT o.species_key) AS species
FROM occurrences o
JOIN protected_areas p ON ST_Within(ST_Point(o.lon, o.lat), p.geom)
GROUP BY 1, 2
ORDER BY records DESC;
