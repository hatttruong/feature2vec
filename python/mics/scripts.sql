# ===========================================================================
# Count the number of the first admission and group by age group FOR heart diseases
# ===========================================================================
WITH age as
(
  SELECT *
      , CASE
          -- all ages > 89 in the database were replaced with 300
          -- we check using > 100 as a conservative threshold to ensure we capture all these patients
          WHEN admission_age > 100
              then '>89'
          WHEN admission_age >= 14
              THEN 'adult'
          WHEN admission_age <= 1
              THEN 'neonate'
          ELSE 'middle'
          END AS age_group
  FROM v_first_heart_admission
)
select age_group, gender
  , count(hadm_id) as NumberOfAdmissions
from age
group by age_group, gender;


# =============================================================================
# select top chart events
# there are XXX chart events
# =============================================================================
WITH top_chart_events AS
(
    SELECT c.hadm_id, c.itemid, count(1) as ct
    FROM chartevents c
        INNER JOIN v_first_heart_admission v ON v.hadm_id = c.hadm_id
    WHERE v.los_icu >= 1
    GROUP BY c.HADM_ID, c.itemid
)
SELECT t.itemid, i.label, count(t.hadm_id) as count_admissions
FROM top_chart_events as t
    INNER JOIN d_items as i ON t.itemid = i.itemid
GROUP BY t.itemid, i.label
ORDER BY count_admissions DESC;


# =============================================================================
# select input events
# =============================================================================
WITH top_input_events AS
(
    SELECT icv.hadm_id, icv.itemid, count(1) as ct
    FROM inputevents_cv icv
        INNER JOIN v_first_heart_admission v ON v.hadm_id = icv.hadm_id
    WHERE v.los_icu >= 1
    GROUP BY icv.hadm_id, icv.itemid

    UNION

    SELECT imv.hadm_id, imv.itemid, count(1) as ct
    FROM inputevents_mv imv
        INNER JOIN v_first_heart_admission v ON v.hadm_id = imv.hadm_id
    WHERE v.los_icu >= 1
    GROUP BY imv.hadm_id, imv.itemid
    HAVING count(1) > 100
)
SELECT t.itemid, i.label, count(t.hadm_id) as count_admissions
FROM top_input_events as t
    INNER JOIN d_items as i ON t.itemid = i.itemid
GROUP BY t.itemid, i.label
ORDER BY count_admissions DESC;

# =============================================================================
# select top output events
# =============================================================================
WITH top_output_events AS
(
    SELECT o.hadm_id, o.itemid, count(1) as ct
    FROM outputevents o
        INNER JOIN v_first_heart_admission v ON v.hadm_id = o.hadm_id
    WHERE v.los_icu >= 1
    GROUP BY o.hadm_id, o.itemid
)
SELECT t.itemid, i.label, count(t.hadm_id) as count_admissions
FROM top_output_events as t
    INNER JOIN d_items as i ON t.itemid = i.itemid
GROUP BY t.itemid, i.label
ORDER BY count_admissions DESC;


# =============================================================================
# query count chartevents
# =============================================================================
WITH top_chart_events AS
(
    SELECT c.hadm_id, jc.conceptid, jc.concept, count(1) as ct
    FROM chartevents c
        INNER JOIN jvn_concepts jc ON c.itemid = jc.itemid_mv OR c.itemid = jc.itemid_cv
        INNER JOIN v_first_heart_admission v ON v.hadm_id = c.hadm_id
    WHERE v.los_icu >= 1 AND c.value is not null
        --AND c.itemid IN (211, 220045, 618, 220210, 814,220228)
        AND c.charttime <= (v.admittime + interval '24 hour')
    GROUP BY c.hadm_id, jc.conceptid, jc.concept
    HAVING count(1) >= 10
)
SELECT t.conceptid, t.concept, count(t.hadm_id) as count_admissions,
    min(t.ct) as min_items, max(t.ct) as max_items, avg(t.ct) as avg_items
FROM top_chart_events as t
GROUP BY t.conceptid, t.concept
ORDER BY count_admissions DESC;
