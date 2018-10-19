-- calculate number of chartevents happens in each hour of each admission

DROP MATERIALIZED VIEW IF EXISTS v_freq_chartevents CASCADE;
CREATE MATERIALIZED VIEW v_freq_chartevents AS
WITH chartevents_per_ad AS (
    SELECT c.hadm_id, c.charttime, c.itemid, c.jvn_value as value
    FROM chartevents c INNER JOIN v_adult_admission v ON c.hadm_id = v.hadm_id
    WHERE c.jvn_value IS NOT NULL
    ORDER BY c.charttime ASC),
min_charttime_per_ad AS (
    SELECT hadm_id, MIN(charttime) as min_charttime
    FROM chartevents_per_ad
    GROUP BY hadm_id
),
chartevents_per_hour AS (
    SELECT C.hadm_id, C.charttime, M.min_charttime,
        (DATE_PART('day', C.charttime::timestamp - M.min_charttime::timestamp) * 24 +
        DATE_PART('hour', C.charttime::timestamp - M.min_charttime::timestamp))
        AS hours_ago, C.itemid AS conceptid, C.value
    FROM chartevents_per_ad as C
        INNER JOIN min_charttime_per_ad as M ON C.hadm_id = M.hadm_id)

SELECT hours_ago, hadm_id, COUNT(1) as numEvents
FROM chartevents_per_hour
GROUP BY hadm_id, hours_ago
ORDER BY hours_ago, hadm_id;