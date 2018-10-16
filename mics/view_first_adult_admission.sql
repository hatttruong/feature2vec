DROP MATERIALIZED VIEW IF EXISTS v_first_adult_admission CASCADE;
CREATE MATERIALIZED VIEW v_first_adult_admission AS

-- filter first admission, adult (>=15), and not dead at hospital
SELECT *
FROM v_adult_admission
WHERE first_hosp_stay = True
ORDER BY subject_id, admittime, intime;