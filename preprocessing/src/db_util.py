"""Summary

Attributes:
    logger (TYPE): Description
"""
from src.connect_db import *
import logging

logger = logging.getLogger(__name__)


def get_d_items():
    """
    Get all d_items

    Returns:
        TYPE: Description
    """
    query = 'SELECT * FROM d_items;'
    df = execute_query_to_df(query)
    return df


def get_chartevents_by_ids(item_ids, output_path=None):
    """
    Get all chartevents by item ids

    Returns:
        TYPE: Description

    Args:
        item_ids (TYPE): Description
        output_path (None, optional): Description
    """
    param = ','.join([str(x) for x in item_ids])
    # query = 'SELECT value FROM chartevents WHERE itemid in (%s) \
    #     and value is not null;' % param
    query = 'SELECT VALUENUM as value FROM chartevents WHERE itemid in (%s) \
        and VALUENUM is not null;' % param

    logger.info('query="%s"', query)
    df = execute_query_to_df(query)
    logger.info('query finishes')

    if output_path is not None:
        df.to_csv(output_path, index=False)

    return df


def get_events_by_admission(admission_id, event_types=['chartevents']):
    """
    Get all events by admission including
        chartevents, inputevents, outputevents, microbiologyevents
    In sample demo, we consider only chartvents

    TODO: inner join with jvn_concepts to get concepid instead of itemid

    Args:
        admission_id (TYPE): Description
        itemids (None, optional): Description

    Returns:
        TYPE: Description
    """
    queries = []
    for t in event_types:
        if t == 'chartevents':
            queries.append(
                "WITH chartevents_per_ad AS ( \
                    SELECT hadm_id, charttime, itemid, jvn_value as value \
                    FROM chartevents \
                    WHERE hadm_id=%s AND jvn_value IS NOT NULL \
                    ORDER BY charttime ASC) \
                SELECT hadm_id, (DATE_PART('day', \
                    C.charttime::timestamp - M.min_charttime::timestamp) * 24 + \
                    DATE_PART('hour', \
                    C.charttime::timestamp - M.min_charttime::timestamp) * 60 + \
                    DATE_PART('minute', \
                    C.charttime::timestamp - M.min_charttime::timestamp)) \
                    AS minutes_ago, itemid AS conceptid, value \
                FROM chartevents_per_ad as C, \
                    (SELECT MIN(charttime) as min_charttime \
                    FROM chartevents_per_ad) as M " % (admission_id))
        elif t == 'outputevents':
            pass
        elif t == 'inputevents':
            pass

    if len(queries) > 1:
        queries = ['(%s)' % q for q in queries]
        query = ' UNION ALL '.join(queries)
    else:
        query = queries[0]

    logger.debug('query=\n"%s"\n', query)
    df = execute_query_to_df(query)
    logger.debug('get_events_by_admission finishes, result=%s', df.shape[0])
    return df


def get_admissions():
    """
    Get all admissions of adult patients who is not dead at hospital

    Returns:
        TYPE: Description
    """
    # get all admission id
    # loop through each admission and get its event value
    query = "SELECT DISTINCT hadm_id, gender, marital_status, admission_type, \
            admission_age, admission_location, los_icu_h \
        FROM v_adult_admission"
    df = execute_query_to_df(query)
    return df


