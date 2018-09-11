ALTER TABLE chartevents
DROP COLUMN IF EXISTS jvn_value;

ALTER TABLE chartevents
ADD COLUMN jvn_value character varying(255);