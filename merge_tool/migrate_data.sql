-- Migrate data from mimiciii.* to public.
-- JvnItems
INSERT INTO "JvnItems" (itemid,
                        label,
                        abbr,
                        dbsource,
                        linksto,
                        isnumeric,
                        unit,
                        min_value,
                        percentile25th,
                        percentile50th,
                        percentile75th,
                        max_value,
                        distribution_img,
                        "createdAt",
                        "updatedAt")
SELECT  itemid,
        label,
        abbr,
        dbsource,
        linksto,
        isnumeric,
        unit,
        min_value,
        percentile25th,
        percentile50th,
        percentile75th,
        max_value,
        distribution_img,
        current_timestamp as createdAt,
        current_timestamp as updatedAt
FROM mimiciii.jvn_items;

-- JvnConcepts
INSERT INTO "JvnConcepts" (conceptid,
                          concept,
                          isnumeric,
                          linksto,
                          created_by,
                          "createdAt",
                          "updatedAt")
SELECT conceptid,
       concept,
       isnumeric,
       linksto,
       created_by,
       current_timestamp as createdAt,
       current_timestamp as updatedAt
FROM mimiciii.jvn_concepts;

-- JvnItemMappings:
INSERT INTO "JvnItemMappings" (conceptid,
                               itemid,
                               label_score,
                               value_score,
                               "createdAt",
                               "updatedAt")
SELECT  conceptid,
        itemid,
        label_score,
        value_score,
        current_timestamp as createdAt,
        current_timestamp as updatedAt
FROM mimiciii.jvn_item_mapping;