def load_concepts():
    """
    return list of item_id
    TODO: after updating concept, return list of conceptid
    """
    linksto_list = [
        # 'outputevents',
        # 'inputevents_cv',
        # 'inputevents_mv',
        'chartevents'
    ]
    # query = "SELECT DISTINCT conceptid, label, linksto \
    #     FROM jvn_concepts WHERE linksto IN ('%s') " % "', '".join(linksto)
    queries = list()
    for linksto in linksto_list:
        if linksto is 'chartevents':
            queries.append("SELECT DISTINCT D.itemid as conceptid, D.label, \
                'chartevents' as linksto \
                FROM chartevents as C \
                    INNER JOIN d_items as D ON C.itemid = D.itemid\
                WHERE C.value IS NOT NULL ")
        elif linksto is 'outputevents':
            # TODO
            pass
        elif linksto is 'inputevents_cv':
            # TODO
            pass
        elif linksto is 'inputevents_mv':
            # TODO
            pass

    query = ''
    if len(queries) > 1:
        queries = ['(%s)' % q for q in queries]
        query = ' UNION ALL '.join(queries) + ' ORDER BY linksto, conceptid'
    elif len(queries) == 1:
        query = queries[0]

    df = execute_query_to_df(query)
    return df


def load_actual_items():
    """
    return list of item_id which is actually used in chartevents, input, output
    """
    linksto_list = [
        # 'outputevents',
        # 'inputevents_cv',
        # 'inputevents_mv',
        'chartevents'
    ]
    # query = "SELECT DISTINCT conceptid, label, linksto \
    #     FROM jvn_concepts WHERE linksto IN ('%s') " % "', '".join(linksto)
    queries = list()
    for linksto in linksto_list:
        if linksto is 'chartevents':
            queries.append(
                "SELECT DISTINCT D.itemid, D.label, \
                    'chartevents' as linksto \
                FROM chartevents as C \
                    INNER JOIN d_items as D ON C.itemid = D.itemid\
                WHERE C.value IS NOT NULL ")
        elif linksto is 'outputevents':
            # TODO
            pass
        elif linksto is 'inputevents_cv':
            # TODO
            pass
        elif linksto is 'inputevents_mv':
            # TODO
            pass

    query = ''
    if len(queries) > 1:
        queries = ['(%s)' % q for q in queries]
        query = ' UNION ALL '.join(queries) + ' ORDER BY linksto, itemid'
    elif len(queries) == 1:
        query = queries[0]

    df = execute_query_to_df(query)
    return df


def load_item2concepts():
    """
    return dataframe of item_id, itemid
    TODO: after updating concept, return dataframe of item_id, itemid
    """
    # query = "SELECT DISTINCT itemid, conceptid from d_items "
    query = "SELECT DISTINCT itemid, itemid as conceptid FROM d_items "
    df = execute_query_to_df(query)
    return df


def load_values_of_concept(conceptid, linksto):
    """
    load all values of item_id from chartevents table

    Args:
        conceptid (TYPE): Description
        linksto (TYPE): Description

    Returns:
        TYPE: Description
    """
    # TODO: query by concepts
    # conditions = 'itemid IN (SELECT itemid FROM d_items WHERE
    # conceptid=%s)'" % conceptid

    condition = 'itemid = %s' % conceptid
    query = ''
    if linksto == 'chartevents':
        query = "SELECT itemid, value, valuenum FROM chartevents \
            WHERE value is not NULL AND (error is NULL or error != 1) \
                AND %s " % condition

    elif linksto == 'outputevents':
        query = "SELECT itemid, value, value as valuenum FROM outputevents \
            WHERE value is not NULL AND (iserror is NULL OR iserror != 1) \
                AND %s " % condition

    elif linksto == 'inputevents':
        query = "SELECT itemid, amount as value, amount as valuenum \
            FROM inputevents_cv \
            WHERE amount is not NULL AND %s \
            UNION ALL \
            SELECT itemid, amount as value, amount as valuenum \
            FROM inputevents_mv \
            WHERE amount is not NULL AND %s " % (condition, condition)

    df = execute_query_to_df(query)
    return df


