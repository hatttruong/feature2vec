DROP TABLE IF EXISTS jvn_los_groups CASCADE;

-- create concept table
CREATE TABLE jvn_los_groups(
    group_id integer,
    lower_bound integer,
    upper_bound integer,
    PRIMARY KEY (group_id)
);