"""Summary

Attributes:
    logger (TYPE): Description
"""
from src.connect_db import *
import logging
import pandas as pd
import os

logger = logging.getLogger(__name__)


def get_all_ditems():
    """Summary

    Returns:
        TYPE: Description
    """
    query = 'SELECT * FROM d_items'
    df = execute_query_to_df(query)
    return df


def get_d_items_from_cv():
    """Summary

    Returns:
        TYPE: Description
    """
    query = 'SELECT * FROM d_items WHERE itemid < 220000'
    df = execute_query_to_df(query)
    return df


def get_d_items_from_mv():
    """Summary

    Returns:
        TYPE: Description
    """
    query = 'SELECT * FROM d_items WHERE itemid > 220000'
    df = execute_query_to_df(query)
    return df


def get_chartevents_of_icd(icd_code):
    """Summary

    Args:
        icd_code (TYPE): Description

    Returns:
        TYPE: Description
    """
    query = "SELECT distinct c.itemid \
        FROM diagnoses_icd d \
            INNER JOIN chartevents c ON d.hadm_id = c.hadm_id \
        WHERE d.icd9_code='%s';" % icd_code
    rows = execute_query(query)
    return [r['itemid'] for r in rows]


def get_top_icd_codes(k):
    """Summary

    Args:
        k (TYPE): Description

    Returns:
        TYPE: Description
    """
    query = 'SELECT d.icd9_code, dd.short_title, dd.long_title, count(1) as ct \
        FROM diagnoses_icd d \
        INNER JOIN d_icd_diagnoses dd ON d.icd9_code = dd.icd9_code \
        GROUP BY d.icd9_code, dd.short_title, dd.long_title \
        ORDER BY ct DESC \
        LIMIT % s ' % k
    logger.info('get top %s icd codes', k)
    rows = execute_query(query)
    icd_codes = list()
    for r in rows:
        item = dict()
        item['icd_code'] = r['icd9_code']
        logger.info('get list distinct chartevents of icd %s',
                    item['icd_code'])
        item['chartevent_ids'] = get_chartevents_of_icd(item['icd_code'])
        icd_codes.append(item)

    return pd.DataFrame.from_dict(icd_codes)


def get_dist_icd_hadm():
    """Summary

    Returns:
        TYPE: Description
    """
    query = 'SELECT C.ct as count_icd, count(1) as count_hadm \
        FROM \
            (SELECT hadm_id, count(1) as ct \
            FROM diagnoses_icd d \
            GROUP BY hadm_id \
            ORDER BY ct DESC \
            ) as C \
        GROUP BY count_icd \
        ORDER BY count_icd;'
    df = execute_query_to_df(query)
    return df


def get_dist_sub_icd_hadm():
    """Summary

    Returns:
        TYPE: Description
    """
    query = 'SELECT C.count_sub_icd as count_sub_icd, count(1) as count_hadm \
        FROM ( \
            SELECT sc.hadm_id, count(1) as count_sub_icd \
            FROM \
                (SELECT substring(d.icd9_code,1,3) as sub_code, hadm_id \
                FROM diagnoses_icd d \
                ) as sc \
            GROUP BY sc.hadm_id \
            ORDER BY count_sub_icd DESC \
            )  as C \
        GROUP BY count_sub_icd \
        ORDER BY count_sub_icd;'
    df = execute_query_to_df(query)
    return df


def get_number_hadm_per_sub_icd():
    """
    Calculate number of hadm per sub icd code

    Returns:
        TYPE: Description
    """
    query = 'SELECT substring(d.icd9_code,1,3) as sub_code, count(1) as count_hadm \
        FROM diagnoses_icd d \
        GROUP BY sub_code \
        ORDER BY count_hadm DESC;'
    df = execute_query_to_df(query)
    return df


