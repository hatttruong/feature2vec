
DROP MATERIALIZED VIEW IF EXISTS v_adult_admission CASCADE;
CREATE MATERIALIZED VIEW v_adult_admission AS
WITH admission_detail AS (
    SELECT
        -- patient level factors
        p.subject_id, p.dob, p.gender

        -- hospital level factors
        , a.hadm_id, a.admittime, a.dischtime, a.deathtime
        -- length of stay in hospital in factional days
        , ROUND( (CAST(EXTRACT(epoch FROM a.dischtime - a.admittime)/(60*60*24) AS numeric)), 4) AS los_hospital
        , ROUND( (CAST(EXTRACT(epoch FROM a.admittime - p.dob)/(60*60*24*365.242) AS numeric)), 4) AS admission_age
        , a.ethnicity, a.admission_type, a.admission_location, a.discharge_location
        , a.insurance, a.language, a.religion, a.marital_status, a.diagnosis
        , a.hospital_expire_flag
        , DENSE_RANK() OVER (PARTITION BY a.subject_id ORDER BY a.admittime) AS hospstay_seq
        , CASE
            WHEN DENSE_RANK() OVER (PARTITION BY a.subject_id ORDER BY a.admittime) = 1 THEN True
            ELSE False END AS first_hosp_stay

        -- icu level factors
        , ie.intime, ie.outtime
        -- distance between admission time and start to be in ICU in minutes
        , ROUND( (CAST(EXTRACT(epoch FROM ie.intime - a.admittime)/60 AS numeric)) ) AS minutes_before_icu
        -- length of stay in ICU with unit = minutes
        , ROUND( (CAST(EXTRACT(epoch FROM ie.outtime - ie.intime)/60 AS numeric)) ) AS los_icu_m
        -- length of stay in ICU with unit = factional hours
        , ROUND( (CAST(EXTRACT(epoch FROM ie.outtime - ie.intime)/(60*60) AS numeric)), 4) AS los_icu_h
        , DENSE_RANK() OVER (PARTITION BY ie.hadm_id ORDER BY ie.intime) AS icustay_seq

        -- first ICU stay *for the current hospitalization*
        , CASE
            WHEN DENSE_RANK() OVER (PARTITION BY ie.hadm_id ORDER BY ie.intime) = 1 THEN True
            ELSE False END AS first_icu_stay

    FROM patients p
        INNER JOIN admissions a ON p.subject_id = a.subject_id
        INNER JOIN icustays ie  ON ie.hadm_id = a.hadm_id
    WHERE a.has_chartevents_data = 1
)

-- filter adult (>=15), and not dead at hospital
SELECT * FROM admission_detail
WHERE
    first_icu_stay = True
    AND admission_age >= 15
    AND deathtime IS NULL
ORDER BY subject_id, admittime, intime;
