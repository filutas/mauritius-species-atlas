SELECT s.common_name,
       COUNT(*) AS records,
       CAST(SUM(CASE WHEN o.in_pa THEN 1 ELSE 0 END) AS INTEGER) AS in_protected_area,
       ROUND(100.0 * SUM(CASE WHEN o.in_pa THEN 1 ELSE 0 END) / COUNT(*), 1)
           AS pct_in_protected_area
FROM occurrences_pa o
JOIN species s USING (species_key)
GROUP BY 1
ORDER BY pct_in_protected_area DESC;
