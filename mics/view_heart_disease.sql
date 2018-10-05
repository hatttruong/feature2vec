-- 390-459 Diseases Of The Circulatory System
--      393-398  Chronic Rheumatic Heart Disease
--      410-414  Ischemic Heart Disease
--      420-429  Other Forms Of Heart Disease
-- 746 Other congenital anomalies of heart: BETWEEN '7461 ' AND '7469 '
-- 785 Symptoms involving cardiovascular system: '7850', '7851', '7852', '7853'
-- 786.5 Chest pain
-- TOTAL: 3416 admissions

DROP MATERIALIZED VIEW IF EXISTS v_first_heart_admission CASCADE;
CREATE MATERIALIZED VIEW v_first_heart_admission AS
WITH icd AS
(
    SELECT hadm_id
        , cast(icd9_code AS char(5)) AS icd9_code
    FROM diagnoses_icd
    WHERE seq_num = 1
),
drg_admission AS
(
    SELECT  hadm_id, icd9_code
        , CASE
            /*393-398  Chronic Rheumatic Heart Disease*/
            WHEN icd9_code BETWEEN '393  ' AND '398  ' THEN 'Chronic Rheumatic Heart Disease'

            /*410-414  Ischemic Heart Disease*/
            WHEN icd9_code BETWEEN '410  ' AND '414  ' THEN 'Ischemic Heart Disease'

            /*420-429  Other Forms Of Heart Disease*/
            WHEN icd9_code BETWEEN '420  ' AND ' 425 ' THEN 'Other Forms Of Heart Disease'
            WHEN icd9_code BETWEEN '427  ' AND ' 429 ' THEN 'Other Forms Of Heart Disease'

            /*746 Other congenital anomalies of heart: BETWEEN '7461 ' AND '7469 '*/
            WHEN icd9_code BETWEEN '7463 ' AND '7466 ' THEN 'Other congenital anomalies of heart'

            /*785 Symptoms involving cardiovascular system: '7850', '7851', '7852', '7853'*/
            WHEN icd9_code BETWEEN '7850 ' AND '7853 ' THEN 'Symptoms involving cardiovascular system'

            /*786.5 Chest pain*/
            WHEN icd9_code IN ('78650', '78651', '78659') THEN 'Chest pain'

            ELSE 'NONE'
            END AS heart_group

    FROM icd
),
heart_admission AS (
    SELECT  hadm_id, icd9_code, heart_group
    FROM drg_admission
    WHERE heart_group != 'NONE'
    ORDER BY hadm_id
),

heart_admission_detail AS (
    SELECT
        -- patient level factors
        p.subject_id, p.dob, p.gender

        -- hospital level factors
        , a.hadm_id, a.admittime, a.dischtime, a.deathtime
        , ROUND( (CAST(EXTRACT(epoch FROM a.dischtime - a.admittime)/(60*60*24) AS numeric)), 4) AS los_hospital
        , ROUND( (CAST(EXTRACT(epoch FROM a.admittime - p.dob)/(60*60*24*365.242) AS numeric)), 4) AS admission_age
        , a.ethnicity, a.admission_type, a.admission_location, a.discharge_location
        , a.insurance, a.language, a.religion, a.marital_status, a.diagnosis
        , a.hospital_expire_flag
        , DENSE_RANK() OVER (PARTITION BY a.subject_id ORDER BY a.admittime) AS hospstay_seq
        , CASE
            WHEN DENSE_RANK() OVER (PARTITION BY a.subject_id ORDER BY a.admittime) = 1 THEN True
            ELSE False END AS first_hosp_stay

        -- diagnosis info
        , h.icd9_code, h.heart_group

        -- icu level factors
        , ie.intime, ie.outtime
        , ROUND( (CAST(EXTRACT(epoch FROM ie.outtime - ie.intime)/(60*60*24) AS numeric)), 4) AS los_icu
        , DENSE_RANK() OVER (PARTITION BY ie.hadm_id ORDER BY ie.intime) AS icustay_seq

        -- first ICU stay *for the current hospitalization*
        , CASE
            WHEN DENSE_RANK() OVER (PARTITION BY ie.hadm_id ORDER BY ie.intime) = 1 THEN True
            ELSE False END AS first_icu_stay

    FROM patients p
        INNER JOIN admissions a ON p.subject_id = a.subject_id
        INNER JOIN heart_admission h ON a.hadm_id = h.hadm_id
        INNER JOIN icustays ie  ON ie.hadm_id = a.hadm_id
    WHERE a.has_chartevents_data = 1
)

-- filter the first admission, adult (>=15), and not dead at hospital
SELECT * FROM heart_admission_detail
WHERE
    first_hosp_stay = True
    AND first_icu_stay = True
    AND admission_age >= 15
    AND deathtime IS NULL
ORDER BY subject_id, admittime, intime;

/*
select gender, avg(los_icu), min(los_icu), max(los_icu), avg(los_hospital), min(los_hospital), max(los_hospital)
from v_first_heart_admission
group by gender;
*/