-- Task 2: 2 . best brand ever ! randks country origins of bands ,
-- ordered by the number of (non-unique) fans
SELECT DISTINCT `origin`, SUM(`fans`) AS `nb_fans`
FROM `metal_bands`
GROUP BY `origin`
ORDER BY `nb_fans` DESC;