def get_number_hadm_per_icd():
    """
    Calculate number of hadm per icd code

    Returns:
        TYPE: Description
    """
    query = 'SELECT d.icd9_code, count(1) as count_hadm \
        FROM diagnoses_icd d \
        GROUP BY d.icd9_code \
        ORDER BY count_hadm DESC;'
    df = execute_query_to_df(query)
    return df


def get_diagnoses_icd():
    """
    Get all diagnoses_icd

    Returns:
        TYPE: Description
    """
    query = 'SELECT * FROM diagnoses_icd;'
    df = execute_query_to_df(query)
    return df


def get_chartevents():
    """
    Get all chartevents

    Returns:
        TYPE: Description
    """
    query = 'SELECT * FROM chartevents;'
    df = execute_query_to_df(query)
    return df


def get_admissions():
    """
    Get all dmissions

    Returns:
        TYPE: Description
    """
    query = 'SELECT * FROM admissions;'
    df = execute_query_to_df(query)
    return df


def get_patients():
    """
    Get all dmissions

    Returns:
        TYPE: Description
    """
    query = 'SELECT * FROM patients;'
    df = execute_query_to_df(query)
    return df


def get_chartevents_for_CVD():
    """
    get list chartevents for CVD

    Returns:
        TYPE: Description
    """
    logger.info('start loading chartevents for CVD from database')
    query = "WITH top_chart_events AS \
        ( \
            SELECT c.hadm_id, c.itemid, count(1) as ct \
            FROM chartevents c \
                INNER JOIN v_first_heart_admission v ON v.hadm_id = c.hadm_id \
            WHERE v.los_icu >= 1 \
                 AND c.charttime <= (v.admittime + interval '24 hour') \
            GROUP BY c.HADM_ID, c.itemid \
            HAVING count(1) >= 10 \
        ) \
        SELECT t.itemid, i.label, count(t.hadm_id) as count_admissions, \
            min(t.ct) as min_items, max(t.ct) as max_items, avg(t.ct) as avg_items \
        FROM top_chart_events as t \
            INNER JOIN d_items as i ON t.itemid = i.itemid \
        GROUP BY t.itemid, i.label \
        ORDER BY count_admissions DESC;"
    df = execute_query_to_df(query)
    logger.info('done loading chartevents for CVD from database')
    return df


def get_inputevents_for_CVD():
    """
    get list input events for CVD

    Returns:
        TYPE: Description
    """
    logger.info('start loading inputevents for CVD from database')
    query = 'WITH top_input_events AS \
        ( \
            SELECT icv.hadm_id, icv.itemid, count(1) as ct \
            FROM inputevents_cv icv \
                INNER JOIN v_first_heart_admission v ON v.hadm_id = icv.hadm_id \
            WHERE v.los_icu >= 1 \
            GROUP BY icv.hadm_id, icv.itemid \
            UNION \
            SELECT imv.hadm_id, imv.itemid, count(1) as ct \
            FROM inputevents_mv imv \
                INNER JOIN v_first_heart_admission v ON v.hadm_id = imv.hadm_id \
            WHERE v.los_icu >= 1 \
            GROUP BY imv.hadm_id, imv.itemid \
        ) \
        SELECT t.itemid, i.label, count(t.hadm_id) as count_admissions \
        FROM top_input_events as t \
            INNER JOIN d_items as i ON t.itemid = i.itemid \
        GROUP BY t.itemid, i.label \
        ORDER BY count_admissions DESC;'
    df = execute_query_to_df(query)
    logger.info('done loading inputevents for CVD from database')
    return df


def count_outputevent_per_admission():
    """
    get list output events for CVD

    Returns:
        TYPE: Description
    """
    logger.info('start count_outputevent_per_admission for CVD from database')
    query = "SELECT o.hadm_id, o.itemid, count(1) as ct \
            FROM outputevents o \
                INNER JOIN v_first_heart_admission v ON v.hadm_id = o.hadm_id \
            WHERE v.los_icu >= 1 AND o.value is not null \
                 AND o.charttime <= (v.admittime + interval '24 hour') \
            GROUP BY o.hadm_id, o.itemid \
            ORDER BY o.hadm_id, o.itemid; "

    df = execute_query_to_df(query)
    logger.info('done count_outputevent_per_admission for CVD from database')
    return df


