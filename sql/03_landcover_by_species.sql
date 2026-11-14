SELECT s.common_name, o.landcover,
       COUNT(*) AS records,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY s.common_name), 1)
           AS pct_of_species_records
FROM occurrences_pa o
JOIN species s USING (species_key)
GROUP BY s.common_name, o.landcover
ORDER BY s.common_name, records DESC;
