"""Summary

Attributes:
    logger (TYPE): Description
"""
from src.connect_db import *
import logging

logger = logging.getLogger(__name__)


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
    item_condition = ''
    if itemids is not None:
        item_condition = ' itemid in (%s) ' % ','.join(itemids)
    else:
        item_condition = ' 1=1 '

    query = "WITH chartevents_per_ad AS ( \
        SELECT hadm_id, charttime, itemid, value, valuenum FROM chartevents \
        WHERE hadm_id=%s AND %s \
        ORDER BY charttime ASC) \
        SELECT hadm_id, (DATE_PART('day', \
            C.charttime::timestamp - M.min_charttime::timestamp) * 24 + \
            DATE_PART('hour', \
            C.charttime::timestamp - M.min_charttime::timestamp) * 60 + \
            DATE_PART('minute', \
            C.charttime::timestamp - M.min_charttime::timestamp)) \
            AS minutes_ago, itemid, value \
        FROM chartevents_per_ad as C, \
        (SELECT MIN(charttime) as min_charttime FROM chartevents_per_ad) as M \
        ORDER BY minutes_ago ASC, itemid ASC;" % (admission_id, item_condition)

    logger.debug('query=\n"%s"\n', query)
    df = execute_query_to_df(query)
    logger.debug('get_events_by_admission finishes, result=%s', df.shape[0])
    return df


def get_admissions():
    """Summary

    Returns:
        TYPE: Description
    """
    # get all admission id
    # loop through each admission and get its event value
    query = "SELECT DISTINCT hadm_id, gender, marital_status, admission_type, \
            admission_age, los_icu_h \
        FROM v_first_admission"
    df = execute_query_to_df(query)
    logger.info('Number of admissions: %s', df.shape[0])

    return df
