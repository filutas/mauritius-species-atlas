SELECT s.common_name, s.scientific_name, s.taxon_group, s.iucn_category,
       COUNT(*) AS records,
       MIN(o.year) AS first_year,
       MAX(o.year) AS last_year,
       COUNT(DISTINCT o.dataset_key) AS datasets
FROM occurrences_pa o
JOIN species s USING (species_key)
GROUP BY 1, 2, 3, 4
ORDER BY records DESC;
