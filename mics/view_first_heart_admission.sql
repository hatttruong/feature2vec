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
)

-- filter the first admission, adult (>=15), and not dead at hospital
SELECT a.*, h.icd9_code, h.heart_group
FROM v_first_adult_admission a
    INNER JOIN heart_admission h ON a.hadm_id = h.hadm_id
ORDER BY a.subject_id, a.admittime, a.intime;
