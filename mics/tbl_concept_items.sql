-- create concept table
DROP TABLE IF EXISTS jvn_concepts CASCADE;
CREATE TABLE jvn_concepts(
    conceptid SERIAL PRIMARY KEY,
    concept varchar(200) NOT NULL,
    created_by varchar(100)
);

-- create mapping_concept table
DROP TABLE IF EXISTS jvn_item_mapping CASCADE;
CREATE TABLE jvn_item_mapping(
    itemid integer,
    label varchar(200),
    abbr varchar(100),
    dbsource varchar(20),
    linksto varchar(50),
    isnumeric boolean,
    unit varchar(50),
    min double precision,
    max double precision,
    percentile25th double precision,
    percentile50th double precision,
    percentile75th double precision,
    category_values varchar(500),
    distribution_img varchar(500),
    candidate_conceptid integer REFERENCES jvn_concepts(conceptid),
    conceptid integer REFERENCES jvn_concepts(conceptid),
    PRIMARY KEY (itemid)
);

-- create mapping value table
DROP TABLE IF EXISTS jvn_value_mapping CASCADE;
CREATE TABLE jvn_value_mapping(
    conceptid integer,
    value varchar(200),
    unified_value varchar(200),
    PRIMARY KEY (conceptid, value)
);