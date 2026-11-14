SELECT dataset_name AS dataset, basis,
       COUNT(*) AS records,
       COUNT(DISTINCT species_key) AS species,
       MIN(year) AS first_year,
       MAX(year) AS last_year
FROM occurrences_pa
GROUP BY 1, 2
ORDER BY records DESC;
