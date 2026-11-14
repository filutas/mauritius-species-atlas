SELECT cell_x, cell_y,
       COUNT(*) AS records,
       COUNT(DISTINCT species_key) AS species_richness
FROM occurrences_pa
GROUP BY cell_x, cell_y
HAVING COUNT(*) >= 3
ORDER BY species_richness DESC, records DESC;
