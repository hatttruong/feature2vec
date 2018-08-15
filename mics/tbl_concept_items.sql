-- create concept table
DROP TABLE IF EXISTS jvn_concepts CASCADE;
CREATE TABLE jvn_concepts(
    conceptid SERIAL PRIMARY KEY,
    concept varchar(200) NOT NULL,
    unitname varchar(100)

);

-- create mapping_concept table
DROP TABLE IF EXISTS jvn_mapping_concept CASCADE;
CREATE TABLE jvn_mapping_concept(
    conceptid integer REFERENCES jvn_concepts(conceptid),
    itemid integer,
    PRIMARY KEY (conceptid, itemid)
);

-- create mapping value table
DROP TABLE IF EXISTS jvn_mapping_value CASCADE;
CREATE TABLE jvn_mapping_value(
    conceptid integer,
    value varchar(200),
    unified_value varchar(200),
    PRIMARY KEY (conceptid, value)
);