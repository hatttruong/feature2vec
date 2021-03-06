DROP TABLE IF EXISTS jvn_item_mapping CASCADE;
DROP TABLE IF EXISTS jvn_value_mapping CASCADE;
DROP TABLE IF EXISTS jvn_concepts CASCADE;
DROP TABLE IF EXISTS jvn_items CASCADE;

-- create concept table
CREATE TABLE jvn_concepts(
    conceptid SERIAL PRIMARY KEY,
    concept varchar(200) NOT NULL,
    isnumeric boolean,
    linksto varchar(50),
    created_by varchar(100)
);

-- create mapping_concept table
CREATE TABLE jvn_items(
    itemid integer,
    label varchar(200),
    abbr varchar(100),
    dbsource varchar(20),
    linksto varchar(50),
    isnumeric boolean,
    unit varchar(50),
    min_value double precision,
    percentile25th double precision,
    percentile50th double precision,
    percentile75th double precision,
    max_value double precision,
    distribution_img varchar(500)
    PRIMARY KEY (itemid)
);

-- create mapping_concept table
CREATE TABLE jvn_item_mapping(
    itemid integer REFERENCES jvn_items(itemid),
    conceptid integer REFERENCES jvn_concepts(conceptid),
    label_score double precision,
    value_score double precision,
    PRIMARY KEY (itemid, conceptid)
);


-- create mapping value table
CREATE TABLE jvn_value_mapping(
    itemid integer REFERENCES jvn_items(itemid),
    value varchar(200),
    unified_value varchar(200),
    PRIMARY KEY (itemid, value)
);

---------------------------------
-- rename column in Postgresql --
-- ALTER TABLE mimiciii.jvn_items RENAME COLUMN min TO min_value;
-- ALTER TABLE mimiciii.jvn_items RENAME COLUMN max TO max_value;
-- ALTER TABLE mimiciii.jvn_items DROP COLUMN IF EXISTS category_values;