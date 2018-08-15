
DROP MATERIALIZED VIEW IF EXISTS v_train_data CASCADE;
CREATE MATERIALIZED VIEW v_train_data AS

WITH chartevents_per_ad AS (
    SELECT hadm_id, charttime, itemid, value, valuenum
    FROM chartevents)

SELECT C.hadm_id, (DATE_PART('day',
    C.charttime::timestamp - M.min_charttime::timestamp) * 24 +
    DATE_PART('hour',
    C.charttime::timestamp - M.min_charttime::timestamp) * 60 +
    DATE_PART('minute',
    C.charttime::timestamp - M.min_charttime::timestamp))
    AS minutes_ago, itemid, value, valuenum
FROM chartevents_per_ad as C
    INNER JOIN (
        SELECT hadm_id, MIN(charttime) as min_charttime
        FROM chartevents_per_ad
        GROUP BY hadm_id) as M ON C.hadm_id = M.hadm_id
ORDER BY hadm_id ASC, minutes_ago ASC, itemid ASC;


DROP INDEX IF EXISTS VIEW_TRAIN_DATA_idx02;
CREATE INDEX VIEW_TRAIN_DATA_idx02
  ON v_train_data (HADM_ID);