def count_labevent_per_admission():
    """
    get list lab events for CVD

    Returns:
        TYPE: Description
    """
    logger.info('start count_labevent_per_admission for CVD from database')
    query = "SELECT l.hadm_id, l.itemid, count(1) as ct \
            FROM labevents l \
                INNER JOIN v_first_heart_admission v ON v.hadm_id = l.hadm_id \
            WHERE v.los_icu >= 1 AND l.value is not null \
                 AND l.charttime <= (v.admittime + interval '24 hour') \
            GROUP BY l.hadm_id, l.itemid \
            ORDER BY l.hadm_id, l.itemid; "

    df = execute_query_to_df(query)
    logger.info('done count_labevent_per_admission for CVD from database')
    return df


def get_heart_items():
    """Summary

    Returns:
        TYPE: Description
    """
    query = "select * from d_items where lower(label) like '%heart%';"
    df = execute_query_to_df(query)
    return df


def get_concepts_for_CVD():
    """
    get list concepts for CVD

    HAVING count(1) >= 10 \

    Returns:
        TYPE: Description
    """
    logger.info('start loading concepts for CVD from database')
    query = "WITH top_concepts AS \
        ( \
            SELECT c.hadm_id, jc.conceptid, jc.concept, count(1) as ct \
            FROM chartevents c \
                INNER JOIN jvn_concepts jc \
                    ON c.itemid = jc.itemid_mv OR c.itemid = jc.itemid_cv \
                INNER JOIN v_first_heart_admission v ON v.hadm_id = c.hadm_id \
            WHERE v.los_icu >= 1 AND c.value is not null \
                AND c.charttime <= (v.admittime + interval '24 hour') \
            GROUP BY c.hadm_id, jc.conceptid, jc.concept \
        ) \
        SELECT t.conceptid, t.concept \
            , count(t.hadm_id) as count_admissions \
            , min(t.ct) as min_items \
            , max(t.ct) as max_items \
            , avg(t.ct) as avg_items \
        FROM top_concepts as t \
        GROUP BY t.conceptid, t.concept \
        ORDER BY count_admissions DESC;"
    df = execute_query_to_df(query)
    logger.info('done loading concepts for CVD from database')
    return df


def count_chartevent_per_admission():
    """
    Count number of time of each chartevent recorded for each admission

    Returns:
        TYPE: Description
    """
    logger.info(
        'start count number of time of each chartevent recorded for each admission')
    query = "SELECT c.hadm_id, c.itemid, count(1) as ct \
            FROM chartevents c \
                INNER JOIN v_first_heart_admission v ON v.hadm_id = c.hadm_id \
            WHERE v.los_icu >= 1 AND c.value is not null \
                 AND c.charttime <= (v.admittime + interval '24 hour') \
            GROUP BY c.HADM_ID, c.itemid \
            ORDER BY c.hadm_id, c.itemid; "
    df = execute_query_to_df(query)
    logger.info(
        'done count number of time of each chartevent recorded for each admission')
    return df


def count_values_for_categoric_items():
    """Summary

    Returns:
        TYPE: Description
    """
    logger.info('start count_values_for_categoric_items')
    items = [212, 220048, 617, 223985, 161, 224650, 162, 226479, 159, 224651,
             160, 226480, 1484, 223754, 1337, 223753, 674, 224642,
             220048, 224650, 226479, 916, 927, 935, 159, 224651, 593, 223987,
             1125, 224640, 1046, 223781, 599, 223986, 428, 223988, 425, 223989,
             547, 224093, 210, 3453, 224080, 223900, 223901, 707, 224015,
             706, 224016, 8480, 224876, 723, 223900, 454, 223901, 432, 226104,
             432, 226104, 478, 223999, 80, 224004, 82, 224056, 83, 224059,
             84, 224057, 85, 224055, 86, 224058, 88, 224054, 54, 224085,
             32, 224086, 550, 31, 224084, 156, 223934, 8381, 223943, ]
    query = "SELECT itemid, value, count(1) as ct FROM chartevents \
        WHERE itemid in (%s) and value is not null \
        GROUP BY itemid, value ORDER BY itemid, value" % ','.join(
            [str(i) for i in items])

    logger.info('query: %s', query)
    df = execute_query_to_df(query)
    logger.info('done count_values_for_categoric_items')
    return df