def load_values_of_itemid(itemid, linksto):
    """
    load all values of item_id from chartevents table

    Args:
        itemid (TYPE): Description
        linksto (TYPE): Description

    Returns:
        TYPE: Description
    """

    condition = 'itemid = %s' % itemid
    query = ''
    if linksto == 'chartevents':
        query = "SELECT itemid, value, valuenum FROM chartevents \
            WHERE value is not NULL AND (error is NULL or error != 1) \
                AND %s " % condition

    elif linksto == 'outputevents':
        query = "SELECT itemid, value, value as valuenum FROM outputevents \
            WHERE value is not NULL AND (iserror is NULL OR iserror != 1) \
                AND %s " % condition

    elif linksto == 'inputevents':
        query = "SELECT itemid, amount as value, amount as valuenum \
            FROM inputevents_cv \
            WHERE amount is not NULL AND %s \
            UNION ALL \
            SELECT itemid, amount as value, amount as valuenum \
            FROM inputevents_mv \
            WHERE amount is not NULL AND %s " % (condition, condition)

    df = execute_query_to_df(query)
    return df


def get_auto_clustered_itemids():
    query = 'SELECT DISTINCT itemid \
        FROM jvn_item_mapping as i \
            INNER JOIN jvn_concepts as c ON i.conceptid=c.conceptid \
        WHERE i.value_score >= 90 '
    df = execute_query_to_df(query)

    if df.shape[0] > 0:
        return df['itemid'].tolist()
    else:
        return []


def insert_jvn_items(itemid, label, abbr, dbsource, linksto, isnumeric,
                     min_value=None, max_value=None,
                     percentile25th=None, percentile50th=None,
                     percentile75th=None, distributionImg=None,
                     values=None):
    insert_query = ''
    label = str(label).replace("'", "''")
    abbr = str(abbr).replace("'", "''")
    if isnumeric:
        insert_query = "INSERT INTO jvn_items \
            (itemid, label, abbr, dbsource, linksto, isnumeric, min_value, \
             max_value, percentile25th, percentile50th, percentile75th, \
             distribution_img) VALUES \
             (%s, '%s', '%s', '%s', '%s', '%s', %s, %s, %s, %s, %s, '%s') \
            ON CONFLICT(itemid) DO NOTHING" % (
            itemid, label, abbr, dbsource, linksto, isnumeric, min_value,
            max_value, percentile25th, percentile50th, percentile75th,
            distributionImg)
    else:
        insert_query = "INSERT INTO jvn_items \
            (itemid, label, abbr, dbsource, linksto, isnumeric) \
            VALUES (%s, '%s', '%s', '%s', '%s', '%s') \
            ON CONFLICT(itemid) DO NOTHING" % (
            itemid, label, abbr, dbsource, linksto, isnumeric)

    execute_non_query(insert_query)

    if isnumeric is False and values is not None:
        for value in values:
            value = str(value).replace("'", "''")
            insert_query = "INSERT INTO \
                jvn_value_mapping (itemid, value, unified_value) \
                VALUES (%s, '%s', '%s') \
                ON CONFLICT(itemid, value) DO NOTHING" % (itemid, value, value)
            execute_non_query(insert_query)


def insert_generated_concept(concept_obj):
    """Summary

    Args:
        concept_obj (TYPE): Description

    Returns:
        TYPE: Description
    """
    # insert concept
    insert_query = "INSERT INTO jvn_concepts \
        (concept, isnumeric, linksto, created_by) \
        VALUES ('%s', %s, '%s', 'SYS')" % (
        concept_obj['concept'].replace("'", "''"),
        concept_obj['isnumeric'],
        concept_obj['linksto'])
    execute_non_query(insert_query)

    # get conceptid
    query = "SELECT last_value FROM jvn_concepts_conceptid_seq"
    df = execute_query_to_df(query)
    conceptid = df['last_value'].tolist()[0]

    # insert jvn_item_mapping
    for itemid, score in concept_obj['items'].items():
        insert_query = "INSERT INTO jvn_item_mapping \
            (itemid, conceptid, label_score, value_score) \
            VALUES (%s, %s, %s, %s)" % (
            itemid, conceptid, score['label_score'], score['value_score'])
        execute_non_query(insert_query)