def export_detail_info_CVD():
    """Summary
    """
    # # export v_first_heart_admission: personal information
    # logger.info('export v_first_heart_admission')
    # query = "SELECT * FROM v_first_heart_admission v \
    #     ORDER BY v.hadm_id ASC; "
    # df = execute_query_to_df(query)
    # df.to_csv(
    #     os.path.join('data', 'raw_CVD', 'CVD_first_heart_admission.csv'),
    #     index=False)

    # # transfer information
    # logger.info('export transfers')
    # query = "SELECT t.subject_id, t.hadm_id, t.eventtype, \
    #         t.prev_careunit, t.curr_careunit, t.prev_wardid, t.curr_wardid, \
    #         t.intime, t.outtime, t.los \
    #     FROM transfers t \
    #         INNER JOIN v_first_heart_admission v ON v.hadm_id = t.hadm_id \
    #     WHERE t.intime <= (v.admittime + interval '24 hour') \
    #     ORDER BY t.hadm_id ASC, t.intime ASC; "
    # df = execute_query_to_df(query)
    # df.to_csv(
    #     os.path.join('data', 'raw_CVD', 'CVD_transfers.csv'), index=False)

    # get list d_items
    logger.info('get list d_items')
    query = "SELECT DISTINCT c.itemid \
        FROM chartevents c \
            INNER JOIN v_first_heart_admission v ON v.hadm_id = c.hadm_id \
        WHERE v.los_icu >= 1 AND c.value is not null \
             AND c.charttime <= (v.admittime + interval '24 hour'); "
    df = execute_query_to_df(query)

    itemids = df['itemid'].tolist()
    logger.info('number of d_item: %s', len(itemids))
    logger.info('start to export chartevents of each d_items')
    for itemid in itemids:
        file_name = os.path.join('data', 'raw_CVD',
                                 'CVD_chartevents_itemid_%s.csv' % itemid)

        if os.path.isfile(file_name):
            continue

        query = "SELECT c.subject_id, c.hadm_id, c.itemid, c.charttime, \
            c.value, c.valuenum, c.valueuom, c.error \
        FROM chartevents c \
            INNER JOIN v_first_heart_admission v ON v.hadm_id = c.hadm_id \
        WHERE c.itemid = %d AND v.los_icu >= 1 AND c.value is not null \
             AND c.charttime <= (v.admittime + interval '24 hour') \
        ORDER BY c.hadm_id ASC, c.charttime ASC; " % int(itemid)
        df = execute_query_to_df(query)
        df.to_csv(file_name, index=False)


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


def get_events_by_admission(admission_id, itemids=None):
    """
    Get all events by admission including
        chartevents, inputevents, outputevents, microbiologyevents
    In sample demo, we consider only chartvents

    Args:
        admission_id (TYPE): Description
        itemids (None, optional): Description

    Returns:
        TYPE: Description
    """
    query = ''
    if itemids is not None:
        query = 'SELECT charttime, itemid, value, valuenum \
            FROM chartevents \
            WHERE hadm_id=%s AND itemid in (%s) \
            ORDER BY charttime ASC ' % (admission_id, ','.join(itemids))
    else:
        query = 'SELECT charttime, value, valuenum \
            FROM chartevents \
            WHERE hadm_id=%s ORDER BY charttime ASC' % (admission_id)
    logger.info('query="%s"', query)
    df = execute_query_to_df(query)
    logger.info('query finishes, result=%s', df.shape[0])
    return df
